from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_portfolio_authority_currentness.py"
SPEC = importlib.util.spec_from_file_location("currentness_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PortfolioAuthorityCurrentnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = validator.load_profile(
            ROOT / "docs" / "portfolio-authority-currentness-v1.json"
        )

    def test_repository_packet_passes(self) -> None:
        report = validator.validate_repository(ROOT)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["repository_count"], 19)
        self.assertEqual(report["authority_effect"], "NONE")

    def test_duplicate_repository_rejected(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["repositories"].append(copy.deepcopy(profile["repositories"][0]))
        with self.assertRaisesRegex(validator.ValidationError, "exactly 19"):
            validator.validate_profile(profile)

    def test_authority_promotion_rejected(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["authority_effect"] = "OWNER_APPOINTED"
        with self.assertRaisesRegex(validator.ValidationError, "authority effect"):
            validator.validate_profile(profile)

    def test_invalid_sha_rejected(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["repositories"][0]["primary_source"]["sha"] = "abc"
        with self.assertRaisesRegex(validator.ValidationError, "invalid exact SHA"):
            validator.validate_profile(profile)

    def test_seeker_mismatch_cannot_be_erased(self) -> None:
        profile = copy.deepcopy(self.profile)
        seeker = next(
            entry
            for entry in profile["repositories"]
            if entry["repository"] == "aevespers2/QSO-SEEKER"
        )
        seeker["body_declared_sha"] = seeker["primary_source"]["sha"]
        with self.assertRaisesRegex(validator.ValidationError, "mismatch witness"):
            validator.validate_profile(profile)

    def test_temporal_missing_workflow_obstruction_required(self) -> None:
        profile = copy.deepcopy(self.profile)
        temporal = next(
            entry
            for entry in profile["repositories"]
            if entry["repository"] == "aevespers2/datarepo-temporal-invariants"
        )
        temporal["conflicts"] = ["overlap only"]
        with self.assertRaisesRegex(validator.ValidationError, "missing-workflow"):
            validator.validate_profile(profile)

    def test_all_operational_authority_flags_must_remain_false(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["safety_boundaries"]["pages_publication"] = True
        with self.assertRaisesRegex(validator.ValidationError, "operational authority"):
            validator.validate_profile(profile)

    def test_duplicate_json_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text('{"profile_id":"a","profile_id":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "duplicate JSON key"):
                validator.load_profile(path)

    def test_non_finite_json_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "non-standard numeric"):
                validator.load_profile(path)

    def test_missing_prose_equivalent_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            self._copy_required_repository(temporary_root)
            guide = temporary_root / "docs" / "portfolio-authority-currentness-review.md"
            guide.write_text(
                guide.read_text(encoding="utf-8").replace("### Prose equivalent", "### Diagram notes"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(validator.ValidationError, "Prose equivalent"):
                validator.validate_repository(temporary_root)

    def test_workflow_cancellation_or_credentials_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            self._copy_required_repository(temporary_root)
            workflow = temporary_root / ".github" / "workflows" / "portfolio-authority-currentness.yml"
            workflow.write_text(
                workflow.read_text(encoding="utf-8")
                .replace("cancel-in-progress: false", "cancel-in-progress: true")
                .replace("persist-credentials: false", "persist-credentials: true"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(validator.ValidationError, "workflow control"):
                validator.validate_repository(temporary_root)

    @staticmethod
    def _copy_required_repository(destination: Path) -> None:
        paths = [
            "docs/portfolio-authority-currentness-v1.json",
            "docs/portfolio-authority-currentness-review.md",
            "mkdocs.yml",
            "taskchain.md",
            "punchlist.md",
            "release.md",
            "changelog.md",
            ".github/workflows/portfolio-authority-currentness.yml",
        ]
        for relative in paths:
            source = ROOT / relative
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())


if __name__ == "__main__":
    unittest.main()
