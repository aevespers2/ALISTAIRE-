from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_runtime_fabric_namespace_partition import (
    DEFAULT_PACKET,
    load_packet,
    validate_packet,
)


class RuntimeFabricNamespacePartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = load_packet(DEFAULT_PACKET)

    def assert_rejected(self, mutate) -> None:
        candidate = copy.deepcopy(self.packet)
        mutate(candidate)
        with self.assertRaises(ValueError):
            validate_packet(candidate, DEFAULT_PACKET)

    def test_reference_packet_passes(self) -> None:
        report = validate_packet(
            copy.deepcopy(self.packet),
            DEFAULT_PACKET,
            "a" * 40,
        )
        self.assertEqual(
            report["disposition"],
            "RUNTIME_FABRIC_PARTITION_VALIDATED_NON_AUTHORIZING",
        )
        self.assertEqual(report["semantic_class_count"], 6)
        self.assertEqual(report["candidate_profile_count"], 3)
        self.assertEqual(report["witness_count"], 3)

    def test_status_cannot_be_promoted(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("status", "APPROVED"))

    def test_authority_effect_cannot_be_promoted(self) -> None:
        self.assert_rejected(
            lambda value: value.__setitem__("authority_effect", "RUNTIME_AUTHORITY")
        )

    def test_profile_cannot_be_selected(self) -> None:
        self.assert_rejected(
            lambda value: value["candidate_profiles"][0].__setitem__("selected", True)
        )

    def test_semantic_class_cannot_be_removed(self) -> None:
        self.assert_rejected(lambda value: value["required_semantic_classes"].pop())

    def test_runtime_class_cannot_gain_authority(self) -> None:
        self.assert_rejected(
            lambda value: value["required_semantic_classes"][0].__setitem__(
                "authority_effect", "APPROVAL"
            )
        )

    def test_mandatory_field_cannot_be_removed(self) -> None:
        self.assert_rejected(lambda value: value["mandatory_fields"].remove("source_set_digest"))

    def test_projection_invariant_cannot_be_removed(self) -> None:
        self.assert_rejected(
            lambda value: value["invariants"].remove(
                "projection_is_not_independent_evidence"
            )
        )

    def test_triple_overlap_witness_cannot_be_removed(self) -> None:
        self.assert_rejected(lambda value: value["required_witnesses"].pop())

    def test_review_gate_cannot_be_removed(self) -> None:
        self.assert_rejected(
            lambda value: value["review_gates"].remove("EXPLICIT_HUMAN_APPROVAL")
        )

    def test_prohibited_promotion_cannot_be_removed(self) -> None:
        self.assert_rejected(
            lambda value: value["prohibited_promotions"].remove("deployment")
        )

    def test_skill_gap_cannot_become_authoritative(self) -> None:
        self.assert_rejected(
            lambda value: value["fysa_120"]["proposed_gap"].__setitem__(
                "authoritative", True
            )
        )

    def test_submitted_sha_must_be_exact(self) -> None:
        with self.assertRaises(ValueError):
            validate_packet(copy.deepcopy(self.packet), DEFAULT_PACKET, "not-a-sha")

    def test_duplicate_json_keys_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"profile_id":"a","profile_id":"b"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_packet(path)

    def test_nonfinite_json_number_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nonfinite.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_packet(path)

    def test_invalid_utf8_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_bytes(b'{"value":"\xff"}')
            with self.assertRaises(UnicodeDecodeError):
                load_packet(path)

    def test_unknown_top_level_field_fails_closed(self) -> None:
        self.assert_rejected(lambda value: value.__setitem__("implementation_authority", True))

    def test_packet_is_strict_json(self) -> None:
        raw = DEFAULT_PACKET.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        self.assertEqual(parsed["profile_id"], self.packet["profile_id"])


if __name__ == "__main__":
    unittest.main()
