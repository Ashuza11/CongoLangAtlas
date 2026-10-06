import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_presence_candidates import build_presence_candidates, validate_presence_bundle


class PresenceCandidateBuildTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_maps_point_and_requires_review_before_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = root / "source"
            source_dir.mkdir()
            csv_path = source_dir / "glottolog-5-3-languages.csv"
            csv_path.write_text(
                "ID,Name,Latitude,Longitude,Glottocode,ISO639P3code,Countries\n"
                "test1234,Test,0.5,0.5,test1234,tst,CD\n",
                encoding="utf-8",
            )
            checksum = hashlib.sha256(csv_path.read_bytes()).hexdigest()
            manifest = root / "sources.json"
            self.write_json(manifest, {
                "manifest_version": 1, "reviewed_at": "2026-10-06", "sources": [{
                    "id": "glottolog-5-3-languages", "citation": "Test Glottolog source",
                    "publisher": "Example", "version": "5.3", "published_at": "2026-03-02",
                    "landing_page": "https://example.org/release", "download_url": "https://example.org/languages.csv",
                    "doi": "https://doi.org/10.1/test", "licence_id": "CC-BY-4.0", "sha256": checksum,
                }],
            })
            languages = root / "languages"
            self.write_json(languages / "language-tst.json", {
                "id": "language-tst", "preferred_name": "Test", "identifiers": {"iso_639_3": "tst"},
            })
            places = root / "places"
            self.write_json(places / "province.json", {
                "id": "place-cod-adm1-test", "name": "Province", "geometry_id": "cod-adm1-test",
            })
            self.write_json(places / "territory.json", {
                "id": "place-cod-adm2-test", "name": "Territory", "geometry_id": "cod-adm2-test",
            })
            geodata = root / "geodata"
            polygon = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}
            for level in (1, 2):
                self.write_json(geodata / f"cod-adm{level}.geojson", {
                    "type": "FeatureCollection", "features": [{
                        "type": "Feature", "properties": {"id": f"cod-adm{level}-test"}, "geometry": polygon,
                    }],
                })
            reviews = root / "reviews"
            reviews.mkdir()
            output = root / "candidates.json"

            bundle = build_presence_candidates(
                manifest, languages, places, geodata, reviews, source_dir, output, offline=True,
            )
            self.assertEqual(bundle["summary"]["mapped-candidate"], 1)
            self.assertEqual(bundle["summary"]["approved"], 0)
            self.assertEqual(bundle["candidates"][0]["territory_place_id"], "place-cod-adm2-test")

            self.write_json(reviews / "tst.json", {
                "decision_version": 1, "candidate_id": "presence-glottolog-5-3-tst",
                "source_version": "5.3", "reviewer_id": "reviewer-test", "reviewed_at": "2026-10-06",
                "checks": {
                    "language_identity": "approved", "representative_location": "approved",
                    "administrative_match": "approved", "temporal_relevance": "approved",
                },
                "decision": "approve", "notes": "Test approval.",
            })
            approved = build_presence_candidates(
                manifest, languages, places, geodata, reviews, source_dir, output, offline=True,
            )
            self.assertEqual(approved["summary"]["approved"], 1)
            self.assertEqual(approved["approved_claims"][0]["place_id"], "place-cod-adm2-test")
            self.assertFalse(validate_presence_bundle(approved))


if __name__ == "__main__":
    unittest.main()
