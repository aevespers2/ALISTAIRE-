from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_runtime_fabric_default_head_owner_inventory import (
    EXPECTED_ROUTES,
    load_packet,
    validate_packet,
)


class RuntimeFabricDefaultHeadOwnerInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet_path = Path("docs/runtime-fabric-default-head-owner-inventory-v1.json")
        self.packet = load_packet(self.packet_path)
        self.submitted_sha = "a" * 40

    def make_routes(self, root: Path) -> None:
        marker = (
            "runtime/Fabric\n"
            "DEFAULT_HEADS_VERIFIED_OWNER_VACANCIES_RECORDED_BINDINGS_UNACCEPTED\n"
        )
        for relative in EXPECTED_ROUTES:
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(marker, encoding="utf-8")

    def validate(self, packet: dict | None = None) -> dict:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_routes(root)
            candidate = self.packet if packet is None else packet
            path = root / "packet.json"
            path.write_text(json.dumps(candidate), encoding="utf-8")
            return validate_packet(candidate, path, self.submitted_sha, root)

    def test_valid_packet_passes(self) -> None:
        report = self.validate()
        self.assertEqual(
            report["disposition"],
            "RUNTIME_FABRIC_DEFAULT_HEAD_OWNER_INVENTORY_VALIDATED_NON_AUTHORIZING",
        )
        self.assertEqual(report["default_head_count"], 6)
        self.assertEqual(report["semantic_owner_vacancy_count"], 6)
        self.assertEqual(report["route_owner_vacancy_count"], 5)

    def test_duplicate_json_key_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text('{"profile_id":"a","profile_id":"b"}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_packet(path)

    def test_non_finite_number_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "non-finite"):
                load_packet(path)

    def test_missing_default_head_observation_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["default_head_observations"].pop()
        with self.assertRaisesRegex(ValueError, "six default-head"):
            self.validate(candidate)

    def test_default_head_drift_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["default_head_observations"][1]["default_head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "default-head closure"):
            self.validate(candidate)

    def test_present_absent_overlap_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        item = candidate["default_head_observations"][1]
        item["absent_paths"].append(item["present_paths"][0])
        with self.assertRaisesRegex(ValueError, "present/absent path overlap"):
            self.validate(candidate)

    def test_reviewed_path_gap_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["default_head_observations"][1]["absent_paths"].pop()
        with self.assertRaisesRegex(ValueError, "reviewed path closure"):
            self.validate(candidate)

    def test_legacy_binding_promotion_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["default_head_observations"][1]["exact_legacy_label_observed"] = True
        with self.assertRaisesRegex(ValueError, "legacy interface binding"):
            self.validate(candidate)

    def test_accepted_semantic_owner_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["semantic_owner_vacancies"][0]["accepted_owner"] = "aevespers2/QuantumStateObjects"
        with self.assertRaisesRegex(ValueError, "accepted semantic owner"):
            self.validate(candidate)

    def test_missing_semantic_vacancy_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["semantic_owner_vacancies"].pop()
        with self.assertRaisesRegex(ValueError, "semantic owner vacancy closure"):
            self.validate(candidate)

    def test_accepted_route_owner_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["route_owner_vacancies"][0]["accepted_owner"] = "aevespers2/ALISTAIRE-"
        with self.assertRaisesRegex(ValueError, "accepted route owner"):
            self.validate(candidate)

    def test_candidate_lineage_drift_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["candidate_lineage"][0]["candidate_head_sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "candidate lineage drifted"):
            self.validate(candidate)

    def test_graph_edge_drift_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["graph_edges"][0]["id"] = "renamed"
        with self.assertRaisesRegex(ValueError, "graph edge identities"):
            self.validate(candidate)

    def test_authority_promotion_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["authority_effect"] = "OPERATIONAL"
        with self.assertRaisesRegex(ValueError, "no authority effect"):
            self.validate(candidate)

    def test_gap_must_remain_non_authoritative(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["fysa_120"]["proposed_gap"]["authoritative"] = True
        with self.assertRaisesRegex(ValueError, "013-H"):
            self.validate(candidate)

    def test_invalid_submitted_sha_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_routes(root)
            path = root / "packet.json"
            path.write_text(json.dumps(self.packet), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "submitted SHA"):
                validate_packet(self.packet, path, "not-a-sha", root)

    def test_missing_controlled_route_marker_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_routes(root)
            missing = root / sorted(EXPECTED_ROUTES)[0]
            missing.write_text("runtime/Fabric only\n", encoding="utf-8")
            path = root / "packet.json"
            path.write_text(json.dumps(self.packet), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "lacks default-head owner inventory markers"):
                validate_packet(self.packet, path, self.submitted_sha, root)


if __name__ == "__main__":
    unittest.main()
