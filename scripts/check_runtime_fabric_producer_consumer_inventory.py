#!/usr/bin/env python3
"""Fail-closed validation for the runtime/Fabric producer-consumer inventory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/runtime-fabric-producer-consumer-inventory-v1.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
STATUS = "OBSERVED_CANDIDATE_INVENTORY_RECORDED_BLOCKED_UNACCEPTED_BINDINGS"

TOP_FIELDS = {
    "profile_id", "profile_version", "status", "authority_effect", "observed_at",
    "scope", "legacy_labels", "repositories", "synthetic_consumer_closure",
    "graph_edges", "invariants", "review_gates", "controlled_routes", "fysa_120",
}
EXPECTED_REPOSITORIES = {
    "aevespers2/ALISTAIRE-": "174f8b32af4b20f7d197942fda7347c501a16a8e",
    "aevespers2/QSO-FABRIC": "25036a5cfcea79e204a4660ddd1af09c054935b1",
    "aevespers2/QuantumStateObjects": "cc9b9c7b06a1a48bbc052b8d6bacd11782285288",
    "aevespers2/1": "47b58fa49c8dda7f44234dab68f78673bb02d269",
    "aevespers2/qsio-kernel": "6468254d7703e5f771e610ed3f76bac1b7205ddb",
    "aevespers2/qso-field.github.io": "a56b1fa93f151ee14f3cdd4183b89a10e268e352",
}
EXPECTED_ROLES = {
    "governance_decision_packet",
    "declaration_producer",
    "runtime_documentation_and_synthetic_consumer",
    "independent_conformance_consumer",
    "executable_reference_kernel_candidate",
    "portfolio_registry_and_governance_reference",
}
EXPECTED_BINDINGS = {
    "NO_ACCEPTED_BINDING",
    "DECLARED_NOT_ACCEPTED",
    "DOCUMENTED_NOT_ACCEPTED",
    "CONSUMER_EVIDENCE_NOT_INTERFACE_ACCEPTANCE",
}
EXPECTED_EDGE_IDS = {
    "runtime_to_fabric_projection",
    "kernel_to_runtime_contract",
    "fabric_to_repository_1_disposition",
    "fabric_to_portfolio_registry",
    "charter_to_candidate_surfaces",
}
EXPECTED_INVARIANTS = {
    "all_repository_observations_bind_exact_heads",
    "synthetic_consumer_evidence_is_not_live_compatibility",
    "internal_qsio_ledger_is_not_silently_mapped_to_legacy_labels",
    "no_repository_is_recorded_as_an_accepted_producer_or_consumer",
    "ambiguous_or_unobserved_legacy_uses_fail_closed",
    "projection_is_not_independent_evidence",
    "runtime_success_is_not_fabric_success",
    "fabric_success_is_not_portfolio_disposition",
    "correction_revocation_and_rollback_routes_remain_unresolved",
    "authority_effect_remains_none",
}
EXPECTED_GATES = {
    "D1_ACCEPTED", "D2_ACCEPTED", "D3_ACCEPTED",
    "PARTITION_PROFILE_SELECTED",
    "REPOSITORY_LOCAL_SEMANTIC_OWNERS_CONFIRMED",
    "EXACT_DEFAULT_HEAD_INVENTORY_VERIFIED",
    "FINAL_PAYLOAD_SCHEMAS_AND_CANONICAL_BYTES_ACCEPTED",
    "LIVE_PRODUCER_AND_CONSUMER_REGISTRATIONS_ACCEPTED",
    "MIGRATION_CORRECTION_REVOCATION_AND_ROLLBACK_FIXTURES_PASS",
    "INDEPENDENT_SECURITY_PRIVACY_ACCESSIBILITY_LICENSE_AND_ARCHITECTURE_REVIEW_COMPLETE",
    "EXPLICIT_HUMAN_APPROVAL", "RESULTING_STATE_VERIFIED",
}
EXPECTED_ROUTES = {
    "docs/runtime-fabric-producer-consumer-inventory.md", "mkdocs.yml",
}
REQUIRED_CATEGORIES = {
    "CAT-011", "CAT-012", "CAT-013", "CAT-017", "CAT-019",
    "CAT-031", "CAT-032", "CAT-040", "CAT-052", "CAT-059", "CAT-070",
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
    raw = path.read_bytes().decode("utf-8", errors="strict")
    packet = json.loads(
        raw, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant
    )
    if not isinstance(packet, dict):
        raise ValueError("packet root must be an object")
    return packet


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    unknown = set(value) - expected
    if missing or unknown:
        raise ValueError(
            f"{label} fields mismatch: missing={sorted(missing)} "
            f"unknown={sorted(unknown)}"
        )


def unique_strings(value: Any, label: str) -> list[str]:
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
    root: Path = Path("."),
) -> dict[str, Any]:
    exact_keys(packet, TOP_FIELDS, "packet")
    if packet["profile_id"] != "ALISTAIRE-RUNTIME-FABRIC-PRODUCER-CONSUMER-INVENTORY-001":
        raise ValueError("unexpected profile_id")
    if packet["profile_version"] != "1.0.0-candidate":
        raise ValueError("unexpected candidate profile version")
    if packet["status"] != STATUS:
        raise ValueError("inventory status changed")
    if packet["authority_effect"] != "NONE":
        raise ValueError("inventory must have no authority effect")
    if packet["observed_at"] != "2026-07-23":
        raise ValueError("unexpected observation date")
    if set(unique_strings(packet["legacy_labels"], "legacy_labels")) != {
        "qso-event-ledger", "qso-runtime-report"
    }:
        raise ValueError("legacy-label closure changed")

    repositories = packet["repositories"]
    if not isinstance(repositories, list) or len(repositories) != 6:
        raise ValueError("exactly six repository observations are required")
    observed: dict[str, str] = {}
    roles: set[str] = set()
    all_paths: set[tuple[str, str]] = set()
    for item in repositories:
        if not isinstance(item, dict):
            raise ValueError("repository observation must be an object")
        exact_keys(item, {
            "repository", "ref_kind", "ref", "head_sha", "candidate_role",
            "observed_paths", "label_uses", "semantic_classification",
            "binding_disposition", "accepted_producer", "accepted_consumer", "notes",
        }, "repository observation")
        repository = item["repository"]
        if repository in observed:
            raise ValueError(f"duplicate repository observation: {repository}")
        head = item["head_sha"]
        if not isinstance(head, str) or not SHA_RE.fullmatch(head):
            raise ValueError(f"invalid exact head for {repository}")
        observed[repository] = head
        roles.add(item["candidate_role"])
        paths = unique_strings(item["observed_paths"], f"{repository} observed_paths")
        for path in paths:
            key = (repository, path)
            if key in all_paths:
                raise ValueError(f"duplicate observed path: {repository}:{path}")
            all_paths.add(key)
        label_uses = item["label_uses"]
        if not isinstance(label_uses, dict) or set(label_uses) != {
            "qso-event-ledger", "qso-runtime-report"
        }:
            raise ValueError(f"legacy-label uses incomplete for {repository}")
        if not all(isinstance(value, str) and value for value in label_uses.values()):
            raise ValueError(f"legacy-label uses invalid for {repository}")
        if item["binding_disposition"] not in EXPECTED_BINDINGS:
            raise ValueError(f"unexpected binding disposition for {repository}")
        if item["accepted_producer"] is not False or item["accepted_consumer"] is not False:
            raise ValueError(f"accepted binding is prohibited for {repository}")
        if not isinstance(item["semantic_classification"], str) or not item["semantic_classification"]:
            raise ValueError(f"semantic classification missing for {repository}")
        if not isinstance(item["notes"], str) or not item["notes"]:
            raise ValueError(f"notes missing for {repository}")

    if observed != EXPECTED_REPOSITORIES:
        raise ValueError(f"repository/head closure changed: {observed}")
    if roles != EXPECTED_ROLES:
        raise ValueError("candidate role closure changed")
    kernel = next(item for item in repositories if item["repository"] == "aevespers2/qsio-kernel")
    if set(kernel["label_uses"].values()) != {
        "exact_legacy_label_not_observed_in_reviewed_paths"
    }:
        raise ValueError("qsio-kernel must remain explicitly unmapped")

    closure = packet["synthetic_consumer_closure"]
    if not isinstance(closure, dict):
        raise ValueError("synthetic consumer closure must be an object")
    exact_keys(closure, {
        "producer_repository", "producer_head", "consumers", "disposition"
    }, "synthetic consumer closure")
    if closure["producer_repository"] != "aevespers2/QSO-FABRIC":
        raise ValueError("unexpected synthetic producer")
    if closure["producer_head"] != EXPECTED_REPOSITORIES["aevespers2/QSO-FABRIC"]:
        raise ValueError("synthetic producer head drifted")
    consumers = closure["consumers"]
    if not isinstance(consumers, list) or len(consumers) != 2:
        raise ValueError("exactly two synthetic consumers are required")
    consumer_map: dict[str, str] = {}
    for item in consumers:
        if not isinstance(item, dict) or set(item) != {"repository", "head_sha"}:
            raise ValueError("consumer tuple schema changed")
        consumer_map[item["repository"]] = item["head_sha"]
    if consumer_map != {
        "aevespers2/QuantumStateObjects": EXPECTED_REPOSITORIES["aevespers2/QuantumStateObjects"],
        "aevespers2/1": EXPECTED_REPOSITORIES["aevespers2/1"],
    }:
        raise ValueError("synthetic consumer closure drifted")
    if closure["disposition"] != "TWO_INDEPENDENT_SYNTHETIC_CONSUMERS_RECORDED_NOT_LIVE_COMPATIBILITY":
        raise ValueError("consumer evidence was promoted beyond its bounded meaning")

    edges = packet["graph_edges"]
    if not isinstance(edges, list) or len(edges) != len(EXPECTED_EDGE_IDS):
        raise ValueError("graph edge closure changed")
    edge_ids: set[str] = set()
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"id", "source", "target", "status"}:
            raise ValueError("graph edge schema changed")
        edge_ids.add(edge["id"])
        if not all(isinstance(edge[key], str) and edge[key] for key in edge):
            raise ValueError("graph edge fields must be non-empty strings")
    if edge_ids != EXPECTED_EDGE_IDS:
        raise ValueError("graph edge identities changed")

    if set(unique_strings(packet["invariants"], "invariants")) != EXPECTED_INVARIANTS:
        raise ValueError("invariant closure changed")
    if set(unique_strings(packet["review_gates"], "review_gates")) != EXPECTED_GATES:
        raise ValueError("review-gate closure changed")
    routes = set(unique_strings(packet["controlled_routes"], "controlled_routes"))
    if routes != EXPECTED_ROUTES:
        raise ValueError("controlled-route closure changed")

    mapping = packet["fysa_120"]
    if not isinstance(mapping, dict) or set(mapping) != {
        "categories", "subdivisions", "proposed_gap"
    }:
        raise ValueError("FYSA-120 mapping schema changed")
    if set(unique_strings(mapping["categories"], "FYSA categories")) != REQUIRED_CATEGORIES:
        raise ValueError("FYSA category mapping changed")
    unique_strings(mapping["subdivisions"], "FYSA subdivisions")
    gap = mapping["proposed_gap"]
    if not isinstance(gap, dict) or set(gap) != {"id", "name", "authoritative"}:
        raise ValueError("proposed gap schema changed")
    if gap["id"] != "040-L" or gap["authoritative"] is not False:
        raise ValueError("proposed gap must remain 040-L and non-authoritative")

    for route in sorted(EXPECTED_ROUTES):
        path = root / route
        if not path.is_file():
            raise ValueError(f"controlled documentation route missing: {route}")
        folded = path.read_text(encoding="utf-8").casefold()
        if "runtime/fabric" not in folded or STATUS.casefold() not in folded:
            raise ValueError(f"controlled route lacks inventory markers: {route}")

    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be an exact lowercase 40-character Git SHA")

    return {
        "profile_id": packet["profile_id"],
        "profile_version": packet["profile_version"],
        "status": packet["status"],
        "repository_count": len(repositories),
        "synthetic_consumer_count": len(consumers),
        "graph_edge_count": len(edges),
        "invariant_count": len(EXPECTED_INVARIANTS),
        "review_gate_count": len(EXPECTED_GATES),
        "controlled_route_count": len(routes),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "submitted_sha": submitted_sha,
        "disposition": "RUNTIME_FABRIC_INVENTORY_VALIDATED_NON_AUTHORIZING",
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
        print(json.dumps({
            "disposition": "RUNTIME_FABRIC_INVENTORY_FAILED_CLOSED",
            "error": str(exc),
        }, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
