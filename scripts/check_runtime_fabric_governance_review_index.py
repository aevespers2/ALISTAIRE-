#!/usr/bin/env python3
"""Validate the documentation-only runtime/Fabric governance review index."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "docs/runtime-fabric-governance-review-index-v1.json"
GUIDE_PATH = ROOT / "docs/runtime-fabric-governance-review-index.md"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
STATUS = "REVIEW_INDEX_COMPLETE_BINDINGS_UNACCEPTED"
PROFILE_ID = "ALISTAIRE-RUNTIME-FABRIC-GOVERNANCE-REVIEW-INDEX-001"
SOURCE_HEAD = "215a0068999105bebe6aab81614ee1a95e3f47b1"
SAFE_DEFAULT = "UNSUPPORTED_KERNEL_RUNTIME_ROUTE"
REJECTED_OPTION = "REJECT_DIRECT_IDENTITY_ALIAS"

EXPECTED_TOP_FIELDS = {
    "profile_id",
    "profile_version",
    "status",
    "authority_effect",
    "source_generation",
    "route",
    "review_surfaces",
    "safe_default",
    "rejected_option",
    "semantic_classes",
    "material_obstructions",
    "review_sequence",
    "controlled_planning_routes",
    "invariants",
    "invalidation_triggers",
    "prohibited_promotions",
    "fysa_120",
}
EXPECTED_ROUTE = [
    "aevespers2/qsio-kernel",
    "aevespers2/QuantumStateObjects",
    "aevespers2/QSO-FABRIC",
    "aevespers2/1",
]
EXPECTED_SURFACES = {
    "namespace_partition": (
        "docs/runtime-fabric-namespace-partition.md",
        "BLOCKED_ROLE_COLLISION",
    ),
    "candidate_inventory": (
        "docs/runtime-fabric-producer-consumer-inventory.md",
        "OBSERVED_CANDIDATE_INVENTORY_RECORDED_BLOCKED_UNACCEPTED_BINDINGS",
    ),
    "default_head_inventory": (
        "docs/runtime-fabric-default-head-owner-inventory.md",
        "DEFAULT_HEADS_VERIFIED_OWNER_VACANCIES_RECORDED_BINDINGS_UNACCEPTED",
    ),
    "lineage_disposition": (
        "docs/runtime-fabric-lineage-disposition.md",
        "CANDIDATE_LINEAGES_CLASSIFIED_REBIND_WITHDRAW_OR_ACCEPT_REQUIRED",
    ),
    "kernel_runtime_crosswalk": (
        "docs/kernel-runtime-crosswalk-options.md",
        "KERNEL_RUNTIME_CROSSWALK_OPTIONS_DOCUMENTED_UNSELECTED",
    ),
}
EXPECTED_CLASSES = {
    "kernel_interaction_record",
    "runtime_event",
    "runtime_execution_report",
    "fabric_projection_receipt",
    "fabric_collaboration_or_aggregate_record",
    "portfolio_disposition",
}
EXPECTED_OBSTRUCTIONS = {
    "kernel_runtime_semantic_mismatch",
    "namespace_and_identity_ambiguity",
    "missing_projection_receipt",
    "source_set_and_duplicate_inflation",
    "ordering_and_replay_ambiguity",
    "correction_and_revocation_discontinuity",
    "semantic_and_route_owner_vacancy",
    "migration_and_rollback_incompleteness",
    "authority_inflation",
}
EXPECTED_SEQUENCE = [
    "CONFIRM_EXACT_SOURCES",
    "RESOLVE_D1_AND_D2",
    "RESOLVE_D3",
    "CONFIRM_SEMANTIC_AND_ROUTE_OWNERS_OR_ACCEPTED_VACANCIES",
    "SELECT_CROSSWALK_OR_PRESERVE_UNSUPPORTED_ROUTE",
    "BUILD_HOSTILE_FIXTURES",
    "VALIDATE_TWO_INDEPENDENT_CONSUMERS",
    "COMPLETE_SECURITY_PRIVACY_RETENTION_LICENSE_ACCESSIBILITY_INCIDENT_REVIEW",
    "RECORD_HUMAN_APPROVAL_AND_VERIFY_RESULTING_STATE",
]
EXPECTED_PLANNING_ROUTES = {
    "taskchain.md",
    "punchlist.md",
    "release.md",
    "changelog.md",
}
EXPECTED_INVARIANTS = {
    "review_surfaces_remain_independently_identified",
    "passing_validation_is_not_interface_acceptance",
    "fixture_agreement_is_not_live_compatibility",
    "repository_name_is_not_semantic_ownership",
    "preserved_lineage_is_not_current_acceptance",
    "unsupported_route_remains_safe_until_all_gates_pass",
    "direct_identity_aliasing_remains_rejected",
    "local_runtime_success_is_not_fabric_success",
    "fabric_success_is_not_portfolio_disposition",
    "projection_is_not_independent_corroboration",
    "correction_revocation_and_rollback_must_propagate_end_to_end",
    "authority_effect_remains_none",
}
EXPECTED_CATEGORIES = {
    "CAT-011",
    "CAT-012",
    "CAT-013",
    "CAT-017",
    "CAT-018",
    "CAT-019",
    "CAT-031",
    "CAT-032",
    "CAT-040",
    "CAT-052",
    "CAT-059",
    "CAT-070",
}
REQUIRED_GUIDE_PHRASES = (
    STATUS,
    SAFE_DEFAULT,
    REJECTED_OPTION,
    "Why this index exists",
    "Current safe disposition",
    "Material gluing obstructions",
    "Required review sequence",
    "Reviewer onboarding",
    "Planning and release consistency",
    "Provenance, correction, and rollback",
    "012-P — Cross-document governance status indexing and controlled-route coherence",
    "No documentation artifact",
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


def unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return value


def validate_profile(profile: dict[str, Any], root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    if set(profile) != EXPECTED_TOP_FIELDS:
        errors.append("profile field closure changed")
    if profile.get("profile_id") != PROFILE_ID:
        errors.append("unexpected profile_id")
    if profile.get("profile_version") != "1.0.0-candidate":
        errors.append("unexpected profile_version")
    if profile.get("status") != STATUS:
        errors.append("review index status changed")
    if profile.get("authority_effect") != "NONE":
        errors.append("authority_effect must remain NONE")
    if profile.get("safe_default") != SAFE_DEFAULT:
        errors.append("unsupported route must remain the safe default")
    if profile.get("rejected_option") != REJECTED_OPTION:
        errors.append("direct identity aliasing must remain rejected")

    source = profile.get("source_generation")
    if not isinstance(source, dict) or set(source) != {
        "repository", "ref", "head_sha", "binding_kind"
    }:
        errors.append("source_generation schema changed")
    else:
        if source.get("repository") != "aevespers2/ALISTAIRE-":
            errors.append("unexpected source repository")
        if source.get("ref") != "docs/consolidation-charter-20260720":
            errors.append("unexpected source ref")
        head = source.get("head_sha")
        if head != SOURCE_HEAD or not isinstance(head, str) or not SHA40.fullmatch(head):
            errors.append("source exact head changed")
        if source.get("binding_kind") != "historical_parent_input_not_self_reference":
            errors.append("source binding kind changed")

    try:
        route = unique_strings(profile.get("route"), "route")
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if route != EXPECTED_ROUTE:
            errors.append("portfolio route changed")

    surfaces = profile.get("review_surfaces")
    if not isinstance(surfaces, list) or len(surfaces) != len(EXPECTED_SURFACES):
        errors.append("review surface closure changed")
    else:
        seen: set[str] = set()
        for surface in surfaces:
            if not isinstance(surface, dict) or set(surface) != {
                "id", "path", "disposition", "authority_effect"
            }:
                errors.append("review surface schema changed")
                continue
            surface_id = surface.get("id")
            if not isinstance(surface_id, str) or surface_id in seen:
                errors.append("review surface identity duplicated or invalid")
                continue
            seen.add(surface_id)
            expected = EXPECTED_SURFACES.get(surface_id)
            if expected is None:
                errors.append(f"unexpected review surface: {surface_id}")
                continue
            if (surface.get("path"), surface.get("disposition")) != expected:
                errors.append(f"review surface drifted: {surface_id}")
            if surface.get("authority_effect") != "NONE":
                errors.append(f"review surface promoted authority: {surface_id}")
            path = root / str(surface.get("path"))
            if not path.is_file():
                errors.append(f"review surface file missing: {surface_id}")
            else:
                text = path.read_text(encoding="utf-8")
                if expected[1] not in text:
                    errors.append(f"review surface disposition missing: {surface_id}")
        if seen != set(EXPECTED_SURFACES):
            errors.append("review surface identity closure changed")

    try:
        classes = set(unique_strings(profile.get("semantic_classes"), "semantic_classes"))
        obstructions = set(unique_strings(profile.get("material_obstructions"), "material_obstructions"))
        sequence = unique_strings(profile.get("review_sequence"), "review_sequence")
        planning_routes = set(unique_strings(profile.get("controlled_planning_routes"), "controlled_planning_routes"))
        invariants = set(unique_strings(profile.get("invariants"), "invariants"))
        unique_strings(profile.get("invalidation_triggers"), "invalidation_triggers")
        prohibited = set(unique_strings(profile.get("prohibited_promotions"), "prohibited_promotions"))
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if classes != EXPECTED_CLASSES:
            errors.append("semantic class closure changed")
        if obstructions != EXPECTED_OBSTRUCTIONS:
            errors.append("material obstruction closure changed")
        if sequence != EXPECTED_SEQUENCE:
            errors.append("review sequence changed")
        if planning_routes != EXPECTED_PLANNING_ROUTES:
            errors.append("planning route closure changed")
        if invariants != EXPECTED_INVARIANTS:
            errors.append("invariant closure changed")
        required_prohibited = {
            "namespace_selection",
            "schema_acceptance",
            "owner_appointment",
            "producer_or_consumer_admission",
            "registry_activation",
            "adapter_activation",
            "runtime_admission",
            "fabric_activation",
            "portfolio_disposition_authority",
            "default_branch_merge",
            "release",
            "pages_publication",
            "deployment",
            "credential_change",
            "infrastructure_apply",
            "destructive_history_rewrite",
        }
        if not required_prohibited.issubset(prohibited):
            errors.append("prohibited promotion closure is incomplete")
        for route_path in sorted(planning_routes):
            if not (root / route_path).is_file():
                errors.append(f"controlled planning route missing: {route_path}")

    fysa = profile.get("fysa_120")
    if not isinstance(fysa, dict) or set(fysa) != {
        "categories", "subdivisions", "proposed_gap"
    }:
        errors.append("FYSA-120 mapping schema changed")
    else:
        try:
            categories = set(unique_strings(fysa.get("categories"), "FYSA categories"))
            unique_strings(fysa.get("subdivisions"), "FYSA subdivisions")
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if categories != EXPECTED_CATEGORIES:
                errors.append("FYSA-120 category mapping changed")
        gap = fysa.get("proposed_gap")
        if not isinstance(gap, dict) or set(gap) != {"id", "name", "authoritative"}:
            errors.append("proposed gap schema changed")
        elif gap.get("id") != "012-P" or gap.get("authoritative") is not False:
            errors.append("proposed gap must remain non-authoritative 012-P")

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
        errors.append("guide must include a prose equivalent")
    for _, (surface_path, disposition) in EXPECTED_SURFACES.items():
        if surface_path.removeprefix("docs/") not in text:
            errors.append(f"guide missing review-surface link: {surface_path}")
        if disposition not in text:
            errors.append(f"guide missing disposition: {disposition}")
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

    if args.submitted_sha is not None and not SHA40.fullmatch(args.submitted_sha):
        errors.append("submitted SHA must be an exact lowercase 40-character Git SHA")

    report = {
        "profile_id": PROFILE_ID,
        "status": "PASS" if not errors else "FAIL",
        "submitted_sha": args.submitted_sha,
        "disposition": STATUS,
        "safe_default": SAFE_DEFAULT,
        "authority_effect": "NONE",
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
