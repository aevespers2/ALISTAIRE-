#!/usr/bin/env python3
"""Validate the documentation-only A.L.I.S.T.A.I.R.E. capability roadmap."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = Path("docs/capability-roadmap-v1.json")
GUIDE_PATH = Path("docs/capability-roadmap.md")
EXPECTED_EXPANSION = "Adaptive Learning & Intelligence System for Trustworthy Autonomous Inference, Reasoning, and Evolution"
EXPECTED_STATUS = "DOCUMENTED_CAPABILITY_ROADMAP_UNACCEPTED"
EXPECTED_NAME_STATUS = "NAME_EXPANSION_DOCUMENTED_CANONICAL_REPOSITORY_UNSELECTED"
EXPECTED_FEATURE_COUNT = 37
EXPECTED_FAMILIES = [f"F{i}" for i in range(1, 7)]
EXPECTED_STAGES = [f"R{i}" for i in range(0, 6)]
EXPECTED_REFINEMENTS = {"012-R", "013-L", "041-F"}
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


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def string_list(value: Any, field: str) -> list[str]:
    require(isinstance(value, list) and value, f"{field} must be a non-empty list")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{field} must contain strings")
    require(len(value) == len(set(value)), f"{field} must not contain duplicates")
    return value


def load_profile(root: Path) -> dict[str, Any]:
    raw = (root / PROFILE_PATH).read_bytes().decode("utf-8", errors="strict")
    value = json.loads(raw, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    require(isinstance(value, dict), "profile root must be an object")
    return value


def validate_repository(root: Path = ROOT) -> dict[str, Any]:
    for relative in (PROFILE_PATH, GUIDE_PATH, Path("docs/name-and-identity.md"), Path("README.md"), Path("docs/index.md"), Path("mkdocs.yml"), Path("changelog.md")):
        path = root / relative
        require(path.is_file() and path.stat().st_size > 0, f"missing or empty file: {relative}")

    profile = load_profile(root)
    require(profile.get("profile_id") == "ALISTAIRE-CAPABILITY-ROADMAP-001", "unexpected profile_id")
    require(profile.get("version") == "1.0.0", "unexpected version")
    require(profile.get("status") == EXPECTED_STATUS, "roadmap must remain unaccepted")
    require(profile.get("authority_effect") == "none", "authority_effect must remain none")

    source = profile.get("name_source")
    require(isinstance(source, dict), "name_source must be an object")
    require(source.get("path") == "docs/name-and-identity.md", "unexpected name source")
    require(source.get("expansion") == EXPECTED_EXPANSION, "name expansion drift")
    require(source.get("status") == EXPECTED_NAME_STATUS, "name status drift")

    stages = profile.get("roadmap_stages")
    require(isinstance(stages, list), "roadmap_stages must be a list")
    require([item.get("id") for item in stages if isinstance(item, dict)] == EXPECTED_STAGES, "stages must be R0 through R5")
    require(stages[-1].get("status") == "prohibited_without_separate_approval", "R5 must remain separately prohibited")
    for stage in stages:
        require(isinstance(stage, dict), "stage must be an object")
        string_list(stage.get("requires"), f"{stage.get('id')}.requires")

    families = profile.get("capability_families")
    require(isinstance(families, list), "capability_families must be a list")
    require([item.get("id") for item in families if isinstance(item, dict)] == EXPECTED_FAMILIES, "families must be F1 through F6")
    feature_ids: list[str] = []
    feature_names: list[str] = []
    for family in families:
        require(isinstance(family, dict), "family must be an object")
        features = family.get("features")
        require(isinstance(features, list) and features, f"{family.get('id')} must contain features")
        for feature in features:
            require(isinstance(feature, dict), "feature must be an object")
            feature_id = feature.get("id")
            require(isinstance(feature_id, str) and FEATURE_ID.fullmatch(feature_id) is not None, f"invalid feature id: {feature_id}")
            require(feature_id.startswith(family["id"] + "-"), f"feature {feature_id} is in the wrong family")
            name = feature.get("name")
            require(isinstance(name, str) and name.strip(), f"feature {feature_id} lacks a name")
            string_list(feature.get("owner_candidates"), f"{feature_id}.owner_candidates")
            string_list(feature.get("blocked_by"), f"{feature_id}.blocked_by")
            feature_ids.append(feature_id)
            feature_names.append(name)
    require(len(feature_ids) == EXPECTED_FEATURE_COUNT, f"expected {EXPECTED_FEATURE_COUNT} features, found {len(feature_ids)}")
    require(len(feature_ids) == len(set(feature_ids)), "feature ids must be unique")
    require(len(feature_names) == len(set(feature_names)), "feature names must be unique")

    obstructions = string_list(profile.get("material_obstructions"), "material_obstructions")
    require(len(obstructions) >= 7, "seven material obstructions are required")

    skills = profile.get("fysa_120")
    require(isinstance(skills, dict), "fysa_120 must be an object")
    refinements = skills.get("proposed_refinements")
    require(isinstance(refinements, list), "proposed_refinements must be a list")
    refinement_ids = {item.get("id") for item in refinements if isinstance(item, dict)}
    require(refinement_ids == EXPECTED_REFINEMENTS, "proposed refinement set changed")
    for item in refinements:
        require(isinstance(item, dict) and item.get("status") == "PROPOSED_NON_AUTHORITATIVE", "refinements must remain non-authoritative")

    promotions = set(string_list(profile.get("prohibited_promotions"), "prohibited_promotions"))
    require("feature listing to implementation" in promotions, "feature-to-implementation promotion guard missing")
    require("repository assignment to ownership" in promotions, "repository-to-owner promotion guard missing")
    require("autonomy language to unrestricted permission" in promotions, "autonomy authority guard missing")

    rollback = profile.get("rollback")
    require(isinstance(rollback, dict), "rollback must be an object")
    for key in ("restore_last_validated_documentation_generation", "preserve_superseded_generation", "propagate_correction_or_withdrawal", "revalidate_controlled_routes"):
        require(rollback.get(key) is True, f"rollback.{key} must remain true")
    require(rollback.get("destructive_history_rewrite") is False, "destructive history rewrite must remain false")

    required_text = {
        GUIDE_PATH: [EXPECTED_EXPANSION, EXPECTED_STATUS, "### Prose equivalent", "012-R", "013-L", "041-F"],
        Path("docs/name-and-identity.md"): [EXPECTED_EXPANSION, EXPECTED_NAME_STATUS],
        Path("README.md"): ["docs/capability-roadmap.md", EXPECTED_STATUS],
        Path("docs/index.md"): ["capability-roadmap.md", EXPECTED_STATUS],
        Path("mkdocs.yml"): ["capability-roadmap.md", "capability-roadmap-v1.json", EXPECTED_STATUS],
        Path("changelog.md"): [EXPECTED_STATUS, "012-R", "013-L", "041-F"],
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
