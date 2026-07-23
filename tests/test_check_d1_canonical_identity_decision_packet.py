from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_d1_canonical_identity_decision_packet.py"
spec = importlib.util.spec_from_file_location("d1_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class D1DecisionPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = validator.load_packet(Path("docs/d1-canonical-identity-decision-packet-v1.json"))

    def packet_copy(self):
        return copy.deepcopy(self.packet)

    def assert_rejected(self, packet):
        with self.assertRaises(ValueError):
            validator.validate(packet, Path("docs/d1-canonical-identity-decision-packet-v1.json"), "1" * 40)

    def test_current_packet_passes(self):
        report = validator.validate(self.packet_copy(), Path("docs/d1-canonical-identity-decision-packet-v1.json"), "1" * 40)
        self.assertEqual(report["disposition"], "D1_REVIEW_READINESS_VALIDATED_DECISION_BLOCKED")

    def test_authority_promotion_fails(self):
        packet = self.packet_copy(); packet["authority_effect"] = "canonical_selection"
        self.assert_rejected(packet)

    def test_selected_option_fails(self):
        packet = self.packet_copy(); packet["decision_options"][0]["disposition"] = "SELECTED"
        self.assert_rejected(packet)

    def test_missing_repository_fails(self):
        packet = self.packet_copy(); packet["observed_sources"].pop()
        self.assert_rejected(packet)

    def test_duplicate_repository_fails(self):
        packet = self.packet_copy(); packet["observed_sources"][1]["repository"] = packet["observed_sources"][0]["repository"]
        self.assert_rejected(packet)

    def test_moved_source_fails(self):
        packet = self.packet_copy(); packet["observed_sources"][0]["observed_default_head"] = "2" * 40
        self.assert_rejected(packet)

    def test_boolean_pull_request_fails(self):
        packet = self.packet_copy(); packet["observed_sources"][0]["documentation_candidate"]["pull_request"] = True
        self.assert_rejected(packet)

    def test_required_field_omission_fails(self):
        packet = self.packet_copy(); packet["required_decision_fields"].pop()
        self.assert_rejected(packet)

    def test_false_gate_completion_fails(self):
        packet = self.packet_copy(); packet["readiness_gates"]["license_decision"] = "SATISFIED"
        self.assert_rejected(packet)

    def test_route_omission_fails(self):
        packet = self.packet_copy(); packet["controlled_routes"].pop()
        self.assert_rejected(packet)

    def test_marker_drift_fails(self):
        packet = self.packet_copy(); packet["propagation_markers"]["stale"] = "STALE"
        self.assert_rejected(packet)

    def test_skill_gap_promotion_fails(self):
        packet = self.packet_copy(); packet["proposed_skill_gap"]["status"] = "ACCEPTED"
        self.assert_rejected(packet)

    def test_invalid_submitted_sha_fails(self):
        with self.assertRaises(ValueError):
            validator.validate(self.packet_copy(), Path("docs/d1-canonical-identity-decision-packet-v1.json"), "not-a-sha")

    def test_duplicate_json_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"packet_id":"a","packet_id":"b"}', encoding="utf-8")
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
