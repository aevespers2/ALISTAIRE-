#!/usr/bin/env python3
"""Fail-closed validation for the D2A common-contract ownership graph."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_GRAPH = Path("docs/d2a-common-contract-ownership-graph-v1.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
EXPECTED_REPOSITORIES = {
    "aevespers2/0", "aevespers2/1", "aevespers2/AionUi", "aevespers2/ALISTAIRE-",
    "aevespers2/Alistaire-agi", "aevespers2/Bridge", "aevespers2/datarepo-temporal-invariants",
    "aevespers2/grok-build-alistaire", "aevespers2/JusticeForMe", "aevespers2/Misc",
    "aevespers2/qsio-kernel", "aevespers2/QSO-DIGITALIS", "aevespers2/QSO-FABRIC",
    "aevespers2/qso-field.github.io", "aevespers2/QSO-GENOMES", "aevespers2/QSO-PAYMENTS",
    "aevespers2/QSO-SEEKER", "aevespers2/QSO-STUDIO", "aevespers2/QuantumStateObjects",
}
EXPECTED_CANDIDATES = {
    ("aevespers2/ALISTAIRE-", 1),
    ("aevespers2/QSO-FABRIC", 21),
    ("aevespers2/qso-field.github.io", 24),
    ("aevespers2/QuantumStateObjects", 12),
    ("aevespers2/1", 2),
}
EXPECTED_FAMILIES = {
    "constitutional_decision", "common_contract_profile",
    "proposal_capability_disposition_recovery", "host_and_source_observation",
    "temporal_assessment", "interpretation_and_policy_projection",
    "transport_artifact_and_delivery_receipt", "genome_identity_lineage_policy",
    "runtime_admission_lifecycle_evidence", "fabric_composition_experiment_evidence",
    "reference_conformance", "review_annotation_and_accessible_projection",
    "financial_intent_authorization_receipt", "engineering_task_change_bundle_execution_receipt",
    "publication_snapshot_and_claim_withdrawal", "compatibility_migration_and_retirement",
}
EXPECTED_ROUTES = {
    "docs/d2a-common-contract-ownership-graph.md",
    "docs/d2a-common-contract-ownership-graph-v1.json",
}
TOP_FIELDS = {
    "profile_id", "version", "status", "authority_effect", "source_generation",
    "observation_date", "repository_heads", "candidate_heads", "contract_families",
    "required_edges", "triple_overlap_witnesses", "material_obstructions",
    "prohibited_promotions", "controlled_routes", "propagation", "skill_tree_mapping",
    "proposed_subdivision_gap",
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


def load_graph(path: Path) -> dict[str, Any]:
    text = path.read_bytes().decode("utf-8", errors="strict")
    value = json.loads(text, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError("graph root must be an object")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    unknown = set(value) - expected
    if missing or unknown:
        raise ValueError(f"{label} fields mismatch: missing={sorted(missing)} unknown={sorted(unknown)}")


def nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def validate_graph(graph: dict[str, Any], graph_path: Path = DEFAULT_GRAPH, submitted_sha: str | None = None) -> dict[str, Any]:
    exact_keys(graph, TOP_FIELDS, "graph")
    if graph["profile_id"] != "ALISTAIRE-D2A-COMMON-CONTRACT-GRAPH-001":
        raise ValueError("unexpected profile_id")
    if graph["status"] != "REVIEW_OBSERVED_HEADS_UNRESOLVED_OWNERSHIP":
        raise ValueError("D2A must remain review-only with unresolved ownership")
    if graph["authority_effect"] != "none":
        raise ValueError("D2A must have no authority effect")
    if not DATE_RE.fullmatch(str(graph["observation_date"])):
        raise ValueError("observation_date must use YYYY-MM-DD")

    source = graph["source_generation"]
    if not isinstance(source, dict) or set(source) != {"repository", "pull_request", "head", "decision"}:
        raise ValueError("invalid source_generation")
    if source["repository"] != "aevespers2/ALISTAIRE-" or source["decision"] != "D2A":
        raise ValueError("unexpected D2A source identity")
    if type(source["pull_request"]) is not int or not SHA_RE.fullmatch(str(source["head"])):
        raise ValueError("D2A source must bind integer PR and exact SHA")

    repos = graph["repository_heads"]
    if not isinstance(repos, list) or len(repos) != 19:
        raise ValueError("repository_heads must contain exactly nineteen entries")
    seen: set[str] = set()
    for entry in repos:
        if not isinstance(entry, dict) or set(entry) != {"repository", "default_branch", "head", "candidate_role", "ownership_state"}:
            raise ValueError("invalid repository head entry")
        repo = nonempty_string(entry["repository"], "repository")
        if repo in seen:
            raise ValueError(f"duplicate repository: {repo}")
        seen.add(repo)
        if entry["default_branch"] != "main":
            raise ValueError(f"unexpected default branch for {repo}")
        if not SHA_RE.fullmatch(str(entry["head"])):
            raise ValueError(f"invalid head for {repo}")
        nonempty_string(entry["candidate_role"], f"candidate_role for {repo}")
        nonempty_string(entry["ownership_state"], f"ownership_state for {repo}")
    if seen != EXPECTED_REPOSITORIES:
        raise ValueError("repository inventory does not close over the owned portfolio")

    candidates = graph["candidate_heads"]
    if not isinstance(candidates, list) or len(candidates) != len(EXPECTED_CANDIDATES):
        raise ValueError("candidate_heads must contain the closed candidate set")
    observed_candidates: set[tuple[str, int]] = set()
    for item in candidates:
        if not isinstance(item, dict) or set(item) != {"repository", "pull_request", "head", "purpose"}:
            raise ValueError("invalid candidate head entry")
        if type(item["pull_request"]) is not int or not SHA_RE.fullmatch(str(item["head"])):
            raise ValueError("candidate heads require integer PR and exact SHA")
        observed_candidates.add((item["repository"], item["pull_request"]))
        nonempty_string(item["purpose"], "candidate purpose")
    if observed_candidates != EXPECTED_CANDIDATES:
        raise ValueError("candidate head set changed")

    families = graph["contract_families"]
    if not isinstance(families, list) or len(families) != len(EXPECTED_FAMILIES):
        raise ValueError("contract family inventory is incomplete")
    family_ids: list[str] = []
    for family in families:
        if not isinstance(family, dict) or set(family) != {"id", "candidate_owner", "producers", "consumers", "state", "conflict"}:
            raise ValueError("invalid contract family entry")
        family_id = nonempty_string(family["id"], "contract family id")
        family_ids.append(family_id)
        if not isinstance(family["producers"], list) or not isinstance(family["consumers"], list):
            raise ValueError(f"producers and consumers must be lists for {family_id}")
        nonempty_string(family["candidate_owner"], f"candidate owner for {family_id}")
        nonempty_string(family["state"], f"state for {family_id}")
        nonempty_string(family["conflict"], f"conflict for {family_id}")
    if set(family_ids) != EXPECTED_FAMILIES or len(family_ids) != len(set(family_ids)):
        raise ValueError("contract family identities changed or duplicated")

    edges = graph["required_edges"]
    if not isinstance(edges, list) or len(edges) < 10:
        raise ValueError("required edge inventory is too small")
    for edge in edges:
        if not isinstance(edge, dict) or set(edge) != {"from", "to", "contract", "state"}:
            raise ValueError("invalid required edge")
        for key in edge:
            nonempty_string(edge[key], f"edge {key}")

    overlaps = graph["triple_overlap_witnesses"]
    if not isinstance(overlaps, list) or len(overlaps) < 6:
        raise ValueError("triple-overlap inventory is incomplete")
    for item in overlaps:
        if not isinstance(item, dict) or set(item) != {"path", "obligation"}:
            raise ValueError("invalid triple-overlap entry")
        if not isinstance(item["path"], list) or len(item["path"]) != 3:
            raise ValueError("each triple-overlap path must contain exactly three nodes")
        if not all(isinstance(node, str) and node for node in item["path"]):
            raise ValueError("triple-overlap nodes must be non-empty strings")
        nonempty_string(item["obligation"], "triple-overlap obligation")

    obstructions = graph["material_obstructions"]
    if not isinstance(obstructions, list) or len(obstructions) < 8:
        raise ValueError("material obstruction inventory is incomplete")
    obstruction_ids: set[str] = set()
    for item in obstructions:
        if not isinstance(item, dict) or set(item) != {"id", "name", "state", "repositories"}:
            raise ValueError("invalid obstruction entry")
        obstruction_id = nonempty_string(item["id"], "obstruction id")
        if obstruction_id in obstruction_ids:
            raise ValueError("duplicate obstruction id")
        obstruction_ids.add(obstruction_id)
        if not isinstance(item["repositories"], list) or not item["repositories"]:
            raise ValueError(f"obstruction {obstruction_id} must bind repositories")

    prohibited = graph["prohibited_promotions"]
    if not isinstance(prohibited, list) or "passing_ci_to_semantic_compatibility" not in prohibited or "skill_mapping_to_competence_or_permission" not in prohibited:
        raise ValueError("prohibited promotions are incomplete")

    if set(graph["controlled_routes"]) != EXPECTED_ROUTES:
        raise ValueError("controlled route set changed")
    propagation = graph["propagation"]
    if not isinstance(propagation, dict) or set(propagation) != {"rebind_marker", "withdrawal_marker", "completion_rule"}:
        raise ValueError("invalid propagation object")
    if propagation["rebind_marker"] != "D2A_REBIND_REQUIRED" or propagation["withdrawal_marker"] != "D2A_GRAPH_WITHDRAWN":
        raise ValueError("D2A propagation markers changed")
    for route in sorted(EXPECTED_ROUTES):
        path = Path(route)
        if not path.is_file():
            raise ValueError(f"controlled route missing: {route}")
        text = path.read_text(encoding="utf-8")
        if "D2A_REBIND_REQUIRED" not in text or "D2A_GRAPH_WITHDRAWN" not in text:
            raise ValueError(f"controlled route lacks D2A propagation markers: {route}")

    gap = graph["proposed_subdivision_gap"]
    if not isinstance(gap, dict) or set(gap) != {"id", "name", "skills", "authority_effect"}:
        raise ValueError("invalid proposed subdivision gap")
    if gap["id"] != "013-G" or gap["authority_effect"] != "none":
        raise ValueError("D2A skill gap must remain non-authoritative")

    if submitted_sha is not None and not SHA_RE.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be exact")

    return {
        "profile_id": graph["profile_id"],
        "status": graph["status"],
        "repository_count": len(repos),
        "candidate_head_count": len(candidates),
        "contract_family_count": len(families),
        "edge_count": len(edges),
        "triple_overlap_count": len(overlaps),
        "obstruction_count": len(obstructions),
        "graph_sha256": hashlib.sha256(graph_path.read_bytes()).hexdigest(),
        "submitted_sha": submitted_sha,
        "disposition": "D2A_COMMON_CONTRACT_GRAPH_VALIDATED_NON_AUTHORIZING",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default=str(DEFAULT_GRAPH))
    parser.add_argument("--submitted-sha")
    args = parser.parse_args()
    try:
        path = Path(args.graph)
        report = validate_graph(load_graph(path), path, args.submitted_sha)
        print(json.dumps(report, sort_keys=True, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"disposition": "D2A_GRAPH_FAILED_CLOSED", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
