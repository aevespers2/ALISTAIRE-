#!/usr/bin/env python3
"""Validate non-authorizing capability and contributor lifecycle coherence."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = Path("docs/capability-lifecycle-coherence-v1.json")
GUIDE_PATH = Path("docs/capability-lifecycle-coherence.md")
EXPECTED_PROFILE_ID = "ALISTAIRE-CAPABILITY-LIFECYCLE-COHERENCE-001"
EXPECTED_VERSION = "1.0.0"
EXPECTED_SOURCE_HEAD = "2953ef6ba8ee86eafdddcf56222c91cbb296bcb7"
EXPECTED_STATUS = "CAPABILITY_AND_CONTRIBUTOR_ROUTES_SYNCHRONIZED_BINDINGS_UNACCEPTED"
EXPECTED_ROADMAP_STATUS = "DOCUMENTED_CAPABILITY_ROADMAP_UNACCEPTED"
EXPECTED_LINEAGE_STATUS = "RECONCILED_INTO_EXISTING_ROADMAP_PRESERVE_SOURCE_BRANCH"
EXPECTED_CONTRIBUTOR_STATUS = "PORTFOLIO_CONTRIBUTOR_PATHS_DOCUMENTED_OWNERSHIP_UNASSIGNED"
EXPECTED_NAME_STATUS = "NAME_EXPANSION_DOCUMENTED_CANONICAL_REPOSITORY_UNSELECTED"
EXPECTED_REFINEMENT = "012-U"
LIFECYCLE_ROUTES = (Path("taskchain.md"), Path("punchlist.md"), Path("release.md"), Path("changelog.md"))
CONTROLLED_ROUTES = {
    "README.md",
    "docs/index.md",
    "docs/capability-roadmap.md",
    "docs/capability-roadmap-v1.json",
    "docs/portfolio-contributor-paths.md",
    "docs/portfolio-contributor-paths-v1.json",
    "taskchain.md",
    "punchlist.md",
    "release.md",
    "changelog.md",
    "mkdocs.yml",
}


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
    profile = json.loads(raw, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    require(isinstance(profile, dict), "profile root must be an object")
    return profile


def require_phrases(root: Path, relative: Path, phrases: list[str]) -> None:
    text = (root / relative).read_text(encoding="utf-8")
    for phrase in phrases:
        require(phrase in text, f"{relative} is missing required phrase: {phrase}")


def validate_repository(root: Path = ROOT) -> dict[str, Any]:
    required_files = {
        PROFILE_PATH,
        GUIDE_PATH,
        Path("docs/capability-roadmap.md"),
        Path("docs/capability-roadmap-v1.json"),
        Path("docs/portfolio-contributor-paths.md"),
        Path("docs/portfolio-contributor-paths-v1.json"),
        Path("README.md"),
        Path("docs/index.md"),
        Path("mkdocs.yml"),
        *LIFECYCLE_ROUTES,
    }
    for relative in required_files:
        path = root / relative
        require(path.is_file() and path.stat().st_size > 0, f"missing or empty file: {relative}")

    profile = load_profile(root)
    require(profile.get("profile_id") == EXPECTED_PROFILE_ID, "unexpected profile_id")
    require(profile.get("version") == EXPECTED_VERSION, "unexpected version")
    require(profile.get("status") == EXPECTED_STATUS, "lifecycle coherence status drift")
    require(profile.get("authority_effect") == "none", "authority_effect must remain none")

    source = profile.get("source_generation")
    require(isinstance(source, dict), "source_generation must be an object")
    require(source.get("repository") == "aevespers2/ALISTAIRE-", "source repository drift")
    require(source.get("branch") == "docs/consolidation-charter-20260720", "source branch drift")
    require(source.get("head") == EXPECTED_SOURCE_HEAD, "source head substitution")
    require(source.get("role") == "historical_input_not_descendant_identity", "source role must reject self-reference")

    statuses = profile.get("controlled_statuses")
    require(isinstance(statuses, dict), "controlled_statuses must be an object")
    expected_statuses = {
        "name": EXPECTED_NAME_STATUS,
        "capability_roadmap": EXPECTED_ROADMAP_STATUS,
        "feature_lineage": EXPECTED_LINEAGE_STATUS,
        "contributor_paths": EXPECTED_CONTRIBUTOR_STATUS,
        "lifecycle_coherence": EXPECTED_STATUS,
    }
    require(statuses == expected_statuses, "controlled status set changed")

    routes = set(string_list(profile.get("controlled_routes"), "controlled_routes"))
    require(routes == CONTROLLED_ROUTES, "controlled route set changed")
    lifecycle_routes = set(string_list(profile.get("lifecycle_routes"), "lifecycle_routes"))
    require(lifecycle_routes == {str(path) for path in LIFECYCLE_ROUTES}, "lifecycle route set changed")

    obstruction = profile.get("repaired_obstruction")
    require(isinstance(obstruction, dict), "repaired_obstruction must be an object")
    require(obstruction.get("class") == "cross_document_lifecycle_route_divergence", "unexpected repaired obstruction")
    require(obstruction.get("architectural_effect") == "documentation_only", "repair must remain documentation-only")
    require(obstruction.get("operational_effect") == "none", "repair must have no operational effect")

    authority_flags = profile.get("authority_flags")
    require(isinstance(authority_flags, dict) and authority_flags, "authority_flags must be a non-empty object")
    require(all(value is False for value in authority_flags.values()), "all authority flags must remain false")

    rollback = profile.get("rollback")
    require(isinstance(rollback, dict), "rollback must be an object")
    for key in (
        "restore_last_validated_documentation_generation",
        "preserve_superseded_generation",
        "propagate_correction_or_withdrawal",
        "revalidate_all_controlled_routes",
    ):
        require(rollback.get(key) is True, f"rollback.{key} must remain true")
    require(rollback.get("destructive_history_rewrite") is False, "destructive history rewrite must remain false")

    skills = profile.get("fysa_120")
    require(isinstance(skills, dict), "fysa_120 must be an object")
    string_list(skills.get("categories"), "fysa_120.categories")
    string_list(skills.get("subdivisions"), "fysa_120.subdivisions")
    refinements = skills.get("proposed_refinements")
    require(isinstance(refinements, list) and len(refinements) == 1, "exactly one proposed refinement is required")
    refinement = refinements[0]
    require(isinstance(refinement, dict), "proposed refinement must be an object")
    require(refinement.get("id") == EXPECTED_REFINEMENT, "unexpected refinement id")
    require(refinement.get("status") == "PROPOSED_NON_AUTHORITATIVE", "refinement must remain non-authoritative")

    lifecycle_phrases = [EXPECTED_ROADMAP_STATUS, EXPECTED_LINEAGE_STATUS, EXPECTED_CONTRIBUTOR_STATUS, EXPECTED_STATUS, "Authority effect: `NONE`"]
    for relative in LIFECYCLE_ROUTES:
        require_phrases(root, relative, lifecycle_phrases)

    require_phrases(root, GUIDE_PATH, [
        EXPECTED_SOURCE_HEAD,
        EXPECTED_ROADMAP_STATUS,
        EXPECTED_LINEAGE_STATUS,
        EXPECTED_CONTRIBUTOR_STATUS,
        EXPECTED_STATUS,
        "### Prose equivalent",
        EXPECTED_REFINEMENT,
    ])
    require_phrases(root, Path("README.md"), ["docs/capability-roadmap.md", "docs/portfolio-contributor-paths.md"])
    require_phrases(root, Path("docs/index.md"), ["capability-roadmap.md", "portfolio-contributor-paths.md"])
    require_phrases(root, Path("mkdocs.yml"), [
        "capability-lifecycle-coherence.md",
        "capability-lifecycle-coherence-v1.json",
        EXPECTED_STATUS,
    ])

    return {
        "result": "PASS",
        "profile_id": profile["profile_id"],
        "version": profile["version"],
        "status": profile["status"],
        "authority_effect": profile["authority_effect"],
        "source_head": source["head"],
        "controlled_route_count": len(routes),
        "lifecycle_route_count": len(lifecycle_routes),
        "authority_flag_count": len(authority_flags),
        "proposed_refinement": refinement["id"],
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
