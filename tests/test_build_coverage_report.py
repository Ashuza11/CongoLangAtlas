import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_coverage_report import build_coverage_report


class CoverageReportBuildTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_reports_thin_and_empty_provinces_without_inventing_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            places = root / "places"
            self.write_json(places / "a.json", {
                "id": "place-a", "name": "A", "admin_level": "province"
            })
            self.write_json(places / "a1.json", {
                "id": "place-a1", "name": "A1", "admin_level": "territory", "parent_id": "place-a"
            })
            self.write_json(places / "b.json", {
                "id": "place-b", "name": "B", "admin_level": "province"
            })
            bundle = root / "bundle.json"
            self.write_json(bundle, {
                "generated_at": "2026-10-06",
                "languages": [{
                    "id": "language-test", "name": "Test",
                    "geographic_candidates": [{
                        "id": "candidate-test", "province_place_id": "place-a",
                        "territory_place_id": "place-a1", "evidence_type": "representative-point"
                    }],
                    "place_claims": []
                }]
            })
            report = build_coverage_report(bundle, places, root / "report.json")
            province_a = next(item for item in report["provinces"] if item["province_id"] == "place-a")
            province_b = next(item for item in report["provinces"] if item["province_id"] == "place-b")
            self.assertEqual(province_a["territories_with_evidence"], 1)
            self.assertIn("fewer-than-three-language-leads", province_a["flags"])
            self.assertIn("no-language-leads", province_b["flags"])
            self.assertEqual(report["summary"]["empty_provinces"], 1)


if __name__ == "__main__":
    unittest.main()
