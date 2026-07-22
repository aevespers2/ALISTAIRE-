from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_constitutional_appointment_lifecycle.py"
CORPUS = ROOT / "fixtures" / "constitutional-appointment-lifecycle-v1.json"

spec = importlib.util.spec_from_file_location("appointment_lifecycle", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class AppointmentLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = CORPUS.read_bytes()
        cls.data = json.loads(cls.raw)

    def mutate(self, mutator) -> bytes:
        data = copy.deepcopy(self.data)
        mutator(data)
        return (json.dumps(data, indent=2) + "\n").encode("utf-8")

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

    def test_non_boolean_control_is_rejected(self) -> None:
        raw = self.mutate(
            lambda data: data["cases"][0]["controls"].update(
                {"nomination_recorded": "true"}
            )
        )
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_missing_case_is_rejected(self) -> None:
        raw = self.mutate(lambda data: data["cases"].pop())
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_duplicate_case_is_rejected(self) -> None:
        raw = self.mutate(lambda data: data["cases"].append(data["cases"][0]))
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(raw)

    def test_out_of_order_events_are_rejected(self) -> None:
        def mutate(data):
            data["cases"][4]["events"][1]["sequence"] = 1
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(mutate))

    def test_event_control_mismatch_is_rejected(self) -> None:
        def mutate(data):
            data["cases"][4]["controls"]["propagation_acknowledged"] = False
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(mutate))

    def test_expected_disposition_drift_is_rejected(self) -> None:
        def mutate(data):
            data["cases"][4]["expected_state"] = "inactive_record"
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(mutate))

    def test_prohibited_secret_bearing_field_is_rejected(self) -> None:
        def mutate(data):
            data["cases"][0]["credential_value"] = "synthetic"
        with self.assertRaises(module.ValidationError):
            module.validate_bytes(self.mutate(mutate))

    def test_deputy_without_vacancy_fails_closed(self) -> None:
        case = next(
            case for case in self.data["cases"]
            if case["case_id"] == "deputy-without-vacancy"
        )
        self.assertEqual(
            module.derive_outcome(case["controls"]),
            ("inactive_record", "deputy_without_vacancy", "none"),
        )

    def test_rollback_restores_without_new_authority(self) -> None:
        case = next(
            case for case in self.data["cases"]
            if case["case_id"] == "rollback-to-prior-verified-state"
        )
        self.assertEqual(
            module.derive_outcome(case["controls"]),
            ("rolled_back", "rollback_complete", "restoration_only"),
        )


if __name__ == "__main__":
    unittest.main()
