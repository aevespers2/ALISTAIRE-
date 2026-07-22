from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_constitutional_lifecycle_transaction_journal.py"
CORPUS = ROOT / "fixtures" / "constitutional-lifecycle-transaction-journal-v1.json"

spec = importlib.util.spec_from_file_location("constitutional_journal", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConstitutionalLifecycleJournalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CORPUS.read_bytes()
        cls.data = json.loads(cls.raw)

    def mutate(self, mutator) -> bytes:
        data = copy.deepcopy(self.data)
        mutator(data)
        return (json.dumps(data, indent=2) + "\n").encode("utf-8")

    def case(self, case_id: str):
        return next(case for case in self.data["cases"] if case["case_id"] == case_id)

    def test_canonical_corpus_passes(self) -> None:
        result = module.validate_bytes(self.raw)
        self.assertEqual(result["cases"], 15)
        self.assertEqual(result["status"], "synthetic_only_non_operational")

    def test_duplicate_keys_are_rejected(self) -> None:
        raw = self.raw.replace(
            b'"profile_version": "1.0.0",',
            b'"profile_version": "1.0.0",\n  "profile_version": "1.0.0",',
            1,
        )
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_non_finite_numbers_are_rejected(self) -> None:
        raw = self.raw.replace(b'"cases": [', b'"unexpected": NaN,\n  "cases": [', 1)
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_invalid_utf8_is_rejected(self) -> None:
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.raw + b"\xff")

    def test_unknown_case_field_is_rejected(self) -> None:
        raw = self.mutate(lambda data: data["cases"][0].update({"authority": True}))
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_missing_and_duplicate_cases_are_rejected(self) -> None:
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(lambda data: data["cases"].pop()))
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(
                self.mutate(lambda data: data["cases"].append(data["cases"][0]))
            )

    def test_unknown_operation_is_rejected(self) -> None:
        raw = self.mutate(lambda data: data["cases"][0].update({"operation": "appoint"}))
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_prohibited_secret_bearing_field_is_rejected(self) -> None:
        raw = self.mutate(
            lambda data: data["cases"][0].update({"private_key": "synthetic"})
        )
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_expected_disposition_drift_is_rejected(self) -> None:
        raw = self.mutate(
            lambda data: data["cases"][0].update({"expected_state": "active"})
        )
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_concurrent_replacement_fails_closed(self) -> None:
        outcome = module.derive_outcome(self.case("concurrent-replacement-conflict"))
        self.assertEqual(
            outcome,
            ("active", "concurrent_replacement_conflict",
             "synthetic_bounded_active", 4, 7),
        )

    def test_suspension_precedes_concurrent_appeal(self) -> None:
        outcome = module.derive_outcome(self.case("suspension-wins-over-appeal-race"))
        self.assertEqual(
            outcome,
            ("suspended_appeal_pending", "suspension_precedence", "none", 8, 2),
        )

    def test_late_and_replayed_acknowledgments_are_bounded(self) -> None:
        late = module.derive_outcome(self.case("late-ack-after-generation-change"))
        replay = module.derive_outcome(self.case("replayed-acknowledgment-idempotent"))
        self.assertEqual(late[1], "stale_ack_rejected")
        self.assertEqual(replay[1], "acknowledgment_idempotent")

    def test_interrupted_rollback_preserves_or_recovers_deterministically(self) -> None:
        before = module.derive_outcome(self.case("rollback-interrupted-before-commit"))
        prepared = module.derive_outcome(self.case("rollback-interrupted-after-prepare"))
        committed = module.derive_outcome(self.case("rollback-committed-before-ack"))
        recovered = module.derive_outcome(
            self.case("recovery-preserves-committed-rollback")
        )
        self.assertEqual(before[3], 7)
        self.assertEqual(prepared[3], 7)
        self.assertEqual(committed[3], 6)
        self.assertEqual(recovered[3], 6)
        self.assertEqual(committed[0], "rolled_back_pending_ack")
        self.assertEqual(recovered[0], "rolled_back_pending_ack")

    def test_corruption_gap_and_duplicate_transactions_quarantine(self) -> None:
        ids = (
            "corrupted-journal-quarantined",
            "journal-sequence-gap-quarantined",
            "duplicate-transaction-id-quarantined",
        )
        for case_id in ids:
            with self.subTest(case_id=case_id):
                self.assertEqual(module.derive_outcome(self.case(case_id))[0], "quarantined")


if __name__ == "__main__":
    unittest.main()
