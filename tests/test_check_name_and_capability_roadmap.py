from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_name_and_capability_roadmap.py"
SPEC = importlib.util.spec_from_file_location("name_capability_roadmap", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NameCapabilityRoadmapTests(unittest.TestCase):
    def make_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for relative in (
            "README.md",
            "mkdocs.yml",
            "changelog.md",
            "docs/index.md",
            "docs/name-and-capability-roadmap.md",
            "docs/name-and-capability-roadmap-v1.json",
        ):
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temporary, root

    def load_profile(self, root: Path) -> dict:
        return json.loads((root / MODULE.PROFILE_PATH).read_text(encoding="utf-8"))

    def write_profile(self, root: Path, profile: dict) -> None:
        (root / MODULE.PROFILE_PATH).write_text(
            json.dumps(profile, indent=2, sort_keys=False) + "\n",
            encoding="utf-8",
        )

    def assert_rejected(self, root: Path, phrase: str) -> None:
        with self.assertRaisesRegex(ValueError, phrase):
            MODULE.validate_repository(root)

    def test_current_repository_passes(self) -> None:
        report = MODULE.validate_repository(ROOT)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["feature_count"], 37)
        self.assertEqual(report["family_count"], 6)

    def test_duplicate_json_key_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / MODULE.PROFILE_PATH
        raw = path.read_text(encoding="utf-8")
        raw = raw.replace(
            '"status": "DOCUMENTED_NAME_EXPANSION_AND_CAPABILITY_ROADMAP_UNACCEPTED",',
            '"status": "DOCUMENTED_NAME_EXPANSION_AND_CAPABILITY_ROADMAP_UNACCEPTED",\n  "status": "accepted",',
            1,
        )
        path.write_text(raw, encoding="utf-8")
        self.assert_rejected(root, "duplicate JSON key")

    def test_authority_inflation_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["authority_effect"] = "operational"
        self.write_profile(root, profile)
        self.assert_rejected(root, "authority_effect must remain none")

    def test_acronym_substitution_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["name"]["terms"][4]["letter"] = "X"
        self.write_profile(root, profile)
        self.assert_rejected(root, "must spell ALISTAIRE")

    def test_feature_removal_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["capability_families"][0]["features"].pop()
        self.write_profile(root, profile)
        self.assert_rejected(root, "expected 37 features")

    def test_ownerless_feature_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["capability_families"][0]["features"][0]["owner_candidates"] = []
        self.write_profile(root, profile)
        self.assert_rejected(root, "owner_candidates must be a non-empty list")

    def test_missing_prohibited_promotion_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["prohibited_promotions"].pop()
        self.write_profile(root, profile)
        self.assert_rejected(root, "prohibited authority promotions changed")

    def test_destructive_rollback_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["rollback"]["destructive_history_rewrite"] = True
        self.write_profile(root, profile)
        self.assert_rejected(root, "destructive history rewrite must remain false")

    def test_cross_document_status_drift_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(MODULE.EXPECTED_STATUS, "STATUS_REMOVED"),
            encoding="utf-8",
        )
        self.assert_rejected(root, "README.md is missing required phrase")


if __name__ == "__main__":
    unittest.main()
