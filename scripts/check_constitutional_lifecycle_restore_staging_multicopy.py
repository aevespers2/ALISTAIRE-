#!/usr/bin/env python3
"""Fail-closed validator for the synthetic restore-staging and multi-copy corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "fixtures" / "constitutional-lifecycle-restore-staging-multicopy-v1.json"
MAX_BYTES = 512 * 1024
SCHEMA = "alistaire.constitutional-lifecycle-restore-staging-multicopy.corpus.v1"
STATUS = "synthetic_only_non_operational"
SOURCE_REPOSITORY = "aevespers2/ALISTAIRE-"
PROFILE = "alistaire.constitutional.lifecycle"

ROOT_FIELDS = {"schema", "profile_version", "status", "cases"}
CASE_FIELDS = {"case_id", "description", "copies", "request", "expected"}
COPY_FIELDS = {
    "copy_id", "available", "manifest_valid", "source_repository", "profile",
    "set_id", "epoch", "state",
}
REQUEST_FIELDS = {
    "target_repository", "expected_profile", "current_epoch", "minimum_quorum",
    "selected_copy_ids", "phase", "commit_marker", "retry_of",
}
EXPECTED_FIELDS = {"disposition", "reason", "state"}
STATE_FIELDS = {
    "sequence", "authority_generation", "credential_generation", "status",
    "suspended_generations", "revoked_generations", "committed_transactions",
    "pending_ack_transaction",
}
EXPECTED_CASE_IDS = {
    "healthy-quorum-commit",
    "one-copy-inaccessible-quorum-met",
    "quorum-not-met",
    "conflicting-state-same-epoch",
    "split-epochs",
    "stale-epoch-anti-rollback",
    "manifest-mismatch-reduces-quorum",
    "verify-only-staged",
    "interrupted-before-commit-aborts",
    "interrupted-after-commit-recovers",
    "retry-after-commit-idempotent",
    "wrong-source-quarantined",
    "wrong-profile-quarantined",
    "revocation-preserved",
    "suspension-preserved",
    "all-copies-inaccessible",
    "selected-copy-missing",
}
STATE_VALUES = {"inactive", "active", "pending_ack", "suspended", "revoked", "rolled_back_pending_ack"}
PHASES = {"verify", "commit", "interrupted_before_commit", "interrupted_after_commit", "retry"}
DISPOSITIONS = {"staged", "converged", "aborted", "quarantined"}
REASONS = {
    "restore_committed",
    "restore_quorum_not_met",
    "restore_copy_conflict",
    "restore_epoch_conflict",
    "restore_anti_rollback",
    "restore_verified_not_committed",
    "restore_interrupted_before_commit",
    "restore_commit_recovered",
    "restore_retry_idempotent",
    "restore_source_mismatch",
    "restore_profile_mismatch",
    "restore_selected_copy_missing",
}
PROHIBITED_TOKENS = {
    "private_key", "secret", "password", "access_token", "credential_value",
    "biometric", "raw_capture", "live_endpoint",
}


class ValidationError(ValueError):
    """Raised when the synthetic corpus fails closed."""


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValidationError(f"non-finite JSON number: {value}")


def load_json_bytes(raw: bytes) -> tuple[dict[str, Any], str]:
    if len(raw) > MAX_BYTES:
        raise ValidationError(f"corpus exceeds {MAX_BYTES} bytes")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValidationError("corpus is not strict UTF-8") from exc
    try:
        value = json.loads(text, object_pairs_hook=_strict_object, parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"malformed JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError("corpus root must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def _check_no_prohibited_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if any(token in key.lower() for token in PROHIBITED_TOKENS):
                raise ValidationError(f"prohibited field at {path}.{key}")
            _check_no_prohibited_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _check_no_prohibited_fields(child, f"{path}[{index}]")
    elif isinstance(value, float) and not math.isfinite(value):
        raise ValidationError(f"non-finite number at {path}")


def _require_exact_fields(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        actual = set(value) if isinstance(value, dict) else set()
        raise ValidationError(
            f"{label}: fields differ; missing={sorted(fields - actual)}, unknown={sorted(actual - fields)}"
        )
    return value


def _require_nonnegative_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValidationError(f"{label} must be a non-negative integer")
    return value


def _require_positive_int(value: Any, label: str) -> int:
    if type(value) is not int or value < 1:
        raise ValidationError(f"{label} must be a positive integer")
    return value


def _require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{label} must be a non-empty string")
    return value


def _require_unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValidationError(f"{label} must be an array of non-empty strings")
    if len(value) != len(set(value)):
        raise ValidationError(f"{label} contains duplicates")
    return value


def _require_unique_ints(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or any(type(item) is not int or item < 0 for item in value):
        raise ValidationError(f"{label} must be an array of non-negative integers")
    if len(value) != len(set(value)):
        raise ValidationError(f"{label} contains duplicates")
    return value


def validate_state(value: Any, label: str) -> dict[str, Any]:
    state = _require_exact_fields(value, STATE_FIELDS, label)
    _require_nonnegative_int(state["sequence"], f"{label}.sequence")
    _require_nonnegative_int(state["authority_generation"], f"{label}.authority_generation")
    _require_nonnegative_int(state["credential_generation"], f"{label}.credential_generation")
    if state["status"] not in STATE_VALUES:
        raise ValidationError(f"{label}.status is unsupported")
    suspended = _require_unique_ints(state["suspended_generations"], f"{label}.suspended_generations")
    revoked = _require_unique_ints(state["revoked_generations"], f"{label}.revoked_generations")
    _require_unique_strings(state["committed_transactions"], f"{label}.committed_transactions")
    pending = state["pending_ack_transaction"]
    if pending is not None and (not isinstance(pending, str) or not pending):
        raise ValidationError(f"{label}.pending_ack_transaction must be null or a non-empty string")
    if set(suspended) & set(revoked):
        raise ValidationError(f"{label}: a generation cannot be both suspended and revoked")
    generation = state["authority_generation"]
    if state["status"] == "suspended" and generation not in suspended:
        raise ValidationError(f"{label}: suspended status must retain its generation")
    if state["status"] == "revoked" and generation not in revoked:
        raise ValidationError(f"{label}: revoked status must retain its generation")
    pending_statuses = {"pending_ack", "rolled_back_pending_ack"}
    if state["status"] in pending_statuses and pending is None:
        raise ValidationError(f"{label}: pending status requires pending_ack_transaction")
    if state["status"] not in pending_statuses and pending is not None:
        raise ValidationError(f"{label}: non-pending status cannot retain pending_ack_transaction")
    return state


def _canonical_state(state: dict[str, Any]) -> str:
    return json.dumps(state, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def validate_copy(value: Any, label: str) -> dict[str, Any]:
    item = _require_exact_fields(value, COPY_FIELDS, label)
    _require_nonempty_string(item["copy_id"], f"{label}.copy_id")
    if type(item["available"]) is not bool:
        raise ValidationError(f"{label}.available must be Boolean")
    if type(item["manifest_valid"]) is not bool:
        raise ValidationError(f"{label}.manifest_valid must be Boolean")
    _require_nonempty_string(item["source_repository"], f"{label}.source_repository")
    _require_nonempty_string(item["profile"], f"{label}.profile")
    _require_nonempty_string(item["set_id"], f"{label}.set_id")
    _require_nonnegative_int(item["epoch"], f"{label}.epoch")
    validate_state(item["state"], f"{label}.state")
    return item


def validate_request(value: Any, label: str) -> dict[str, Any]:
    request = _require_exact_fields(value, REQUEST_FIELDS, label)
    _require_nonempty_string(request["target_repository"], f"{label}.target_repository")
    _require_nonempty_string(request["expected_profile"], f"{label}.expected_profile")
    _require_nonnegative_int(request["current_epoch"], f"{label}.current_epoch")
    _require_positive_int(request["minimum_quorum"], f"{label}.minimum_quorum")
    selected = _require_unique_strings(request["selected_copy_ids"], f"{label}.selected_copy_ids")
    if not selected:
        raise ValidationError(f"{label}.selected_copy_ids cannot be empty")
    if request["phase"] not in PHASES:
        raise ValidationError(f"{label}.phase is unsupported")
    if type(request["commit_marker"]) is not bool:
        raise ValidationError(f"{label}.commit_marker must be Boolean")
    retry_of = request["retry_of"]
    if retry_of is not None and (not isinstance(retry_of, str) or not retry_of):
        raise ValidationError(f"{label}.retry_of must be null or a non-empty string")
    if request["phase"] == "retry" and retry_of is None:
        raise ValidationError(f"{label}: retry phase requires retry_of")
    if request["phase"] != "retry" and retry_of is not None:
        raise ValidationError(f"{label}: retry_of is only valid for retry phase")
    return request


def evaluate_case(case: dict[str, Any]) -> tuple[str, str, dict[str, Any] | None]:
    copies = {item["copy_id"]: item for item in case["copies"]}
    request = case["request"]
    selected_ids = request["selected_copy_ids"]
    if any(copy_id not in copies for copy_id in selected_ids):
        return "quarantined", "restore_selected_copy_missing", None

    selected = [copies[copy_id] for copy_id in selected_ids]
    available = [item for item in selected if item["available"] and item["manifest_valid"]]
    if len(available) < request["minimum_quorum"]:
        return "quarantined", "restore_quorum_not_met", None

    if any(
        item["source_repository"] != SOURCE_REPOSITORY
        or request["target_repository"] != SOURCE_REPOSITORY
        for item in available
    ):
        return "quarantined", "restore_source_mismatch", None
    if any(item["profile"] != PROFILE or request["expected_profile"] != PROFILE for item in available):
        return "quarantined", "restore_profile_mismatch", None

    set_ids = {item["set_id"] for item in available}
    epochs = {item["epoch"] for item in available}
    if len(set_ids) != 1 or len(epochs) != 1:
        return "quarantined", "restore_epoch_conflict", None
    epoch = next(iter(epochs))
    if epoch < request["current_epoch"]:
        return "quarantined", "restore_anti_rollback", None

    canonical_states = {_canonical_state(item["state"]) for item in available}
    if len(canonical_states) != 1:
        return "quarantined", "restore_copy_conflict", None
    state = available[0]["state"]

    phase = request["phase"]
    marker = request["commit_marker"]
    if phase == "verify":
        if marker:
            return "quarantined", "restore_copy_conflict", None
        return "staged", "restore_verified_not_committed", state
    if phase == "interrupted_before_commit":
        if marker:
            return "quarantined", "restore_copy_conflict", None
        return "aborted", "restore_interrupted_before_commit", None
    if phase == "interrupted_after_commit":
        if not marker:
            return "aborted", "restore_interrupted_before_commit", None
        return "converged", "restore_commit_recovered", state
    if phase == "retry":
        if not marker:
            return "aborted", "restore_interrupted_before_commit", None
        return "converged", "restore_retry_idempotent", state
    if not marker:
        return "aborted", "restore_interrupted_before_commit", None
    return "converged", "restore_committed", state


def validate_corpus(value: dict[str, Any]) -> dict[str, Any]:
    root = _require_exact_fields(value, ROOT_FIELDS, "root")
    if root["schema"] != SCHEMA:
        raise ValidationError("unsupported schema")
    if root["profile_version"] != "1.0.0":
        raise ValidationError("unsupported profile_version")
    if root["status"] != STATUS:
        raise ValidationError("status must remain synthetic_only_non_operational")
    cases = root["cases"]
    if not isinstance(cases, list):
        raise ValidationError("cases must be an array")
    case_ids: list[str] = []
    for index, raw_case in enumerate(cases):
        case = _require_exact_fields(raw_case, CASE_FIELDS, f"cases[{index}]")
        case_id = _require_nonempty_string(case["case_id"], f"cases[{index}].case_id")
        _require_nonempty_string(case["description"], f"cases[{index}].description")
        if not isinstance(case["copies"], list) or not case["copies"]:
            raise ValidationError(f"cases[{index}].copies must be a non-empty array")
        copies = [validate_copy(item, f"cases[{index}].copies[{copy_index}]")
                  for copy_index, item in enumerate(case["copies"])]
        copy_ids = [item["copy_id"] for item in copies]
        if len(copy_ids) != len(set(copy_ids)):
            raise ValidationError(f"cases[{index}].copies contains duplicate copy_id")
        request = validate_request(case["request"], f"cases[{index}].request")
        if request["minimum_quorum"] > len(request["selected_copy_ids"]):
            raise ValidationError(f"cases[{index}]: minimum_quorum exceeds selected copies")
        expected = _require_exact_fields(case["expected"], EXPECTED_FIELDS, f"cases[{index}].expected")
        if expected["disposition"] not in DISPOSITIONS:
            raise ValidationError(f"cases[{index}].expected.disposition is unsupported")
        if expected["reason"] not in REASONS:
            raise ValidationError(f"cases[{index}].expected.reason is unsupported")
        expected_state = expected["state"]
        if expected_state is not None:
            validate_state(expected_state, f"cases[{index}].expected.state")
        actual = evaluate_case(case)
        expected_tuple = (expected["disposition"], expected["reason"], expected_state)
        if actual != expected_tuple:
            raise ValidationError(
                f"{case_id}: expected {expected_tuple!r}, evaluator produced {actual!r}"
            )
        case_ids.append(case_id)
    if len(case_ids) != len(set(case_ids)):
        raise ValidationError("duplicate case_id")
    if set(case_ids) != EXPECTED_CASE_IDS:
        raise ValidationError(
            f"fixture coverage differs; missing={sorted(EXPECTED_CASE_IDS - set(case_ids))}, "
            f"unknown={sorted(set(case_ids) - EXPECTED_CASE_IDS)}"
        )
    _check_no_prohibited_fields(root)
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "case_count": len(cases),
        "case_ids": sorted(case_ids),
        "errors": [],
        "authority_effect": "none",
    }


def validate_bytes(raw: bytes, expected_sha256: str | None = None) -> dict[str, Any]:
    value, digest = load_json_bytes(raw)
    if expected_sha256 is not None and digest != expected_sha256:
        raise ValidationError(f"fixture digest mismatch: expected {expected_sha256}, got {digest}")
    report = validate_corpus(value)
    report["sha256"] = digest
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate_bytes(args.fixture.read_bytes(), args.expected_sha256)
    except (OSError, ValidationError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True))
        return 1
    output = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
