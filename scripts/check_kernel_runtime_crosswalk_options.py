#!/usr/bin/env python3
"""Validate the documentation-only kernel-to-runtime crosswalk options packet."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "docs/kernel-runtime-crosswalk-options-v1.json"
GUIDE_PATH = ROOT / "docs/kernel-runtime-crosswalk-options.md"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_STATUS = "KERNEL_RUNTIME_CROSSWALK_OPTIONS_DOCUMENTED_UNSELECTED"
EXPECTED_PROFILE_ID = "ALISTAIRE-KERNEL-RUNTIME-CROSSWALK-OPTIONS-001"
EXPECTED_SAFE_DEFAULT = "UNSUPPORTED_KERNEL_RUNTIME_ROUTE"
EXPECTED_REPOSITORIES = {
    "aevespers2/qsio-kernel",
    "aevespers2/QuantumStateObjects",
    "aevespers2/ALISTAIRE-",
}
EXPECTED_HEADS = {
    "6468254d7703e5f771e610ed3f76bac1b7205ddb",
    "40efcbf8ce2bda7d6b05b3fb1f3ccf0384facc51",
    "cc9b9c7b06a1a48bbc052b8d6bacd11782285288",
    "b31f9f3385ebf05576bd55bde36e4d42158f2adb",
}
EXPECTED_CLASSES = {
    "kernel_interaction_record",
    "runtime_event",
    "runtime_execution_report",
    "projection_receipt",
    "fabric_record",
    "portfolio_disposition",
}
EXPECTED_FIELDS = {
    "qsio_id",
    "qsi",
    "pre_state_hashes",
    "proposed_transitions",
    "accepted_transitions",
    "witnesses",
    "outcome",
    "reason_codes",
    "parent_qsio_hashes",
    "created_at",
    "content_hash",
}
EXPECTED_OPTION_IDS = {"A", "B", "C", "D"}
EXPECTED_GATES = {
    "D1_ACCEPTED",
    "D2_STEWARD_ACCEPTED",
    "D3_CANONICAL_PROFILE_ACCEPTED",
    "COMPLETE_LOCAL_USE_INVENTORY",
    "SEMANTIC_AND_ROUTE_OWNERS_OR_ACCEPTED_VACANCIES",
    "VERSIONED_SOURCE_TARGET_SCHEMAS_AND_VOCABULARIES",
    "TWO_INDEPENDENT_VALIDATORS",
    "SECURITY_PRIVACY_LICENSE_ACCESSIBILITY_RETENTION_INCIDENT_REVIEW",
    "CONSUMER_REGISTRATION_AND_REMOVAL_GOVERNANCE",
    "MIGRATION_CORRECTION_REVOCATION_WITHDRAWAL_ROLLBACK_RESTORATION_EVIDENCE",
    "EXPLICIT_HUMAN_APPROVAL",
    "RESULTING_DEFAULT_HEAD_EVIDENCE",
}
REQUIRED_GUIDE_PHRASES = (
    EXPECTED_STATUS,
    EXPECTED_SAFE_DEFAULT,
    "REJECT_DIRECT_IDENTITY_ALIAS",
    "Option A — Explicitly unsupported route",
    "Option B — Read-only projection adapter",
    "Option C — Neutral shared envelope with qualified semantic classes",
    "Option D — Direct identity aliasing",
    "Projection receipt minimum",
    "Hostile and boundary cases",
    "Acceptance gates",
    "Invalidation and rollback",
    "040-N — Internal-ledger to runtime-record crosswalk, loss accounting, and unsupported-route preservation",
    "No crosswalk option is selected",
)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value prohibited: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    raw = path.read_bytes().decode("utf-8", errors="strict")
    value = json.loads(
        raw,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("profile root must be an object")
    return value


def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if profile.get("profile_id") != EXPECTED_PROFILE_ID:
        errors.append("unexpected profile_id")
    if profile.get("version") != 1:
        errors.append("version must be 1")
    if profile.get("status") != EXPECTED_STATUS:
        errors.append("status must remain unselected")
    if profile.get("authority_effect") != "none":
        errors.append("authority_effect must be none")
    if profile.get("safe_default") != EXPECTED_SAFE_DEFAULT:
        errors.append("safe default must remain the unsupported route")

    generations = profile.get("observed_generations")
    if not isinstance(generations, list) or len(generations) != 4:
        errors.append("exactly four observed generations are required")
    else:
        repositories: set[str] = set()
        heads: set[str] = set()
        for index, generation in enumerate(generations):
            if not isinstance(generation, dict):
                errors.append(f"observed generation {index} must be an object")
                continue
            repository = generation.get("repository")
            head = generation.get("head")
            repositories.add(str(repository))
            heads.add(str(head))
            if repository not in EXPECTED_REPOSITORIES:
                errors.append(f"unexpected observed repository: {repository}")
            if not isinstance(head, str) or not SHA40.fullmatch(head):
                errors.append(f"invalid exact head for {repository}")
            if generation.get("role") in (None, ""):
                errors.append(f"missing role for {repository}")
        if repositories != EXPECTED_REPOSITORIES:
            errors.append("observed repository set does not match")
        if heads != EXPECTED_HEADS:
            errors.append("observed exact-head set does not match")

    classes = profile.get("semantic_classes")
    if not isinstance(classes, list) or set(classes) != EXPECTED_CLASSES:
        errors.append("semantic classes must remain complete and distinct")

    fields = profile.get("kernel_fields")
    if not isinstance(fields, list) or set(fields) != EXPECTED_FIELDS:
        errors.append("kernel field inventory is incomplete or changed")

    options = profile.get("options")
    if not isinstance(options, list) or len(options) != 4:
        errors.append("exactly four crosswalk options are required")
    else:
        by_id = {
            str(option.get("id")): option
            for option in options
            if isinstance(option, dict)
        }
        if set(by_id) != EXPECTED_OPTION_IDS:
            errors.append("option IDs must be A through D")
        else:
            option_a = by_id["A"]
            option_b = by_id["B"]
            option_c = by_id["C"]
            option_d = by_id["D"]
            if option_a.get("disposition") != EXPECTED_SAFE_DEFAULT:
                errors.append("Option A must preserve the unsupported-route disposition")
            if option_a.get("selectable_now") is not True:
                errors.append("Option A must remain the only currently selectable safe route")
            if option_b.get("selectable_now") is not False or option_b.get("requires_projection_receipt") is not True:
                errors.append("Option B must remain unselected and receipt-bound")
            if option_c.get("selectable_now") is not False or set(option_c.get("requires", [])) != {"D2", "D3"}:
                errors.append("Option C must remain unselected and depend on D2 and D3")
            if option_d.get("disposition") != "REJECT_DIRECT_IDENTITY_ALIAS":
                errors.append("Option D must remain rejected")
            if option_d.get("selectable_now") is not False:
                errors.append("Option D cannot be selectable")
            for option_id, option in by_id.items():
                if option.get("authority_effect") != "none":
                    errors.append(f"Option {option_id} must not create authority")

    receipt_fields = profile.get("projection_receipt_required_fields")
    if not isinstance(receipt_fields, list) or len(receipt_fields) < 30:
        errors.append("projection receipt field set is incomplete")
    elif len(receipt_fields) != len(set(receipt_fields)):
        errors.append("projection receipt fields must be unique")
    elif "authority_effect" not in receipt_fields or "rollback_target" not in receipt_fields:
        errors.append("projection receipt must bind authority effect and rollback")

    gates = profile.get("acceptance_gates")
    if not isinstance(gates, list) or set(gates) != EXPECTED_GATES:
        errors.append("acceptance gate set is incomplete or changed")

    prohibited = profile.get("prohibited_promotions")
    required_prohibited = {
        "namespace_selection",
        "adapter_activation",
        "runtime_admission",
        "fabric_activation",
        "portfolio_disposition_authority",
        "release",
        "pages_publication",
        "deployment",
        "credential_change",
        "infrastructure_apply",
        "destructive_history_rewrite",
    }
    if not isinstance(prohibited, list) or not required_prohibited.issubset(set(prohibited)):
        errors.append("prohibited promotion set is incomplete")

    fysa = profile.get("fysa_120")
    if not isinstance(fysa, dict):
        errors.append("FYSA-120 map is required")
    else:
        categories = fysa.get("categories")
        required_categories = {
            "CAT-011", "CAT-012", "CAT-013", "CAT-017", "CAT-018",
            "CAT-019", "CAT-031", "CAT-032", "CAT-040", "CAT-052",
            "CAT-059", "CAT-070",
        }
        if not isinstance(categories, list) or set(categories) != required_categories:
            errors.append("FYSA-120 category map is incomplete")
        gap = fysa.get("proposed_gap")
        if not isinstance(gap, dict) or gap.get("id") != "040-N" or gap.get("authoritative") is not False:
            errors.append("proposed skill-tree gap must remain non-authoritative 040-N")

    return errors


def validate_guide(path: Path = GUIDE_PATH) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = [
        f"guide missing required phrase: {phrase}"
        for phrase in REQUIRED_GUIDE_PHRASES
        if phrase not in text
    ]
    if text.count("```mermaid") != 1:
        errors.append("guide must contain exactly one Mermaid graph")
    if "### Prose equivalent" not in text:
        errors.append("guide must include a prose equivalent for the graph")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submitted-sha", default=None)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        profile = load_profile()
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"invalid profile: {exc}")
    else:
        errors.extend(validate_profile(profile))
    try:
        errors.extend(validate_guide())
    except (OSError, UnicodeError) as exc:
        errors.append(f"invalid guide: {exc}")

    report = {
        "profile_id": EXPECTED_PROFILE_ID,
        "status": "PASS" if not errors else "FAIL",
        "submitted_sha": args.submitted_sha,
        "disposition": EXPECTED_STATUS,
        "safe_default": EXPECTED_SAFE_DEFAULT,
        "authority_effect": "none",
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
