#!/usr/bin/env python3
"""Validate the documentation-only A.L.I.S.T.A.I.R.E. charter surface.

This script intentionally uses only the Python standard library. It checks the
required documentation set, local Markdown links, publication-sensitive marker
patterns, authority-boundary language, repository provenance, and the complete
portfolio authority-currentness packet. It does not validate implementation,
operational security, migration approval, or architectural acceptance.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "taskchain.md",
    "punchlist.md",
    "release.md",
    "changelog.md",
    "mkdocs.yml",
    "requirements-docs.txt",
    "docs/index.md",
    "docs/architecture.md",
    "docs/portfolio-contract-authority-matrix.md",
    "docs/portfolio-authority-currentness-review.md",
    "docs/portfolio-authority-currentness-v1.json",
    "docs/portable-security-foundation.md",
    "docs/portfolio-integration-roadmap.md",
    "docs/governance-charter.md",
    "docs/constitutional-sovereignty-and-system-participation.md",
    "docs/repository-consolidation.md",
    "docs/repository-provenance-and-migration.md",
    "docs/repository-provenance-manifest-v1.json",
    "docs/security-and-governance.md",
    "docs/development.md",
    "docs/diagrams.md",
    "docs/adr/0001-governance-consolidation-and-cali-sanders-parker.md",
    "scripts/check_portfolio_authority_currentness.py",
    "tests/test_check_portfolio_authority_currentness.py",
    ".github/workflows/portfolio-authority-currentness.yml",
)

REQUIRED_PHRASES = {
    "docs/governance-charter.md": (
        "D1 — Canonical charter and repository identity",
        "D2 — Neutral contract steward",
        "D3 — Canonical bytes and identity primitives",
        "D4 — Independent authority and recovery roots",
        "D5 — Portfolio incident command",
        "Unknown is not secure",
        "Execution is not acceptance",
    ),
    "docs/constitutional-sovereignty-and-system-participation.md": (
        "Founding Sovereign and Constitutional Sponsor",
        "The role is:",
        "The governed system may not:",
        "governed-system nomination or informed assent",
        "independent human fiduciary approval",
        "constitutional and conformance review",
        "This participation model does not assert",
        "documentation merge       -> charter acceptance",
    ),
    "docs/portfolio-contract-authority-matrix.md": (
        "The matrix is documentation and governance evidence only",
        "Every record family has its own identity",
        "Pairwise compatibility is insufficient",
        "This is an engineering method, not a claim that a formal homology or cohomology computation has been completed",
        "A repository-local document may narrow its own scope but may not silently broaden constitutional authority",
    ),
    "docs/portfolio-authority-currentness-review.md": (
        "PORTFOLIO_AUTHORITY_CURRENTNESS_RECONCILED_CONFLICTS_DISSENT_AND_VACANCIES_RECORDED_BINDINGS_UNACCEPTED",
        "Authority effect: `NONE`",
        "### Prose equivalent",
        "NO_VERIFIED_HUMAN_DISSENT_LOCATED_IN_REVIEWED_CURRENTNESS_SNAPSHOT",
        "QSO-SEEKER PR #14 currently resolves to head",
        "V1–V10",
        "013-I — Cross-repository authority-currentness, conflict, dissent, and vacancy reconciliation",
    ),
    "docs/portable-security-foundation.md": (
        "Repository `0`",
        "Repository `1`",
        "Execution success is evidence",
        "UNKNOWN",
        "ownership or explicit permission",
    ),
    "docs/portfolio-integration-roadmap.md": (
        "Minimal constitutional decision set",
        "Acceptance DAG",
        "A downstream success cannot retroactively satisfy an upstream gate",
    ),
    "docs/repository-provenance-and-migration.md": (
        "Exact observed generations",
        "The empty topic tree remains useful as a **taxonomy proposal**",
        "Neither repository exposes a `LICENSE` file",
        "LIMITED_PASS_WITH_RESIDUAL_RISK",
        "040-F — Repository-identity consolidation and provenance-preserving retirement",
        "creates no canonical authority",
    ),
    "README.md": (
        "documentation-first research architecture",
        "Explicit non-capabilities",
        "No automatic runtime or operational authority",
        "Founding Sovereign and Constitutional Sponsor",
        "system preference is not legal personhood or self-appointment",
        "repository-provenance-manifest-v1.json",
    ),
}

EXPECTED_REPOSITORIES = {
    "aevespers2/ALISTAIRE-",
    "aevespers2/Alistaire-agi",
}
EXPECTED_MAIN_HEADS = {
    "aevespers2/ALISTAIRE-": "7adbbf963616d09b4ebafea7c0963a2fac5688a9",
    "aevespers2/Alistaire-agi": "504222dbecb1e1e49c01d74e536de5b6fa93c39a",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")

SENSITIVE_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
)

MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
CODE_FENCE = re.compile(r"^\s*```")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value is prohibited: {value}")


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def iter_text_files() -> list[Path]:
    files = [ROOT / name for name in REQUIRED_FILES if name.endswith((".md", ".yml", ".txt"))]
    files.extend((ROOT / "docs").rglob("*.md"))
    return sorted({path for path in files if path.is_file()})


def check_required_files() -> int:
    errors = 0
    for relative in REQUIRED_FILES:
        path = ROOT / relative
        if not path.is_file():
            fail(f"missing required file: {relative}")
            errors += 1
        elif path.stat().st_size == 0:
            fail(f"required file is empty: {relative}")
            errors += 1
    return errors


def check_required_phrases() -> int:
    errors = 0
    for relative, phrases in REQUIRED_PHRASES.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                fail(f"{relative} is missing required boundary phrase: {phrase!r}")
                errors += 1
    return errors


def strip_fragment_and_query(target: str) -> str:
    parsed = urlsplit(target)
    return unquote(parsed.path)


def check_local_links() -> int:
    errors = 0
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        in_fence = False
        for line_number, line in enumerate(text.splitlines(), start=1):
            if CODE_FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in MARKDOWN_LINK.finditer(line):
                raw_target = match.group(1).strip()
                if not raw_target or raw_target.startswith(("#", "mailto:", "tel:")):
                    continue
                if urlsplit(raw_target).scheme or raw_target.startswith("//"):
                    continue
                target_path = strip_fragment_and_query(raw_target)
                if not target_path:
                    continue
                candidate = (path.parent / target_path).resolve()
                try:
                    candidate.relative_to(ROOT.resolve())
                except ValueError:
                    fail(f"{path.relative_to(ROOT)}:{line_number}: link escapes repository: {raw_target}")
                    errors += 1
                    continue
                if not candidate.exists():
                    fail(f"{path.relative_to(ROOT)}:{line_number}: missing local link target: {raw_target}")
                    errors += 1
    return errors


def check_sensitive_patterns() -> int:
    errors = 0
    for path in iter_text_files():
        text = path.read_text(encoding="utf-8")
        for pattern in SENSITIVE_PATTERNS:
            if pattern.search(text):
                fail(f"publication-sensitive pattern found in {path.relative_to(ROOT)}: {pattern.pattern}")
                errors += 1
    return errors


def check_provenance_manifest() -> int:
    errors = 0
    path = ROOT / "docs/repository-provenance-manifest-v1.json"
    try:
        raw = path.read_bytes().decode("utf-8", errors="strict")
        manifest = json.loads(raw, object_pairs_hook=reject_duplicate_keys, parse_constant=reject_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        fail(f"invalid provenance manifest: {exc}")
        return 1

    if not isinstance(manifest, dict):
        fail("provenance manifest root must be an object")
        return 1
    if manifest.get("manifest_id") != "ALISTAIRE-REPOSITORY-PROVENANCE-001":
        fail("unexpected provenance manifest_id")
        errors += 1
    if manifest.get("status") != "DOCUMENTATION_ONLY_REVIEW" or manifest.get("authority_effect") != "none":
        fail("provenance manifest must remain documentation-only and non-authorizing")
        errors += 1

    repositories = manifest.get("repositories")
    if not isinstance(repositories, list) or len(repositories) != 2:
        fail("provenance manifest must contain exactly two repository records")
        return errors + 1

    observed: set[str] = set()
    for record in repositories:
        if not isinstance(record, dict):
            fail("repository record must be an object")
            errors += 1
            continue
        repository = record.get("repository")
        observed.add(repository)
        main_head = record.get("observed_main_head")
        if main_head != EXPECTED_MAIN_HEADS.get(repository) or not SHA40.fullmatch(str(main_head)):
            fail(f"unexpected or invalid observed main head for {repository}")
            errors += 1
        candidate = record.get("active_candidate")
        if not isinstance(candidate, dict) or not SHA40.fullmatch(str(candidate.get("head", ""))):
            fail(f"invalid active candidate for {repository}")
            errors += 1
        commits = record.get("observed_commits_newest_first")
        if not isinstance(commits, list) or not commits or len(commits) != len(set(commits)):
            fail(f"invalid or duplicate commit history for {repository}")
            errors += 1
        elif not all(isinstance(sha, str) and SHA40.fullmatch(sha) for sha in commits):
            fail(f"invalid commit SHA in history for {repository}")
            errors += 1
        license_record = record.get("license")
        if not isinstance(license_record, dict) or license_record.get("status") != "MISSING":
            fail(f"license status must remain explicit for {repository}")
            errors += 1

    if observed != EXPECTED_REPOSITORIES:
        fail(f"repository closure mismatch: {sorted(observed)}")
        errors += 1

    scan = manifest.get("sensitive_data_review")
    if not isinstance(scan, dict) or scan.get("status") != "LIMITED_PASS_WITH_RESIDUAL_RISK":
        fail("sensitive-data review must preserve its limited-pass qualification")
        errors += 1
    if not manifest.get("current_obstructions"):
        fail("provenance manifest must retain current obstructions")
        errors += 1
    gap = manifest.get("proposed_skill_gap")
    if not isinstance(gap, dict) or gap.get("status") != "PROPOSED_NON_AUTHORITATIVE":
        fail("proposed skill gap must remain non-authoritative")
        errors += 1

    return errors


def check_portfolio_authority_currentness() -> int:
    path = ROOT / "scripts" / "check_portfolio_authority_currentness.py"
    spec = importlib.util.spec_from_file_location("portfolio_authority_currentness", path)
    if spec is None or spec.loader is None:
        fail("cannot load portfolio authority currentness validator")
        return 1
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        report = module.validate_repository(ROOT)
    except Exception as exc:  # Fail closed on any validator or input defect.
        fail(f"portfolio authority currentness validation failed: {exc}")
        return 1
    if report.get("result") != "PASS" or report.get("repository_count") != 19:
        fail(f"unexpected portfolio authority currentness report: {report}")
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


def main() -> int:
    errors = 0
    errors += check_required_files()
    errors += check_required_phrases()
    errors += check_local_links()
    errors += check_sensitive_patterns()
    errors += check_provenance_manifest()
    errors += check_portfolio_authority_currentness()

    if errors:
        fail(f"documentation validation failed with {errors} error(s)")
        return 1

    print(f"validated {len(REQUIRED_FILES)} required files")
    print("validated authority-boundary phrases")
    print("validated local Markdown links")
    print("validated publication-sensitive marker patterns")
    print("validated repository provenance manifest")
    print("validated nineteen-repository authority currentness packet")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
