from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_portfolio_authority_currentness_rebind.py"
SPEC = importlib.util.spec_from_file_location("currentness_rebind_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PortfolioAuthorityCurrentnessRebindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.profile = validator.load_profile(
            ROOT / "docs" / "portfolio-authority-currentness-rebind-v1.json"
        )

    def test_repository_packet_passes(self) -> None:
        report = validator.validate_repository(ROOT)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["rebind_count"], 4)
        self.assertEqual(report["authority_effect"], "NONE")

    def test_duplicate_rebind_repository_rejected(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["rebindings"].append(copy.deepcopy(profile["rebindings"][0]))
        with self.assertRaisesRegex(validator.ValidationError, "exactly four"):
            validator.validate_profile(profile)

    def test_equal_previous_and_new_sha_rejected(self) -> None:
        profile = copy.deepcopy(self.profile)
        profile["rebindings"][0]["new_sha"] = profile["rebindings"][0]["previous_sha"]
        with self.assertRaisesRegex(validator.ValidationError, "must differ"):
            validator.validate_profile(profile)

    def test_self_referential_source_role_rejected(self) -> None:
        profile = copy.deepcopy(self.profile)
        alistaire = next(
            entry for entry in profile["rebindings"]
            if entry["repository"] == "aevespers2/ALISTAIRE-"
        )
        alistaire["source_role"] = "future_resulting_generation"
        with self.assertRaisesRegex(validator.ValidationError, "existing parent"):
            validator.validate_profile(profile)

    def test_seeker_historical_mismatch_cannot_be_erased(self) -> None:
        profile = copy.deepcopy(self.profile)
        seeker = next(
            entry for entry in profile["rebindings"]
            if entry["repository"] == "aevespers2/QSO-SEEKER"
        )
        seeker["previous_body_declared_sha"] = seeker["previous_sha"]
        with self.assertRaisesRegex(validator.ValidationError, "mismatch witness erased"):
            validator.validate_profile(profile)

    def test_seeker_current_body_must_match_current_head(self) -> None:
        profile = copy.deepcopy(self.profile)
        seeker = next(
            entry for entry in profile["rebindings"]
            if entry["repository"] == "aevespers2/QSO-SEEKER"
        )
        seeker["current_body_declared_sha"] = seeker["previous_sha"]
        with self.assertRaisesRegex(validator.ValidationError, "body/head agreement"):
            validator.validate_profile(profile)

    def test_justice_resulting_validation_cannot_be_promoted(self) -> None:
        profile = copy.deepcopy(self.profile)
        justice = next(
            entry for entry in profile["rebindings"]
            if entry["repository"] == "aevespers2/JusticeForMe"
        )
        justice["evidence"]["resulting_validation"] = "PASS"
        with self.assertRaisesRegex(validator.ValidationError, "must not be promoted"):
            validator.validate_profile(profile)

    def test_authority_promotion_rejected(self) -> None:
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

    def test_non_standard_number_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(validator.ValidationError, "non-standard numeric"):
                validator.load_profile(path)

    def test_missing_prose_equivalent_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            self._copy_required_repository(temporary_root)
            guide = temporary_root / "docs" / "portfolio-authority-currentness-rebind.md"
            guide.write_text(
                guide.read_text(encoding="utf-8").replace(
                    "### Prose equivalent", "### Diagram notes"
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(validator.ValidationError, "Prose equivalent"):
                validator.validate_repository(temporary_root)

    def test_workflow_cancellation_or_credentials_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            temporary_root = Path(directory)
            self._copy_required_repository(temporary_root)
            workflow = temporary_root / ".github" / "workflows" / "portfolio-authority-currentness-rebind.yml"
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
            "docs/portfolio-authority-currentness-rebind-v1.json",
            "docs/portfolio-authority-currentness-rebind.md",
            "mkdocs.yml",
            "taskchain.md",
            "punchlist.md",
            "release.md",
            "changelog.md",
            ".github/workflows/portfolio-authority-currentness-rebind.yml",
        ]
        for relative in paths:
            source = ROOT / relative
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())


if __name__ == "__main__":
    unittest.main()
