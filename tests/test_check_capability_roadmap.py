from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_capability_roadmap.py"
SPEC = importlib.util.spec_from_file_location("capability_roadmap", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CapabilityRoadmapTests(unittest.TestCase):
    def make_copy(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for relative in (
            "README.md",
            "mkdocs.yml",
            "changelog.md",
            "docs/index.md",
            "docs/name-and-identity.md",
            "docs/capability-roadmap.md",
            "docs/capability-roadmap-v1.json",
        ):
            source = ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        return temporary, root

    def load_profile(self, root: Path) -> dict:
        return json.loads((root / MODULE.PROFILE_PATH).read_text(encoding="utf-8"))

    def write_profile(self, root: Path, profile: dict) -> None:
        (root / MODULE.PROFILE_PATH).write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")

    def assert_rejected(self, root: Path, phrase: str) -> None:
        with self.assertRaisesRegex(ValueError, phrase):
            MODULE.validate_repository(root)

    def test_current_repository_passes(self) -> None:
        report = MODULE.validate_repository(ROOT)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["feature_count"], 37)

    def test_duplicate_json_key_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        path = root / MODULE.PROFILE_PATH
        raw = path.read_text(encoding="utf-8").replace(
            '"authority_effect": "none",',
            '"authority_effect": "none",\n  "authority_effect": "operational",',
            1,
        )
        path.write_text(raw, encoding="utf-8")
        self.assert_rejected(root, "duplicate JSON key")

    def test_name_expansion_drift_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["name_source"]["expansion"] = "substituted"
        self.write_profile(root, profile)
        self.assert_rejected(root, "name expansion drift")

    def test_authority_inflation_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["authority_effect"] = "operational"
        self.write_profile(root, profile)
        self.assert_rejected(root, "authority_effect must remain none")

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

    def test_r5_authority_inflation_is_rejected(self) -> None:
        temporary, root = self.make_copy()
        self.addCleanup(temporary.cleanup)
        profile = self.load_profile(root)
        profile["roadmap_stages"][-1]["status"] = "approved"
        self.write_profile(root, profile)
        self.assert_rejected(root, "R5 must remain separately prohibited")

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
        path.write_text(path.read_text(encoding="utf-8").replace(MODULE.EXPECTED_STATUS, "REMOVED"), encoding="utf-8")
        self.assert_rejected(root, "README.md is missing required phrase")


if __name__ == "__main__":
    unittest.main()
