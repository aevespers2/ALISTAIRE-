#!/usr/bin/env python3
"""Fail-closed validation for the portfolio authority-currentness rebind addendum."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

PROFILE_ID = "ALISTAIRE-PORTFOLIO-CURRENTNESS-REBIND-v1"
STATUS = "PORTFOLIO_CURRENTNESS_REBIND_COMPLETED_STALE_TUPLES_PRESERVED_BINDINGS_UNACCEPTED"
BASE_STATUS = "PORTFOLIO_AUTHORITY_CURRENTNESS_RECONCILED_CONFLICTS_DISSENT_AND_VACANCIES_RECORDED_BINDINGS_UNACCEPTED"
PROPAGATION_MARKER = "PORTFOLIO_CURRENTNESS_REBIND_REQUIRED"
EXPECTED_REPOSITORIES = {
    "aevespers2/ALISTAIRE-",
    "aevespers2/JusticeForMe",
    "aevespers2/QSO-GENOMES",
    "aevespers2/QSO-SEEKER",
}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_PLANNING_FILES = ("taskchain.md", "punchlist.md", "release.md", "changelog.md")


class ValidationError(ValueError):
    """Raised when the rebind packet violates a closed validation rule."""


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


def _valid_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    _walk_finite(profile)
    _require(profile.get("profile_id") == PROFILE_ID, "unexpected profile_id")
    _require(profile.get("status") == STATUS, "unexpected controlled status")
    _require(profile.get("reviewed_at") == "2026-07-24", "review date drift")
    _require(profile.get("authority_effect") == "NONE", "authority effect must be NONE")
    _require(profile.get("supersedes_snapshot_findings_only") is True, "snapshot boundary missing")

    policy = profile.get("source_policy")
    _require(isinstance(policy, dict), "source policy missing")
    for field in (
        "previous_tuple_preserved",
        "self_referential_head_claims_prohibited",
        "candidate_evidence_is_non_authorizing",
        "passing_ci_is_non_authorizing",
        "descendant_revalidation_required",
    ):
        _require(policy.get(field) is True, f"source policy weakened: {field}")

    rebindings = profile.get("rebindings")
    _require(isinstance(rebindings, list), "rebindings must be a list")
    _require(len(rebindings) == 4, "exactly four bounded rebindings are required")

    by_name: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(rebindings):
        _require(isinstance(entry, dict), f"rebind entry {index} must be an object")
        name = entry.get("repository")
        _require(isinstance(name, str) and name, f"rebind entry {index} lacks repository")
        _require(name not in by_name, f"duplicate rebind repository: {name}")
        by_name[name] = entry

        _require(isinstance(entry.get("pull_request"), int) and entry["pull_request"] > 0, f"{name}: invalid PR")
        old_sha = entry.get("previous_sha")
        new_sha = entry.get("new_sha")
        _require(_valid_sha(old_sha), f"{name}: invalid previous SHA")
        _require(_valid_sha(new_sha), f"{name}: invalid new SHA")
        _require(old_sha != new_sha, f"{name}: previous and new tuple must differ")
        _require(entry.get("authority_effect") == "NONE", f"{name}: authority effect must remain NONE")
        _require(entry.get("descendant_revalidation_required") is True, f"{name}: descendant revalidation missing")
        for field in ("source_role", "currentness", "reason"):
            _require(isinstance(entry.get(field), str) and entry[field].strip(), f"{name}: missing {field}")
        evidence = entry.get("evidence")
        _require(isinstance(evidence, dict) and evidence, f"{name}: evidence record missing")

    _require(set(by_name) == EXPECTED_REPOSITORIES, "rebind coverage mismatch")

    self_entry = by_name["aevespers2/ALISTAIRE-"]
    _require(self_entry["source_role"] == "reviewed_parent_generation", "ALISTAIRE self-currentness must bind an existing parent")
    _require("parent_generation" in self_entry["currentness"], "ALISTAIRE parent-generation classification missing")

    seeker = by_name["aevespers2/QSO-SEEKER"]
    previous_declared = seeker.get("previous_body_declared_sha")
    current_declared = seeker.get("current_body_declared_sha")
    _require(_valid_sha(previous_declared), "QSO-SEEKER previous body SHA missing")
    _require(_valid_sha(current_declared), "QSO-SEEKER current body SHA missing")
    _require(previous_declared != seeker["previous_sha"], "QSO-SEEKER historical mismatch witness erased")
    _require(current_declared == seeker["new_sha"], "QSO-SEEKER current body/head agreement missing")
    _require("resolved" in seeker["currentness"], "QSO-SEEKER resolved classification missing")

    justice = by_name["aevespers2/JusticeForMe"]
    _require(
        justice["evidence"].get("resulting_validation") == "PENDING",
        "JusticeForMe resulting validation must not be promoted",
    )

    genomes = by_name["aevespers2/QSO-GENOMES"]
    for field in ("documentation_run", "capability_review_run", "consent_run"):
        _require(isinstance(genomes["evidence"].get(field), int), f"QSO-GENOMES missing {field}")

    compatibility = profile.get("planning_route_compatibility")
    _require(isinstance(compatibility, dict), "planning-route compatibility missing")
    _require(compatibility.get("base_status") == BASE_STATUS, "base currentness status drift")
    _require(compatibility.get("propagation_marker") == PROPAGATION_MARKER, "rebind marker drift")

    obstructions = profile.get("unchanged_material_obstructions")
    _require(isinstance(obstructions, list) and len(obstructions) >= 8, "material obstruction set incomplete")

    skills = profile.get("fysa_120")
    _require(isinstance(skills, dict), "FYSA-120 mapping missing")
    _require(skills.get("evidence_level") == "applied", "skill evidence level must remain applied")
    _require(
        isinstance(skills.get("proposed_subdivision"), str)
        and skills["proposed_subdivision"].startswith("017-H"),
        "proposed subdivision missing",
    )
    _require("do not establish competence" in skills.get("authority_boundary", ""), "skill authority boundary missing")

    safety = profile.get("safety_boundaries")
    _require(isinstance(safety, dict) and safety, "safety boundaries missing")
    _require(all(value is False for value in safety.values()), "every operational authority flag must remain false")

    return {
        "profile_id": PROFILE_ID,
        "status": STATUS,
        "rebind_count": len(by_name),
        "authority_effect": "NONE",
        "result": "PASS",
    }


def validate_repository(root: Path) -> dict[str, Any]:
    profile = load_profile(root / "docs" / "portfolio-authority-currentness-rebind-v1.json")
    report = validate_profile(profile)

    guide = (root / "docs" / "portfolio-authority-currentness-rebind.md").read_text(
        encoding="utf-8", errors="strict"
    )
    for marker in (
        STATUS,
        "Authority effect: `NONE`",
        "```mermaid",
        "### Prose equivalent",
        BASE_STATUS,
        PROPAGATION_MARKER,
        "017-H — Exact-source correction ledger and non-self-referential currentness rebinding",
    ):
        _require(marker in guide, f"guide marker missing: {marker}")
    for repository in sorted(EXPECTED_REPOSITORIES):
        _require(f"`{repository}`" in guide, f"guide omits repository: {repository}")

    mkdocs = (root / "mkdocs.yml").read_text(encoding="utf-8", errors="strict")
    _require("portfolio-authority-currentness-rebind.md" in mkdocs, "MkDocs navigation omits rebind guide")
    _require("portfolio-authority-currentness-rebind-v1.json" in mkdocs, "MkDocs navigation omits rebind profile")
    _require(STATUS in mkdocs, "MkDocs metadata omits rebind status")

    for path in REQUIRED_PLANNING_FILES:
        text = (root / path).read_text(encoding="utf-8", errors="strict")
        _require(BASE_STATUS in text, f"{path} omits base currentness status")
        _require(PROPAGATION_MARKER in text, f"{path} omits rebind propagation marker")

    workflow = (root / ".github" / "workflows" / "portfolio-authority-currentness-rebind.yml").read_text(
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
            _require(_valid_sha(args.submitted_sha), "submitted SHA must be 40 lowercase hex characters")
            report["submitted_sha"] = args.submitted_sha
        print(json.dumps(report, sort_keys=True, indent=2))
        return 0
    except (OSError, UnicodeError, ValidationError) as exc:
        print(json.dumps({"result": "FAIL", "error": str(exc)}, sort_keys=True, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
