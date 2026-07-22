from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_constitutional_lifecycle_snapshot_compaction.py"
CORPUS = ROOT / "fixtures" / "constitutional-lifecycle-snapshot-compaction-v1.json"

spec = importlib.util.spec_from_file_location("snapshot_compaction", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SnapshotCompactionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CORPUS.read_bytes()
        cls.data = json.loads(cls.raw)

    def mutate(self, mutator) -> bytes:
        data = copy.deepcopy(self.data)
        mutator(data)
        return (json.dumps(data, indent=2) + "\n").encode("utf-8")

    def case(self, case_id: str):
        return next(item for item in self.data["cases"] if item["case_id"] == case_id)

    def test_canonical_corpus_passes(self) -> None:
        report = module.validate_bytes(self.raw)
        self.assertEqual(report["case_count"], 15)
        self.assertEqual(report["status"], "synthetic_only_non_operational")
        self.assertFalse(report["grants_authority"])
        self.assertFalse(report["mutates_state"])

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

    def test_unknown_fields_are_rejected(self) -> None:
        raw = self.mutate(lambda data: data["cases"][0].update({"authority": True}))
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_missing_and_duplicate_cases_are_rejected(self) -> None:
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(lambda data: data["cases"].pop()))
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(
                self.mutate(lambda data: data["cases"].append(copy.deepcopy(data["cases"][0])))
            )

    def test_non_boolean_snapshot_digest_is_rejected(self) -> None:
        raw = self.mutate(
            lambda data: data["cases"][0]["snapshot"].update({"digest_valid": 1})
        )
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_prohibited_secret_fields_are_rejected(self) -> None:
        raw = self.mutate(
            lambda data: data["cases"][0]["snapshot"].update({"private_key": "synthetic"})
        )
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_expected_state_drift_is_rejected(self) -> None:
        def mutate(data):
            case = next(item for item in data["cases"] if item["case_id"] == "healthy-compaction")
            case["expected"]["state"]["authority_generation"] += 1
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(mutate))

    def test_torn_snapshot_paths_are_bounded(self) -> None:
        replayed = module.derive_case(self.case("torn-snapshot-full-log-replay"))
        blocked = module.derive_case(self.case("torn-snapshot-after-prune-quarantined"))
        self.assertEqual(replayed[0:2], ("converged", "full_log_replay"))
        self.assertEqual(
            blocked[0:2],
            ("quarantined", "snapshot_unrecoverable_after_prune"),
        )

    def test_snapshot_divergence_and_sequence_gap_quarantine(self) -> None:
        divergence = module.derive_case(self.case("snapshot-log-divergence-quarantined"))
        gap = module.derive_case(self.case("log-sequence-gap-quarantined"))
        self.assertEqual(divergence[1], "snapshot_log_divergence")
        self.assertEqual(gap[1], "journal_sequence_gap")

    def test_duplicate_commits_are_idempotent_only_when_identical(self) -> None:
        accepted = module.derive_case(self.case("duplicate-commit-idempotent"))
        blocked = module.derive_case(self.case("conflicting-duplicate-commit-quarantined"))
        self.assertEqual(accepted[1], "duplicate_commit_idempotent")
        self.assertEqual(blocked[1], "conflicting_duplicate_transaction")

    def test_suspension_and_revocation_survive_compaction(self) -> None:
        suspension = module.derive_case(self.case("suspension-survives-compaction"))
        revocation = module.derive_case(self.case("revocation-survives-compaction"))
        self.assertEqual(suspension[2]["status"], "suspended")
        self.assertIn(
            suspension[2]["authority_generation"],
            suspension[2]["suspended_generations"],
        )
        self.assertEqual(revocation[2]["status"], "revoked")
        self.assertIn(
            revocation[2]["authority_generation"],
            revocation[2]["revoked_generations"],
        )

    def test_revoked_authority_cannot_be_resurrected(self) -> None:
        outcome = module.derive_case(
            self.case("replacement-cannot-resurrect-revoked-authority")
        )
        self.assertEqual(
            outcome[0:2],
            ("quarantined", "superseded_authority_resurrection_blocked"),
        )

    def test_lost_and_late_acknowledgments_converge_safely(self) -> None:
        pending = module.derive_case(self.case("lost-ack-preserves-pending-state"))
        completed = module.derive_case(
            self.case("acknowledgment-after-compaction-converges")
        )
        self.assertEqual(pending[2]["status"], "pending_ack")
        self.assertIsNotNone(pending[2]["pending_ack_transaction"])
        self.assertEqual(completed[2]["status"], "active")
        self.assertIsNone(completed[2]["pending_ack_transaction"])


if __name__ == "__main__":
    unittest.main()
