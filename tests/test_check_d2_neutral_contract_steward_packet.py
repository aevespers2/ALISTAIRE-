from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_d2_neutral_contract_steward_packet.py"
spec = importlib.util.spec_from_file_location("d2_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class D2NeutralContractStewardPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet_path = Path("docs/d2-neutral-contract-steward-decision-packet-v1.json")
        cls.packet = validator.load_packet(cls.packet_path)

    def fresh(self):
        return copy.deepcopy(self.packet)

    def reject(self, packet):
        with self.assertRaises(ValueError):
            validator.validate_packet(packet, self.packet_path, "1" * 40)

    def test_current_packet_passes(self):
        report = validator.validate_packet(self.fresh(), self.packet_path, "1" * 40)
        self.assertEqual(report["disposition"], "D2_DECISION_READINESS_VALIDATED_NON_AUTHORIZING")
        self.assertEqual(report["candidate_model_count"], 3)

    def test_unknown_field_fails(self):
        packet = self.fresh(); packet["selected_steward"] = "self"
        self.reject(packet)

    def test_authority_effect_fails(self):
        packet = self.fresh(); packet["authority_effect"] = "operational"
        self.reject(packet)

    def test_unblocked_status_fails(self):
        packet = self.fresh(); packet["status"] = "ACCEPTED"
        self.reject(packet)

    def test_boolean_pull_request_fails(self):
        packet = self.fresh(); packet["source_generation"]["pull_request"] = True
        self.reject(packet)

    def test_bad_source_sha_fails(self):
        packet = self.fresh(); packet["source_generation"]["head"] = "main"
        self.reject(packet)

    def test_missing_dependency_fails(self):
        packet = self.fresh(); packet["dependencies"].pop()
        self.reject(packet)

    def test_candidate_model_omission_fails(self):
        packet = self.fresh(); packet["candidate_models"].pop()
        self.reject(packet)

    def test_candidate_model_selection_injection_fails(self):
        packet = self.fresh(); packet["candidate_models"][0]["selected"] = True
        self.reject(packet)

    def test_required_decision_field_omission_fails(self):
        packet = self.fresh(); packet["required_decision_fields"].pop()
        self.reject(packet)

    def test_gate_order_drift_fails(self):
        packet = self.fresh(); packet["readiness_gates"][0], packet["readiness_gates"][1] = packet["readiness_gates"][1], packet["readiness_gates"][0]
        self.reject(packet)

    def test_unsafe_promotion_omission_fails(self):
        packet = self.fresh(); packet["prohibited_promotions"].pop()
        self.reject(packet)

    def test_route_omission_fails(self):
        packet = self.fresh(); packet["controlled_routes"].pop()
        self.reject(packet)

    def test_marker_drift_fails(self):
        packet = self.fresh(); packet["propagation"]["rebind_marker"] = "REVIEW"
        self.reject(packet)

    def test_gap_authority_fails(self):
        packet = self.fresh(); packet["proposed_subdivision_gap"]["authority_effect"] = "permission"
        self.reject(packet)

    def test_invalid_submitted_sha_fails(self):
        with self.assertRaises(ValueError):
            validator.validate_packet(self.fresh(), self.packet_path, "not-a-sha")

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
