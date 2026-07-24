#!/usr/bin/env python3
"""Fail-closed validator for the synthetic lifecycle backup/restore corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "fixtures" / "constitutional-lifecycle-backup-restore-v1.json"
MAX_BYTES = 512 * 1024
SCHEMA = "alistaire.constitutional-lifecycle-backup-restore.corpus.v1"
STATUS = "synthetic_only_non_operational"
SOURCE_REPOSITORY = "aevespers2/ALISTAIRE-"
PROFILE = "alistaire.constitutional.lifecycle"

ROOT_FIELDS = {"schema", "profile_version", "status", "cases"}
CASE_FIELDS = {"case_id", "description", "backup", "restore", "expected"}
BACKUP_FIELDS = {"phase", "manifest_valid", "source_repository", "profile", "backup_epoch", "state"}
RESTORE_FIELDS = {
    "target_repository", "expected_profile", "requested_epoch",
    "journal_head_sequence", "log_floor", "retained_events",
    "replay_transaction_id", "required_suspended_generations",
    "required_revoked_generations",
}
EXPECTED_FIELDS = {"disposition", "reason", "state"}
STATE_FIELDS = {
    "sequence", "authority_generation", "credential_generation", "status",
    "suspended_generations", "revoked_generations", "committed_transactions",
    "pending_ack_transaction",
}
EVENT_FIELDS = {
    "sequence", "transaction_id", "operation", "authority_generation",
    "credential_generation", "reference_transaction_id",
}
EXPECTED_CASE_IDS = {
    "healthy-backup-restore", "stale-backup-complete-log-converges",
    "stale-backup-pruned-log-quarantined", "partial-backup-quarantined",
    "manifest-mismatch-quarantined", "wrong-source-repository-quarantined",
    "wrong-profile-quarantined", "backup-epoch-mismatch-quarantined",
    "backup-ahead-of-journal-quarantined", "revocation-preserved",
    "suspension-preserved", "missing-revocation-quarantined",
    "post-restore-replay-blocked", "unknown-replay-target-quarantined",
    "rollback-across-compaction-converges",
    "rollback-cannot-resurrect-revoked-authority", "lost-ack-remains-pending",
}
STATE_VALUES = {"inactive", "active", "pending_ack", "suspended", "revoked", "rolled_back_pending_ack"}
OPERATIONS = {"replacement", "suspend", "revoke", "credential_rotate", "acknowledge", "rollback"}
BACKUP_PHASES = {"complete", "partial", "absent"}
DISPOSITIONS = {"converged", "quarantined"}
REASONS = {
    "state_restored", "log_replay_converged", "restore_log_gap",
    "backup_incomplete", "backup_manifest_mismatch", "backup_source_mismatch",
    "backup_profile_mismatch", "backup_epoch_mismatch", "backup_ahead_of_journal",
    "revocation_preserved", "suspension_preserved", "required_revocation_missing",
    "replay_blocked", "unknown_replay_target", "rollback_pending_ack",
    "revoked_authority_resurrection_blocked", "pending_ack_preserved",
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


def _require_unique_ints(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or any(type(item) is not int or item < 0 for item in value):
        raise ValidationError(f"{label} must be an array of non-negative integers")
    if len(value) != len(set(value)):
        raise ValidationError(f"{label} contains duplicates")
    return value


def _require_unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValidationError(f"{label} must be an array of non-empty strings")
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
    if state["status"] == "suspended" and state["authority_generation"] not in suspended:
        raise ValidationError(f"{label}: suspended status must retain its generation")
    if state["status"] == "revoked" and state["authority_generation"] not in revoked:
        raise ValidationError(f"{label}: revoked status must retain its generation")
    pending_statuses = {"pending_ack", "rolled_back_pending_ack"}
    if state["status"] in pending_statuses and pending is None:
        raise ValidationError(f"{label}: pending status requires pending_ack_transaction")
    if state["status"] not in pending_statuses and pending is not None:
        raise ValidationError(f"{label}: non-pending status cannot retain pending_ack_transaction")
    return state


def validate_event(value: Any, label: str) -> dict[str, Any]:
    event = _require_exact_fields(value, EVENT_FIELDS, label)
    _require_nonnegative_int(event["sequence"], f"{label}.sequence")
    if not isinstance(event["transaction_id"], str) or not event["transaction_id"]:
        raise ValidationError(f"{label}.transaction_id must be a non-empty string")
    if event["operation"] not in OPERATIONS:
        raise ValidationError(f"{label}.operation is unsupported")
    _require_nonnegative_int(event["authority_generation"], f"{label}.authority_generation")
    _require_nonnegative_int(event["credential_generation"], f"{label}.credential_generation")
    reference = event["reference_transaction_id"]
    if reference is not None and (not isinstance(reference, str) or not reference):
        raise ValidationError(f"{label}.reference_transaction_id must be null or a non-empty string")
    return event


def _copy_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "sequence": state["sequence"],
        "authority_generation": state["authority_generation"],
        "credential_generation": state["credential_generation"],
        "status": state["status"],
        "suspended_generations": list(state["suspended_generations"]),
        "revoked_generations": list(state["revoked_generations"]),
        "committed_transactions": list(state["committed_transactions"]),
        "pending_ack_transaction": state["pending_ack_transaction"],
    }


def _apply_event(state: dict[str, Any], event: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    output = _copy_state(state)
    tx_id = event["transaction_id"]
    if tx_id in output["committed_transactions"]:
        return output, "duplicate"
    if event["sequence"] != output["sequence"] + 1:
        return output, "sequence_gap"
    operation = event["operation"]
    generation = event["authority_generation"]
    credential = event["credential_generation"]
    if operation == "replacement":
        if output["status"] == "revoked" or generation in output["revoked_generations"]:
            return output, "resurrection"
        if generation != output["authority_generation"] + 1:
            return output, "stale"
        output["authority_generation"] = generation
        output["status"] = "active"
        output["pending_ack_transaction"] = None
    elif operation == "suspend":
        if generation != output["authority_generation"] or credential != output["credential_generation"]:
            return output, "stale"
        if generation not in output["suspended_generations"]:
            output["suspended_generations"].append(generation)
            output["suspended_generations"].sort()
        output["status"] = "suspended"
        output["pending_ack_transaction"] = None
    elif operation == "revoke":
        if generation != output["authority_generation"] or credential != output["credential_generation"]:
            return output, "stale"
        if generation in output["suspended_generations"]:
            output["suspended_generations"].remove(generation)
        if generation not in output["revoked_generations"]:
            output["revoked_generations"].append(generation)
            output["revoked_generations"].sort()
        output["status"] = "revoked"
        output["pending_ack_transaction"] = None
    elif operation == "credential_rotate":
        if generation != output["authority_generation"] or credential != output["credential_generation"] + 1:
            return output, "stale"
        if output["status"] == "revoked":
            return output, "resurrection"
        output["credential_generation"] = credential
        output["status"] = "pending_ack"
        output["pending_ack_transaction"] = tx_id
    elif operation == "acknowledge":
        if generation != output["authority_generation"] or credential != output["credential_generation"]:
            return output, "stale"
        if event["reference_transaction_id"] != output["pending_ack_transaction"]:
            return output, "stale"
        output["status"] = "active"
        output["pending_ack_transaction"] = None
    elif operation == "rollback":
        if generation >= output["authority_generation"] or credential != output["credential_generation"]:
            return output, "stale"
        if generation in output["revoked_generations"] or output["status"] == "revoked":
            return output, "resurrection"
        output["authority_generation"] = generation
        output["status"] = "rolled_back_pending_ack"
        output["pending_ack_transaction"] = tx_id
    output["sequence"] = event["sequence"]
    output["committed_transactions"].append(tx_id)
    return output, None


def evaluate_case(case: dict[str, Any]) -> tuple[str, str, dict[str, Any] | None]:
    backup = case["backup"]
    restore = case["restore"]
    if backup["phase"] != "complete" or backup["state"] is None:
        return "quarantined", "backup_incomplete", None
    if backup["manifest_valid"] is not True:
        return "quarantined", "backup_manifest_mismatch", None
    if backup["source_repository"] != SOURCE_REPOSITORY or restore["target_repository"] != SOURCE_REPOSITORY:
        return "quarantined", "backup_source_mismatch", None
    if backup["profile"] != PROFILE or restore["expected_profile"] != PROFILE:
        return "quarantined", "backup_profile_mismatch", None
    if backup["backup_epoch"] != restore["requested_epoch"]:
        return "quarantined", "backup_epoch_mismatch", None
    state = _copy_state(backup["state"])
    if state["sequence"] > restore["journal_head_sequence"]:
        return "quarantined", "backup_ahead_of_journal", None
    events = restore["retained_events"]
    if state["sequence"] < restore["journal_head_sequence"]:
        required_start = state["sequence"] + 1
        if restore["log_floor"] > required_start or not events or events[0]["sequence"] != required_start:
            return "quarantined", "restore_log_gap", None
    for event in events:
        state, error = _apply_event(state, event)
        if error == "resurrection":
            return "quarantined", "revoked_authority_resurrection_blocked", None
        if error in {"stale", "sequence_gap", "duplicate"}:
            return "quarantined", "restore_log_gap", None
    if state["sequence"] != restore["journal_head_sequence"]:
        return "quarantined", "restore_log_gap", None
    if not set(restore["required_revoked_generations"]).issubset(set(state["revoked_generations"])):
        return "quarantined", "required_revocation_missing", None
    if not set(restore["required_suspended_generations"]).issubset(set(state["suspended_generations"])):
        return "quarantined", "required_revocation_missing", None
    replay = restore["replay_transaction_id"]
    if replay is not None:
        if replay in state["committed_transactions"]:
            return "converged", "replay_blocked", state
        return "quarantined", "unknown_replay_target", None
    if state["status"] == "revoked":
        return "converged", "revocation_preserved", state
    if state["status"] == "suspended":
        return "converged", "suspension_preserved", state
    if state["status"] in {"pending_ack", "rolled_back_pending_ack"}:
        reason = "rollback_pending_ack" if state["status"] == "rolled_back_pending_ack" else "pending_ack_preserved"
        return "converged", reason, state
    if events:
        return "converged", "log_replay_converged", state
    return "converged", "state_restored", state


def validate_corpus(document: dict[str, Any]) -> dict[str, Any]:
    _require_exact_fields(document, ROOT_FIELDS, "root")
    if document["schema"] != SCHEMA:
        raise ValidationError("unsupported schema")
    if document["profile_version"] != "1.0.0":
        raise ValidationError("unsupported profile version")
    if document["status"] != STATUS:
        raise ValidationError("corpus must remain synthetic and non-operational")
    _check_no_prohibited_fields(document)
    cases = document["cases"]
    if not isinstance(cases, list):
        raise ValidationError("cases must be an array")
    case_ids: list[str] = []
    results: list[dict[str, Any]] = []
    for index, value in enumerate(cases):
        case = _require_exact_fields(value, CASE_FIELDS, f"cases[{index}]")
        case_id = case["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValidationError(f"cases[{index}].case_id must be a non-empty string")
        if not isinstance(case["description"], str) or not case["description"]:
            raise ValidationError(f"cases[{index}].description must be a non-empty string")
        case_ids.append(case_id)
        backup = _require_exact_fields(case["backup"], BACKUP_FIELDS, f"{case_id}.backup")
        if backup["phase"] not in BACKUP_PHASES:
            raise ValidationError(f"{case_id}.backup.phase is unsupported")
        if type(backup["manifest_valid"]) is not bool:
            raise ValidationError(f"{case_id}.backup.manifest_valid must be Boolean")
        for key in ("source_repository", "profile"):
            if not isinstance(backup[key], str) or not backup[key]:
                raise ValidationError(f"{case_id}.backup.{key} must be non-empty")
        _require_nonnegative_int(backup["backup_epoch"], f"{case_id}.backup.backup_epoch")
        if backup["state"] is not None:
            validate_state(backup["state"], f"{case_id}.backup.state")
        restore = _require_exact_fields(case["restore"], RESTORE_FIELDS, f"{case_id}.restore")
        for key in ("target_repository", "expected_profile"):
            if not isinstance(restore[key], str) or not restore[key]:
                raise ValidationError(f"{case_id}.restore.{key} must be non-empty")
        _require_nonnegative_int(restore["requested_epoch"], f"{case_id}.restore.requested_epoch")
        _require_nonnegative_int(restore["journal_head_sequence"], f"{case_id}.restore.journal_head_sequence")
        _require_nonnegative_int(restore["log_floor"], f"{case_id}.restore.log_floor")
        _require_unique_ints(restore["required_suspended_generations"], f"{case_id}.restore.required_suspended_generations")
        _require_unique_ints(restore["required_revoked_generations"], f"{case_id}.restore.required_revoked_generations")
        replay = restore["replay_transaction_id"]
        if replay is not None and (not isinstance(replay, str) or not replay):
            raise ValidationError(f"{case_id}.restore.replay_transaction_id is invalid")
        events = restore["retained_events"]
        if not isinstance(events, list):
            raise ValidationError(f"{case_id}.restore.retained_events must be an array")
        tx_ids: list[str] = []
        for event_index, event_value in enumerate(events):
            event = validate_event(event_value, f"{case_id}.restore.retained_events[{event_index}]")
            tx_ids.append(event["transaction_id"])
        if len(tx_ids) != len(set(tx_ids)):
            raise ValidationError(f"{case_id}.restore.retained_events contains duplicate transactions")
        expected = _require_exact_fields(case["expected"], EXPECTED_FIELDS, f"{case_id}.expected")
        if expected["disposition"] not in DISPOSITIONS:
            raise ValidationError(f"{case_id}.expected.disposition is unsupported")
        if expected["reason"] not in REASONS:
            raise ValidationError(f"{case_id}.expected.reason is unsupported")
        if expected["state"] is not None:
            validate_state(expected["state"], f"{case_id}.expected.state")
        actual_disposition, actual_reason, actual_state = evaluate_case(case)
        if actual_disposition != expected["disposition"] or actual_reason != expected["reason"] or actual_state != expected["state"]:
            raise ValidationError(
                f"{case_id}: expected {expected!r}, got disposition={actual_disposition!r}, reason={actual_reason!r}, state={actual_state!r}"
            )
        results.append({"case_id": case_id, "disposition": actual_disposition, "reason": actual_reason})
    if len(case_ids) != len(set(case_ids)):
        raise ValidationError("case identifiers must be unique")
    if set(case_ids) != EXPECTED_CASE_IDS:
        raise ValidationError(
            f"case coverage differs; missing={sorted(EXPECTED_CASE_IDS - set(case_ids))}, unknown={sorted(set(case_ids) - EXPECTED_CASE_IDS)}"
        )
    return {"schema": SCHEMA, "status": "PASS", "case_count": len(results), "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        raw = args.fixture.read_bytes()
        document, digest = load_json_bytes(raw)
        if args.expected_sha256 and digest != args.expected_sha256:
            raise ValidationError(f"fixture SHA-256 mismatch: expected {args.expected_sha256}, got {digest}")
        report = validate_corpus(document)
        report["sha256"] = digest
    except (OSError, ValidationError) as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    encoded = json.dumps(report, indent=2, sort_keys=True)
    print(encoded)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
