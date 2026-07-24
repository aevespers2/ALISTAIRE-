#!/usr/bin/env python3
"""Fail-closed validation for the proposed D2 neutral contract steward packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/d2-neutral-contract-steward-decision-packet-v1.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_MODELS = {
    "DEDICATED_NEUTRAL_CONTRACT_REPOSITORY",
    "SPLIT_SOURCE_AND_EVIDENCE_CUSTODY",
    "FEDERATED_STEWARDSHIP_WITH_NEUTRAL_RELEASE_GATE",
}
EXPECTED_ROUTES = {
    "README.md",
    "docs/index.md",
    "docs/d2-neutral-contract-steward-decision-packet.md",
    "taskchain.md",
    "release.md",
    "punchlist.md",
    "changelog.md",
}
TOP_FIELDS = {
    "profile_id", "version", "status", "authority_effect", "source_generation",
    "dependencies", "purpose", "candidate_models", "required_decision_fields",
    "readiness_gates", "governance_scope", "prohibited_promotions", "controlled_routes",
    "propagation", "skill_tree_mapping", "proposed_subdivision_gap",
}
REQUIRED_DECISION_FIELDS = {
    "selected_model", "steward_identity", "repository_and_package_location",
    "contract_family_scope", "explicit_non_operational_authority", "source_precedence",
    "identifier_and_namespace_governance", "schema_and_reason_code_governance",
    "fixture_and_conformance_custody", "review_and_release_quorum",
    "signing_and_key_custody", "compatibility_and_consumer_registry",
    "migration_and_deprecation_policy", "correction_withdrawal_and_supersession",
    "compromise_and_emergency_freeze", "backup_restore_and_continuity",
    "dispute_appeal_and_recusal", "license_privacy_and_public_private_boundary",
    "audit_evidence_and_retention", "rollback_and_failed_rollback",
}
PROHIBITED = {
    "dependency_use_to_canonical_authority",
    "schema_publication_to_operational_approval",
    "passing_ci_to_contract_acceptance",
    "stewardship_to_capability_issuance",
    "stewardship_to_device_or_runtime_disposition",
    "release_signing_to_semantic_ownership",
    "portfolio_summary_to_repository_local_acceptance",
    "skill_mapping_to_competence_or_permission",
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
    packet = json.loads(text, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    if not isinstance(packet, dict):
        raise ValueError("packet root must be an object")
    return packet


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    unknown = set(value) - expected
    missing = expected - set(value)
    if unknown or missing:
        raise ValueError(f"{label} fields mismatch: missing={sorted(missing)} unknown={sorted(unknown)}")


def validate_packet(packet: dict[str, Any], packet_path: Path = DEFAULT_PACKET, submitted_sha: str | None = None) -> dict[str, Any]:
    exact_keys(packet, TOP_FIELDS, "packet")
    if packet["profile_id"] != "ALISTAIRE-D2-NEUTRAL-CONTRACT-STEWARD-001":
        raise ValueError("unexpected profile_id")
    if packet["status"] != "BLOCKED_UPSTREAM_D1_AND_MISSING_STEWARD_EVIDENCE":
        raise ValueError("D2 must remain blocked until upstream and approval evidence exist")
    if packet["authority_effect"] != "none":
        raise ValueError("D2 packet must have no authority effect")

    source = packet["source_generation"]
    if not isinstance(source, dict) or set(source) != {"repository", "pull_request", "head", "decision"}:
        raise ValueError("source_generation must use the closed source tuple")
    if source["repository"] != "aevespers2/ALISTAIRE-" or type(source["pull_request"]) is not int or source["decision"] != "D2":
        raise ValueError("invalid source generation identity")
    if not SHA_RE.fullmatch(str(source["head"])):
        raise ValueError("source head must be a lowercase 40-character Git SHA")

    dependencies = packet["dependencies"]
    if not isinstance(dependencies, list) or len(dependencies) != 2:
        raise ValueError("D2 must bind exactly D1 and D3 dependencies")
    dependency_ids = {item.get("decision") for item in dependencies if isinstance(item, dict)}
    if dependency_ids != {"D1", "D3"}:
        raise ValueError("dependency closure must contain D1 and D3")

    models = packet["candidate_models"]
    if not isinstance(models, list) or {item.get("id") for item in models if isinstance(item, dict)} != EXPECTED_MODELS:
        raise ValueError("candidate model set is incomplete or changed")
    for model in models:
        if set(model) != {"id", "summary", "principal_risk"} or not all(isinstance(model[k], str) and model[k] for k in model):
            raise ValueError("candidate model entries must use the closed non-empty schema")

    if set(packet["required_decision_fields"]) != REQUIRED_DECISION_FIELDS:
        raise ValueError("required decision fields do not close over D2")

    gates = packet["readiness_gates"]
    if not isinstance(gates, list) or len(gates) != 10:
        raise ValueError("D2 requires ten readiness gates")
    gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    if gate_ids != [f"D2-G{i:02d}" for i in range(1, 11)]:
        raise ValueError("readiness gate identities or ordering changed")
    for gate in gates:
        if set(gate) != {"id", "name", "status"} or gate["status"] not in {"BLOCKED", "REVIEW"}:
            raise ValueError("invalid readiness gate")

    if set(packet["prohibited_promotions"]) != PROHIBITED:
        raise ValueError("prohibited authority promotions are incomplete")
    if set(packet["controlled_routes"]) != EXPECTED_ROUTES:
        raise ValueError("controlled routes are incomplete")

    propagation = packet["propagation"]
    if not isinstance(propagation, dict) or set(propagation) != {"rebind_marker", "withdrawal_marker", "completion_rule"}:
        raise ValueError("invalid propagation object")
    if propagation["rebind_marker"] != "D2_REBIND_REQUIRED" or propagation["withdrawal_marker"] != "D2_PACKET_WITHDRAWN":
        raise ValueError("propagation markers changed")

    for route in sorted(EXPECTED_ROUTES):
        path = Path(route)
        if not path.is_file():
            raise ValueError(f"controlled route missing: {route}")
        text = path.read_text(encoding="utf-8")
        if "D2_REBIND_REQUIRED" not in text or "D2_PACKET_WITHDRAWN" not in text:
            raise ValueError(f"controlled route lacks D2 propagation markers: {route}")

    gap = packet["proposed_subdivision_gap"]
    if not isinstance(gap, dict) or set(gap) != {"id", "name", "skills", "authority_effect"}:
        raise ValueError("invalid skill-tree gap")
    if gap["id"] != "013-F" or gap["authority_effect"] != "none":
        raise ValueError("skill-tree gap must remain non-authoritative")

    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be exact")

    return {
        "profile_id": packet["profile_id"],
        "status": packet["status"],
        "candidate_model_count": len(models),
        "readiness_gate_count": len(gates),
        "controlled_route_count": len(EXPECTED_ROUTES),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "submitted_sha": submitted_sha,
        "disposition": "D2_DECISION_READINESS_VALIDATED_NON_AUTHORIZING",
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
        print(json.dumps({"disposition": "D2_PACKET_FAILED_CLOSED", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
