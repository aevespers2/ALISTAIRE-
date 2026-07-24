from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.check_capability_lifecycle_coherence import (
    EXPECTED_SOURCE_HEAD,
    LIFECYCLE_ROUTES,
    PROFILE_PATH,
    validate_repository,
)


class CapabilityLifecycleCoherenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name) / "repo"
        source_root = Path(__file__).resolve().parents[1]
        shutil.copytree(source_root, self.root, ignore=shutil.ignore_patterns(".git", "site", ".venv", "__pycache__"))

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def load_profile(self) -> dict:
        return json.loads((self.root / PROFILE_PATH).read_text(encoding="utf-8"))

    def save_profile(self, profile: dict) -> None:
        (self.root / PROFILE_PATH).write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")

    def assert_invalid(self, fragment: str) -> None:
        with self.assertRaisesRegex(ValueError, fragment):
            validate_repository(self.root)

    def test_baseline_passes(self) -> None:
        report = validate_repository(self.root)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["source_head"], EXPECTED_SOURCE_HEAD)
        self.assertEqual(report["lifecycle_route_count"], len(LIFECYCLE_ROUTES))

    def test_missing_status_in_release_fails(self) -> None:
        path = self.root / "release.md"
        text = path.read_text(encoding="utf-8").replace(
            "CAPABILITY_AND_CONTRIBUTOR_ROUTES_SYNCHRONIZED_BINDINGS_UNACCEPTED",
            "CAPABILITY_ROUTE_STATUS_REMOVED",
        )
        path.write_text(text, encoding="utf-8")
        self.assert_invalid("release.md is missing required phrase")

    def test_source_head_substitution_fails(self) -> None:
        profile = self.load_profile()
        profile["source_generation"]["head"] = "0" * 40
        self.save_profile(profile)
        self.assert_invalid("source head substitution")

    def test_authority_inflation_fails(self) -> None:
        profile = self.load_profile()
        profile["authority_flags"]["implementation_authorized"] = True
        self.save_profile(profile)
        self.assert_invalid("all authority flags must remain false")

    def test_destructive_history_rewrite_fails(self) -> None:
        profile = self.load_profile()
        profile["rollback"]["destructive_history_rewrite"] = True
        self.save_profile(profile)
        self.assert_invalid("destructive history rewrite must remain false")

    def test_missing_lifecycle_route_fails(self) -> None:
        profile = self.load_profile()
        profile["lifecycle_routes"].remove("changelog.md")
        self.save_profile(profile)
        self.assert_invalid("lifecycle route set changed")

    def test_duplicate_json_key_fails(self) -> None:
        path = self.root / PROFILE_PATH
        raw = path.read_text(encoding="utf-8")
        raw = raw.replace(
            '"version": "1.0.0",',
            '"version": "1.0.0",\n  "version": "1.0.0",',
            1,
        )
        path.write_text(raw, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            validate_repository(self.root)

    def test_operational_effect_promotion_fails(self) -> None:
        profile = self.load_profile()
        profile["repaired_obstruction"]["operational_effect"] = "enabled"
        self.save_profile(profile)
        self.assert_invalid("repair must have no operational effect")


if __name__ == "__main__":
    unittest.main()
