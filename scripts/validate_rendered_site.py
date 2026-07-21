#!/usr/bin/env python3
"""Validate a rendered static documentation site without network access.

The validator checks deterministic, review-relevant properties that source-level
Markdown validation cannot establish: required HTML entry points, language
metadata, duplicate element identifiers, image alternative text, and local link
and fragment integrity. It deliberately does not claim browser, screen-reader,
contrast, reflow, or keyboard-navigation conformance.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit


@dataclass
class Document:
    path: Path
    lang: str | None = None
    ids: set[str] = field(default_factory=set)
    duplicate_ids: set[str] = field(default_factory=set)
    links: list[str] = field(default_factory=list)
    images_without_alt: int = 0


class SiteHTMLParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__(convert_charrefs=True)
        self.document = Document(path=path)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.lower(): value for name, value in attrs}
        element_id = values.get("id")
        if element_id:
            if element_id in self.document.ids:
                self.document.duplicate_ids.add(element_id)
            self.document.ids.add(element_id)

        if tag.lower() == "html":
            self.document.lang = values.get("lang")
        elif tag.lower() == "a" and values.get("href") is not None:
            self.document.links.append(values["href"] or "")
        elif tag.lower() == "img" and "alt" not in values:
            self.document.images_without_alt += 1


def parse_document(path: Path) -> Document:
    parser = SiteHTMLParser(path)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser.document


def resolve_local_target(site_dir: Path, source: Path, raw_href: str) -> tuple[Path, str | None] | None:
    parsed = urlsplit(raw_href)
    if parsed.scheme or parsed.netloc or raw_href.startswith(("mailto:", "tel:", "data:", "javascript:")):
        return None

    decoded_path = unquote(parsed.path)
    fragment = unquote(parsed.fragment) or None
    if decoded_path.startswith("/"):
        relative = PurePosixPath(decoded_path.lstrip("/"))
        candidate = site_dir.joinpath(*relative.parts)
    elif decoded_path:
        relative = PurePosixPath(decoded_path)
        candidate = source.parent.joinpath(*relative.parts)
    else:
        candidate = source

    candidate = candidate.resolve()
    try:
        candidate.relative_to(site_dir.resolve())
    except ValueError as exc:
        raise ValueError(f"link escapes rendered site: {raw_href}") from exc

    if candidate.is_dir() or decoded_path.endswith("/"):
        candidate = candidate / "index.html"
    elif candidate.suffix == "":
        html_candidate = candidate.with_suffix(".html")
        index_candidate = candidate / "index.html"
        if html_candidate.exists():
            candidate = html_candidate
        elif index_candidate.exists():
            candidate = index_candidate

    return candidate, fragment


def validate_site(site_dir: Path) -> list[str]:
    site_dir = site_dir.resolve()
    errors: list[str] = []
    if not site_dir.is_dir():
        return [f"rendered site directory does not exist: {site_dir}"]

    entry = site_dir / "index.html"
    if not entry.is_file():
        errors.append("rendered site is missing index.html")

    html_files = sorted(site_dir.rglob("*.html"))
    if not html_files:
        errors.append("rendered site contains no HTML files")
        return errors

    documents: dict[Path, Document] = {}
    for path in html_files:
        if path.is_symlink():
            errors.append(f"rendered HTML must not be a symlink: {path.relative_to(site_dir)}")
            continue
        try:
            document = parse_document(path)
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot parse {path.relative_to(site_dir)} as UTF-8 HTML: {exc}")
            continue
        documents[path.resolve()] = document
        relative = path.relative_to(site_dir)
        if not document.lang or not document.lang.strip():
            errors.append(f"{relative}: <html> is missing a non-empty lang attribute")
        for duplicate in sorted(document.duplicate_ids):
            errors.append(f"{relative}: duplicate id {duplicate!r}")
        if document.images_without_alt:
            errors.append(f"{relative}: {document.images_without_alt} image(s) missing alt attributes")

    for path, document in documents.items():
        relative = path.relative_to(site_dir)
        for href in document.links:
            if href == "":
                errors.append(f"{relative}: empty href")
                continue
            try:
                resolved = resolve_local_target(site_dir, path, href)
            except ValueError as exc:
                errors.append(f"{relative}: {exc}")
                continue
            if resolved is None:
                continue
            target, fragment = resolved
            if not target.is_file():
                errors.append(f"{relative}: missing rendered link target {href!r}")
                continue
            if fragment:
                target_document = documents.get(target.resolve())
                if target_document is None:
                    errors.append(f"{relative}: fragment target is not parsed HTML {href!r}")
                elif fragment not in target_document.ids:
                    errors.append(f"{relative}: missing rendered fragment {href!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site_dir", nargs="?", default="site", type=Path)
    args = parser.parse_args(argv)

    errors = validate_site(args.site_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"rendered-site validation failed with {len(errors)} error(s)", file=sys.stderr)
        return 1

    html_count = sum(1 for _ in args.site_dir.rglob("*.html"))
    print(f"validated {html_count} rendered HTML files")
    print("validated language metadata, unique ids, image alt attributes, and local links/fragments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
