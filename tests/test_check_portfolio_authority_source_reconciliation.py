from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "reconciliation",
    ROOT / "scripts" / "check_portfolio_authority_source_reconciliation.py",
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReconciliationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.packet = MODULE.load_packet(
            ROOT / "docs" / "portfolio-authority-source-reconciliation-v1.json"
        )

    def invalid(self, packet: dict, marker: str) -> None:
        with self.assertRaisesRegex(MODULE.PacketError, marker):
            MODULE.validate(packet, ROOT)

    def test_valid_packet(self) -> None:
        result = MODULE.validate(self.packet, ROOT, "a" * 40)
        self.assertEqual(result["repositories"], 19)
        self.assertEqual(result["authority_effect"], "NONE")

    def test_missing_repository(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["repositories"].pop()
        self.invalid(packet, "nineteen")

    def test_default_head_substitution(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["repositories"][0]["default_head"] = "b" * 40
        self.invalid(packet, "default-head closure")

    def test_candidate_head_substitution(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["repositories"][1]["candidates"][0]["head"] = "b" * 40
        self.invalid(packet, "candidate-head closure")

    def test_boolean_pr_rejected(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["repositories"][1]["candidates"][0]["pr"] = True
        self.invalid(packet, "positive integer")

    def test_conflict_removed(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["conflicts"].pop()
        self.invalid(packet, "conflict closure")

    def test_vacancy_removed(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["vacancies"].pop()
        self.invalid(packet, "vacancy closure")

    def test_dissent_removed(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["dissent"].pop()
        self.invalid(packet, "dissent closure")

    def test_authority_effect_changed(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["authority_effect"] = "ADOPTED"
        self.invalid(packet, "authority_effect")

    def test_controlled_route_removed(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["controlled_routes"].remove("release.md")
        self.invalid(packet, "controlled-route closure")

    def test_invalid_submitted_sha(self) -> None:
        with self.assertRaisesRegex(MODULE.PacketError, "submitted SHA"):
            MODULE.validate(self.packet, ROOT, "main")

    def test_duplicate_json_key(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"profile_id":"x","profile_id":"y"}', encoding="utf-8")
            with self.assertRaisesRegex(MODULE.PacketError, "duplicate JSON key"):
                MODULE.load_packet(path)

    def test_non_finite_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nan.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaisesRegex(MODULE.PacketError, "non-finite JSON"):
                MODULE.load_packet(path)


if __name__ == "__main__":
    unittest.main()
