from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "constitutional-lifecycle-backup-restore-v1.json"
SCRIPT = ROOT / "scripts" / "check_constitutional_lifecycle_backup_restore.py"
EXPECTED_SHA256 = "1da592ac85a1880e7b3701860e5c360260622bf4ca36f8eb6c14693a7201a83b"

spec = importlib.util.spec_from_file_location("backup_restore_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class BackupRestoreContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.raw = FIXTURE.read_bytes()
        self.document, self.digest = validator.load_json_bytes(self.raw)

    def test_frozen_fixture_is_valid(self) -> None:
        self.assertEqual(EXPECTED_SHA256, self.digest)
        report = validator.validate_corpus(copy.deepcopy(self.document))
        self.assertEqual("PASS", report["status"])
        self.assertEqual(17, report["case_count"])

    def test_duplicate_key_is_rejected(self) -> None:
        with self.assertRaises(validator.ValidationError):
            validator.load_json_bytes(b'{"schema":"a","schema":"b"}')

    def test_non_finite_number_is_rejected(self) -> None:
        with self.assertRaises(validator.ValidationError):
            validator.load_json_bytes(b'{"value":NaN}')

    def test_invalid_utf8_is_rejected(self) -> None:
        with self.assertRaises(validator.ValidationError):
            validator.load_json_bytes(b"\xff")

    def test_unknown_root_field_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["unexpected"] = True
        with self.assertRaises(validator.ValidationError):
            validator.validate_corpus(document)

    def test_missing_case_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["cases"].pop()
        with self.assertRaises(validator.ValidationError):
            validator.validate_corpus(document)

    def test_non_boolean_manifest_flag_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["cases"][0]["backup"]["manifest_valid"] = 1
        with self.assertRaises(validator.ValidationError):
            validator.validate_corpus(document)

    def test_prohibited_secret_field_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["cases"][0]["backup"]["private_key"] = "synthetic"
        with self.assertRaises(validator.ValidationError):
            validator.validate_corpus(document)

    def test_disposition_drift_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["cases"][0]["expected"]["reason"] = "restore_log_gap"
        with self.assertRaises(validator.ValidationError):
            validator.validate_corpus(document)

    def test_duplicate_event_transaction_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        case = next(
            item for item in document["cases"]
            if item["case_id"] == "stale-backup-complete-log-converges"
        )
        case["restore"]["retained_events"].append(
            copy.deepcopy(case["restore"]["retained_events"][0])
        )
        with self.assertRaises(validator.ValidationError):
            validator.validate_corpus(document)

    def test_oversized_input_is_rejected(self) -> None:
        with self.assertRaises(validator.ValidationError):
            validator.load_json_bytes(b" " * (validator.MAX_BYTES + 1))


if __name__ == "__main__":
    unittest.main()
