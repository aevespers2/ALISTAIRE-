#!/usr/bin/env python3
"""Fail-closed validation for the portfolio authority-source reconciliation packet."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PACKET = Path("docs/portfolio-authority-source-reconciliation-v1.json")
STATUS = "PORTFOLIO_AUTHORITY_SOURCES_RECONCILED_CONFLICTS_DISSENT_AND_VACANCIES_RECORDED_BINDINGS_UNACCEPTED"
SHA = re.compile(r"^[0-9a-f]{40}$")

DEFAULTS = {
    "aevespers2/0": "476953e3016de56eb7a0d5a4b1ed889c80435f71",
    "aevespers2/1": "6685872ceafdefa4961e261abb45202e664e3666",
    "aevespers2/AionUi": "66b89879a0ef204a11cf0ea17fb58e5ad88dd930",
    "aevespers2/ALISTAIRE-": "7adbbf963616d09b4ebafea7c0963a2fac5688a9",
    "aevespers2/Alistaire-agi": "504222dbecb1e1e49c01d74e536de5b6fa93c39a",
    "aevespers2/Bridge": "12616ad0e2f04572d8bf6af606f078489607b83f",
    "aevespers2/datarepo-temporal-invariants": "5d549f1082d4bc0ee59a34d09f24b4fa44e6e9bb",
    "aevespers2/grok-build-alistaire": "ba76b0a683fa52e4e60685017b85905451be17bc",
    "aevespers2/JusticeForMe": "d286fc874394d2fcdc07b303436024f100ad1541",
    "aevespers2/Misc": "b565920c6a9203378d3fb8643ac5b49234c9dc7e",
    "aevespers2/qsio-kernel": "6468254d7703e5f771e610ed3f76bac1b7205ddb",
    "aevespers2/QSO-DIGITALIS": "3d127a327fefa534e34ea9cdee7c7dd2362362c7",
    "aevespers2/QSO-FABRIC": "bd0ac7af3b34602082db03e71055b652707c9b18",
    "aevespers2/qso-field.github.io": "2d7adf88ce84f01f0ff1067cef09388481f7e4ae",
    "aevespers2/QSO-GENOMES": "f61bb271f46c595467c172332cc0759e40ccd272",
    "aevespers2/QSO-PAYMENTS": "8ab3b97b44fc1a38cec9aa4e8b0aac3ac6bda161",
    "aevespers2/QSO-SEEKER": "01b08e61edd7f212f43cfe9b6f17b5695c46cb25",
    "aevespers2/QSO-STUDIO": "652463f6066bf67877c5a7f1fc59e01172bda286",
    "aevespers2/QuantumStateObjects": "40efcbf8ce2bda7d6b05b3fb1f3ccf0384facc51",
}
CANDIDATES = {
    ("aevespers2/1", 2): "47b58fa49c8dda7f44234dab68f78673bb02d269",
    ("aevespers2/AionUi", 1): "ea90ee294a0c2c5985dff187cf5482113ddaff88",
    ("aevespers2/ALISTAIRE-", 1): "38213e4e57dd1b03e434cc9cfb0da3c4e0d25477",
    ("aevespers2/Alistaire-agi", 2): "0ede0c6a796fe9f16c10d25fc79ba6962875ba82",
    ("aevespers2/Alistaire-agi", 4): "9e953992dfefbfa0fd61ce37e955b75f79a8e1d6",
    ("aevespers2/Bridge", 22): "644a5f45f7ee41adbba4578bb364b04a24245206",
    ("aevespers2/datarepo-temporal-invariants", 1): "5417295e5e9231d39e878ba68729d26c89ed7e55",
    ("aevespers2/datarepo-temporal-invariants", 2): "74c40d723e1f4ea744346e8a19b19be1cc485672",
    ("aevespers2/datarepo-temporal-invariants", 3): "023fc1c753e16c3c72f1933701b4daf74decd4ec",
    ("aevespers2/grok-build-alistaire", 1): "de42b047af506b31944d89622034e667636407e7",
    ("aevespers2/qsio-kernel", 1): "980e981952fd1c2c7c5b4a30b8e30664dcc6f6bc",
    ("aevespers2/QSO-DIGITALIS", 6): "fa2a4e842a4a9ddecbaad7ebc9bb995e5031e213",
    ("aevespers2/QSO-FABRIC", 21): "25036a5cfcea79e204a4660ddd1af09c054935b1",
    ("aevespers2/QSO-FABRIC", 23): "765b5caeda4c2c4dd68d4f8a9a7fda141c1dd989",
    ("aevespers2/qso-field.github.io", 23): "198dd81a4fd55c777cebcc51ab3973f94d9469fa",
    ("aevespers2/qso-field.github.io", 24): "a56b1fa93f151ee14f3cdd4183b89a10e268e352",
    ("aevespers2/QSO-GENOMES", 15): "c29bd681bab680e467903784527776d284469a3d",
    ("aevespers2/QSO-PAYMENTS", 1): "46e4a5bb1ca6f61d3024b818ac73b3c539755bc0",
    ("aevespers2/QSO-SEEKER", 14): "49e7ff008b04fd386ad86bd3881105821c4b55e6",
    ("aevespers2/QuantumStateObjects", 10): "e993e9f9a062d298bb06e3418b3948d485232dc2",
    ("aevespers2/QuantumStateObjects", 12): "cc9b9c7b06a1a48bbc052b8d6bacd11782285288",
}
CONFLICTS = {
    "IDENTITY_ALISTAIRE_DUAL_REPOSITORY",
    "RUNTIME_FABRIC_LEGACY_LABEL_COLLISION",
    "KERNEL_RUNTIME_UNSUPPORTED_CROSSWALK",
    "REPOSITORY_1_AUTHORITY_VACANCY",
    "SOURCE_EVIDENCE_ROUTE_OWNERSHIP",
    "REVIEW_DISPLAY_APPROVAL_SEPARATION",
    "FINANCIAL_AUTHORIZATION_TECHNICAL_CAPABILITY_SEPARATION",
    "PUBLIC_REGISTRY_CUSTODY",
    "TEMPORAL_REPOSITORY_SOURCE_PRECEDENCE",
    "CANDIDATE_CURRENTNESS_AND_RESULTING_HEAD_EVIDENCE",
}
VACANCIES = {
    "D1_CANONICAL_IDENTITY_OWNER", "D2_NEUTRAL_CONTRACT_STEWARD",
    "D3_CANONICAL_REPRESENTATION_CUSTODIAN",
    "D4_INDEPENDENT_AUTHORITY_AND_RECOVERY", "D5_INCIDENT_COMMAND",
    "RUNTIME_FABRIC_SEMANTIC_AND_ROUTE_OWNERS",
    "SOURCE_RIGHTS_PRIVACY_RETENTION_PUBLICATION_OWNERS",
    "REVIEW_ACCESSIBILITY_CORRECTION_OWNER",
    "INDEPENDENT_FINANCIAL_AUTHORIZER", "PUBLICATION_AND_REGISTRY_CUSTODIAN",
}
DISSENT = {
    "D1_REPOSITORY_IDENTITY_OPTIONS", "RUNTIME_FABRIC_PARTITION_OPTIONS",
    "KERNEL_RUNTIME_ROUTE_OPTIONS", "DATAREPO_PRECEDENCE_OPTIONS",
    "QSO_FIELD_CANDIDATE_RECONCILIATION", "QSO_DIGITALIS_DISPOSITION",
}
ROUTES = {
    "docs/portfolio-authority-source-reconciliation.md",
    "docs/portfolio-authority-source-reconciliation-v1.json",
    "docs/portfolio-contract-authority-matrix.md", "taskchain.md", "punchlist.md",
    "release.md", "changelog.md", "mkdocs.yml",
}
CATEGORIES = {
    "CAT-011", "CAT-012", "CAT-013", "CAT-017", "CAT-018", "CAT-019",
    "CAT-031", "CAT-032", "CAT-040", "CAT-052", "CAT-059", "CAT-070",
}
TOP = {
    "profile_id", "profile_version", "status", "authority_effect", "observed_at",
    "repositories", "conflicts", "vacancies", "dissent", "invariants",
    "review_gates", "controlled_routes", "fysa_120",
}


class PacketError(ValueError):
    pass


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PacketError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> None:
    raise PacketError(f"non-finite JSON number prohibited: {value}")


def load_packet(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_bytes().decode("utf-8", errors="strict"),
            object_pairs_hook=_object,
            parse_constant=_constant,
        )
    except PacketError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PacketError(f"unable to load packet: {exc}") from exc
    if not isinstance(value, dict):
        raise PacketError("packet root must be an object")
    return value


def _exact(value: dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise PacketError(f"{label} fields changed")


def _strings(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PacketError(f"{label} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise PacketError(f"{label} must contain strings")
    if len(value) != len(set(value)):
        raise PacketError(f"{label} contains duplicates")
    return value


def validate(packet: dict[str, Any], root: Path = Path("."), submitted_sha: str | None = None) -> dict[str, Any]:
    _exact(packet, TOP, "packet")
    if packet["profile_id"] != "ALISTAIRE-PORTFOLIO-AUTHORITY-SOURCE-RECONCILIATION-001":
        raise PacketError("profile_id changed")
    if packet["profile_version"] != "1.0.0-candidate":
        raise PacketError("profile_version changed")
    if packet["status"] != STATUS:
        raise PacketError("status changed")
    if packet["authority_effect"] != "NONE":
        raise PacketError("authority_effect must remain NONE")
    if packet["observed_at"] != "2026-07-24":
        raise PacketError("observation date changed")

    entries = packet["repositories"]
    if not isinstance(entries, list) or len(entries) != 19:
        raise PacketError("exactly nineteen repositories are required")
    defaults: dict[str, str] = {}
    candidates: dict[tuple[str, int], str] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise PacketError("repository entry must be an object")
        _exact(entry, {"repository", "default_head", "candidates", "role_state"}, "repository")
        repository = entry["repository"]
        head = entry["default_head"]
        if not isinstance(repository, str) or not repository:
            raise PacketError("repository name missing")
        if repository in defaults:
            raise PacketError(f"duplicate repository: {repository}")
        if not isinstance(head, str) or not SHA.fullmatch(head):
            raise PacketError(f"invalid default head: {repository}")
        defaults[repository] = head
        if not isinstance(entry["role_state"], str) or not entry["role_state"]:
            raise PacketError(f"role state missing: {repository}")
        if not isinstance(entry["candidates"], list):
            raise PacketError("candidates must be a list")
        for candidate in entry["candidates"]:
            _exact(candidate, {"pr", "head", "evidence"}, "candidate")
            pr = candidate["pr"]
            if not isinstance(pr, int) or isinstance(pr, bool) or pr <= 0:
                raise PacketError("candidate PR must be a positive integer")
            key = (repository, pr)
            if key in candidates:
                raise PacketError(f"duplicate candidate: {key}")
            if not isinstance(candidate["head"], str) or not SHA.fullmatch(candidate["head"]):
                raise PacketError(f"invalid candidate head: {key}")
            if not isinstance(candidate["evidence"], str) or not candidate["evidence"]:
                raise PacketError(f"candidate evidence missing: {key}")
            candidates[key] = candidate["head"]
    if defaults != DEFAULTS:
        raise PacketError("default-head closure changed")
    if candidates != CANDIDATES:
        raise PacketError("candidate-head closure changed")

    if set(_strings(packet["conflicts"], "conflicts")) != CONFLICTS:
        raise PacketError("conflict closure changed")
    if set(_strings(packet["vacancies"], "vacancies")) != VACANCIES:
        raise PacketError("vacancy closure changed")
    if set(_strings(packet["dissent"], "dissent")) != DISSENT:
        raise PacketError("dissent closure changed")
    _strings(packet["invariants"], "invariants")
    _strings(packet["review_gates"], "review_gates")
    if set(_strings(packet["controlled_routes"], "controlled routes")) != ROUTES:
        raise PacketError("controlled-route closure changed")
    for route in ROUTES:
        if not (root / route).is_file():
            raise PacketError(f"controlled route missing: {route}")

    mapping = packet["fysa_120"]
    if not isinstance(mapping, dict):
        raise PacketError("fysa_120 must be an object")
    _exact(mapping, {"categories", "subdivisions", "proposed_gap"}, "fysa_120")
    if set(_strings(mapping["categories"], "categories")) != CATEGORIES:
        raise PacketError("category closure changed")
    _strings(mapping["subdivisions"], "subdivisions")
    if not isinstance(mapping["proposed_gap"], str) or not mapping["proposed_gap"].startswith("013-I"):
        raise PacketError("proposed gap changed")

    markdown = (root / "docs/portfolio-authority-source-reconciliation.md").read_text(encoding="utf-8")
    for marker in (
        STATUS, "Authority effect: `NONE`", "Repository snapshot", "Material conflicts",
        "Explicit vacancies", "Preserved dissent", "Prose equivalent", "013-I",
    ):
        if marker not in markdown:
            raise PacketError(f"documentation marker missing: {marker}")
    for repository in DEFAULTS:
        if repository not in markdown:
            raise PacketError(f"repository missing from documentation: {repository}")

    if submitted_sha is not None and not SHA.fullmatch(submitted_sha):
        raise PacketError("submitted SHA must be lowercase 40-character hex")

    return {
        "status": STATUS, "authority_effect": "NONE", "repositories": len(defaults),
        "candidates": len(candidates), "conflicts": len(CONFLICTS),
        "vacancies": len(VACANCIES), "dissent": len(DISSENT),
        "submitted_sha": submitted_sha,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", type=Path, default=PACKET)
    parser.add_argument("--submitted-sha")
    args = parser.parse_args()
    try:
        result = validate(load_packet(args.packet), Path("."), args.submitted_sha)
    except (PacketError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps({"valid": True, **result}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
