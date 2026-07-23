#!/usr/bin/env python3
"""Validate the documentation-only D1 canonical identity decision packet."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_PACKET = Path("docs/d1-canonical-identity-decision-packet-v1.json")
EXPECTED_REPOSITORIES = {
    "aevespers2/ALISTAIRE-": ("7adbbf963616d09b4ebafea7c0963a2fac5688a9", 1, "f3cd97c2418c87f6c4aa7cac7731460ed57f13b7"),
    "aevespers2/Alistaire-agi": ("504222dbecb1e1e49c01d74e536de5b6fa93c39a", 2, "0ede0c6a796fe9f16c10d25fc79ba6962875ba82"),
}
EXPECTED_ROUTES = {
    "README.md",
    "docs/repository-consolidation.md",
    "docs/d1-canonical-identity-decision-packet.md",
    "taskchain.md",
}
REQUIRED_FIELDS = {
    "canonical_repository", "final_repository_name", "display_name", "package_identifier",
    "package_identifier_disposition", "license_or_explicit_no_reuse_status",
    "canonical_documentation_authority", "canonical_release_authority",
    "noncanonical_repository_disposition", "path_level_migration_manifest",
    "attribution_and_history_preservation", "compatibility_window", "public_notice",
    "support_route", "security_reporting_route", "redirect_archive_or_bounded_role_plan",
    "post_transition_monitoring", "rollback_plan", "approver_identity", "approval_date",
    "approved_source_head",
}
MISSING_GATES = {
    "complete_path_level_migration_manifest", "license_decision",
    "history_aware_secret_and_privacy_review", "support_security_and_rollback_owners",
    "compatibility_and_redirect_plan", "rollback_drill", "explicit_human_approval",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value prohibited: {value}")


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_packet(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_bytes().decode("utf-8", errors="strict"),
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("packet root must be an object")
    return value


def validate(packet: dict[str, Any], packet_path: Path = DEFAULT_PACKET, submitted_sha: str | None = None) -> dict[str, Any]:
    if packet.get("packet_id") != "ALISTAIRE-D1-CANONICAL-IDENTITY-DECISION-READINESS-001":
        raise ValueError("unexpected packet_id")
    if packet.get("status") != "REVIEW_READY_BLOCKED" or packet.get("authority_effect") != "none":
        raise ValueError("packet must remain blocked and non-authorizing")
    if packet.get("decision_id") != "D1":
        raise ValueError("packet must bind D1")

    sources = packet.get("observed_sources")
    if not isinstance(sources, list) or len(sources) != 2:
        raise ValueError("observed_sources must contain exactly two repositories")
    seen: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("source record must be an object")
        repository = source.get("repository")
        if repository in seen or repository not in EXPECTED_REPOSITORIES:
            raise ValueError(f"unexpected or duplicate repository: {repository}")
        seen.add(repository)
        expected_main, expected_pr, expected_head = EXPECTED_REPOSITORIES[repository]
        if source.get("observed_default_head") != expected_main or not SHA40.fullmatch(str(source.get("observed_default_head", ""))):
            raise ValueError(f"default-head mismatch for {repository}")
        candidate = source.get("documentation_candidate")
        if not isinstance(candidate, dict) or type(candidate.get("pull_request")) is not int:
            raise ValueError(f"invalid documentation candidate for {repository}")
        if candidate.get("pull_request") != expected_pr or candidate.get("base_head") != expected_head:
            raise ValueError(f"candidate tuple mismatch for {repository}")
    if seen != set(EXPECTED_REPOSITORIES):
        raise ValueError("repository closure mismatch")

    options = packet.get("decision_options")
    if not isinstance(options, list) or [item.get("option_id") for item in options if isinstance(item, dict)] != ["A", "B", "C"]:
        raise ValueError("decision options must be ordered A, B, C")
    if any("SELECTED" == str(item.get("disposition")) for item in options):
        raise ValueError("packet may not select a canonical option")

    if set(packet.get("required_decision_fields", [])) != REQUIRED_FIELDS:
        raise ValueError("required decision field closure mismatch")

    gates = packet.get("readiness_gates")
    if not isinstance(gates, dict):
        raise ValueError("readiness_gates must be an object")
    for gate in MISSING_GATES:
        if gates.get(gate) != "MISSING":
            raise ValueError(f"unresolved gate must remain MISSING: {gate}")
    if packet.get("current_disposition") != "BLOCKED_MISSING_DECISION_EVIDENCE_AND_APPROVAL":
        raise ValueError("current disposition must remain blocked")

    if set(packet.get("controlled_routes", [])) != EXPECTED_ROUTES:
        raise ValueError("controlled route closure mismatch")
    markers = packet.get("propagation_markers")
    if not isinstance(markers, dict) or markers.get("stale") != "D1_REBIND_REQUIRED" or markers.get("withdrawn") != "D1_PACKET_WITHDRAWN":
        raise ValueError("propagation markers mismatch")
    for route in sorted(EXPECTED_ROUTES):
        path = Path(route)
        if not path.is_file():
            raise ValueError(f"missing controlled route: {route}")
        text = path.read_text(encoding="utf-8")
        if "D1_REBIND_REQUIRED" not in text or "D1_PACKET_WITHDRAWN" not in text:
            raise ValueError(f"route lacks D1 propagation markers: {route}")

    prohibited = set(packet.get("prohibited_promotions", []))
    required_prohibited = {
        "recommendation_to_canonical_selection", "passing_ci_to_decision_approval",
        "mergeability_to_authority", "package_name_to_package_authority",
        "copied_content_to_license_permission", "documentation_candidate_to_release_authority",
    }
    if prohibited != required_prohibited:
        raise ValueError("prohibited promotion closure mismatch")

    gap = packet.get("proposed_skill_gap")
    if not isinstance(gap, dict) or gap.get("id") != "040-G" or gap.get("status") != "PROPOSED_NON_AUTHORITATIVE":
        raise ValueError("skill gap must remain proposed and non-authoritative")
    if submitted_sha is not None and not SHA40.fullmatch(submitted_sha):
        raise ValueError("submitted SHA must be exact lowercase Git SHA")

    return {
        "packet_id": packet["packet_id"],
        "source_count": len(sources),
        "controlled_route_count": len(EXPECTED_ROUTES),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "submitted_sha": submitted_sha,
        "disposition": "D1_REVIEW_READINESS_VALIDATED_DECISION_BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", default=str(DEFAULT_PACKET))
    parser.add_argument("--submitted-sha")
    args = parser.parse_args()
    try:
        path = Path(args.packet)
        print(json.dumps(validate(load_packet(path), path, args.submitted_sha), indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc), "disposition": "D1_VALIDATION_FAILED_CLOSED"}, sort_keys=True), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
