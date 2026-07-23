#!/usr/bin/env python3
"""Fail-closed validation for the runtime/Fabric namespace-partition packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/runtime-fabric-namespace-partition-v1.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

TOP_FIELDS = {
    "profile_id",
    "profile_version",
    "status",
    "authority_effect",
    "decision_scope",
    "prohibited_promotions",
    "legacy_collisions",
    "required_semantic_classes",
    "candidate_profiles",
    "mandatory_fields",
    "invariants",
    "required_witnesses",
    "migration_requirements",
    "rollback_requirements",
    "review_gates",
    "fysa_120",
}

EXPECTED_CLASSES = {
    "runtime_event",
    "runtime_execution_report",
    "fabric_projection_receipt",
    "fabric_collaboration_event",
    "fabric_aggregate_report",
    "portfolio_disposition",
}

EXPECTED_PROFILES = {
    "fully_separate_namespaces",
    "common_envelope_mandatory_semantic_qualifiers",
    "separate_canonical_classes_with_bounded_compatibility_views",
}

EXPECTED_INVARIANTS = {
    "runtime_success_is_not_fabric_success",
    "fabric_success_is_not_portfolio_disposition",
    "projection_is_not_independent_evidence",
    "aggregate_identity_is_domain_separated_from_source_identity",
    "authority_effect_defaults_to_none",
    "ambiguous_legacy_records_fail_closed",
    "correction_and_revocation_reach_all_dependents",
    "rollback_does_not_restore_stale_or_withdrawn_state",
    "components_do_not_define_or_approve_their_own_authority",
}

EXPECTED_WITNESSES = {
    "runtime_to_fabric_projection",
    "fabric_aggregate_to_repository_1",
    "runtime_fabric_repository_1_triple_overlap",
}

REQUIRED_FIELDS = {
    "profile_id",
    "profile_version",
    "semantic_namespace",
    "semantic_class",
    "producer_id",
    "producer_role",
    "producer_generation",
    "record_id",
    "record_identity_inputs",
    "subject_id",
    "subject_generation",
    "source_record_ids",
    "source_set_digest",
    "event_time",
    "observation_time",
    "trusted_time_status",
    "local_sequence",
    "causal_parents",
    "ordering_scope",
    "duplicate_disposition",
    "replay_disposition",
    "idempotency_key",
    "conflict_disposition",
    "transformation_or_aggregation_rule_id",
    "projection_or_aggregation_receipt_id",
    "privacy_classification",
    "retention_classification",
    "correction_refs",
    "revocation_refs",
    "supersession_refs",
    "withdrawal_refs",
    "consumer_profile",
    "unsupported_version_behavior",
    "authority_effect",
    "rollback_target",
    "restored_state_verification",
}

EXPECTED_ROUTES = {
    "README.md",
    "docs/index.md",
    "docs/runtime-fabric-namespace-partition.md",
    "taskchain.md",
    "release.md",
    "punchlist.md",
    "changelog.md",
    "mkdocs.yml",
}

REQUIRED_ROUTE_MARKERS = (
    "runtime/Fabric",
    "BLOCKED_ROLE_COLLISION",
)

PROHIBITED = {
    "canonical_namespace_selection",
    "schema_acceptance",
    "consumer_registration",
    "runtime_admission",
    "fabric_activation",
    "repository_1_authority",
    "credential_or_capability_creation",
    "merge_to_default_branch",
    "release",
    "pages_publication",
    "deployment",
    "infrastructure_apply",
}

REVIEW_GATES = {
    "D1_ACCEPTED",
    "D2_ACCEPTED",
    "D3_ACCEPTED",
    "EXACT_REPOSITORY_LOCAL_INVENTORY_COMPLETE",
    "PARTITION_PROFILE_SELECTED",
    "SEMANTIC_CLASSES_IMMUTABLE",
    "SECURITY_REVIEW_COMPLETE",
    "PRIVACY_REVIEW_COMPLETE",
    "ACCESSIBILITY_REVIEW_COMPLETE",
    "LICENSE_REVIEW_COMPLETE",
    "ARCHITECTURE_REVIEW_COMPLETE",
    "TWO_INDEPENDENT_CONSUMERS_OR_VALIDATORS_PASS",
    "MIGRATION_AND_ROLLBACK_EVIDENCE_COMPLETE",
    "EXPLICIT_HUMAN_APPROVAL",
    "RESULTING_STATE_VERIFIED",
}


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number prohibited: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_packet(path: Path) -> dict[str, Any]:
    text = path.read_bytes().decode("utf-8", errors="strict")
    value = json.loads(
        text,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("packet root must be an object")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    unknown = set(value) - expected
    if missing or unknown:
        raise ValueError(
            f"{label} fields mismatch: missing={sorted(missing)} unknown={sorted(unknown)}"
        )


def require_unique_strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return value


def validate_packet(
    packet: dict[str, Any],
    packet_path: Path = DEFAULT_PACKET,
    submitted_sha: str | None = None,
) -> dict[str, Any]:
    exact_keys(packet, TOP_FIELDS, "packet")
    if packet["profile_id"] != "ALISTAIRE-RUNTIME-FABRIC-NAMESPACE-PARTITION-001":
        raise ValueError("unexpected profile_id")
    if packet["profile_version"] != "1.0.0-candidate":
        raise ValueError("unexpected candidate profile version")
    if packet["status"] != "BLOCKED_ROLE_COLLISION":
        raise ValueError("role collision must remain blocked")
    if packet["authority_effect"] != "NONE":
        raise ValueError("packet must have no authority effect")

    prohibited = set(require_unique_strings(packet["prohibited_promotions"], "prohibited_promotions"))
    if prohibited != PROHIBITED:
        raise ValueError("prohibited promotions are incomplete or changed")

    collisions = packet["legacy_collisions"]
    if not isinstance(collisions, list) or len(collisions) != 2:
        raise ValueError("exactly two legacy label collisions are required")
    collision_map: dict[str, set[str]] = {}
    for item in collisions:
        if not isinstance(item, dict) or set(item) != {"label", "candidate_meanings"}:
            raise ValueError("legacy collision entries must use the closed schema")
        collision_map[item["label"]] = set(
            require_unique_strings(item["candidate_meanings"], "candidate_meanings")
        )
    if collision_map != {
        "qso-event-ledger": {"runtime_local_event", "fabric_collaboration_event"},
        "qso-runtime-report": {"runtime_execution_report", "fabric_aggregate_report"},
    }:
        raise ValueError("legacy collision closure changed")

    classes = packet["required_semantic_classes"]
    if not isinstance(classes, list) or len(classes) != len(EXPECTED_CLASSES):
        raise ValueError("semantic class count changed")
    class_ids: set[str] = set()
    for item in classes:
        if not isinstance(item, dict) or set(item) != {
            "id",
            "candidate_producer",
            "authority_effect",
        }:
            raise ValueError("semantic class entries must use the closed schema")
        class_ids.add(item["id"])
        if item["id"] == "portfolio_disposition":
            if item["authority_effect"] != "SEPARATE_APPROVED_AUTHORITY_REQUIRED":
                raise ValueError("portfolio disposition must require separate authority")
        elif item["authority_effect"] != "NONE":
            raise ValueError("non-disposition classes must have no authority effect")
    if class_ids != EXPECTED_CLASSES:
        raise ValueError("semantic class closure changed")

    profiles = packet["candidate_profiles"]
    if not isinstance(profiles, list) or len(profiles) != 3:
        raise ValueError("three candidate profiles are required")
    profile_names: set[str] = set()
    for item in profiles:
        if not isinstance(item, dict):
            raise ValueError("candidate profiles must be objects")
        if set(item) not in (
            {"id", "name", "selected", "examples"},
            {"id", "name", "selected", "required_qualifiers"},
            {"id", "name", "selected", "compatibility_requirements"},
        ):
            raise ValueError("candidate profile schema changed")
        if item["selected"] is not False:
            raise ValueError("no candidate partition profile may be selected")
        profile_names.add(item["name"])
    if profile_names != EXPECTED_PROFILES:
        raise ValueError("candidate profile closure changed")

    mandatory_fields = set(require_unique_strings(packet["mandatory_fields"], "mandatory_fields"))
    if mandatory_fields != REQUIRED_FIELDS:
        raise ValueError("mandatory field closure changed")

    invariants = set(require_unique_strings(packet["invariants"], "invariants"))
    if invariants != EXPECTED_INVARIANTS:
        raise ValueError("invariant closure changed")

    witnesses = packet["required_witnesses"]
    if not isinstance(witnesses, list) or len(witnesses) != 3:
        raise ValueError("three witnesses are required")
    witness_ids: set[str] = set()
    for item in witnesses:
        if not isinstance(item, dict) or set(item) != {"id", "requirements"}:
            raise ValueError("witness entries must use the closed schema")
        witness_ids.add(item["id"])
        if len(require_unique_strings(item["requirements"], "witness requirements")) < 4:
            raise ValueError("each witness must close at least four requirements")
    if witness_ids != EXPECTED_WITNESSES:
        raise ValueError("witness closure changed")

    if len(require_unique_strings(packet["migration_requirements"], "migration_requirements")) < 8:
        raise ValueError("migration requirements are incomplete")
    if len(require_unique_strings(packet["rollback_requirements"], "rollback_requirements")) < 8:
        raise ValueError("rollback requirements are incomplete")
    if set(require_unique_strings(packet["review_gates"], "review_gates")) != REVIEW_GATES:
        raise ValueError("review gate closure changed")

    mapping = packet["fysa_120"]
    if not isinstance(mapping, dict) or set(mapping) != {
        "categories",
        "subdivisions",
        "proposed_gap",
    }:
        raise ValueError("FYSA-120 mapping must use the closed schema")
    required_categories = {
        "CAT-011",
        "CAT-012",
        "CAT-013",
        "CAT-017",
        "CAT-019",
        "CAT-031",
        "CAT-032",
        "CAT-040",
        "CAT-052",
        "CAT-070",
    }
    if set(require_unique_strings(mapping["categories"], "FYSA categories")) != required_categories:
        raise ValueError("FYSA category mapping changed")
    require_unique_strings(mapping["subdivisions"], "FYSA subdivisions")
    gap = mapping["proposed_gap"]
    if not isinstance(gap, dict) or set(gap) != {"id", "name", "authoritative"}:
        raise ValueError("proposed gap must use the closed schema")
    if gap["id"] != "032-F" or gap["authoritative"] is not False:
        raise ValueError("proposed gap must remain 032-F and non-authoritative")

    for route in sorted(EXPECTED_ROUTES):
        path = Path(route)
        if not path.is_file():
            raise ValueError(f"controlled documentation route missing: {route}")
        text = path.read_text(encoding="utf-8")
        if not all(marker in text for marker in REQUIRED_ROUTE_MARKERS):
            raise ValueError(f"controlled route lacks partition markers: {route}")

    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be an exact lowercase 40-character Git SHA")

    return {
        "profile_id": packet["profile_id"],
        "profile_version": packet["profile_version"],
        "status": packet["status"],
        "semantic_class_count": len(class_ids),
        "candidate_profile_count": len(profile_names),
        "mandatory_field_count": len(mandatory_fields),
        "invariant_count": len(invariants),
        "witness_count": len(witness_ids),
        "review_gate_count": len(REVIEW_GATES),
        "controlled_route_count": len(EXPECTED_ROUTES),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "submitted_sha": submitted_sha,
        "disposition": "RUNTIME_FABRIC_PARTITION_VALIDATED_NON_AUTHORIZING",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--submitted-sha")
    args = parser.parse_args()
    try:
        path = Path(args.packet)
        report = validate_packet(load_packet(path), path, args.submitted_sha)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "disposition": "RUNTIME_FABRIC_PARTITION_FAILED_CLOSED",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
