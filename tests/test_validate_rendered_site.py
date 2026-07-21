from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_rendered_site import validate_site


class RenderedSiteValidationTests(unittest.TestCase):
    def make_site(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        site = Path(temporary.name)
        return temporary, site

    def test_accepts_local_links_and_fragments(self) -> None:
        temporary, site = self.make_site()
        self.addCleanup(temporary.cleanup)
        (site / "index.html").write_text(
            '<html lang="en"><body><a href="guide/#topic">Guide</a></body></html>',
            encoding="utf-8",
        )
        (site / "guide").mkdir()
        (site / "guide" / "index.html").write_text(
            '<html lang="en"><body><h1 id="topic">Topic</h1><img alt="diagram" src="x.png"></body></html>',
            encoding="utf-8",
        )
        self.assertEqual(validate_site(site), [])

    def test_rejects_missing_fragment(self) -> None:
        temporary, site = self.make_site()
        self.addCleanup(temporary.cleanup)
        (site / "index.html").write_text(
            '<html lang="en"><body><a href="#missing">Missing</a></body></html>',
            encoding="utf-8",
        )
        self.assertTrue(any("missing rendered fragment" in item for item in validate_site(site)))

    def test_rejects_duplicate_ids_and_missing_alt(self) -> None:
        temporary, site = self.make_site()
        self.addCleanup(temporary.cleanup)
        (site / "index.html").write_text(
            '<html lang="en"><body><h1 id="same">One</h1><h2 id="same">Two</h2><img src="x.png"></body></html>',
            encoding="utf-8",
        )
        errors = validate_site(site)
        self.assertTrue(any("duplicate id" in item for item in errors))
        self.assertTrue(any("missing alt attributes" in item for item in errors))

    def test_rejects_escape_and_missing_language(self) -> None:
        temporary, site = self.make_site()
        self.addCleanup(temporary.cleanup)
        (site / "index.html").write_text(
            '<html><body><a href="../outside.html">Outside</a></body></html>',
            encoding="utf-8",
        )
        errors = validate_site(site)
        self.assertTrue(any("missing a non-empty lang" in item for item in errors))
        self.assertTrue(any("escapes rendered site" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
