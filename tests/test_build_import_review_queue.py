import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_import_review_queue import ReviewQueueError, build_queue


class ImportReviewQueueTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def create_fixture(self, root: Path, restricted: bool = True) -> tuple[Path, Path, Path]:
        draft = root / "draft"
        report = root / "report.json"
        public = root / "public"
        language = {
            "entity_type": "language", "id": "language-tst", "preferred_name": "Test",
            "identifiers": {"iso_639_3": "tst"},
            "alternate_names": [{"name": "Test Variety", "source_id": "source-test"}],
        }
        self.write_json(draft / "language.json", language)
        for kind in ("bitext", "benchmark"):
            self.write_json(draft / f"{kind}.json", {
                "entity_type": "resource", "id": f"resource-test-{kind}",
                "resource_type": kind, "languages": [{"language_id": "language-tst"}],
                "redistribution": "restricted" if restricted else "metadata-only",
                "geographic_scope": "uncertain" if restricted else "drc-labelled",
            })
        self.write_json(report, {
            "passed": True, "source_commit": "a" * 40, "retrieved_at": "2026-10-05",
            "manual_review_warnings": [{"iso_code": "tst"}] if restricted else [],
        })
        self.write_json(public / "language.json", {
            "entity_type": "language", "id": "language-existing-test",
            "identifiers": {"iso_639_3": "tst"},
        })
        return draft, report, public

    def test_prioritizes_restricted_track_and_reuses_existing_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            draft, report, public = self.create_fixture(root)
            queue = build_queue(draft, report, public, root / "queue.json", root / "decisions")

            self.assertEqual(queue["summary"]["high_priority"], 1)
            track = queue["tracks"][0]
            self.assertEqual(track["suggested_atlas_language_id"], "language-existing-test")
            self.assertIn("restricted-content", track["publication_blockers"])
            self.assertFalse(track["ready_for_promotion"])

    def test_rejects_missing_draft_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ReviewQueueError, "run the CongoLangBench importer first"):
                build_queue(root / "missing", root / "missing-report.json", root, root / "queue.json", root / "decisions")

    def test_applies_valid_deferred_source_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            draft, report, public = self.create_fixture(root, restricted=False)
            decisions = root / "decisions"
            self.write_json(decisions / "tst.json", {
                "decision_version": 1,
                "source_commit": "a" * 40,
                "iso_639_3": "tst",
                "atlas_language_id": "language-existing-test",
                "reviewer_id": "reviewer-automated-source-audit",
                "reviewed_at": "2026-10-05",
                "checks": {check: "approved" for check in (
                    "language_identity", "variety_identity", "geographic_scope",
                    "licence", "access", "source_links"
                )},
                "decision": "defer",
                "notes": "Automated evidence review passes; human approval is still required.",
                "evidence_urls": ["https://example.org/evidence"]
            })
            queue = build_queue(draft, report, public, root / "queue.json", decisions)

            self.assertEqual(queue["summary"]["reviewed"], 1)
            self.assertEqual(queue["summary"]["deferred"], 1)
            self.assertEqual(queue["tracks"][0]["publication_blockers"], ["human-approval"])
            self.assertFalse(queue["tracks"][0]["ready_for_promotion"])


if __name__ == "__main__":
    unittest.main()
