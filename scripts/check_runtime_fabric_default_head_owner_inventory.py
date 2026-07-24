#!/usr/bin/env python3
"""Fail-closed validation for the runtime/Fabric default-head and owner-vacancy inventory."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/runtime-fabric-default-head-owner-inventory-v1.json")
STATUS = "DEFAULT_HEADS_VERIFIED_OWNER_VACANCIES_RECORDED_BINDINGS_UNACCEPTED"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TOP_FIELDS = {
    "profile_id", "profile_version", "status", "authority_effect", "observed_at",
    "scope", "legacy_labels", "default_head_observations", "candidate_lineage",
    "semantic_owner_vacancies", "route_owner_vacancies", "graph_edges",
    "invariants", "review_gates", "controlled_routes", "fysa_120",
}
EXPECTED_DEFAULT_HEADS = {
    "aevespers2/ALISTAIRE-": "7adbbf963616d09b4ebafea7c0963a2fac5688a9",
    "aevespers2/QSO-FABRIC": "bd0ac7af3b34602082db03e71055b652707c9b18",
    "aevespers2/QuantumStateObjects": "40efcbf8ce2bda7d6b05b3fb1f3ccf0384facc51",
    "aevespers2/1": "6685872ceafdefa4961e261abb45202e664e3666",
    "aevespers2/qsio-kernel": "6468254d7703e5f771e610ed3f76bac1b7205ddb",
    "aevespers2/qso-field.github.io": "2d7adf88ce84f01f0ff1067cef09388481f7e4ae",
}
EXPECTED_CANDIDATES = {
    ("aevespers2/ALISTAIRE-", 1): "84cdb1848449c40b54aab430a19c59e0167736dd",
    ("aevespers2/QSO-FABRIC", 21): "25036a5cfcea79e204a4660ddd1af09c054935b1",
    ("aevespers2/QuantumStateObjects", 12): "cc9b9c7b06a1a48bbc052b8d6bacd11782285288",
    ("aevespers2/1", 2): "47b58fa49c8dda7f44234dab68f78673bb02d269",
    ("aevespers2/qso-field.github.io", 24): "a56b1fa93f151ee14f3cdd4183b89a10e268e352",
}
EXPECTED_SEMANTIC_CLASSES = {
    "runtime_event_record", "runtime_execution_report", "fabric_projection_receipt",
    "fabric_collaboration_event", "fabric_aggregate_report", "portfolio_disposition",
}
EXPECTED_ROUTE_VACANCIES = {
    "kernel_to_runtime_mapping", "namespace_and_schema_registry",
    "live_producer_and_consumer_registration", "correction_and_revocation_propagation",
    "migration_and_rollback_coordination",
}
EXPECTED_EDGE_IDS = {
    "kernel_to_runtime_default_head", "runtime_to_fabric_default_head",
    "fabric_to_repository_1_default_head", "fabric_to_registry_default_head",
    "candidate_to_default_reconciliation",
}
EXPECTED_INVARIANTS = {
    "all_default_head_observations_bind_exact_commits",
    "path_absence_is_qualified_and_not_repository_wide_absence",
    "generic_ledger_or_receipt_terms_are_not_legacy_interface_bindings",
    "candidate_documentation_is_not_default_head_state",
    "candidate_role_is_not_semantic_ownership",
    "all_semantic_classes_have_explicit_owner_vacancies",
    "all_cross_repository_routes_have_explicit_owner_vacancies",
    "no_default_head_is_recorded_as_an_accepted_producer_or_consumer",
    "no_vacancy_is_silently_filled_by_repository_naming_or_documentation",
    "authority_effect_remains_none",
}
EXPECTED_GATES = {
    "CANDIDATE_HEADS_REBOUND_OR_WITHDRAWN",
    "REPOSITORY_LOCAL_COMPLETE_USE_INVENTORIES_VERIFIED",
    "SEMANTIC_OWNERS_APPOINTED_OR_VACANCIES_FORMALLY_ACCEPTED",
    "D1_D2_D3_ACCEPTED", "CANONICAL_PAYLOADS_IDENTITIES_AND_NAMESPACES_ACCEPTED",
    "LIVE_REGISTRATION_GOVERNANCE_ACCEPTED",
    "CORRECTION_REVOCATION_MIGRATION_AND_ROLLBACK_FIXTURES_PASS",
    "INDEPENDENT_SECURITY_PRIVACY_ACCESSIBILITY_LICENSE_AND_ARCHITECTURE_REVIEW_COMPLETE",
    "EXPLICIT_HUMAN_APPROVAL", "RESULTING_DEFAULT_HEADS_AND_RESTORED_STATE_VERIFIED",
}
EXPECTED_ROUTES = {
    "docs/runtime-fabric-default-head-owner-inventory.md",
    "docs/runtime-fabric-default-head-owner-inventory-v1.json", "mkdocs.yml",
}
REQUIRED_CATEGORIES = {
    "CAT-011", "CAT-012", "CAT-013", "CAT-017", "CAT-018", "CAT-019",
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
    packet = json.loads(raw, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    if not isinstance(packet, dict):
        raise ValueError("packet root must be an object")
    return packet


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing, unknown = expected - set(value), set(value) - expected
    if missing or unknown:
        raise ValueError(f"{label} fields mismatch: missing={sorted(missing)} unknown={sorted(unknown)}")


def unique_strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        raise ValueError(f"{label} must be {'a list' if allow_empty else 'a non-empty list'}")
    if not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{label} must contain non-empty strings")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return value


def validate_packet(packet: dict[str, Any], packet_path: Path = DEFAULT_PACKET,
                    submitted_sha: str | None = None, root: Path = Path(".")) -> dict[str, Any]:
    exact_keys(packet, TOP_FIELDS, "packet")
    if packet["profile_id"] != "ALISTAIRE-RUNTIME-FABRIC-DEFAULT-HEAD-OWNER-INVENTORY-001":
        raise ValueError("unexpected profile_id")
    if packet["profile_version"] != "1.0.0-candidate":
        raise ValueError("unexpected candidate profile version")
    if packet["status"] != STATUS:
        raise ValueError("inventory status changed")
    if packet["authority_effect"] != "NONE":
        raise ValueError("inventory must have no authority effect")
    if packet["observed_at"] != "2026-07-23":
        raise ValueError("unexpected observation date")
    if set(unique_strings(packet["legacy_labels"], "legacy_labels")) != {"qso-event-ledger", "qso-runtime-report"}:
        raise ValueError("legacy-label closure changed")

    observations = packet["default_head_observations"]
    if not isinstance(observations, list) or len(observations) != 6:
        raise ValueError("exactly six default-head observations are required")
    observed: dict[str, str] = {}
    for item in observations:
        if not isinstance(item, dict):
            raise ValueError("default-head observation must be an object")
        exact_keys(item, {"repository", "default_branch", "default_head_sha", "reviewed_paths",
            "present_paths", "absent_paths", "exact_legacy_label_observed", "generic_related_terms",
            "default_head_disposition", "owner_effect", "notes"}, "default-head observation")
        repository = item["repository"]
        if repository in observed:
            raise ValueError(f"duplicate default-head observation: {repository}")
        head = item["default_head_sha"]
        if not isinstance(head, str) or not SHA_RE.fullmatch(head):
            raise ValueError(f"invalid default head for {repository}")
        if item["default_branch"] != "main":
            raise ValueError(f"unexpected default branch for {repository}")
        observed[repository] = head
        reviewed = set(unique_strings(item["reviewed_paths"], f"{repository} reviewed_paths"))
        present = set(unique_strings(item["present_paths"], f"{repository} present_paths", allow_empty=True))
        absent = set(unique_strings(item["absent_paths"], f"{repository} absent_paths", allow_empty=True))
        if present & absent:
            raise ValueError(f"present/absent path overlap for {repository}")
        if present | absent != reviewed:
            raise ValueError(f"reviewed path closure mismatch for {repository}")
        if item["exact_legacy_label_observed"] is not False:
            raise ValueError(f"legacy interface binding was promoted at default head: {repository}")
        unique_strings(item["generic_related_terms"], f"{repository} generic_related_terms", allow_empty=True)
        if item["owner_effect"] != "NONE":
            raise ValueError(f"default head cannot create owner effect: {repository}")
        if not item["default_head_disposition"] or not item["notes"]:
            raise ValueError(f"default-head explanation missing for {repository}")
    if observed != EXPECTED_DEFAULT_HEADS:
        raise ValueError(f"default-head closure changed: {observed}")

    lineage = packet["candidate_lineage"]
    if not isinstance(lineage, list) or len(lineage) != len(EXPECTED_CANDIDATES):
        raise ValueError("candidate lineage closure changed")
    candidate_map: dict[tuple[str, int], str] = {}
    for item in lineage:
        exact_keys(item, {"repository", "pull_request", "candidate_head_sha", "relation_to_default"}, "candidate lineage entry")
        if not isinstance(item["pull_request"], int) or isinstance(item["pull_request"], bool):
            raise ValueError("pull_request must be an integer")
        key = (item["repository"], item["pull_request"])
        if key in candidate_map:
            raise ValueError(f"duplicate candidate lineage entry: {key}")
        head = item["candidate_head_sha"]
        if not isinstance(head, str) or not SHA_RE.fullmatch(head):
            raise ValueError(f"invalid candidate head: {key}")
        if not item["relation_to_default"]:
            raise ValueError(f"candidate relation missing: {key}")
        candidate_map[key] = head
    if candidate_map != EXPECTED_CANDIDATES:
        raise ValueError("candidate lineage drifted")

    semantic = packet["semantic_owner_vacancies"]
    if not isinstance(semantic, list) or len(semantic) != len(EXPECTED_SEMANTIC_CLASSES):
        raise ValueError("semantic owner vacancy closure changed")
    semantic_classes: set[str] = set()
    for item in semantic:
        exact_keys(item, {"semantic_class", "candidate_repository", "accepted_owner", "owner_status",
                          "authority_effect", "rationale"}, "semantic owner vacancy")
        semantic_classes.add(item["semantic_class"])
        if item["accepted_owner"] is not None:
            raise ValueError("accepted semantic owner assignment is prohibited")
        if item["owner_status"] != "EXPLICIT_VACANCY" or item["authority_effect"] != "NONE":
            raise ValueError("semantic owner must remain a non-authorizing explicit vacancy")
        if not item["candidate_repository"] or not item["rationale"]:
            raise ValueError("semantic vacancy explanation missing")
    if semantic_classes != EXPECTED_SEMANTIC_CLASSES:
        raise ValueError("semantic class closure changed")

    route_vacancies = packet["route_owner_vacancies"]
    if not isinstance(route_vacancies, list) or len(route_vacancies) != len(EXPECTED_ROUTE_VACANCIES):
        raise ValueError("route owner vacancy closure changed")
    routes_seen: set[str] = set()
    for item in route_vacancies:
        exact_keys(item, {"route", "accepted_owner", "owner_status", "required_before_acceptance"}, "route owner vacancy")
        routes_seen.add(item["route"])
        if item["accepted_owner"] is not None:
            raise ValueError("accepted route owner assignment is prohibited")
        if item["owner_status"] != "EXPLICIT_VACANCY" or not item["required_before_acceptance"]:
            raise ValueError("route owner must remain an explained explicit vacancy")
    if routes_seen != EXPECTED_ROUTE_VACANCIES:
        raise ValueError("route owner vacancy identities changed")

    edges = packet["graph_edges"]
    if not isinstance(edges, list) or len(edges) != len(EXPECTED_EDGE_IDS):
        raise ValueError("graph edge closure changed")
    edge_ids: set[str] = set()
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"id", "source", "target", "status"}:
            raise ValueError("graph edge schema changed")
        if not all(isinstance(edge[key], str) and edge[key] for key in edge):
            raise ValueError("graph edge fields must be non-empty strings")
        edge_ids.add(edge["id"])
    if edge_ids != EXPECTED_EDGE_IDS:
        raise ValueError("graph edge identities changed")
    if set(unique_strings(packet["invariants"], "invariants")) != EXPECTED_INVARIANTS:
        raise ValueError("invariant closure changed")
    if set(unique_strings(packet["review_gates"], "review_gates")) != EXPECTED_GATES:
        raise ValueError("review-gate closure changed")
    controlled = set(unique_strings(packet["controlled_routes"], "controlled_routes"))
    if controlled != EXPECTED_ROUTES:
        raise ValueError("controlled-route closure changed")

    mapping = packet["fysa_120"]
    if not isinstance(mapping, dict) or set(mapping) != {"categories", "subdivisions", "proposed_gap"}:
        raise ValueError("FYSA-120 mapping schema changed")
    if set(unique_strings(mapping["categories"], "FYSA categories")) != REQUIRED_CATEGORIES:
        raise ValueError("FYSA category mapping changed")
    unique_strings(mapping["subdivisions"], "FYSA subdivisions")
    gap = mapping["proposed_gap"]
    if not isinstance(gap, dict) or set(gap) != {"id", "name", "authoritative"}:
        raise ValueError("proposed gap schema changed")
    if gap["id"] != "013-H" or gap["authoritative"] is not False:
        raise ValueError("proposed gap must remain 013-H and non-authoritative")

    for route in sorted(EXPECTED_ROUTES):
        path = root / route
        if not path.is_file():
            raise ValueError(f"controlled documentation route missing: {route}")
        folded = path.read_text(encoding="utf-8").casefold()
        if "runtime/fabric" not in folded or STATUS.casefold() not in folded:
            raise ValueError(f"controlled route lacks default-head owner inventory markers: {route}")
    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be an exact lowercase 40-character Git SHA")
    return {
        "profile_id": packet["profile_id"], "profile_version": packet["profile_version"],
        "status": packet["status"], "default_head_count": len(observations),
        "candidate_lineage_count": len(lineage), "semantic_owner_vacancy_count": len(semantic),
        "route_owner_vacancy_count": len(route_vacancies), "graph_edge_count": len(edges),
        "controlled_route_count": len(controlled), "authority_effect": "NONE",
        "disposition": "RUNTIME_FABRIC_DEFAULT_HEAD_OWNER_INVENTORY_VALIDATED_NON_AUTHORIZING",
        "submitted_sha": submitted_sha, "packet_path": str(packet_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--submitted-sha")
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    try:
        report = validate_packet(load_packet(args.packet), args.packet, args.submitted_sha, args.root)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "INVALID", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
