from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_runtime_fabric_governance_review_index import (
    GUIDE_PATH,
    REJECTED_OPTION,
    SAFE_DEFAULT,
    STATUS,
    load_profile,
    validate_guide,
    validate_profile,
)


class RuntimeFabricGovernanceReviewIndexTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile = load_profile()

    def assert_rejected(self, mutator) -> None:
        candidate = copy.deepcopy(self.profile)
        mutator(candidate)
        self.assertTrue(validate_profile(candidate))

    def test_current_profile_and_guide_pass(self) -> None:
        self.assertEqual([], validate_profile(self.profile))
        self.assertEqual([], validate_guide())

    def test_rejects_authority_promotion(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("authority_effect", "runtime"))

    def test_rejects_selected_binding_status(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("status", "ACCEPTED"))

    def test_rejects_unsupported_route_removal(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("safe_default", "READ_ONLY_ADAPTER"))

    def test_rejects_direct_alias_reclassification(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("rejected_option", "SELECT_DIRECT_ALIAS"))

    def test_rejects_source_head_drift(self) -> None:
        self.assert_rejected(
            lambda value: value["source_generation"].__setitem__("head_sha", "0" * 40)
        )

    def test_rejects_route_reordering(self) -> None:
        self.assert_rejected(lambda value: value["route"].reverse())

    def test_rejects_missing_review_surface(self) -> None:
        self.assert_rejected(lambda value: value["review_surfaces"].pop())

    def test_rejects_review_surface_disposition_drift(self) -> None:
        self.assert_rejected(
            lambda value: value["review_surfaces"][0].__setitem__("disposition", "RESOLVED")
        )

    def test_rejects_missing_semantic_class(self) -> None:
        self.assert_rejected(
            lambda value: value["semantic_classes"].remove("fabric_projection_receipt")
        )

    def test_rejects_missing_obstruction(self) -> None:
        self.assert_rejected(
            lambda value: value["material_obstructions"].remove("authority_inflation")
        )

    def test_rejects_reordered_review_sequence(self) -> None:
        def mutate(value):
            value["review_sequence"][0], value["review_sequence"][1] = (
                value["review_sequence"][1],
                value["review_sequence"][0],
            )
        self.assert_rejected(mutate)

    def test_rejects_missing_planning_route(self) -> None:
        self.assert_rejected(
            lambda value: value["controlled_planning_routes"].remove("changelog.md")
        )

    def test_rejects_missing_invariant(self) -> None:
        self.assert_rejected(
            lambda value: value["invariants"].remove("authority_effect_remains_none")
        )

    def test_rejects_missing_prohibited_promotion(self) -> None:
        self.assert_rejected(
            lambda value: value["prohibited_promotions"].remove("deployment")
        )

    def test_rejects_skill_gap_authority(self) -> None:
        self.assert_rejected(
            lambda value: value["fysa_120"]["proposed_gap"].__setitem__("authoritative", True)
        )

    def test_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text('{"profile_id":"one","profile_id":"two"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_rejects_non_finite_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_profile(path)

    def test_guide_preserves_safe_disposition(self) -> None:
        text = GUIDE_PATH.read_text(encoding="utf-8")
        self.assertIn(STATUS, text)
        self.assertIn(SAFE_DEFAULT, text)
        self.assertIn(REJECTED_OPTION, text)
        self.assertIn("### Prose equivalent", text)


if __name__ == "__main__":
    unittest.main()
