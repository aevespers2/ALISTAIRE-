#!/usr/bin/env python3
"""Fail-closed validation for the portfolio authority currentness packet."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

PROFILE_ID = "ALISTAIRE-PORTFOLIO-AUTHORITY-CURRENTNESS-v1"
STATUS = (
    "PORTFOLIO_AUTHORITY_CURRENTNESS_RECONCILED_"
    "CONFLICTS_DISSENT_AND_VACANCIES_RECORDED_BINDINGS_UNACCEPTED"
)
EXPECTED_REPOSITORIES = {
    "aevespers2/0",
    "aevespers2/1",
    "aevespers2/AionUi",
    "aevespers2/ALISTAIRE-",
    "aevespers2/Alistaire-agi",
    "aevespers2/Bridge",
    "aevespers2/datarepo-temporal-invariants",
    "aevespers2/grok-build-alistaire",
    "aevespers2/JusticeForMe",
    "aevespers2/Misc",
    "aevespers2/qsio-kernel",
    "aevespers2/QSO-DIGITALIS",
    "aevespers2/QSO-FABRIC",
    "aevespers2/qso-field.github.io",
    "aevespers2/QSO-GENOMES",
    "aevespers2/QSO-PAYMENTS",
    "aevespers2/QSO-SEEKER",
    "aevespers2/QSO-STUDIO",
    "aevespers2/QuantumStateObjects",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_KINDS = {"pull_request", "default_branch"}
ALLOWED_STATES = {"open_draft", "merged"}
ALLOWED_MERGEABILITY = {"mergeable", "conflicting", "unknown", "not_applicable"}
REQUIRED_VACANCIES = {f"V{i}" for i in range(1, 11)}
REQUIRED_PLANNING_FILES = ("taskchain.md", "punchlist.md", "release.md", "changelog.md")


class ValidationError(ValueError):
    """Raised when the packet violates a closed validation rule."""


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValidationError(f"non-standard numeric constant: {value}")


def load_profile(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise ValidationError(f"cannot read strict UTF-8 profile: {exc}") from exc
    try:
        data = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ValidationError(f"invalid profile JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError("profile root must be an object")
    return data


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _walk_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float):
        _require(math.isfinite(value), f"non-finite number at {path}")
    elif isinstance(value, dict):
        for key, item in value.items():
            _walk_finite(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _walk_finite(item, f"{path}[{index}]")


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    _walk_finite(profile)
    _require(profile.get("profile_id") == PROFILE_ID, "unexpected profile_id")
    _require(profile.get("status") == STATUS, "unexpected controlled status")
    _require(profile.get("authority_effect") == "NONE", "authority effect must be NONE")
    _require(profile.get("reviewed_at") == "2026-07-24", "review date drift")

    repositories = profile.get("repositories")
    _require(isinstance(repositories, list), "repositories must be a list")
    _require(len(repositories) == 19, "exactly 19 repositories are required")

    by_name: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(repositories):
        _require(isinstance(entry, dict), f"repository entry {index} must be an object")
        name = entry.get("repository")
        _require(isinstance(name, str) and name, f"repository entry {index} lacks identity")
        _require(name not in by_name, f"duplicate repository identity: {name}")
        by_name[name] = entry

        source = entry.get("primary_source")
        _require(isinstance(source, dict), f"{name}: primary_source must be an object")
        _require(source.get("kind") in ALLOWED_KINDS, f"{name}: invalid source kind")
        _require(source.get("state") in ALLOWED_STATES, f"{name}: invalid source state")
        _require(
            source.get("mergeability") in ALLOWED_MERGEABILITY,
            f"{name}: invalid mergeability",
        )
        sha = source.get("sha")
        _require(isinstance(sha, str) and SHA_RE.fullmatch(sha) is not None, f"{name}: invalid exact SHA")
        if source.get("kind") == "pull_request":
            _require(isinstance(source.get("number"), int) and source["number"] > 0, f"{name}: invalid PR number")
        else:
            _require(source.get("ref") == "main", f"{name}: default source must bind main")

        for field in (
            "corridor",
            "currentness",
            "candidate_responsibility",
            "semantic_owner_status",
            "route_owner_status",
            "required_disposition",
        ):
            _require(isinstance(entry.get(field), str) and entry[field].strip(), f"{name}: missing {field}")
        for field in ("non_authorities", "conflicts", "vacancies"):
            value = entry.get(field)
            _require(isinstance(value, list) and value, f"{name}: {field} must be a non-empty list")
            _require(all(isinstance(item, str) and item.strip() for item in value), f"{name}: invalid {field}")

    _require(set(by_name) == EXPECTED_REPOSITORIES, "repository coverage does not equal the owned 19-repository portfolio")

    seeker = by_name["aevespers2/QSO-SEEKER"]
    declared = seeker.get("body_declared_sha")
    actual = seeker["primary_source"]["sha"]
    _require(isinstance(declared, str) and SHA_RE.fullmatch(declared) is not None, "QSO-SEEKER declared SHA missing")
    _require(declared != actual, "QSO-SEEKER mismatch witness must preserve distinct declared and actual heads")
    _require(seeker.get("currentness") == "declared_head_mismatch", "QSO-SEEKER mismatch classification missing")
    _require(any("metadata head differs" in item for item in seeker["conflicts"]), "QSO-SEEKER mismatch conflict missing")

    for name in ("aevespers2/0", "aevespers2/JusticeForMe"):
        _require(by_name[name]["primary_source"]["mergeability"] == "conflicting", f"{name}: current conflict must be preserved")

    required_multiple = {
        "aevespers2/Alistaire-agi",
        "aevespers2/1",
        "aevespers2/QSO-GENOMES",
        "aevespers2/QuantumStateObjects",
        "aevespers2/QSO-FABRIC",
        "aevespers2/qso-field.github.io",
    }
    for name in required_multiple:
        _require(by_name[name]["currentness"] == "multiple_active_lineages", f"{name}: multiple-lineage classification missing")

    temporal = by_name["aevespers2/datarepo-temporal-invariants"]
    _require(temporal["currentness"] == "overlapping_unvalidated_candidates", "temporal overlap classification missing")
    _require(any("Actions execution" in item for item in temporal["conflicts"]), "temporal missing-workflow obstruction missing")

    dissent = profile.get("dissent")
    _require(isinstance(dissent, dict), "dissent record missing")
    _require(
        dissent.get("status") == "NO_VERIFIED_HUMAN_DISSENT_LOCATED_IN_REVIEWED_CURRENTNESS_SNAPSHOT",
        "dissent status must distinguish structural conflict from verified human dissent",
    )
    requirements = dissent.get("future_record_requirements")
    _require(isinstance(requirements, list) and len(requirements) >= 8, "dissent evidence requirements incomplete")

    vacancies = profile.get("portfolio_vacancies")
    _require(isinstance(vacancies, list), "portfolio_vacancies must be a list")
    vacancy_ids = {entry.get("id") for entry in vacancies if isinstance(entry, dict)}
    _require(vacancy_ids == REQUIRED_VACANCIES, "portfolio vacancy coverage must be V1-V10 exactly")

    skills = profile.get("fysa_120")
    _require(isinstance(skills, dict), "FYSA-120 mapping missing")
    _require(skills.get("source_status") == "external_unbound", "FYSA-120 source boundary weakened")
    _require(skills.get("evidence_level") == "applied", "skill evidence level must remain applied")
    proposed = skills.get("proposed_subdivision", "")
    _require(isinstance(proposed, str) and proposed.startswith("013-I"), "proposed subdivision missing")
    _require("do not establish competence" in skills.get("authority_boundary", ""), "skill authority boundary missing")

    safety = profile.get("safety_boundaries")
    _require(isinstance(safety, dict) and safety, "safety boundaries missing")
    _require(all(value is False for value in safety.values()), "every operational authority flag must remain false")

    return {
        "profile_id": PROFILE_ID,
        "status": STATUS,
        "repository_count": len(by_name),
        "vacancy_count": len(vacancy_ids),
        "authority_effect": "NONE",
        "result": "PASS",
    }


def validate_repository(root: Path) -> dict[str, Any]:
    profile_path = root / "docs" / "portfolio-authority-currentness-v1.json"
    profile = load_profile(profile_path)
    report = validate_profile(profile)

    guide_path = root / "docs" / "portfolio-authority-currentness-review.md"
    try:
        guide = guide_path.read_text(encoding="utf-8", errors="strict")
    except (OSError, UnicodeError) as exc:
        raise ValidationError(f"cannot read currentness guide: {exc}") from exc
    for marker in (
        STATUS,
        "Authority effect: `NONE`",
        "```mermaid",
        "### Prose equivalent",
        "NO_VERIFIED_HUMAN_DISSENT_LOCATED_IN_REVIEWED_CURRENTNESS_SNAPSHOT",
        "013-I — Cross-repository authority-currentness, conflict, dissent, and vacancy reconciliation",
    ):
        _require(marker in guide, f"guide marker missing: {marker}")
    for repository in sorted(EXPECTED_REPOSITORIES):
        _require(f"`{repository}`" in guide, f"guide omits repository: {repository}")

    mkdocs = (root / "mkdocs.yml").read_text(encoding="utf-8", errors="strict")
    _require("portfolio-authority-currentness-review.md" in mkdocs, "MkDocs navigation omits currentness guide")
    _require(STATUS in mkdocs, "MkDocs metadata omits controlled currentness status")

    for path in REQUIRED_PLANNING_FILES:
        text = (root / path).read_text(encoding="utf-8", errors="strict")
        _require(STATUS in text, f"{path} omits controlled currentness status")
        _require("portfolio-authority-currentness-review.md" in text, f"{path} omits currentness guide link")
        _require("013-I" in text, f"{path} omits proposed subdivision")

    workflow = (root / ".github" / "workflows" / "portfolio-authority-currentness.yml").read_text(
        encoding="utf-8", errors="strict"
    )
    required_workflow_markers = (
        "permissions:\n  contents: read",
        "cancel-in-progress: false",
        "github.event.pull_request.head.sha || github.sha",
        "persist-credentials: false",
        "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "if: always()",
        "Fail closed after evidence retention",
    )
    for marker in required_workflow_markers:
        _require(marker in workflow, f"workflow control missing: {marker}")

    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--submitted-sha")
    args = parser.parse_args()
    try:
        report = validate_repository(args.root)
        if args.submitted_sha is not None:
            _require(SHA_RE.fullmatch(args.submitted_sha) is not None, "submitted SHA must be 40 lowercase hex characters")
            report["submitted_sha"] = args.submitted_sha
        print(json.dumps(report, sort_keys=True, indent=2))
        return 0
    except (OSError, UnicodeError, ValidationError) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
