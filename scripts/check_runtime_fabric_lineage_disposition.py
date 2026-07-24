#!/usr/bin/env python3
"""Fail-closed validation for the runtime/Fabric candidate-lineage disposition packet."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/runtime-fabric-lineage-disposition-v1.json")
STATUS = "CANDIDATE_LINEAGES_CLASSIFIED_REBIND_WITHDRAW_OR_ACCEPT_REQUIRED"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
TOP_FIELDS = {
    "profile_id", "profile_version", "status", "authority_effect", "observed_at",
    "scope", "source_generation", "legacy_labels", "lineages",
    "disposition_vocabulary", "graph_edges", "invariants", "review_gates",
    "controlled_routes", "planning_alignment", "fysa_120",
}
EXPECTED_LINEAGES = {
    ("aevespers2/ALISTAIRE-", 1): (
        "22b6c93ad48a0c3aeaa492b1ba97338bbcbddfd5", "PRESERVE_AND_REBIND"
    ),
    ("aevespers2/QSO-FABRIC", 21): (
        "25036a5cfcea79e204a4660ddd1af09c054935b1", "PRESERVE_PENDING_ARCHITECTURE"
    ),
    ("aevespers2/QuantumStateObjects", 12): (
        "cc9b9c7b06a1a48bbc052b8d6bacd11782285288", "PRESERVE_PENDING_ARCHITECTURE"
    ),
    ("aevespers2/1", 2): (
        "47b58fa49c8dda7f44234dab68f78673bb02d269", "PRESERVE_PENDING_ARCHITECTURE"
    ),
    ("aevespers2/qso-field.github.io", 24): (
        "a56b1fa93f151ee14f3cdd4183b89a10e268e352", "PRESERVE_PENDING_ARCHITECTURE"
    ),
    ("aevespers2/qsio-kernel", None): (
        "6468254d7703e5f771e610ed3f76bac1b7205ddb", "NO_CANDIDATE_MAPPING"
    ),
}
EXPECTED_DISPOSITIONS = {
    "PRESERVE_AND_REBIND", "PRESERVE_PENDING_ARCHITECTURE",
    "WITHDRAW_IF_SUPERSEDED", "NO_CANDIDATE_MAPPING",
}
EXPECTED_EDGE_IDS = {
    "kernel_to_runtime", "runtime_to_fabric", "fabric_to_repository_1",
    "fabric_to_registry", "governance_to_portfolio",
}
EXPECTED_INVARIANTS = {
    "every_lineage_binds_one_exact_commit",
    "candidate_state_is_distinct_from_default_branch_state",
    "historical_workflow_success_does_not_validate_a_moved_head",
    "preservation_does_not_mean_acceptance_or_merge",
    "synthetic_consumer_evidence_does_not_create_live_registration",
    "repository_name_or_documentation_does_not_assign_semantic_ownership",
    "kernel_internal_records_are_not_runtime_or_fabric_bindings_without_a_crosswalk",
    "supersession_requires_replacement_identity_reason_and_propagation",
    "withdrawal_preserves_history_and_rollback_target",
    "authority_effect_remains_none",
}
EXPECTED_GATES = {
    "CURRENT_CANDIDATE_AND_DEFAULT_HEADS_RECONCILED",
    "PREDECESSOR_PROVENANCE_AND_ROLLBACK_TARGETS_PRESERVED",
    "SEMANTIC_AND_ROUTE_OWNERS_APPOINTED_OR_VACANCIES_FORMALLY_ACCEPTED",
    "D1_D2_D3_ACCEPTED_OR_BLOCK_STATUS_RECORDED",
    "CANONICAL_PAYLOADS_BYTES_IDENTITIES_NAMESPACES_AND_SOURCE_SETS_ACCEPTED",
    "LIVE_PRODUCER_AND_CONSUMER_REGISTRATION_GOVERNANCE_ACCEPTED",
    "PAIRWISE_AND_TRIPLE_OVERLAP_FIXTURES_PASS",
    "MIXED_GENERATION_CORRECTION_REVOCATION_ROLLBACK_AND_RESTORATION_PASS",
    "INDEPENDENT_SECURITY_PRIVACY_ACCESSIBILITY_LICENSE_AND_ARCHITECTURE_REVIEW_COMPLETE",
    "EXPLICIT_HUMAN_APPROVAL",
    "RESULTING_DEFAULT_HEADS_AND_RETAINED_EVIDENCE_VERIFIED",
}
EXPECTED_ROUTES = {
    "docs/runtime-fabric-lineage-disposition.md",
    "docs/runtime-fabric-lineage-disposition-v1.json",
    "mkdocs.yml",
}
EXPECTED_PLANNING = {"taskchain.md", "release.md", "punchlist.md", "changelog.md"}
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
    value = json.loads(raw, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError("packet root must be an object")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    unknown = set(value) - expected
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


def validate_packet(
    packet: dict[str, Any],
    packet_path: Path = DEFAULT_PACKET,
    submitted_sha: str | None = None,
    root: Path = Path("."),
) -> dict[str, Any]:
    exact_keys(packet, TOP_FIELDS, "packet")
    if packet["profile_id"] != "ALISTAIRE-RUNTIME-FABRIC-LINEAGE-DISPOSITION-001":
        raise ValueError("unexpected profile_id")
    if packet["profile_version"] != "1.0.0-candidate":
        raise ValueError("unexpected profile version")
    if packet["status"] != STATUS:
        raise ValueError("lineage disposition status changed")
    if packet["authority_effect"] != "NONE":
        raise ValueError("authority effect must remain NONE")
    if packet["observed_at"] != "2026-07-23":
        raise ValueError("unexpected observation date")
    if not isinstance(packet["scope"], str) or not packet["scope"]:
        raise ValueError("scope must be a non-empty string")

    source = packet["source_generation"]
    if not isinstance(source, dict):
        raise ValueError("source_generation must be an object")
    exact_keys(source, {"repository", "pull_request", "head_sha", "source_profile", "relation"}, "source_generation")
    if source != {
        "repository": "aevespers2/ALISTAIRE-",
        "pull_request": 1,
        "head_sha": "22b6c93ad48a0c3aeaa492b1ba97338bbcbddfd5",
        "source_profile": "docs/runtime-fabric-default-head-owner-inventory-v1.json",
        "relation": "HISTORICAL_PARENT_INPUT_NOT_SELF_REFERENCE",
    }:
        raise ValueError("source generation drifted")
    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA is invalid")

    if set(unique_strings(packet["legacy_labels"], "legacy_labels")) != {"qso-event-ledger", "qso-runtime-report"}:
        raise ValueError("legacy-label closure changed")

    lineages = packet["lineages"]
    if not isinstance(lineages, list) or len(lineages) != len(EXPECTED_LINEAGES):
        raise ValueError("lineage closure changed")
    observed: dict[tuple[str, int | None], tuple[str, str]] = {}
    for item in lineages:
        if not isinstance(item, dict):
            raise ValueError("lineage entry must be an object")
        exact_keys(item, {
            "repository", "surface_kind", "pull_request", "branch", "exact_head_sha",
            "observed_use_classes", "current_state", "disposition", "accepted_binding",
            "authority_effect", "required_next_action",
        }, "lineage entry")
        pr = item["pull_request"]
        if pr is not None and (not isinstance(pr, int) or isinstance(pr, bool) or pr < 1):
            raise ValueError("pull_request must be null or a positive integer")
        key = (item["repository"], pr)
        if key in observed:
            raise ValueError(f"duplicate lineage: {key}")
        head = item["exact_head_sha"]
        if not isinstance(head, str) or not SHA_RE.fullmatch(head):
            raise ValueError(f"invalid exact head for {key}")
        if item["disposition"] not in EXPECTED_DISPOSITIONS:
            raise ValueError(f"unknown disposition for {key}")
        if item["accepted_binding"] is not False:
            raise ValueError(f"lineage binding was promoted for {key}")
        if item["authority_effect"] != "NONE":
            raise ValueError(f"lineage authority was promoted for {key}")
        unique_strings(item["observed_use_classes"], f"{key} observed_use_classes")
        if not all(isinstance(item[field], str) and item[field] for field in ("surface_kind", "branch", "current_state", "required_next_action")):
            raise ValueError(f"lineage explanation incomplete for {key}")
        observed[key] = (head, item["disposition"])
    if observed != EXPECTED_LINEAGES:
        raise ValueError(f"lineage identities or dispositions changed: {observed}")

    vocabulary = packet["disposition_vocabulary"]
    if not isinstance(vocabulary, list) or len(vocabulary) != len(EXPECTED_DISPOSITIONS):
        raise ValueError("disposition vocabulary closure changed")
    vocab_ids: set[str] = set()
    for item in vocabulary:
        if not isinstance(item, dict):
            raise ValueError("disposition vocabulary entry must be an object")
        exact_keys(item, {"id", "meaning"}, "disposition vocabulary entry")
        if not isinstance(item["meaning"], str) or not item["meaning"]:
            raise ValueError("disposition meaning missing")
        vocab_ids.add(item["id"])
    if vocab_ids != EXPECTED_DISPOSITIONS:
        raise ValueError("disposition vocabulary changed")

    edges = packet["graph_edges"]
    if not isinstance(edges, list) or len(edges) != len(EXPECTED_EDGE_IDS):
        raise ValueError("graph-edge closure changed")
    edge_ids: set[str] = set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("graph edge must be an object")
        exact_keys(edge, {"id", "source", "target", "status"}, "graph edge")
        if not all(isinstance(edge[field], str) and edge[field] for field in edge):
            raise ValueError("graph-edge fields must be non-empty strings")
        edge_ids.add(edge["id"])
    if edge_ids != EXPECTED_EDGE_IDS:
        raise ValueError("graph-edge identities changed")

    if set(unique_strings(packet["invariants"], "invariants")) != EXPECTED_INVARIANTS:
        raise ValueError("invariant closure changed")
    if set(unique_strings(packet["review_gates"], "review_gates")) != EXPECTED_GATES:
        raise ValueError("review-gate closure changed")
    routes = set(unique_strings(packet["controlled_routes"], "controlled_routes"))
    if routes != EXPECTED_ROUTES:
        raise ValueError("controlled-route closure changed")
    for route in routes:
        if not (root / route).is_file():
            raise ValueError(f"controlled route missing: {route}")

    planning = packet["planning_alignment"]
    if not isinstance(planning, dict) or set(planning) != EXPECTED_PLANNING:
        raise ValueError("planning alignment closure changed")
    if not all(isinstance(value, str) and value for value in planning.values()):
        raise ValueError("planning alignment explanations must be non-empty")

    mapping = packet["fysa_120"]
    if not isinstance(mapping, dict):
        raise ValueError("fysa_120 must be an object")
    exact_keys(mapping, {"categories", "subdivisions", "proposed_gap"}, "fysa_120")
    if set(unique_strings(mapping["categories"], "FYSA categories")) != REQUIRED_CATEGORIES:
        raise ValueError("FYSA category mapping changed")
    unique_strings(mapping["subdivisions"], "FYSA subdivisions")
    gap = mapping["proposed_gap"]
    if not isinstance(gap, dict):
        raise ValueError("proposed_gap must be an object")
    exact_keys(gap, {"id", "name", "status"}, "proposed_gap")
    if gap["id"] != "040-M" or gap["status"] != "NON_AUTHORITATIVE_PROPOSAL" or not gap["name"]:
        raise ValueError("proposed skill-tree gap changed")

    document = (root / "docs/runtime-fabric-lineage-disposition.md").read_text(encoding="utf-8")
    required_markers = {
        STATUS,
        "```mermaid",
        "### Prose equivalent",
        "PRESERVE_AND_REBIND",
        "PRESERVE_PENDING_ARCHITECTURE",
        "WITHDRAW_IF_SUPERSEDED",
        "NO_CANDIDATE_MAPPING",
        "040-M",
        "Authority effect: **none**",
    }
    missing = sorted(marker for marker in required_markers if marker not in document)
    if missing:
        raise ValueError(f"documentation markers missing: {missing}")
    for repository, _ in EXPECTED_LINEAGES:
        if repository not in document:
            raise ValueError(f"repository omitted from documentation: {repository}")

    return {
        "profile_id": packet["profile_id"],
        "status": packet["status"],
        "authority_effect": packet["authority_effect"],
        "source_head": source["head_sha"],
        "submitted_sha": submitted_sha,
        "lineage_count": len(lineages),
        "edge_count": len(edges),
        "review_gate_count": len(packet["review_gates"]),
        "result": "PASS",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--submitted-sha")
    args = parser.parse_args()
    try:
        packet = load_packet(args.packet)
        report = validate_packet(packet, args.packet, args.submitted_sha)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
