from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_constitutional_lifecycle_restore_staging_multicopy.py"
FIXTURE = ROOT / "fixtures" / "constitutional-lifecycle-restore-staging-multicopy-v1.json"
EXPECTED_SHA256 = "812f1e5580caa687d30e96e9efed8214d47a131337f82577cfcaa1c27d1e46a2"

SPEC = importlib.util.spec_from_file_location("restore_multicopy", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RestoreStagingMultiCopyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FIXTURE.read_bytes()
        cls.corpus, cls.digest = MODULE.load_json_bytes(cls.raw)

    def validate(self, corpus: dict) -> dict:
        return MODULE.validate_corpus(copy.deepcopy(corpus))

    def test_frozen_fixture_digest_and_full_corpus(self) -> None:
        report = MODULE.validate_bytes(self.raw, EXPECTED_SHA256)
        self.assertEqual(report["case_count"], 17)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["authority_effect"], "none")

    def test_digest_mismatch_fails(self) -> None:
        with self.assertRaises(MODULE.ValidationError):
            MODULE.validate_bytes(self.raw, "0" * 64)

    def test_duplicate_json_key_fails(self) -> None:
        with self.assertRaises(MODULE.ValidationError):
            MODULE.load_json_bytes(b'{"schema":"a","schema":"b"}')

    def test_non_finite_number_fails(self) -> None:
        with self.assertRaises(MODULE.ValidationError):
            MODULE.load_json_bytes(b'{"value":NaN}')

    def test_invalid_utf8_fails(self) -> None:
        with self.assertRaises(MODULE.ValidationError):
            MODULE.load_json_bytes(b"\xff")

    def test_unknown_root_field_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["authority"] = "granted"
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_duplicate_case_id_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][1]["case_id"] = corpus["cases"][0]["case_id"]
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_duplicate_copy_id_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][0]["copies"][1]["copy_id"] = corpus["cases"][0]["copies"][0]["copy_id"]
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_non_boolean_availability_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][0]["copies"][0]["available"] = 1
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_selected_copy_duplicates_fail(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][0]["request"]["selected_copy_ids"] = ["copy-a", "copy-a"]
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_quorum_larger_than_selection_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][0]["request"]["minimum_quorum"] = 4
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_retry_without_reference_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        case = next(item for item in corpus["cases"] if item["case_id"] == "retry-after-commit-idempotent")
        case["request"]["retry_of"] = None
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_expected_disposition_drift_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][0]["expected"]["reason"] = "restore_copy_conflict"
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)

    def test_prohibited_secret_field_fails(self) -> None:
        corpus = copy.deepcopy(self.corpus)
        corpus["cases"][0]["copies"][0]["state"]["private_key"] = "synthetic"
        with self.assertRaises(MODULE.ValidationError):
            self.validate(corpus)


if __name__ == "__main__":
    unittest.main()
