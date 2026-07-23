#!/usr/bin/env python3
"""Fail-closed validation for the ALISTAIRE decision source-generation rebind."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_REBIND = Path("docs/decision-source-generation-rebind-v1.json")
DEFAULT_D2A = Path("docs/d2a-common-contract-ownership-graph-v1.json")
DEFAULT_D3 = Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")

TOP_FIELDS = {
    "profile_id",
    "version",
    "status",
    "authority_effect",
    "repository",
    "pull_request",
    "rebind_parent",
    "ancestry_rule",
    "historical_sources",
    "validated_files",
    "invalidates_on",
    "prohibited_promotions",
    "rollback",
    "skill_tree_mapping",
    "proposed_subdivision_gap",
}
HISTORICAL_FIELDS = {
    "d2a_packet_source_head",
    "d2a_alistaire_candidate_head",
    "d3_packet_source_head",
}
EXPECTED_VALIDATED_FILES = {
    str(DEFAULT_D2A),
    str(DEFAULT_D3),
}
EXPECTED_INVALIDATIONS = {
    "rebind_parent_change",
    "embedded_packet_source_change",
    "d2a_alistaire_candidate_change",
    "packet_identity_or_scope_change",
    "ancestry_rule_change",
    "correction_withdrawal_or_rollback_rule_change",
}
EXPECTED_PROHIBITIONS = {
    "historical_source_to_current_portfolio_observation",
    "passing_ci_to_decision_acceptance",
    "mergeability_to_canonical_selection",
    "canonical_bytes_or_digest_to_authority",
    "documentation_to_publication_or_release_authority",
    "skill_mapping_to_competence_or_permission",
}
EXPECTED_ROLLBACK = {
    "preserve_failed_evidence",
    "restore_last_reviewed_candidate_without_force_update",
    "invalidate_derived_currentness_claims",
    "rerun_d2a_d3_documentation_and_rebind_validation",
}
EXPECTED_SKILL_CATEGORIES = {
    "CAT-012",
    "CAT-013",
    "CAT-017",
    "CAT-031",
    "CAT-040",
    "CAT-052",
    "CAT-059",
    "CAT-070",
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


def load_json(path: Path) -> dict[str, Any]:
    text = path.read_bytes().decode("utf-8", errors="strict")
    value = json.loads(
        text,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} root must be an object")
    return value


def exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    missing = expected - set(value)
    unknown = set(value) - expected
    if missing or unknown:
        raise ValueError(
            f"{label} fields mismatch: missing={sorted(missing)} unknown={sorted(unknown)}"
        )


def exact_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA_RE.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase 40-character Git SHA")
    return value


def find_d2a_candidate_head(d2a: dict[str, Any]) -> str:
    candidates = d2a.get("candidate_heads")
    if not isinstance(candidates, list):
        raise ValueError("D2A candidate_heads must be a list")
    matches = [
        item
        for item in candidates
        if isinstance(item, dict)
        and item.get("repository") == "aevespers2/ALISTAIRE-"
        and item.get("pull_request") == 1
    ]
    if len(matches) != 1:
        raise ValueError("D2A must contain exactly one ALISTAIRE PR #1 candidate")
    return exact_sha(matches[0].get("head"), "D2A ALISTAIRE candidate head")


def validate_rebind(
    rebind: dict[str, Any],
    d2a: dict[str, Any],
    d3: dict[str, Any],
    *,
    rebind_path: Path = DEFAULT_REBIND,
    submitted_sha: str,
    first_parent: str,
) -> dict[str, Any]:
    exact_keys(rebind, TOP_FIELDS, "rebind")

    if rebind["profile_id"] != "ALISTAIRE-DECISION-SOURCE-GENERATION-REBIND-001":
        raise ValueError("unexpected rebind profile_id")
    if rebind["status"] != "REBOUND_TO_PARENT_NON_AUTHORIZING":
        raise ValueError("rebind status must remain non-authorizing")
    if rebind["authority_effect"] != "none":
        raise ValueError("rebind must have no authority effect")
    if rebind["repository"] != "aevespers2/ALISTAIRE-":
        raise ValueError("unexpected repository")
    if type(rebind["pull_request"]) is not int or rebind["pull_request"] != 1:
        raise ValueError("rebind must remain scoped to ALISTAIRE PR #1")
    if rebind["ancestry_rule"] != "submitted commit first parent must equal rebind_parent":
        raise ValueError("ancestry rule changed")

    submitted_sha = exact_sha(submitted_sha, "submitted SHA")
    first_parent = exact_sha(first_parent, "first parent")
    rebind_parent = exact_sha(rebind["rebind_parent"], "rebind parent")
    if submitted_sha == first_parent:
        raise ValueError("submitted SHA must be a descendant, not the rebind parent itself")
    if first_parent != rebind_parent:
        raise ValueError("submitted commit first parent does not equal rebind_parent")

    if d2a.get("profile_id") != "ALISTAIRE-D2A-COMMON-CONTRACT-GRAPH-001":
        raise ValueError("unexpected D2A profile")
    if d3.get("profile_id") != "ALISTAIRE-D3-CANONICAL-BYTES-IDENTITY-001":
        raise ValueError("unexpected D3 profile")

    d2a_source = d2a.get("source_generation")
    d3_source = d3.get("source_generation")
    if not isinstance(d2a_source, dict) or not isinstance(d3_source, dict):
        raise ValueError("decision packets must contain source_generation objects")

    historical = rebind["historical_sources"]
    if not isinstance(historical, dict):
        raise ValueError("historical_sources must be an object")
    exact_keys(historical, HISTORICAL_FIELDS, "historical_sources")

    actual_d2a_source = exact_sha(d2a_source.get("head"), "D2A packet source head")
    actual_d3_source = exact_sha(d3_source.get("head"), "D3 packet source head")
    actual_d2a_candidate = find_d2a_candidate_head(d2a)

    if exact_sha(historical["d2a_packet_source_head"], "recorded D2A source") != actual_d2a_source:
        raise ValueError("recorded D2A source does not match the packet")
    if exact_sha(historical["d3_packet_source_head"], "recorded D3 source") != actual_d3_source:
        raise ValueError("recorded D3 source does not match the packet")
    if exact_sha(
        historical["d2a_alistaire_candidate_head"],
        "recorded D2A ALISTAIRE candidate",
    ) != actual_d2a_candidate:
        raise ValueError("recorded D2A ALISTAIRE candidate does not match the graph")

    if set(rebind["validated_files"]) != EXPECTED_VALIDATED_FILES:
        raise ValueError("validated file set changed")
    if set(rebind["invalidates_on"]) != EXPECTED_INVALIDATIONS:
        raise ValueError("rebind invalidation closure is incomplete")
    if set(rebind["prohibited_promotions"]) != EXPECTED_PROHIBITIONS:
        raise ValueError("prohibited promotions are incomplete")

    rollback = rebind["rollback"]
    if not isinstance(rollback, dict) or set(rollback) != {"mode", "requirements"}:
        raise ValueError("invalid rollback object")
    if rollback["mode"] != "non_destructive_documentation_only":
        raise ValueError("rollback mode must remain non-destructive and documentation-only")
    if set(rollback["requirements"]) != EXPECTED_ROLLBACK:
        raise ValueError("rollback requirements are incomplete")

    mapping = rebind["skill_tree_mapping"]
    if not isinstance(mapping, list):
        raise ValueError("skill_tree_mapping must be a list")
    categories = {item.get("category") for item in mapping if isinstance(item, dict)}
    if categories != EXPECTED_SKILL_CATEGORIES:
        raise ValueError("skill-tree category mapping changed or is incomplete")
    for item in mapping:
        if not isinstance(item, dict) or set(item) != {"category", "subdivisions"}:
            raise ValueError("invalid skill-tree mapping entry")
        if not isinstance(item["subdivisions"], list) or not item["subdivisions"]:
            raise ValueError("skill-tree mapping entries require subdivisions")

    gap = rebind["proposed_subdivision_gap"]
    if not isinstance(gap, dict) or set(gap) != {
        "id",
        "name",
        "skills",
        "authority_effect",
    }:
        raise ValueError("invalid proposed subdivision gap")
    if gap["id"] != "017-F" or gap["authority_effect"] != "none":
        raise ValueError("skill-tree gap must remain 017-F and non-authorizing")
    if not isinstance(gap["skills"], list) or len(gap["skills"]) < 5:
        raise ValueError("skill-tree gap must record bounded missing capabilities")

    return {
        "profile_id": rebind["profile_id"],
        "status": rebind["status"],
        "submitted_sha": submitted_sha,
        "first_parent": first_parent,
        "rebind_parent": rebind_parent,
        "historical_source_count": len(historical),
        "rebind_sha256": hashlib.sha256(rebind_path.read_bytes()).hexdigest(),
        "disposition": "DECISION_SOURCE_GENERATION_REBOUND_NON_AUTHORIZING",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rebind", default=str(DEFAULT_REBIND))
    parser.add_argument("--d2a", default=str(DEFAULT_D2A))
    parser.add_argument("--d3", default=str(DEFAULT_D3))
    parser.add_argument("--submitted-sha", required=True)
    parser.add_argument("--first-parent", required=True)
    args = parser.parse_args()

    try:
        rebind_path = Path(args.rebind)
        report = validate_rebind(
            load_json(rebind_path),
            load_json(Path(args.d2a)),
            load_json(Path(args.d3)),
            rebind_path=rebind_path,
            submitted_sha=args.submitted_sha,
            first_parent=args.first_parent,
        )
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(
            json.dumps(
                {
                    "disposition": "DECISION_SOURCE_GENERATION_REBIND_FAILED_CLOSED",
                    "error": str(exc),
                },
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
