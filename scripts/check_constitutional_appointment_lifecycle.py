#!/usr/bin/env python3
"""Fail-closed validator for the synthetic constitutional appointment lifecycle corpus."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS = ROOT / "fixtures" / "constitutional-appointment-lifecycle-v1.json"
MAX_BYTES = 256 * 1024
SCHEMA = "alistaire.constitutional-appointment-lifecycle.corpus.v1"
STATUS = "synthetic_only_non_operational"
TOP_LEVEL_FIELDS = {"schema", "profile_version", "status", "cases"}
CASE_FIELDS = {
    "case_id", "description", "events", "controls", "expected_state",
    "expected_reason", "expected_authority_effect",
}
EVENT_FIELDS = {"sequence", "event", "actor_role"}
CONTROL_NAMES = {
    "nomination_recorded", "system_assent_recorded",
    "fiduciary_approval_recorded", "conformance_review_passed",
    "conflict_clear", "recusal_active", "credential_bound",
    "credential_current", "independently_verified", "term_current",
    "suspended", "vacancy_declared", "deputy_authorized",
    "replacement_verified", "appeal_pending", "rollback_verified",
    "propagation_acknowledged",
}
EXPECTED_CASE_IDS = {
    "nomination-only", "assent-without-fiduciary-approval",
    "approval-without-conformance-review", "complete-record-without-credential",
    "bounded-active-after-independent-verification", "recusal-before-activation",
    "term-expired", "emergency-suspension", "appeal-pending",
    "verified-replacement", "rollback-to-prior-verified-state",
    "stale-credential-binding", "deputy-without-vacancy",
    "bounded-deputy-during-vacancy", "lost-propagation-acknowledgment",
}
ALLOWED_EVENTS = {
    "nominate", "record_assent", "fiduciary_approve", "conformance_approve",
    "bind_credential_reference", "independent_verify",
    "acknowledge_propagation", "record_recusal", "expire_term", "suspend",
    "open_appeal", "declare_vacancy", "verify_replacement", "rollback",
    "authorize_deputy",
}
ALLOWED_ACTORS = {
    "founding_sponsor", "governed_system_representative", "human_fiduciary",
    "constitutional_reviewer", "independent_rights_reviewer",
    "technical_custodian", "independent_verifier", "authority_registry",
    "recovery_owner",
}
EVENT_REQUIREMENTS = {
    "nominate": "nomination_recorded",
    "record_assent": "system_assent_recorded",
    "fiduciary_approve": "fiduciary_approval_recorded",
    "conformance_approve": "conformance_review_passed",
    "bind_credential_reference": "credential_bound",
    "independent_verify": "independently_verified",
    "acknowledge_propagation": "propagation_acknowledged",
    "record_recusal": "recusal_active",
    "expire_term": "term_current",
    "suspend": "suspended",
    "open_appeal": "appeal_pending",
    "declare_vacancy": "vacancy_declared",
    "verify_replacement": "replacement_verified",
    "rollback": "rollback_verified",
    "authorize_deputy": "deputy_authorized",
}
PROHIBITED_FIELD_TOKENS = {
    "password", "secret", "private_key", "token", "credential_value",
    "biometric", "raw_capture", "api_key",
}
ALLOWED_STATES = {
    "proposed", "inactive_record", "active", "recused", "expired",
    "suspended", "appeal_pending", "replaced", "rolled_back",
    "deputy_active", "pending_propagation",
}
ALLOWED_REASONS = {
    "missing_nomination", "missing_system_assent",
    "missing_fiduciary_approval", "missing_conformance_review",
    "conflict_unresolved", "credential_unbound", "stale_credential_binding",
    "missing_independent_verification", "missing_propagation_acknowledgment",
    "bounded_active", "recusal_required", "term_expired",
    "emergency_suspension", "appeal_unresolved", "replacement_recorded",
    "rollback_complete", "deputy_without_vacancy", "bounded_deputy",
}
ALLOWED_EFFECTS = {
    "none", "record_only", "synthetic_bounded_active",
    "synthetic_bounded_deputy", "restoration_only",
}


class ValidationError(ValueError):
    """Raised when the corpus fails a bounded fail-closed check."""


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


def derive_outcome(controls: dict[str, bool]) -> tuple[str, str, str]:
    if controls["rollback_verified"]:
        return "rolled_back", "rollback_complete", "restoration_only"
    if controls["recusal_active"]:
        return "recused", "recusal_required", "none"
    if controls["suspended"]:
        return "suspended", "emergency_suspension", "none"
    if not controls["term_current"]:
        return "expired", "term_expired", "none"
    if controls["appeal_pending"]:
        return "appeal_pending", "appeal_unresolved", "none"
    if controls["replacement_verified"]:
        if not controls["vacancy_declared"]:
            raise ValidationError("replacement_verified requires vacancy_declared")
        if not controls["propagation_acknowledged"]:
            return "pending_propagation", "missing_propagation_acknowledgment", "none"
        return "replaced", "replacement_recorded", "record_only"
    if controls["deputy_authorized"] and not controls["vacancy_declared"]:
        return "inactive_record", "deputy_without_vacancy", "none"
    if not controls["nomination_recorded"]:
        return "proposed", "missing_nomination", "none"
    if not controls["system_assent_recorded"]:
        return "proposed", "missing_system_assent", "none"
    if not controls["fiduciary_approval_recorded"]:
        return "proposed", "missing_fiduciary_approval", "none"
    if not controls["conformance_review_passed"]:
        return "proposed", "missing_conformance_review", "none"
    if not controls["conflict_clear"]:
        return "proposed", "conflict_unresolved", "none"
    if not controls["credential_bound"]:
        return "inactive_record", "credential_unbound", "record_only"
    if not controls["credential_current"]:
        return "inactive_record", "stale_credential_binding", "none"
    if not controls["independently_verified"]:
        return "inactive_record", "missing_independent_verification", "none"
    if not controls["propagation_acknowledged"]:
        return "pending_propagation", "missing_propagation_acknowledgment", "none"
    if controls["vacancy_declared"] and controls["deputy_authorized"]:
        return "deputy_active", "bounded_deputy", "synthetic_bounded_deputy"
    return "active", "bounded_active", "synthetic_bounded_active"


def _validate_events(events: Any, controls: dict[str, bool], case_id: str) -> None:
    if not isinstance(events, list) or not events:
        raise ValidationError(f"{case_id}: events must be a non-empty array")
    previous = 0
    seen_events: set[str] = set()
    for event in events:
        if not isinstance(event, dict) or set(event) != EVENT_FIELDS:
            raise ValidationError(f"{case_id}: invalid event fields")
        sequence = event["sequence"]
        name = event["event"]
        actor = event["actor_role"]
        if type(sequence) is not int or sequence <= previous:
            raise ValidationError(f"{case_id}: event sequence must strictly increase")
        if not isinstance(name, str) or name not in ALLOWED_EVENTS:
            raise ValidationError(f"{case_id}: unsupported event {name!r}")
        if not isinstance(actor, str) or actor not in ALLOWED_ACTORS:
            raise ValidationError(f"{case_id}: unsupported actor {actor!r}")
        previous = sequence
        seen_events.add(name)

    for event_name, control_name in EVENT_REQUIREMENTS.items():
        if control_name == "term_current":
            if event_name in seen_events and controls["term_current"]:
                raise ValidationError(f"{case_id}: expire_term requires term_current=false")
        elif event_name in seen_events and not controls[control_name]:
            raise ValidationError(
                f"{case_id}: event {event_name} requires {control_name}=true"
            )
    for control_name, event_name in (
        ("rollback_verified", "rollback"),
        ("replacement_verified", "verify_replacement"),
        ("deputy_authorized", "authorize_deputy"),
    ):
        if controls[control_name] and event_name not in seen_events:
            raise ValidationError(f"{case_id}: {control_name} requires {event_name}")


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

    seen_case_ids: set[str] = set()
    for case in data["cases"]:
        if not isinstance(case, dict) or set(case) != CASE_FIELDS:
            raise ValidationError("invalid case fields")
        case_id = case["case_id"]
        if not isinstance(case_id, str) or not case_id:
            raise ValidationError("case_id must be a non-empty string")
        if case_id in seen_case_ids:
            raise ValidationError(f"duplicate case_id: {case_id}")
        seen_case_ids.add(case_id)
        if not isinstance(case["description"], str) or len(case["description"].strip()) < 20:
            raise ValidationError(f"{case_id}: description is too short")

        controls = case["controls"]
        if not isinstance(controls, dict) or set(controls) != CONTROL_NAMES:
            raise ValidationError(f"{case_id}: invalid control set")
        for key, value in controls.items():
            if type(value) is not bool:
                raise ValidationError(f"{case_id}: control {key} must be boolean")
        _validate_events(case["events"], controls, case_id)

        if case["expected_state"] not in ALLOWED_STATES:
            raise ValidationError(f"{case_id}: unsupported expected_state")
        if case["expected_reason"] not in ALLOWED_REASONS:
            raise ValidationError(f"{case_id}: unsupported expected_reason")
        if case["expected_authority_effect"] not in ALLOWED_EFFECTS:
            raise ValidationError(f"{case_id}: unsupported authority effect")
        expected = (
            case["expected_state"], case["expected_reason"],
            case["expected_authority_effect"],
        )
        actual = derive_outcome(controls)
        if actual != expected:
            raise ValidationError(f"{case_id}: expected {expected!r}, derived {actual!r}")

    if seen_case_ids != EXPECTED_CASE_IDS:
        missing = sorted(EXPECTED_CASE_IDS - seen_case_ids)
        extra = sorted(seen_case_ids - EXPECTED_CASE_IDS)
        raise ValidationError(f"fixture coverage drift: missing={missing}, extra={extra}")
    return {
        "schema": SCHEMA, "status": STATUS, "cases": len(seen_case_ids),
        "case_ids": sorted(seen_case_ids),
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
