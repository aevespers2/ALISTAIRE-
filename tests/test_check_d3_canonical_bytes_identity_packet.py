from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_d3_canonical_bytes_identity_packet.py"
spec = importlib.util.spec_from_file_location("d3_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class D3CanonicalBytesPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = validator.load_packet(Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json"))

    def mutate(self):
        return copy.deepcopy(self.packet)

    def assertRejected(self, packet):
        with self.assertRaises(ValueError):
            validator.validate_packet(packet, Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json"), "1" * 40)

    def test_current_packet_passes(self):
        report = validator.validate_packet(
            self.mutate(),
            Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json"),
            "1" * 40,
        )
        self.assertEqual(report["disposition"], "D3_DECISION_READINESS_VALIDATED_NON_AUTHORIZING")
        self.assertEqual(report["candidate_profile_count"], 3)
        self.assertEqual(report["hostile_fixture_class_count"], 19)

    def test_unknown_top_level_field_fails(self):
        packet = self.mutate(); packet["unexpected"] = True
        self.assertRejected(packet)

    def test_missing_top_level_field_fails(self):
        packet = self.mutate(); packet.pop("purpose")
        self.assertRejected(packet)

    def test_authority_effect_fails(self):
        packet = self.mutate(); packet["authority_effect"] = "canonical"
        self.assertRejected(packet)

    def test_status_promotion_fails(self):
        packet = self.mutate(); packet["status"] = "ACCEPTED"
        self.assertRejected(packet)

    def test_boolean_pull_request_fails(self):
        packet = self.mutate(); packet["source_generation"]["pull_request"] = True
        self.assertRejected(packet)

    def test_invalid_source_sha_fails(self):
        packet = self.mutate(); packet["source_generation"]["head"] = "not-a-sha"
        self.assertRejected(packet)

    def test_dependency_omission_fails(self):
        packet = self.mutate(); packet["dependencies"].pop()
        self.assertRejected(packet)

    def test_candidate_profile_omission_fails(self):
        packet = self.mutate(); packet["candidate_profiles"].pop()
        self.assertRejected(packet)

    def test_candidate_profile_unknown_field_fails(self):
        packet = self.mutate(); packet["candidate_profiles"][0]["selected"] = True
        self.assertRejected(packet)

    def test_primitive_omission_fails(self):
        packet = self.mutate(); packet["required_primitives"].pop()
        self.assertRejected(packet)

    def test_decision_field_omission_fails(self):
        packet = self.mutate(); packet["required_decision_fields"].pop()
        self.assertRejected(packet)

    def test_gate_reordering_fails(self):
        packet = self.mutate(); packet["readiness_gates"][0], packet["readiness_gates"][1] = packet["readiness_gates"][1], packet["readiness_gates"][0]
        self.assertRejected(packet)

    def test_gate_acceptance_promotion_fails(self):
        packet = self.mutate(); packet["readiness_gates"][0]["status"] = "PASS"
        self.assertRejected(packet)

    def test_hostile_fixture_omission_fails(self):
        packet = self.mutate(); packet["hostile_fixture_classes"].pop()
        self.assertRejected(packet)

    def test_independence_must_remain_required(self):
        packet = self.mutate(); packet["cross_language_witness"]["implementation_independence_required"] = False
        self.assertRejected(packet)

    def test_boolean_implementation_count_fails(self):
        packet = self.mutate(); packet["cross_language_witness"]["minimum_independent_implementations"] = True
        self.assertRejected(packet)

    def test_claimed_witness_fails(self):
        packet = self.mutate(); packet["cross_language_witness"]["current_state"] = "VERIFIED"
        self.assertRejected(packet)

    def test_prohibited_promotion_omission_fails(self):
        packet = self.mutate(); packet["prohibited_promotions"].pop()
        self.assertRejected(packet)

    def test_controlled_route_omission_fails(self):
        packet = self.mutate(); packet["controlled_routes"].pop()
        self.assertRejected(packet)

    def test_marker_drift_fails(self):
        packet = self.mutate(); packet["propagation"]["withdrawal_marker"] = "WITHDRAWN"
        self.assertRejected(packet)

    def test_skill_gap_authority_fails(self):
        packet = self.mutate(); packet["proposed_subdivision_gap"]["authority_effect"] = "permission"
        self.assertRejected(packet)

    def test_invalid_submitted_sha_fails(self):
        with self.assertRaises(ValueError):
            validator.validate_packet(self.mutate(), Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json"), "bad")

    def test_duplicate_json_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"profile_id":"a","profile_id":"b"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.load_packet(path)

    def test_nonfinite_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nan.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.load_packet(path)

    def test_invalid_utf8_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_bytes(b'{"value":"\xff"}')
            with self.assertRaises(UnicodeDecodeError):
                validator.load_packet(path)


if __name__ == "__main__":
    unittest.main()
