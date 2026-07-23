from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_kernel_runtime_crosswalk_options import (
    EXPECTED_STATUS,
    GUIDE_PATH,
    load_profile,
    validate_guide,
    validate_profile,
)


class KernelRuntimeCrosswalkOptionsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = load_profile()

    def assert_rejected(self, mutator) -> None:
        candidate = copy.deepcopy(self.profile)
        mutator(candidate)
        self.assertTrue(validate_profile(candidate))

    def test_current_packet_passes(self) -> None:
        self.assertEqual([], validate_profile(self.profile))
        self.assertEqual([], validate_guide())

    def test_rejects_selected_status(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("status", "APPROVED"))

    def test_rejects_authority_effect(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("authority_effect", "runtime"))

    def test_rejects_removed_unsupported_route(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("safe_default", "read_only_projection_adapter"))

    def test_rejects_direct_alias_selection(self) -> None:
        def mutate(value):
            option = next(item for item in value["options"] if item["id"] == "D")
            option["selectable_now"] = True
            option["disposition"] = "SELECTED"
        self.assert_rejected(mutate)

    def test_rejects_projection_without_receipt(self) -> None:
        def mutate(value):
            option = next(item for item in value["options"] if item["id"] == "B")
            option["requires_projection_receipt"] = False
        self.assert_rejected(mutate)

    def test_rejects_missing_semantic_class(self) -> None:
        self.assert_rejected(lambda value: value["semantic_classes"].remove("projection_receipt"))

    def test_rejects_missing_kernel_field(self) -> None:
        self.assert_rejected(lambda value: value["kernel_fields"].remove("reason_codes"))

    def test_rejects_wrong_exact_head(self) -> None:
        def mutate(value):
            value["observed_generations"][0]["head"] = "0" * 40
        self.assert_rejected(mutate)

    def test_rejects_missing_acceptance_gate(self) -> None:
        self.assert_rejected(lambda value: value["acceptance_gates"].remove("EXPLICIT_HUMAN_APPROVAL"))

    def test_rejects_missing_rollback_receipt_field(self) -> None:
        self.assert_rejected(lambda value: value["projection_receipt_required_fields"].remove("rollback_target"))

    def test_rejects_duplicate_json_keys(self) -> None:
        raw = '{"profile_id":"one","profile_id":"two"}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_rejects_non_finite_json(self) -> None:
        raw = '{"value":NaN}'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_guide_status_is_unselected(self) -> None:
        text = GUIDE_PATH.read_text(encoding="utf-8")
        self.assertIn(EXPECTED_STATUS, text)
        self.assertIn("No crosswalk option is selected", text)


if __name__ == "__main__":
    unittest.main()
