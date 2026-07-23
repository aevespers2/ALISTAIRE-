from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_decision_source_generation_rebind.py"
spec = importlib.util.spec_from_file_location("rebind_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class DecisionSourceGenerationRebindTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rebind_path = Path("docs/decision-source-generation-rebind-v1.json")
        cls.d2a_path = Path("docs/d2a-common-contract-ownership-graph-v1.json")
        cls.d3_path = Path("docs/d3-canonical-bytes-identity-decision-packet-v1.json")
        cls.rebind = validator.load_json(cls.rebind_path)
        cls.d2a = validator.load_json(cls.d2a_path)
        cls.d3 = validator.load_json(cls.d3_path)

    def fresh(self):
        return (
            copy.deepcopy(self.rebind),
            copy.deepcopy(self.d2a),
            copy.deepcopy(self.d3),
        )

    def validate(self, rebind, d2a, d3, *, submitted="2" * 40, anchor=None):
        return validator.validate_rebind(
            rebind,
            d2a,
            d3,
            rebind_path=self.rebind_path,
            submitted_sha=submitted,
            ancestry_anchor=anchor or rebind["rebind_parent"],
        )

    def reject(self, rebind, d2a, d3, **kwargs):
        with self.assertRaises(ValueError):
            self.validate(rebind, d2a, d3, **kwargs)

    def test_current_rebind_passes(self):
        rebind, d2a, d3 = self.fresh()
        report = self.validate(rebind, d2a, d3)
        self.assertEqual(
            report["disposition"],
            "DECISION_SOURCE_GENERATION_REBOUND_NON_AUTHORIZING",
        )
        self.assertEqual(report["ancestry_anchor"], rebind["rebind_parent"])

    def test_wrong_ancestry_anchor_fails(self):
        rebind, d2a, d3 = self.fresh()
        self.reject(rebind, d2a, d3, anchor="3" * 40)

    def test_submitted_equal_to_anchor_fails(self):
        rebind, d2a, d3 = self.fresh()
        anchor = rebind["rebind_parent"]
        self.reject(rebind, d2a, d3, submitted=anchor, anchor=anchor)

    def test_invalid_submitted_sha_fails(self):
        rebind, d2a, d3 = self.fresh()
        self.reject(rebind, d2a, d3, submitted="not-a-sha")

    def test_authority_promotion_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["authority_effect"] = "operational"
        self.reject(rebind, d2a, d3)

    def test_status_promotion_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["status"] = "ACCEPTED"
        self.reject(rebind, d2a, d3)

    def test_ancestry_rule_drift_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["ancestry_rule"] = "any ancestor is acceptable"
        self.reject(rebind, d2a, d3)

    def test_recorded_d2a_source_drift_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["historical_sources"]["d2a_packet_source_head"] = "4" * 40
        self.reject(rebind, d2a, d3)

    def test_recorded_d3_source_drift_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["historical_sources"]["d3_packet_source_head"] = "5" * 40
        self.reject(rebind, d2a, d3)

    def test_recorded_candidate_drift_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["historical_sources"]["d2a_alistaire_candidate_head"] = "6" * 40
        self.reject(rebind, d2a, d3)

    def test_packet_source_mutation_fails(self):
        rebind, d2a, d3 = self.fresh()
        d3["source_generation"]["head"] = "7" * 40
        self.reject(rebind, d2a, d3)

    def test_candidate_omission_fails(self):
        rebind, d2a, d3 = self.fresh()
        d2a["candidate_heads"] = [
            item
            for item in d2a["candidate_heads"]
            if not (
                item.get("repository") == "aevespers2/ALISTAIRE-"
                and item.get("pull_request") == 1
            )
        ]
        self.reject(rebind, d2a, d3)

    def test_invalidation_omission_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["invalidates_on"].pop()
        self.reject(rebind, d2a, d3)

    def test_prohibition_omission_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["prohibited_promotions"].pop()
        self.reject(rebind, d2a, d3)

    def test_rollback_mode_promotion_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["rollback"]["mode"] = "force_update"
        self.reject(rebind, d2a, d3)

    def test_skill_gap_authority_fails(self):
        rebind, d2a, d3 = self.fresh()
        rebind["proposed_subdivision_gap"]["authority_effect"] = "permission"
        self.reject(rebind, d2a, d3)

    def test_duplicate_json_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"profile_id":"a","profile_id":"b"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.load_json(path)

    def test_nonfinite_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nan.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.load_json(path)

    def test_invalid_utf8_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_bytes(b'{"value":"\xff"}')
            with self.assertRaises(UnicodeDecodeError):
                validator.load_json(path)


if __name__ == "__main__":
    unittest.main()
