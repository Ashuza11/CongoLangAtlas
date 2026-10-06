import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_catalog import ROOT
from scripts.validate_presence import validate_presence


class PresenceValidationTests(unittest.TestCase):
    def test_repository_manifest_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            self.assertFalse(validate_presence(
                ROOT / "data/presence/sources.json", Path(temporary),
            ))

    def test_rejects_approval_with_unresolved_check(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            reviews = Path(temporary)
            (reviews / "decision.json").write_text(json.dumps({
                "decision_version": 1,
                "candidate_id": "presence-glottolog-5-3-tst",
                "source_version": "5.3",
                "reviewer_id": "reviewer-test",
                "reviewed_at": "2026-10-06",
                "checks": {
                    "language_identity": "approved",
                    "representative_location": "unresolved",
                    "administrative_match": "approved",
                    "temporal_relevance": "approved",
                },
                "decision": "approve",
                "notes": "Invalid test approval.",
            }), encoding="utf-8")
            errors = validate_presence(ROOT / "data/presence/sources.json", reviews)
            self.assertTrue(any("every check" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
