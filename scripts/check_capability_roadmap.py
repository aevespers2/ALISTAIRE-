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
EXPECTED_VERSION = "1.1.0"
EXPECTED_FEATURE_COUNT = 40
EXPECTED_FAMILIES = [f"F{i}" for i in range(1, 7)]
EXPECTED_STAGES = [f"R{i}" for i in range(0, 6)]
EXPECTED_REFINEMENTS = {"012-R", "012-S", "013-L", "032-J", "040-Q", "041-F", "054-L"}
EXPECTED_RECONCILED_FEATURES = {
    "Repository Role Classifier",
    "Portfolio Status Dashboard",
    "Systemic Obstruction Register",
}
EXPECTED_SOURCE_HEAD = "6c7595e81914ab680acb25088193d495db9f28f7"
EXPECTED_SOURCE_DISPOSITION = "RECONCILED_INTO_EXISTING_ROADMAP_PRESERVE_SOURCE_BRANCH"
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
    require(profile.get("version") == EXPECTED_VERSION, "unexpected version")
    require(profile.get("status") == EXPECTED_STATUS, "roadmap must remain unaccepted")
    require(profile.get("authority_effect") == "none", "authority_effect must remain none")

    source = profile.get("name_source")
    require(isinstance(source, dict), "name_source must be an object")
    require(source.get("path") == "docs/name-and-identity.md", "unexpected name source")
    require(source.get("expansion") == EXPECTED_EXPANSION, "name expansion drift")
    require(source.get("status") == EXPECTED_NAME_STATUS, "name status drift")

    reconciliation = profile.get("source_reconciliation")
    require(isinstance(reconciliation, dict), "source_reconciliation must be an object")
    require(reconciliation.get("superseded_candidate_pr") == 22, "unexpected superseded candidate PR")
    require(reconciliation.get("superseded_head") == EXPECTED_SOURCE_HEAD, "superseded source head substitution")
    require(reconciliation.get("disposition") == EXPECTED_SOURCE_DISPOSITION, "unexpected source reconciliation disposition")
    require(reconciliation.get("feature_count_before") == 37, "source feature count must remain 37")
    require(reconciliation.get("feature_count_after") == EXPECTED_FEATURE_COUNT, "reconciled feature count must remain 40")
    added_features = set(string_list(reconciliation.get("added_features"), "source_reconciliation.added_features"))
    require(added_features == EXPECTED_RECONCILED_FEATURES, "reconciled feature delta changed")
    require(reconciliation.get("identifier_policy") == "preserve_family_scoped_ids", "family-scoped identifier policy changed")
    require(reconciliation.get("duplicate_registry_policy") == "do_not_create_parallel_authority_source", "parallel authority registry is prohibited")

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
    require(EXPECTED_RECONCILED_FEATURES <= set(feature_names), "one or more reconciled features are missing")

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
    require("012-Q" not in refinement_ids, "012-Q is reserved for public naming and identity guidance")

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
        GUIDE_PATH: [
            EXPECTED_EXPANSION,
            EXPECTED_STATUS,
            "### Prose equivalent",
            EXPECTED_SOURCE_HEAD,
            EXPECTED_SOURCE_DISPOSITION,
            "Repository Role Classifier",
            "Portfolio Status Dashboard",
            "Systemic Obstruction Register",
            "012-R",
            "012-S",
            "013-L",
            "032-J",
            "040-Q",
            "041-F",
            "054-L",
        ],
        Path("docs/name-and-identity.md"): [EXPECTED_EXPANSION, EXPECTED_NAME_STATUS],
        Path("README.md"): ["docs/capability-roadmap.md", EXPECTED_STATUS],
        Path("docs/index.md"): ["capability-roadmap.md", EXPECTED_STATUS],
        Path("mkdocs.yml"): ["capability-roadmap.md", "capability-roadmap-v1.json", EXPECTED_STATUS],
        Path("changelog.md"): [EXPECTED_STATUS, EXPECTED_SOURCE_HEAD, EXPECTED_SOURCE_DISPOSITION, "012-S", "032-J", "040-Q", "054-L"],
    }
    for relative, phrases in required_text.items():
        text = (root / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            require(phrase in text, f"{relative} is missing required phrase: {phrase}")

    return {
        "result": "PASS",
        "profile_id": profile["profile_id"],
        "version": profile["version"],
        "status": profile["status"],
        "authority_effect": profile["authority_effect"],
        "source_disposition": reconciliation["disposition"],
        "source_head": reconciliation["superseded_head"],
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
