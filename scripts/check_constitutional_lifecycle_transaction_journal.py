#!/usr/bin/env python3
"""Fail-closed validator for the synthetic constitutional lifecycle transaction journal."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "fixtures" / "constitutional-lifecycle-transaction-journal-v1.json"
MAX_BYTES = 256 * 1024
SCHEMA = "alistaire.constitutional-lifecycle-transaction-journal.corpus.v1"
STATUS = "synthetic_only_non_operational"
TOP_LEVEL_FIELDS = {"schema", "profile_version", "status", "cases"}
CASE_FIELDS = {
    "case_id", "description", "operation", "current_state", "current_generation",
    "current_credential_generation", "operation_generation",
    "operation_credential_generation", "journal_phase", "interruption",
    "concurrent_operation", "concurrent_generation", "transaction_id",
    "prior_transaction_ids", "ack_generation", "acknowledged_generations",
    "sequence_start", "sequence_values", "expected_state", "expected_reason",
    "expected_effect", "expected_generation", "expected_credential_generation",
}
EXPECTED_CASE_IDS = {
    "replacement-committed-and-acknowledged",
    "concurrent-replacement-conflict",
    "suspension-wins-over-appeal-race",
    "appeal-without-suspension",
    "late-ack-after-generation-change",
    "replayed-acknowledgment-idempotent",
    "credential-generation-rotation",
    "rollback-interrupted-before-commit",
    "rollback-interrupted-after-prepare",
    "rollback-committed-before-ack",
    "recovery-preserves-committed-rollback",
    "corrupted-journal-quarantined",
    "journal-sequence-gap-quarantined",
    "duplicate-transaction-id-quarantined",
    "stale-suspension-after-replacement",
}
OPERATIONS = {
    "replacement", "suspension", "appeal", "propagation_ack",
    "credential_rotation", "rollback", "recovery",
}
STATES = {
    "active", "suspended", "appeal_pending", "suspended_appeal_pending",
    "replaced", "rolled_back", "rolled_back_pending_ack",
    "pending_propagation", "quarantined",
}
PHASES = {"none", "prepared", "committed", "acknowledged", "corrupt"}
INTERRUPTIONS = {"none", "before_commit", "after_prepare", "after_commit_before_ack"}
CONCURRENT_OPERATIONS = {None, "replacement", "suspension", "appeal", "rollback"}
REASONS = {
    "replacement_committed", "replacement_committed_unacknowledged",
    "concurrent_replacement_conflict", "suspension_recorded",
    "suspension_precedence", "appeal_recorded", "stale_ack_rejected",
    "acknowledgment_idempotent", "propagation_acknowledged",
    "credential_rotation_pending_ack", "prior_state_preserved",
    "prepared_state_discarded", "rollback_committed_unacknowledged",
    "rollback_complete", "recovery_preserved_committed_state",
    "journal_corrupt", "journal_sequence_gap", "duplicate_transaction_id",
    "stale_operation_rejected", "recovery_noop",
}
EFFECTS = {"none", "record_only", "restoration_only", "synthetic_bounded_active"}
PROHIBITED_FIELD_TOKENS = {
    "password", "secret", "private_key", "token", "credential_value",
    "biometric", "raw_capture", "api_key",
}


class ValidationError(ValueError):
    """Raised when the journal corpus fails a bounded check."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValidationError(f"non-finite JSON number: {value}")


def load_json_bytes(raw: bytes) -> Any:
    if len(raw) > MAX_BYTES:
        raise ValidationError(f"corpus exceeds {MAX_BYTES} bytes")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationError("corpus is not strict UTF-8") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValidationError(f"malformed JSON: {exc.msg}") from exc


def _check_no_prohibited_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if any(token in key.lower() for token in PROHIBITED_FIELD_TOKENS):
                raise ValidationError(f"prohibited field at {path}.{key}")
            _check_no_prohibited_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_no_prohibited_fields(child, f"{path}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValidationError(f"non-finite number at {path}")


def _state_effect(state: str) -> str:
    if state == "active":
        return "synthetic_bounded_active"
    if state == "replaced":
        return "record_only"
    if state in {"rolled_back", "rolled_back_pending_ack"}:
        return "restoration_only"
    return "none"


def _preserve(case: dict[str, Any], reason: str) -> tuple[str, str, str, int, int]:
    state = case["current_state"]
    return (
        state,
        reason,
        _state_effect(state),
        case["current_generation"],
        case["current_credential_generation"],
    )


def _has_sequence_gap(case: dict[str, Any]) -> bool:
    start = case["sequence_start"]
    return case["sequence_values"] != list(
        range(start + 1, start + 1 + len(case["sequence_values"]))
    )


def derive_outcome(case: dict[str, Any]) -> tuple[str, str, str, int, int]:
    if case["journal_phase"] == "corrupt":
        return (
            "quarantined", "journal_corrupt", "none",
            case["current_generation"], case["current_credential_generation"],
        )
    if _has_sequence_gap(case):
        return (
            "quarantined", "journal_sequence_gap", "none",
            case["current_generation"], case["current_credential_generation"],
        )
    if case["transaction_id"] in case["prior_transaction_ids"]:
        return (
            "quarantined", "duplicate_transaction_id", "none",
            case["current_generation"], case["current_credential_generation"],
        )

    operation = case["operation"]
    current_generation = case["current_generation"]
    current_credential = case["current_credential_generation"]
    operation_generation = case["operation_generation"]
    operation_credential = case["operation_credential_generation"]

    if case["interruption"] == "before_commit":
        return _preserve(case, "prior_state_preserved")
    if case["interruption"] == "after_prepare":
        return _preserve(case, "prepared_state_discarded")

    if operation == "replacement":
        if (
            case["concurrent_operation"] == "replacement"
            and case["concurrent_generation"] == operation_generation
        ):
            return _preserve(case, "concurrent_replacement_conflict")
        if operation_generation != current_generation + 1 or operation_credential != current_credential:
            return _preserve(case, "stale_operation_rejected")
        if case["journal_phase"] == "acknowledged" and case["ack_generation"] == operation_generation:
            return (
                "replaced", "replacement_committed", "record_only",
                operation_generation, current_credential,
            )
        if case["journal_phase"] == "committed" or case["interruption"] == "after_commit_before_ack":
            return (
                "pending_propagation", "replacement_committed_unacknowledged", "none",
                operation_generation, current_credential,
            )
        return _preserve(case, "prior_state_preserved")

    if operation == "suspension":
        if operation_generation != current_generation or operation_credential != current_credential:
            return _preserve(case, "stale_operation_rejected")
        if (
            case["concurrent_operation"] == "appeal"
            and case["concurrent_generation"] == current_generation
        ):
            return (
                "suspended_appeal_pending", "suspension_precedence", "none",
                current_generation, current_credential,
            )
        return (
            "suspended", "suspension_recorded", "none",
            current_generation, current_credential,
        )

    if operation == "appeal":
        if operation_generation != current_generation or operation_credential != current_credential:
            return _preserve(case, "stale_operation_rejected")
        if (
            case["concurrent_operation"] == "suspension"
            and case["concurrent_generation"] == current_generation
        ):
            return (
                "suspended_appeal_pending", "suspension_precedence", "none",
                current_generation, current_credential,
            )
        return (
            "appeal_pending", "appeal_recorded", "none",
            current_generation, current_credential,
        )

    if operation == "propagation_ack":
        if case["ack_generation"] != current_generation or operation_credential != current_credential:
            return _preserve(case, "stale_ack_rejected")
        if case["ack_generation"] in case["acknowledged_generations"]:
            return _preserve(case, "acknowledgment_idempotent")
        return (
            "active", "propagation_acknowledged", "synthetic_bounded_active",
            current_generation, current_credential,
        )

    if operation == "credential_rotation":
        if operation_generation != current_generation or operation_credential != current_credential + 1:
            return _preserve(case, "stale_operation_rejected")
        return (
            "pending_propagation", "credential_rotation_pending_ack", "none",
            current_generation, operation_credential,
        )

    if operation == "rollback":
        if operation_generation >= current_generation or operation_credential != current_credential:
            return _preserve(case, "stale_operation_rejected")
        if case["journal_phase"] == "acknowledged" and case["ack_generation"] == operation_generation:
            return (
                "rolled_back", "rollback_complete", "restoration_only",
                operation_generation, current_credential,
            )
        if case["journal_phase"] == "committed" or case["interruption"] == "after_commit_before_ack":
            return (
                "rolled_back_pending_ack", "rollback_committed_unacknowledged",
                "restoration_only", operation_generation, current_credential,
            )
        return _preserve(case, "prior_state_preserved")

    if operation == "recovery":
        if case["journal_phase"] == "prepared":
            return _preserve(case, "prepared_state_discarded")
        if case["journal_phase"] == "committed":
            if operation_generation >= current_generation:
                return _preserve(case, "stale_operation_rejected")
            return (
                "rolled_back_pending_ack", "recovery_preserved_committed_state",
                "restoration_only", operation_generation, current_credential,
            )
        if case["journal_phase"] == "acknowledged":
            if operation_generation >= current_generation:
                return _preserve(case, "stale_operation_rejected")
            return (
                "rolled_back", "rollback_complete", "restoration_only",
                operation_generation, current_credential,
            )
        return _preserve(case, "recovery_noop")

    raise ValidationError(f"unsupported operation: {operation}")


def _validate_string_list(value: Any, name: str, case_id: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValidationError(f"{case_id}: {name} must be an array of non-empty strings")
    if len(value) != len(set(value)):
        raise ValidationError(f"{case_id}: {name} contains duplicates")


def _validate_int_list(value: Any, name: str, case_id: str) -> None:
    if not isinstance(value, list) or any(type(item) is not int or item < 0 for item in value):
        raise ValidationError(f"{case_id}: {name} must be an array of non-negative integers")
    if len(value) != len(set(value)):
        raise ValidationError(f"{case_id}: {name} contains duplicates")


def validate_corpus(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or set(data) != TOP_LEVEL_FIELDS:
        raise ValidationError("invalid top-level fields")
    if data["schema"] != SCHEMA or data["profile_version"] != "1.0.0":
        raise ValidationError("unexpected schema or profile version")
    if data["status"] != STATUS:
        raise ValidationError(f"status must be {STATUS!r}")
    if not isinstance(data["cases"], list):
        raise ValidationError("cases must be an array")
    _check_no_prohibited_fields(data)

    seen: set[str] = set()
    for case in data["cases"]:
        if not isinstance(case, dict) or set(case) != CASE_FIELDS:
            raise ValidationError("invalid case fields")
        case_id = case["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValidationError("case_id must be a non-empty string")
        if case_id in seen:
            raise ValidationError(f"duplicate case_id: {case_id}")
        seen.add(case_id)
        if not isinstance(case["description"], str) or len(case["description"].strip()) < 20:
            raise ValidationError(f"{case_id}: description is too short")
        if case["operation"] not in OPERATIONS:
            raise ValidationError(f"{case_id}: unsupported operation")
        if case["current_state"] not in STATES - {"quarantined"}:
            raise ValidationError(f"{case_id}: unsupported current_state")
        if case["journal_phase"] not in PHASES:
            raise ValidationError(f"{case_id}: unsupported journal_phase")
        if case["interruption"] not in INTERRUPTIONS:
            raise ValidationError(f"{case_id}: unsupported interruption")
        if case["concurrent_operation"] not in CONCURRENT_OPERATIONS:
            raise ValidationError(f"{case_id}: unsupported concurrent_operation")
        if case["concurrent_operation"] is None:
            if case["concurrent_generation"] is not None:
                raise ValidationError(f"{case_id}: concurrent_generation requires an operation")
        elif type(case["concurrent_generation"]) is not int or case["concurrent_generation"] < 0:
            raise ValidationError(f"{case_id}: concurrent_generation must be non-negative")
        for name in (
            "current_generation", "current_credential_generation",
            "operation_generation", "operation_credential_generation",
            "sequence_start", "expected_generation",
            "expected_credential_generation",
        ):
            if type(case[name]) is not int or case[name] < 0:
                raise ValidationError(f"{case_id}: {name} must be a non-negative integer")
        if case["ack_generation"] is not None and (
            type(case["ack_generation"]) is not int or case["ack_generation"] < 0
        ):
            raise ValidationError(f"{case_id}: ack_generation must be null or non-negative")
        if not isinstance(case["transaction_id"], str) or not case["transaction_id"]:
            raise ValidationError(f"{case_id}: transaction_id must be a non-empty string")
        _validate_string_list(case["prior_transaction_ids"], "prior_transaction_ids", case_id)
        _validate_int_list(case["acknowledged_generations"], "acknowledged_generations", case_id)
        _validate_int_list(case["sequence_values"], "sequence_values", case_id)
        if case["expected_state"] not in STATES:
            raise ValidationError(f"{case_id}: unsupported expected_state")
        if case["expected_reason"] not in REASONS:
            raise ValidationError(f"{case_id}: unsupported expected_reason")
        if case["expected_effect"] not in EFFECTS:
            raise ValidationError(f"{case_id}: unsupported expected_effect")
        expected = (
            case["expected_state"], case["expected_reason"], case["expected_effect"],
            case["expected_generation"], case["expected_credential_generation"],
        )
        actual = derive_outcome(case)
        if actual != expected:
            raise ValidationError(f"{case_id}: expected {expected!r}, derived {actual!r}")

    if seen != EXPECTED_CASE_IDS:
        missing = sorted(EXPECTED_CASE_IDS - seen)
        extra = sorted(seen - EXPECTED_CASE_IDS)
        raise ValidationError(f"fixture coverage drift: missing={missing}, extra={extra}")
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "cases": len(seen),
        "case_ids": sorted(seen),
    }


def validate_bytes(raw: bytes) -> dict[str, Any]:
    return validate_corpus(load_json_bytes(raw))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", nargs="?", type=Path, default=DEFAULT_CORPUS)
    args = parser.parse_args(argv)
    try:
        result = validate_bytes(args.corpus.read_bytes())
    except (OSError, ValidationError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
