#!/usr/bin/env python3
"""Validate the documentation-only A.L.I.S.T.A.I.R.E. charter surface.

This script intentionally uses only the Python standard library. It checks the
required documentation set, local Markdown links, publication-sensitive marker
patterns, and the presence of core authority-boundary language. It does not
validate implementation, operational security, or architectural acceptance.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
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
    "docs/portable-security-foundation.md",
    "docs/portfolio-integration-roadmap.md",
    "docs/governance-charter.md",
    "docs/constitutional-sovereignty-and-system-participation.md",
    "docs/repository-consolidation.md",
    "docs/security-and-governance.md",
    "docs/development.md",
    "docs/diagrams.md",
    "docs/adr/0001-governance-consolidation-and-cali-sanders-parker.md",
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
    "README.md": (
        "documentation-first research architecture",
        "Explicit non-capabilities",
        "No automatic runtime or operational authority",
        "Founding Sovereign and Constitutional Sponsor",
        "system preference is not legal personhood or self-appointment",
    ),
}

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


def iter_text_files() -> list[Path]:
    files = [ROOT / name for name in REQUIRED_FILES]
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


def main() -> int:
    errors = 0
    errors += check_required_files()
    errors += check_required_phrases()
    errors += check_local_links()
    errors += check_sensitive_patterns()

    if errors:
        fail(f"documentation validation failed with {errors} error(s)")
        return 1

    print(f"validated {len(REQUIRED_FILES)} required files")
    print("validated authority-boundary phrases")
    print("validated local Markdown links")
    print("validated publication-sensitive marker patterns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
