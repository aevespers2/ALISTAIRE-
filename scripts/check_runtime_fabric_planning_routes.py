#!/usr/bin/env python3
"""Validate synchronized, non-authorizing runtime/Fabric planning routes."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = "PLANNING_ROUTES_SYNCHRONIZED_BINDINGS_UNACCEPTED"
SAFE_DEFAULT = "UNSUPPORTED_KERNEL_RUNTIME_ROUTE"
REJECTED_OPTION = "REJECT_DIRECT_IDENTITY_ALIAS"
SHA40 = re.compile(r"^[0-9a-f]{40}$")

ROUTES = {
    "taskchain.md",
    "punchlist.md",
    "release.md",
    "changelog.md",
}

REVIEW_DISPOSITIONS = {
    "BLOCKED_ROLE_COLLISION",
    "OBSERVED_CANDIDATE_INVENTORY_RECORDED_BLOCKED_UNACCEPTED_BINDINGS",
    "DEFAULT_HEADS_VERIFIED_OWNER_VACANCIES_RECORDED_BINDINGS_UNACCEPTED",
    "CANDIDATE_LINEAGES_CLASSIFIED_REBIND_WITHDRAW_OR_ACCEPT_REQUIRED",
    "KERNEL_RUNTIME_CROSSWALK_OPTIONS_DOCUMENTED_UNSELECTED",
    "REVIEW_INDEX_COMPLETE_BINDINGS_UNACCEPTED",
}

COMMON_PHRASES = {
    STATUS,
    SAFE_DEFAULT,
    REJECTED_OPTION,
}

REQUIRED_BY_ROUTE = {
    "taskchain.md": REVIEW_DISPOSITIONS
    | {
        "Current controlled planning-route state",
        "Material composition obstructions",
        "FYSA-120 capability map",
        "Synchronization records documentation currentness only.",
    },
    "punchlist.md": REVIEW_DISPOSITIONS
    | {
        "Current planning-route disposition",
        "Remaining gates",
        "Controlled planning-route synchronization",
        "Authority effect: `NONE`",
    },
    "release.md": REVIEW_DISPOSITIONS
    | {
        "Current runtime/Fabric dispositions",
        "Controlled propagation",
        "Acceptance gates",
        "Artifact requirements",
        "These artifacts do not create credentials",
    },
    "changelog.md": {
        "default-head inventory",
        "candidate-lineage dispositions",
        "kernel-to-runtime crosswalk options",
        "No Pages publication",
        "012-P — Cross-document governance status indexing and controlled-route coherence",
    },
}

NON_ACTIVATION_BOUNDARY = {
    "taskchain.md": "No real device inspection",
    "punchlist.md": "Authority effect: `NONE`",
    "release.md": "No release is ready",
    "changelog.md": "No Pages publication",
}

PROHIBITED_PHRASES = {
    "PLANNING_ROUTES_SYNCHRONIZED_BINDINGS_ACCEPTED",
    "`SUPPORTED_KERNEL_RUNTIME_ROUTE`",
    "SELECT_DIRECT_IDENTITY_ALIAS",
    "authority effect `OPERATIONAL`",
    "authority effect: `OPERATIONAL`",
}


def validate_routes(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}

    for relative in sorted(ROUTES):
        path = root / relative
        if not path.is_file():
            errors.append(f"controlled planning route missing: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        texts[relative] = text
        for phrase in COMMON_PHRASES:
            if phrase not in text:
                errors.append(f"{relative} missing common planning phrase: {phrase}")
        for phrase in REQUIRED_BY_ROUTE[relative]:
            if phrase not in text:
                errors.append(f"{relative} missing route-specific phrase: {phrase}")
        for phrase in PROHIBITED_PHRASES:
            if phrase in text:
                errors.append(f"{relative} contains prohibited promotion: {phrase}")
        boundary = NON_ACTIVATION_BOUNDARY[relative]
        if boundary not in text:
            errors.append(f"{relative} lacks explicit non-activation boundary: {boundary}")

    if len(texts) != len(ROUTES):
        return errors

    for disposition in REVIEW_DISPOSITIONS:
        missing = sorted(
            relative
            for relative in ("taskchain.md", "punchlist.md", "release.md")
            if disposition not in texts[relative]
        )
        if missing:
            errors.append(
                f"planning disposition {disposition} missing from controlled decision routes: {missing}"
            )

    for relative, text in texts.items():
        if text.count(STATUS) < 1:
            errors.append(f"{relative} must contain synchronization status")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--submitted-sha", default=None)
    args = parser.parse_args()

    errors = validate_routes()
    if args.submitted_sha is not None and not SHA40.fullmatch(args.submitted_sha):
        errors.append("submitted SHA must be an exact lowercase 40-character Git SHA")

    report = {
        "status": "PASS" if not errors else "FAIL",
        "submitted_sha": args.submitted_sha,
        "planning_disposition": STATUS,
        "safe_default": SAFE_DEFAULT,
        "rejected_option": REJECTED_OPTION,
        "authority_effect": "NONE",
        "controlled_routes": sorted(ROUTES),
        "review_dispositions": sorted(REVIEW_DISPOSITIONS),
        "errors": errors,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
