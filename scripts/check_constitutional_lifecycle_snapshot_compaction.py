#!/usr/bin/env python3
"""Fail-closed validator for the synthetic lifecycle snapshot/compaction corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "fixtures" / "constitutional-lifecycle-snapshot-compaction-v1.json"
MAX_BYTES = 512 * 1024
SCHEMA = "alistaire.constitutional-lifecycle-snapshot-compaction.corpus.v1"
STATUS = "synthetic_only_non_operational"
ROOT_FIELDS = {"schema", "profile_version", "status", "cases"}
CASE_FIELDS = {
    "case_id", "description", "initial_state", "journal_floor", "journal",
    "snapshot", "compaction", "expected",
}
STATE_FIELDS = {
    "sequence", "authority_generation", "credential_generation", "status",
    "suspended_generations", "revoked_generations", "committed_transactions",
    "pending_ack_transaction",
}
ENTRY_FIELDS = {
    "sequence", "transaction_id", "operation", "authority_generation",
    "credential_generation", "reference_transaction_id", "payload_digest", "phase",
}
SNAPSHOT_FIELDS = {"phase", "sequence", "digest_valid", "state"}
COMPACTION_FIELDS = {"phase", "cutoff_sequence", "interruption"}
EXPECTED_FIELDS = {"disposition", "reason", "state"}
EXPECTED_CASE_IDS = {
    "healthy-compaction",
    "torn-snapshot-full-log-replay",
    "torn-snapshot-after-prune-quarantined",
    "snapshot-log-divergence-quarantined",
    "compaction-interrupted-before-prune-converges",
    "compaction-interrupted-after-prune-converges",
    "duplicate-commit-idempotent",
    "conflicting-duplicate-commit-quarantined",
    "lost-ack-preserves-pending-state",
    "suspension-survives-compaction",
    "revocation-survives-compaction",
    "replacement-cannot-resurrect-revoked-authority",
    "log-sequence-gap-quarantined",
    "compaction-cutoff-beyond-snapshot-quarantined",
    "acknowledgment-after-compaction-converges",
}
STATE_VALUES = {
    "inactive", "active", "pending_ack", "suspended", "revoked",
    "rolled_back_pending_ack",
}
OPERATIONS = {
    "replacement", "suspend", "revoke", "credential_rotate",
    "acknowledge", "rollback",
}
ENTRY_PHASES = {"prepared", "committed"}
SNAPSHOT_PHASES = {"absent", "prepared", "committed", "torn"}
COMPACTION_PHASES = {"none", "prepared", "committed"}
INTERRUPTIONS = {
    "none", "before_snapshot_commit", "after_snapshot_commit_before_prune",
    "after_prune_before_ack",
}
DISPOSITIONS = {"converged", "quarantined"}
REASONS = {
    "state_converged", "full_log_replay", "snapshot_unrecoverable_after_prune",
    "snapshot_log_divergence", "duplicate_commit_idempotent",
    "conflicting_duplicate_transaction", "pending_ack_preserved",
    "suspension_preserved", "revocation_preserved",
    "superseded_authority_resurrection_blocked", "journal_sequence_gap",
    "compaction_cutoff_beyond_snapshot", "acknowledgment_converged",
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
        value = json.loads(
            text,
            object_pairs_hook=_strict_object,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValidationError(f"malformed JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValidationError("corpus root must be an object")
    return value, hashlib.sha256(raw).hexdigest()


def _check_no_prohibited_fields(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            lowered = key.lower()
            if any(token in lowered for token in PROHIBITED_TOKENS):
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
            f"{label}: fields differ; missing={sorted(fields - actual)}, "
            f"unknown={sorted(actual - fields)}"
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
    if state["status"] in {"pending_ack", "rolled_back_pending_ack"} and pending is None:
        raise ValidationError(f"{label}: pending status requires pending_ack_transaction")
    if state["status"] not in {"pending_ack", "rolled_back_pending_ack"} and pending is not None:
        raise ValidationError(f"{label}: non-pending status cannot retain pending_ack_transaction")
    return state


def validate_entry(value: Any, label: str) -> dict[str, Any]:
    entry = _require_exact_fields(value, ENTRY_FIELDS, label)
    _require_nonnegative_int(entry["sequence"], f"{label}.sequence")
    if not isinstance(entry["transaction_id"], str) or not entry["transaction_id"]:
        raise ValidationError(f"{label}.transaction_id must be a non-empty string")
    if entry["operation"] not in OPERATIONS:
        raise ValidationError(f"{label}.operation is unsupported")
    _require_nonnegative_int(entry["authority_generation"], f"{label}.authority_generation")
    _require_nonnegative_int(entry["credential_generation"], f"{label}.credential_generation")
    reference = entry["reference_transaction_id"]
    if reference is not None and (not isinstance(reference, str) or not reference):
        raise ValidationError(f"{label}.reference_transaction_id must be null or a non-empty string")
    digest = entry["payload_digest"]
    if (
        not isinstance(digest, str)
        or len(digest) != 64
        or any(char not in "0123456789abcdef" for char in digest)
    ):
        raise ValidationError(f"{label}.payload_digest must be lowercase SHA-256 hex")
    if entry["phase"] not in ENTRY_PHASES:
        raise ValidationError(f"{label}.phase is unsupported")
    return entry


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


def _entry_identity(entry: dict[str, Any]) -> tuple[Any, ...]:
    return (
        entry["operation"],
        entry["authority_generation"],
        entry["credential_generation"],
        entry["reference_transaction_id"],
        entry["payload_digest"],
        entry["phase"],
    )


def _apply_entry(state: dict[str, Any], entry: dict[str, Any]) -> tuple[dict[str, Any], str | None]:
    output = _copy_state(state)
    output["sequence"] = entry["sequence"]
    if entry["phase"] == "prepared":
        return output, None

    tx_id = entry["transaction_id"]
    if tx_id in output["committed_transactions"]:
        return output, "duplicate"

    operation = entry["operation"]
    generation = entry["authority_generation"]
    credential = entry["credential_generation"]

    if operation == "replacement":
        if output["status"] == "revoked" or generation in output["revoked_generations"]:
            return output, "resurrection"
        if generation != output["authority_generation"] + 1:
            return output, "stale"
        if credential != output["credential_generation"]:
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
        if entry["reference_transaction_id"] != output["pending_ack_transaction"]:
            if entry["reference_transaction_id"] in output["committed_transactions"]:
                output["committed_transactions"].append(tx_id)
                return output, "ack_idempotent"
            return output, "stale"
        output["status"] = "active"
        output["pending_ack_transaction"] = None
    elif operation == "rollback":
        if generation >= output["authority_generation"] or credential != output["credential_generation"]:
            return output, "stale"
        if output["status"] == "revoked" or generation in output["revoked_generations"]:
            return output, "resurrection"
        output["authority_generation"] = generation
        output["status"] = "rolled_back_pending_ack"
        output["pending_ack_transaction"] = tx_id
    else:
        raise ValidationError(f"unsupported operation: {operation}")

    output["committed_transactions"].append(tx_id)
    return output, None


def _state_for_compare(state: dict[str, Any]) -> dict[str, Any]:
    value = _copy_state(state)
    value["suspended_generations"].sort()
    value["revoked_generations"].sort()
    return value


def derive_case(case: dict[str, Any]) -> tuple[str, str, dict[str, Any] | None]:
    initial = _copy_state(case["initial_state"])
    journal = case["journal"]
    snapshot = case["snapshot"]
    compaction = case["compaction"]

    if (
        compaction["phase"] == "committed"
        and snapshot["phase"] == "committed"
        and compaction["cutoff_sequence"] > snapshot["sequence"]
    ):
        return "quarantined", "compaction_cutoff_beyond_snapshot", None

    committed_snapshot = snapshot["phase"] == "committed" and snapshot["digest_valid"]
    if committed_snapshot:
        base = _copy_state(snapshot["state"])
        if base["sequence"] != snapshot["sequence"]:
            return "quarantined", "snapshot_log_divergence", None
        prefix = [entry for entry in journal if entry["sequence"] <= snapshot["sequence"]]
        if case["journal_floor"] <= initial["sequence"] + 1 and prefix:
            replay = _copy_state(initial)
            seen_payloads: dict[str, tuple[Any, ...]] = {}
            expected_sequence = initial["sequence"] + 1
            for entry in prefix:
                if entry["sequence"] != expected_sequence:
                    return "quarantined", "journal_sequence_gap", None
                expected_sequence += 1
                identity = _entry_identity(entry)
                prior = seen_payloads.get(entry["transaction_id"])
                if prior is not None and prior != identity:
                    return "quarantined", "conflicting_duplicate_transaction", None
                seen_payloads.setdefault(entry["transaction_id"], identity)
                replay, signal = _apply_entry(replay, entry)
                if signal == "resurrection":
                    return "quarantined", "superseded_authority_resurrection_blocked", None
            if _state_for_compare(replay) != _state_for_compare(base):
                return "quarantined", "snapshot_log_divergence", None
    else:
        if case["journal_floor"] != initial["sequence"] + 1:
            return "quarantined", "snapshot_unrecoverable_after_prune", None
        base = _copy_state(initial)

    entries = [entry for entry in journal if entry["sequence"] > base["sequence"]]
    if entries:
        expected_sequence = max(case["journal_floor"], base["sequence"] + 1)
        if entries[0]["sequence"] != expected_sequence:
            return "quarantined", "journal_sequence_gap", None
    seen: dict[str, tuple[Any, ...]] = {}
    duplicate_idempotent = False
    ack_idempotent = False
    state = base
    for entry in entries:
        if entry["sequence"] != state["sequence"] + 1:
            return "quarantined", "journal_sequence_gap", None
        identity = _entry_identity(entry)
        prior = seen.get(entry["transaction_id"])
        if prior is not None:
            if prior != identity:
                return "quarantined", "conflicting_duplicate_transaction", None
            duplicate_idempotent = True
        else:
            seen[entry["transaction_id"]] = identity
        state, signal = _apply_entry(state, entry)
        if signal == "duplicate":
            duplicate_idempotent = True
        elif signal == "ack_idempotent":
            ack_idempotent = True
        elif signal == "resurrection":
            return "quarantined", "superseded_authority_resurrection_blocked", None
        elif signal == "stale":
            return "quarantined", "superseded_authority_resurrection_blocked", None

    if duplicate_idempotent:
        reason = "duplicate_commit_idempotent"
    elif ack_idempotent:
        reason = "acknowledgment_converged"
    elif state["status"] in {"pending_ack", "rolled_back_pending_ack"}:
        reason = "pending_ack_preserved"
    elif state["status"] == "suspended":
        reason = "suspension_preserved"
    elif state["status"] == "revoked":
        reason = "revocation_preserved"
    elif not committed_snapshot:
        reason = "full_log_replay"
    elif any(entry["operation"] == "acknowledge" for entry in entries):
        reason = "acknowledgment_converged"
    else:
        reason = "state_converged"
    return "converged", reason, _state_for_compare(state)


def validate_case(case: Any) -> dict[str, Any]:
    case = _require_exact_fields(case, CASE_FIELDS, "case")
    case_id = case["case_id"]
    if not isinstance(case_id, str) or not case_id:
        raise ValidationError("case_id must be a non-empty string")
    if not isinstance(case["description"], str) or len(case["description"].strip()) < 20:
        raise ValidationError(f"{case_id}: description is too short")
    validate_state(case["initial_state"], f"{case_id}.initial_state")
    floor = _require_nonnegative_int(case["journal_floor"], f"{case_id}.journal_floor")
    if floor < case["initial_state"]["sequence"] + 1:
        raise ValidationError(f"{case_id}: journal_floor precedes initial state")
    if not isinstance(case["journal"], list):
        raise ValidationError(f"{case_id}: journal must be an array")
    entries = [
        validate_entry(entry, f"{case_id}.journal[{index}]")
        for index, entry in enumerate(case["journal"])
    ]
    if entries != sorted(entries, key=lambda item: item["sequence"]):
        raise ValidationError(f"{case_id}: journal entries must be sequence ordered")

    snapshot = _require_exact_fields(case["snapshot"], SNAPSHOT_FIELDS, f"{case_id}.snapshot")
    if snapshot["phase"] not in SNAPSHOT_PHASES:
        raise ValidationError(f"{case_id}: unsupported snapshot phase")
    _require_nonnegative_int(snapshot["sequence"], f"{case_id}.snapshot.sequence")
    if type(snapshot["digest_valid"]) is not bool:
        raise ValidationError(f"{case_id}: snapshot.digest_valid must be boolean")
    validate_state(snapshot["state"], f"{case_id}.snapshot.state")

    compaction = _require_exact_fields(case["compaction"], COMPACTION_FIELDS, f"{case_id}.compaction")
    if compaction["phase"] not in COMPACTION_PHASES:
        raise ValidationError(f"{case_id}: unsupported compaction phase")
    _require_nonnegative_int(compaction["cutoff_sequence"], f"{case_id}.compaction.cutoff_sequence")
    if compaction["interruption"] not in INTERRUPTIONS:
        raise ValidationError(f"{case_id}: unsupported compaction interruption")

    expected = _require_exact_fields(case["expected"], EXPECTED_FIELDS, f"{case_id}.expected")
    if expected["disposition"] not in DISPOSITIONS:
        raise ValidationError(f"{case_id}: unsupported expected disposition")
    if expected["reason"] not in REASONS:
        raise ValidationError(f"{case_id}: unsupported expected reason")
    if expected["state"] is not None:
        validate_state(expected["state"], f"{case_id}.expected.state")

    actual = derive_case(case)
    wanted = (
        expected["disposition"],
        expected["reason"],
        _state_for_compare(expected["state"]) if expected["state"] is not None else None,
    )
    if actual != wanted:
        raise ValidationError(f"{case_id}: expected {wanted!r}, derived {actual!r}")
    return {
        "case_id": case_id,
        "disposition": actual[0],
        "reason": actual[1],
    }


def validate_corpus(data: Any) -> dict[str, Any]:
    root = _require_exact_fields(data, ROOT_FIELDS, "root")
    if root["schema"] != SCHEMA or root["profile_version"] != "1.0.0":
        raise ValidationError("unexpected schema or profile version")
    if root["status"] != STATUS:
        raise ValidationError(f"status must be {STATUS!r}")
    if not isinstance(root["cases"], list):
        raise ValidationError("cases must be an array")
    _check_no_prohibited_fields(root)

    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for case in root["cases"]:
        result = validate_case(case)
        if result["case_id"] in seen:
            raise ValidationError(f"duplicate case_id: {result['case_id']}")
        seen.add(result["case_id"])
        results.append(result)
    if seen != EXPECTED_CASE_IDS:
        raise ValidationError(
            f"fixture coverage differs; missing={sorted(EXPECTED_CASE_IDS - seen)}, "
            f"unknown={sorted(seen - EXPECTED_CASE_IDS)}"
        )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "case_count": len(results),
        "cases": results,
        "grants_authority": False,
        "mutates_state": False,
    }


def validate_bytes(raw: bytes) -> dict[str, Any]:
    data, digest = load_json_bytes(raw)
    report = validate_corpus(data)
    report["sha256"] = digest
    report["cases_validated"] = report["case_count"]
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        report = validate_bytes(args.fixture.read_bytes())
        digest = report["sha256"]
        if args.expected_sha256 and digest != args.expected_sha256:
            raise ValidationError(
                f"fixture digest mismatch: expected {args.expected_sha256}, got {digest}"
            )
        output = json.dumps(report, indent=2, sort_keys=True)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(output + "\n", encoding="utf-8")
        print(output)
        return 0
    except (OSError, ValidationError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
