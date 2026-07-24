from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "check_d2a_common_contract_graph.py"
spec = importlib.util.spec_from_file_location("d2a_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(validator)


class D2ACommonContractGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.graph_path = Path("docs/d2a-common-contract-ownership-graph-v1.json")
        cls.graph = validator.load_graph(cls.graph_path)

    def fresh(self):
        return copy.deepcopy(self.graph)

    def reject(self, graph):
        with self.assertRaises(ValueError):
            validator.validate_graph(graph, self.graph_path, "1" * 40)

    def test_current_graph_passes(self):
        report = validator.validate_graph(self.fresh(), self.graph_path, "1" * 40)
        self.assertEqual(report["disposition"], "D2A_COMMON_CONTRACT_GRAPH_VALIDATED_NON_AUTHORIZING")
        self.assertEqual(report["repository_count"], 19)
        self.assertEqual(report["contract_family_count"], 16)

    def test_unknown_top_field_fails(self):
        graph = self.fresh(); graph["selected_steward"] = "self"
        self.reject(graph)

    def test_authority_promotion_fails(self):
        graph = self.fresh(); graph["authority_effect"] = "operational"
        self.reject(graph)

    def test_boolean_pull_request_fails(self):
        graph = self.fresh(); graph["source_generation"]["pull_request"] = True
        self.reject(graph)

    def test_bad_source_sha_fails(self):
        graph = self.fresh(); graph["source_generation"]["head"] = "main"
        self.reject(graph)

    def test_repository_omission_fails(self):
        graph = self.fresh(); graph["repository_heads"].pop()
        self.reject(graph)

    def test_duplicate_repository_fails(self):
        graph = self.fresh(); graph["repository_heads"][1]["repository"] = graph["repository_heads"][0]["repository"]
        self.reject(graph)

    def test_candidate_head_omission_fails(self):
        graph = self.fresh(); graph["candidate_heads"].pop()
        self.reject(graph)

    def test_contract_family_omission_fails(self):
        graph = self.fresh(); graph["contract_families"].pop()
        self.reject(graph)

    def test_contract_family_duplicate_fails(self):
        graph = self.fresh(); graph["contract_families"][1]["id"] = graph["contract_families"][0]["id"]
        self.reject(graph)

    def test_edge_schema_drift_fails(self):
        graph = self.fresh(); graph["required_edges"][0]["accepted"] = True
        self.reject(graph)

    def test_triple_overlap_size_fails(self):
        graph = self.fresh(); graph["triple_overlap_witnesses"][0]["path"].pop()
        self.reject(graph)

    def test_obstruction_duplicate_fails(self):
        graph = self.fresh(); graph["material_obstructions"][1]["id"] = graph["material_obstructions"][0]["id"]
        self.reject(graph)

    def test_route_omission_fails(self):
        graph = self.fresh(); graph["controlled_routes"].pop()
        self.reject(graph)

    def test_marker_drift_fails(self):
        graph = self.fresh(); graph["propagation"]["rebind_marker"] = "CURRENT"
        self.reject(graph)

    def test_skill_gap_authority_fails(self):
        graph = self.fresh(); graph["proposed_subdivision_gap"]["authority_effect"] = "permission"
        self.reject(graph)

    def test_invalid_submitted_sha_fails(self):
        with self.assertRaises(ValueError):
            validator.validate_graph(self.fresh(), self.graph_path, "not-a-sha")

    def test_duplicate_json_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text('{"profile_id":"a","profile_id":"b"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.load_graph(path)

    def test_nonfinite_json_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nan.json"
            path.write_text('{"value":NaN}', encoding="utf-8")
            with self.assertRaises(ValueError):
                validator.load_graph(path)

    def test_invalid_utf8_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_bytes(b'{"value":"\xff"}')
            with self.assertRaises(UnicodeDecodeError):
                validator.load_graph(path)


if __name__ == "__main__":
    unittest.main()
