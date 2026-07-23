from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_runtime_fabric_producer_consumer_inventory import (
    EXPECTED_ROUTES,
    load_packet,
    validate_packet,
)


class RuntimeFabricInventoryValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet_path = Path("docs/runtime-fabric-producer-consumer-inventory-v1.json")
        self.packet = load_packet(self.packet_path)
        self.submitted_sha = "a" * 40

    def make_routes(self, root: Path) -> None:
        marker = (
            "runtime/Fabric\n"
            "OBSERVED_CANDIDATE_INVENTORY_RECORDED_BLOCKED_UNACCEPTED_BINDINGS\n"
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
            "RUNTIME_FABRIC_INVENTORY_VALIDATED_NON_AUTHORIZING",
        )
        self.assertEqual(report["repository_count"], 6)
        self.assertEqual(report["synthetic_consumer_count"], 2)
        self.assertEqual(report["controlled_route_count"], 6)

    def test_planning_routes_are_controlled(self) -> None:
        self.assertEqual(
            EXPECTED_ROUTES,
            {
                "docs/runtime-fabric-producer-consumer-inventory.md",
                "mkdocs.yml",
                "taskchain.md",
                "punchlist.md",
                "release.md",
                "changelog.md",
            },
        )

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

    def test_missing_repository_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["repositories"].pop()
        with self.assertRaisesRegex(ValueError, "six repository"):
            self.validate(candidate)

    def test_exact_head_drift_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["repositories"][1]["head_sha"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "repository/head closure"):
            self.validate(candidate)

    def test_authority_promotion_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["authority_effect"] = "OPERATIONAL"
        with self.assertRaisesRegex(ValueError, "no authority effect"):
            self.validate(candidate)

    def test_accepted_producer_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["repositories"][1]["accepted_producer"] = True
        with self.assertRaisesRegex(ValueError, "accepted binding is prohibited"):
            self.validate(candidate)

    def test_consumer_closure_drift_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["synthetic_consumer_closure"]["consumers"][0]["head_sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "consumer closure drifted"):
            self.validate(candidate)

    def test_live_compatibility_promotion_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["synthetic_consumer_closure"]["disposition"] = "LIVE_COMPATIBLE"
        with self.assertRaisesRegex(ValueError, "promoted"):
            self.validate(candidate)

    def test_qsio_kernel_silent_mapping_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        kernel = next(
            item for item in candidate["repositories"]
            if item["repository"] == "aevespers2/qsio-kernel"
        )
        kernel["label_uses"]["qso-event-ledger"] = "runtime_event"
        with self.assertRaisesRegex(ValueError, "explicitly unmapped"):
            self.validate(candidate)

    def test_duplicate_repository_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["repositories"][1]["repository"] = candidate["repositories"][0]["repository"]
        with self.assertRaisesRegex(ValueError, "duplicate repository"):
            self.validate(candidate)

    def test_duplicate_observed_path_rejected(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["repositories"][0]["observed_paths"].append(
            candidate["repositories"][0]["observed_paths"][0]
        )
        with self.assertRaisesRegex(ValueError, "contains duplicates"):
            self.validate(candidate)

    def test_gap_must_remain_non_authoritative(self) -> None:
        candidate = copy.deepcopy(self.packet)
        candidate["fysa_120"]["proposed_gap"]["authoritative"] = True
        with self.assertRaisesRegex(ValueError, "040-L"):
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
            with self.assertRaisesRegex(ValueError, "lacks inventory markers"):
                validate_packet(self.packet, path, self.submitted_sha, root)


if __name__ == "__main__":
    unittest.main()
