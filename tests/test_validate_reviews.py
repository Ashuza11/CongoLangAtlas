import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_reviews import DEFAULT_DECISIONS_DIR, DEFAULT_IMPORT_CONFIG, validate_reviews


class ReviewValidationTests(unittest.TestCase):
    def test_repository_reviews_are_valid_and_complete(self) -> None:
        self.assertEqual(validate_reviews(DEFAULT_DECISIONS_DIR, DEFAULT_IMPORT_CONFIG), [])

    def test_rejects_decision_for_unpinned_commit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decisions = root / "decisions"
            decisions.mkdir()
            config = root / "import.json"
            config.write_text(json.dumps({"source_commit": "a" * 40, "expected_tracks": 1}), encoding="utf-8")
            (decisions / "tst.json").write_text(json.dumps({
                "decision_version": 1,
                "source_commit": "b" * 40,
                "iso_639_3": "tst",
                "atlas_language_id": "language-tst",
                "reviewer_id": "reviewer-test",
                "reviewed_at": "2026-10-06",
                "checks": {
                    "language_identity": "approved",
                    "variety_identity": "approved",
                    "geographic_scope": "approved",
                    "licence": "approved",
                    "access": "approved",
                    "source_links": "approved"
                },
                "decision": "defer",
                "notes": "A named human reviewer is still required."
            }), encoding="utf-8")

            errors = validate_reviews(decisions, config)
            self.assertTrue(any("source_commit does not match" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
