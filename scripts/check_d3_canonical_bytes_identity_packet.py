#!/usr/bin/env python3
"""Fail-closed validation for the proposed D3 canonical-bytes packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_PROFILES = {
    "STRICT_CANONICAL_JSON_SUBSET",
    "DETERMINISTIC_CBOR_PROFILE",
    "TYPED_MODEL_WITH_CANONICAL_JSON_ENVELOPE",
}
EXPECTED_ROUTES = {
    "README.md",
    "docs/index.md",
    "docs/d3-canonical-bytes-identity-decision-packet.md",
    "taskchain.md",
    "release.md",
    "punchlist.md",
    "changelog.md",
}
TOP_FIELDS = {
    "profile_id", "version", "status", "authority_effect", "source_generation",
    "dependencies", "purpose", "candidate_profiles", "required_primitives",
    "required_decision_fields", "readiness_gates", "hostile_fixture_classes",
    "cross_language_witness", "prohibited_promotions", "controlled_routes",
    "propagation", "skill_tree_mapping", "proposed_subdivision_gap",
}
REQUIRED_PRIMITIVES = {
    "utf8_encoding", "unicode_normalization", "object_member_order",
    "duplicate_key_rejection", "integer_and_decimal_domain",
    "negative_zero_and_nonfinite_values", "null_missing_and_default_semantics",
    "timestamp_duration_and_clock_profile", "binary_value_representation",
    "digest_algorithm_and_domain_separation",
    "signature_reference_and_attestation_binding", "namespace_and_identifier_grammar",
    "subject_device_and_environment_identity",
    "proposal_capability_receipt_and_disposition_identity",
    "correction_revocation_checkpoint_and_supersession_identity",
    "extension_unknown_field_and_replay_domain_rules",
}
REQUIRED_DECISION_FIELDS = {
    "selected_profile_by_contract_family", "canonical_abstract_data_model",
    "utf8_and_unicode_normalization", "object_and_map_ordering",
    "integer_decimal_and_precision_rules", "negative_zero_nan_and_infinity_rules",
    "null_missing_default_and_optional_semantics",
    "timestamp_duration_clock_and_skew_rules",
    "binary_value_and_attachment_reference_rules",
    "digest_algorithms_and_domain_separation",
    "signature_reference_and_attestation_semantics",
    "namespace_version_and_identifier_grammar",
    "subject_device_environment_and_workspace_identity",
    "proposal_capability_receipt_disposition_and_result_identity",
    "correction_revocation_checkpoint_supersession_and_tombstone_identity",
    "replay_domain_sequence_idempotency_and_duplicate_rules",
    "extension_unknown_field_and_unsupported_version_behavior",
    "cross_language_fixture_and_expected_result_custody",
    "compatibility_migration_deprecation_correction_and_withdrawal",
    "rollback_restored_state_and_failed_rollback",
}
HOSTILE_CLASSES = {
    "invalid_utf8", "duplicate_object_keys", "non_normalized_unicode",
    "confusable_identifier", "nonfinite_number", "negative_zero_alias",
    "integer_out_of_profile", "decimal_rounding_divergence",
    "timestamp_offset_alias", "unsupported_leap_second",
    "null_missing_default_collapse", "unknown_field_acceptance",
    "extension_namespace_collision", "identifier_case_collision",
    "digest_domain_confusion", "signature_reference_substitution",
    "replay_domain_collision", "lossy_transcoding_without_disclosure",
    "unsupported_profile_version",
}
PROHIBITED = {
    "parser_success_to_canonical_acceptance",
    "same_digest_to_same_semantic_class",
    "same_shape_to_compatible_contract",
    "transport_or_encoding_to_authority",
    "signature_presence_to_valid_authorization",
    "canonical_bytes_to_truth_or_currentness",
    "passing_ci_to_profile_acceptance",
    "registry_entry_to_consumer_admission",
    "skill_mapping_to_competence_or_permission",
}
WITNESS_COMPARE = {
    "accepted_or_rejected_disposition", "normalized_abstract_value",
    "canonical_bytes", "digest", "record_identity", "reason_code",
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
    if packet["profile_id"] != "ALISTAIRE-D3-CANONICAL-BYTES-IDENTITY-001":
        raise ValueError("unexpected profile_id")
    if packet["status"] != "BLOCKED_UPSTREAM_D2_AND_MISSING_CROSS_LANGUAGE_EVIDENCE":
        raise ValueError("D3 must remain blocked until D2 and independent evidence exist")
    if packet["authority_effect"] != "none":
        raise ValueError("D3 packet must have no authority effect")

    source = packet["source_generation"]
    if not isinstance(source, dict) or set(source) != {"repository", "pull_request", "head", "decision"}:
        raise ValueError("source_generation must use the closed source tuple")
    if source["repository"] != "aevespers2/ALISTAIRE-" or type(source["pull_request"]) is not int or source["decision"] != "D3":
        raise ValueError("invalid source generation identity")
    if not SHA_RE.fullmatch(str(source["head"])):
        raise ValueError("source head must be a lowercase 40-character Git SHA")

    dependencies = packet["dependencies"]
    if not isinstance(dependencies, list) or len(dependencies) != 2:
        raise ValueError("D3 must bind exactly D1 and D2 dependencies")
    dependency_ids = {item.get("decision") for item in dependencies if isinstance(item, dict)}
    if dependency_ids != {"D1", "D2"}:
        raise ValueError("dependency closure must contain D1 and D2")
    for item in dependencies:
        if not isinstance(item, dict) or set(item) != {"decision", "required_state", "current_state"}:
            raise ValueError("dependency entries must use the closed schema")

    profiles = packet["candidate_profiles"]
    if not isinstance(profiles, list) or {item.get("id") for item in profiles if isinstance(item, dict)} != EXPECTED_PROFILES:
        raise ValueError("candidate profile set is incomplete or changed")
    for profile in profiles:
        if set(profile) != {"id", "summary", "principal_risk"} or not all(isinstance(profile[key], str) and profile[key] for key in profile):
            raise ValueError("candidate profile entries must use the closed non-empty schema")

    if set(packet["required_primitives"]) != REQUIRED_PRIMITIVES:
        raise ValueError("required primitives do not close over D3")
    if set(packet["required_decision_fields"]) != REQUIRED_DECISION_FIELDS:
        raise ValueError("required decision fields do not close over D3")

    gates = packet["readiness_gates"]
    if not isinstance(gates, list) or len(gates) != 12:
        raise ValueError("D3 requires twelve readiness gates")
    gate_ids = [gate.get("id") for gate in gates if isinstance(gate, dict)]
    if gate_ids != [f"D3-G{i:02d}" for i in range(1, 13)]:
        raise ValueError("readiness gate identities or ordering changed")
    for gate in gates:
        if set(gate) != {"id", "name", "status"} or gate["status"] not in {"BLOCKED", "REVIEW"}:
            raise ValueError("invalid readiness gate")

    if set(packet["hostile_fixture_classes"]) != HOSTILE_CLASSES:
        raise ValueError("hostile fixture coverage is incomplete")

    witness = packet["cross_language_witness"]
    if not isinstance(witness, dict) or set(witness) != {
        "minimum_independent_implementations", "implementation_independence_required",
        "compare", "current_state",
    }:
        raise ValueError("invalid cross-language witness object")
    if type(witness["minimum_independent_implementations"]) is not int or witness["minimum_independent_implementations"] < 2:
        raise ValueError("at least two independent implementations are required")
    if witness["implementation_independence_required"] is not True:
        raise ValueError("implementation independence must remain required")
    if set(witness["compare"]) != WITNESS_COMPARE:
        raise ValueError("cross-language comparison closure is incomplete")
    if witness["current_state"] != "NO_ACCEPTED_CROSS_LANGUAGE_WITNESS":
        raise ValueError("packet cannot claim accepted cross-language evidence")

    if set(packet["prohibited_promotions"]) != PROHIBITED:
        raise ValueError("prohibited authority promotions are incomplete")
    if set(packet["controlled_routes"]) != EXPECTED_ROUTES:
        raise ValueError("controlled routes are incomplete")

    propagation = packet["propagation"]
    if not isinstance(propagation, dict) or set(propagation) != {"rebind_marker", "withdrawal_marker", "completion_rule"}:
        raise ValueError("invalid propagation object")
    if propagation["rebind_marker"] != "D3_REBIND_REQUIRED" or propagation["withdrawal_marker"] != "D3_PACKET_WITHDRAWN":
        raise ValueError("propagation markers changed")

    for route in sorted(EXPECTED_ROUTES):
        path = Path(route)
        if not path.is_file():
            raise ValueError(f"controlled route missing: {route}")
        text = path.read_text(encoding="utf-8")
        if "D3_REBIND_REQUIRED" not in text or "D3_PACKET_WITHDRAWN" not in text:
            raise ValueError(f"controlled route lacks D3 propagation markers: {route}")

    gap = packet["proposed_subdivision_gap"]
    if not isinstance(gap, dict) or set(gap) != {"id", "name", "skills", "authority_effect"}:
        raise ValueError("invalid skill-tree gap")
    if gap["id"] != "031-Q" or gap["authority_effect"] != "none":
        raise ValueError("skill-tree gap must remain non-authoritative")
    if not isinstance(gap["skills"], list) or len(gap["skills"]) < 5:
        raise ValueError("skill-tree gap must record bounded missing capabilities")

    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be exact")

    return {
        "profile_id": packet["profile_id"],
        "status": packet["status"],
        "candidate_profile_count": len(profiles),
        "primitive_count": len(REQUIRED_PRIMITIVES),
        "readiness_gate_count": len(gates),
        "hostile_fixture_class_count": len(HOSTILE_CLASSES),
        "controlled_route_count": len(EXPECTED_ROUTES),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "submitted_sha": submitted_sha,
        "disposition": "D3_DECISION_READINESS_VALIDATED_NON_AUTHORIZING",
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
        print(json.dumps({"disposition": "D3_PACKET_FAILED_CLOSED", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
