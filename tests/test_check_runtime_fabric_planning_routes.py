from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.check_runtime_fabric_planning_routes import (
    REJECTED_OPTION,
    REVIEW_DISPOSITIONS,
    ROUTES,
    SAFE_DEFAULT,
    STATUS,
    validate_routes,
)

ROOT = Path(__file__).resolve().parents[1]


class RuntimeFabricPlanningRouteTests(unittest.TestCase):
    def make_root(self) -> Path:
        directory = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, directory, True)
        for relative in ROUTES:
            shutil.copy2(ROOT / relative, directory / relative)
        return directory

    def mutate(self, relative: str, old: str, new: str = "") -> list[str]:
        root = self.make_root()
        path = root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")
        return validate_routes(root)

    def test_current_routes_pass(self) -> None:
        self.assertEqual([], validate_routes())

    def test_rejects_missing_route(self) -> None:
        root = self.make_root()
        (root / "release.md").unlink()
        self.assertTrue(validate_routes(root))

    def test_rejects_missing_synchronization_status(self) -> None:
        self.assertTrue(self.mutate("taskchain.md", STATUS, "STALE"))

    def test_rejects_selected_synchronization_status(self) -> None:
        self.assertTrue(
            self.mutate(
                "release.md",
                STATUS,
                "PLANNING_ROUTES_SYNCHRONIZED_BINDINGS_ACCEPTED",
            )
        )

    def test_rejects_safe_default_removal(self) -> None:
        self.assertTrue(self.mutate("punchlist.md", SAFE_DEFAULT, "READ_ONLY_ADAPTER"))

    def test_rejects_direct_alias_selection(self) -> None:
        self.assertTrue(self.mutate("changelog.md", REJECTED_OPTION, "SELECT_DIRECT_IDENTITY_ALIAS"))

    def test_rejects_default_head_disposition_drift(self) -> None:
        disposition = "DEFAULT_HEADS_VERIFIED_OWNER_VACANCIES_RECORDED_BINDINGS_UNACCEPTED"
        self.assertIn(disposition, REVIEW_DISPOSITIONS)
        self.assertTrue(self.mutate("taskchain.md", disposition, "DEFAULT_HEADS_ACCEPTED"))

    def test_rejects_lineage_disposition_drift(self) -> None:
        disposition = "CANDIDATE_LINEAGES_CLASSIFIED_REBIND_WITHDRAW_OR_ACCEPT_REQUIRED"
        self.assertTrue(self.mutate("release.md", disposition, "CANDIDATES_ACCEPTED"))

    def test_rejects_crosswalk_disposition_drift(self) -> None:
        disposition = "KERNEL_RUNTIME_CROSSWALK_OPTIONS_DOCUMENTED_UNSELECTED"
        self.assertTrue(self.mutate("punchlist.md", disposition, "CROSSWALK_SELECTED"))

    def test_rejects_review_index_disposition_drift(self) -> None:
        disposition = "REVIEW_INDEX_COMPLETE_BINDINGS_UNACCEPTED"
        self.assertTrue(self.mutate("taskchain.md", disposition, "BINDINGS_ACCEPTED"))

    def test_rejects_missing_authority_boundary(self) -> None:
        self.assertTrue(self.mutate("punchlist.md", "Authority effect: `NONE`", "Authority effect: `OPERATIONAL`"))

    def test_rejects_missing_skill_gap_mapping(self) -> None:
        self.assertTrue(
            self.mutate(
                "changelog.md",
                "012-P — Cross-document governance status indexing and controlled-route coherence",
                "",
            )
        )


if __name__ == "__main__":
    unittest.main()
