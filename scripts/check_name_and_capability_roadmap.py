#!/usr/bin/env python3
"""Validate the documentation-only A.L.I.S.T.A.I.R.E. name and capability roadmap.

The validator checks internal consistency, closed identifiers, cross-document naming,
feature counts, authority boundaries, FYSA-120 mapping, and rollback posture. It does
not approve the name, capabilities, owners, contracts, publication, release, or runtime.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = Path("docs/name-and-capability-roadmap-v1.json")
GUIDE_PATH = Path("docs/name-and-capability-roadmap.md")

EXPECTED_EXPANSION = (
    "Adaptive Learning and Intelligence System for Trustworthy Autonomous "
    "Inference, Reasoning, and Evolution"
)
EXPECTED_STATUS = "DOCUMENTED_NAME_EXPANSION_AND_CAPABILITY_ROADMAP_UNACCEPTED"
EXPECTED_LETTERS = list("ALISTAIRE")
EXPECTED_FAMILY_IDS = [f"F{i}" for i in range(1, 7)]
EXPECTED_STAGE_IDS = [f"R{i}" for i in range(0, 6)]
EXPECTED_FEATURE_COUNT = 37
EXPECTED_REFINEMENTS = {"012-Q", "013-L", "041-F"}
REQUIRED_CATEGORIES = {
    "CAT-011",
    "CAT-012",
    "CAT-013",
    "CAT-017",
    "CAT-018",
    "CAT-019",
    "CAT-030",
    "CAT-031",
    "CAT-032",
    "CAT-033",
    "CAT-040",
    "CAT-041",
    "CAT-054",
    "CAT-070",
}
REQUIRED_PROMOTIONS = {
    "documentation to canonical acceptance",
    "feature listing to implementation",
    "repository assignment to ownership",
    "workflow success to trust or authority",
    "interface existence to compatibility",
    "simulation to production readiness",
    "autonomy language to unrestricted permission",
}
FEATURE_ID = re.compile(r"^F[1-6]-0[1-9]$")


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value is prohibited: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_profile(root: Path) -> dict[str, Any]:
    path = root / PROFILE_PATH
    raw = path.read_bytes().decode("utf-8", errors="strict")
    value = json.loads(
        raw,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("roadmap profile root must be an object")
    return value


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def require_string_list(value: Any, field: str) -> list[str]:
    require(isinstance(value, list) and value, f"{field} must be a non-empty list")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{field} must contain non-empty strings")
    require(len(value) == len(set(value)), f"{field} must not contain duplicates")
    return value


def validate_repository(root: Path = ROOT) -> dict[str, Any]:
    required_files = [
        root / PROFILE_PATH,
        root / GUIDE_PATH,
        root / "README.md",
        root / "docs/index.md",
        root / "mkdocs.yml",
        root / "changelog.md",
    ]
    for path in required_files:
        require(path.is_file() and path.stat().st_size > 0, f"missing or empty file: {path.relative_to(root)}")

    profile = load_profile(root)
    require(profile.get("profile_id") == "ALISTAIRE-NAME-CAPABILITY-ROADMAP-001", "unexpected profile_id")
    require(profile.get("version") == "1.0.0", "unexpected profile version")
    require(profile.get("status") == EXPECTED_STATUS, "roadmap status must remain unaccepted")
    require(profile.get("authority_effect") == "none", "authority_effect must remain none")
    require(profile.get("canonical_decision_dependency") == "D1", "canonical naming must remain dependent on D1")

    name = profile.get("name")
    require(isinstance(name, dict), "name must be an object")
    require(name.get("display") == "A.L.I.S.T.A.I.R.E.", "unexpected display name")
    require(name.get("expansion") == EXPECTED_EXPANSION, "unexpected acronym expansion")
    require(name.get("canonical_status") == "proposed_pending_D1", "name must remain proposed pending D1")
    terms = name.get("terms")
    require(isinstance(terms, list) and len(terms) == len(EXPECTED_LETTERS), "name terms must contain nine entries")
    require([term.get("letter") for term in terms if isinstance(term, dict)] == EXPECTED_LETTERS, "name term letters must spell ALISTAIRE")
    for index, term in enumerate(terms):
        require(isinstance(term, dict), f"name term {index} must be an object")
        require(isinstance(term.get("term"), str) and term["term"].strip(), f"name term {index} lacks a term")
        require(isinstance(term.get("boundary"), str) and term["boundary"].strip(), f"name term {index} lacks a boundary")

    stages = profile.get("roadmap_stages")
    require(isinstance(stages, list), "roadmap_stages must be a list")
    require([stage.get("id") for stage in stages if isinstance(stage, dict)] == EXPECTED_STAGE_IDS, "roadmap stages must be R0 through R5 in order")
    for stage in stages:
        require(isinstance(stage, dict), "roadmap stage must be an object")
        require(isinstance(stage.get("name"), str) and stage["name"].strip(), f"{stage.get('id')} lacks a name")
        require(isinstance(stage.get("status"), str) and stage["status"].strip(), f"{stage.get('id')} lacks a status")
        require_string_list(stage.get("requires"), f"{stage.get('id')}.requires")
    require(stages[-1].get("status") == "prohibited_without_separate_approval", "R5 must remain separately prohibited")

    families = profile.get("capability_families")
    require(isinstance(families, list), "capability_families must be a list")
    require([family.get("id") for family in families if isinstance(family, dict)] == EXPECTED_FAMILY_IDS, "capability families must be F1 through F6 in order")

    feature_ids: list[str] = []
    feature_names: list[str] = []
    for family in families:
        require(isinstance(family, dict), "capability family must be an object")
        require(isinstance(family.get("name"), str) and family["name"].strip(), f"{family.get('id')} lacks a name")
        features = family.get("features")
        require(isinstance(features, list) and features, f"{family.get('id')} must contain features")
        for feature in features:
            require(isinstance(feature, dict), "feature must be an object")
            feature_id = feature.get("id")
            feature_name = feature.get("name")
            require(isinstance(feature_id, str) and FEATURE_ID.fullmatch(feature_id) is not None, f"invalid feature id: {feature_id}")
            require(feature_id.startswith(family["id"] + "-"), f"feature {feature_id} is in the wrong family")
            require(isinstance(feature_name, str) and feature_name.strip(), f"feature {feature_id} lacks a name")
            require_string_list(feature.get("owner_candidates"), f"{feature_id}.owner_candidates")
            require_string_list(feature.get("blocked_by"), f"{feature_id}.blocked_by")
            feature_ids.append(feature_id)
            feature_names.append(feature_name)

    require(len(feature_ids) == EXPECTED_FEATURE_COUNT, f"expected {EXPECTED_FEATURE_COUNT} features, found {len(feature_ids)}")
    require(len(feature_ids) == len(set(feature_ids)), "feature ids must be unique")
    require(len(feature_names) == len(set(feature_names)), "feature names must be unique")

    obstructions = require_string_list(profile.get("material_obstructions"), "material_obstructions")
    require(len(obstructions) >= 7, "at least seven material obstructions must remain explicit")

    skill_map = profile.get("fysa_120")
    require(isinstance(skill_map, dict), "fysa_120 must be an object")
    categories = set(require_string_list(skill_map.get("applied_categories"), "fysa_120.applied_categories"))
    require(REQUIRED_CATEGORIES <= categories, "required FYSA-120 categories are missing")
    refinements = skill_map.get("proposed_refinements")
    require(isinstance(refinements, list), "proposed_refinements must be a list")
    refinement_ids = {item.get("id") for item in refinements if isinstance(item, dict)}
    require(refinement_ids == EXPECTED_REFINEMENTS, "unexpected proposed refinement set")
    for item in refinements:
        require(isinstance(item, dict), "proposed refinement must be an object")
        require(item.get("status") == "PROPOSED_NON_AUTHORITATIVE", f"{item.get('id')} must remain non-authoritative")

    promotions = set(require_string_list(profile.get("prohibited_promotions"), "prohibited_promotions"))
    require(promotions == REQUIRED_PROMOTIONS, "prohibited authority promotions changed")

    rollback = profile.get("rollback")
    require(isinstance(rollback, dict), "rollback must be an object")
    for key in (
        "restore_last_validated_documentation_generation",
        "preserve_superseded_generation",
        "propagate_correction_or_withdrawal",
        "revalidate_controlled_routes",
    ):
        require(rollback.get(key) is True, f"rollback.{key} must remain true")
    require(rollback.get("destructive_history_rewrite") is False, "destructive history rewrite must remain false")

    required_text = {
        GUIDE_PATH: [EXPECTED_EXPANSION, EXPECTED_STATUS, "### Prose equivalent", "Authority effect: `NONE`"],
        Path("README.md"): [EXPECTED_EXPANSION, "docs/name-and-capability-roadmap.md", EXPECTED_STATUS],
        Path("docs/index.md"): [EXPECTED_EXPANSION, "name-and-capability-roadmap.md", EXPECTED_STATUS],
        Path("mkdocs.yml"): ["name-and-capability-roadmap.md", "name-and-capability-roadmap-v1.json", EXPECTED_STATUS],
        Path("changelog.md"): [EXPECTED_EXPANSION, EXPECTED_STATUS, "012-Q", "013-L", "041-F"],
    }
    for relative, phrases in required_text.items():
        text = (root / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            require(phrase in text, f"{relative} is missing required phrase: {phrase}")

    return {
        "result": "PASS",
        "profile_id": profile["profile_id"],
        "status": profile["status"],
        "authority_effect": profile["authority_effect"],
        "family_count": len(families),
        "feature_count": len(feature_ids),
        "stage_count": len(stages),
        "obstruction_count": len(obstructions),
        "skill_category_count": len(categories),
        "proposed_refinements": sorted(refinement_ids),
    }


def main() -> int:
    try:
        report = validate_repository(ROOT)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
