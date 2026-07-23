from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path("scripts/check_runtime_fabric_lineage_disposition.py")
SPEC = importlib.util.spec_from_file_location("lineage_validator", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class RuntimeFabricLineageDispositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = validator.load_packet(validator.DEFAULT_PACKET)

    def validate(self, packet: dict) -> dict:
        return validator.validate_packet(copy.deepcopy(packet), root=Path("."))

    def test_current_packet_passes(self) -> None:
        report = self.validate(self.packet)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["lineage_count"], 6)

    def test_status_promotion_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["status"] = "ACCEPTED"
        with self.assertRaisesRegex(ValueError, "status changed"):
            self.validate(packet)

    def test_authority_promotion_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["authority_effect"] = "NAMESPACE_OWNER"
        with self.assertRaisesRegex(ValueError, "authority effect"):
            self.validate(packet)

    def test_candidate_head_drift_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["lineages"][1]["exact_head_sha"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "lineage identities"):
            self.validate(packet)

    def test_boolean_pull_request_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["lineages"][0]["pull_request"] = True
        with self.assertRaisesRegex(ValueError, "pull_request"):
            self.validate(packet)

    def test_binding_promotion_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["lineages"][2]["accepted_binding"] = True
        with self.assertRaisesRegex(ValueError, "binding was promoted"):
            self.validate(packet)

    def test_unknown_disposition_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["lineages"][3]["disposition"] = "MERGE_NOW"
        with self.assertRaisesRegex(ValueError, "unknown disposition"):
            self.validate(packet)

    def test_missing_lineage_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["lineages"].pop()
        with self.assertRaisesRegex(ValueError, "lineage closure"):
            self.validate(packet)

    def test_duplicate_use_class_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["lineages"][0]["observed_use_classes"].append(
            packet["lineages"][0]["observed_use_classes"][0]
        )
        with self.assertRaisesRegex(ValueError, "contains duplicates"):
            self.validate(packet)

    def test_edge_identity_drift_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["graph_edges"][0]["id"] = "renamed"
        with self.assertRaisesRegex(ValueError, "graph-edge identities"):
            self.validate(packet)

    def test_review_gate_omission_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["review_gates"].pop()
        with self.assertRaisesRegex(ValueError, "review-gate closure"):
            self.validate(packet)

    def test_planning_route_omission_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["planning_alignment"].pop("release.md")
        with self.assertRaisesRegex(ValueError, "planning alignment closure"):
            self.validate(packet)

    def test_skill_gap_promotion_fails(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["fysa_120"]["proposed_gap"]["status"] = "ADOPTED"
        with self.assertRaisesRegex(ValueError, "skill-tree gap"):
            self.validate(packet)

    def test_duplicate_json_key_fails(self) -> None:
        raw = validator.DEFAULT_PACKET.read_text(encoding="utf-8")
        duplicate = raw.replace(
            '  "profile_version": "1.0.0-candidate",',
            '  "profile_version": "1.0.0-candidate",\n  "profile_version": "1.0.0-candidate",',
            1,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text(duplicate, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                validator.load_packet(path)

    def test_nonfinite_number_fails(self) -> None:
        raw = validator.DEFAULT_PACKET.read_text(encoding="utf-8")
        malformed = raw[:-2] + ',\n  "unexpected": NaN\n}\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text(malformed, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite"):
                validator.load_packet(path)


if __name__ == "__main__":
    unittest.main()
