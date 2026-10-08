import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_presence_candidates import (
    _caid_documented_presence,
    build_presence_candidates,
    validate_presence_bundle,
)


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
                manifest, languages, places, geodata, reviews, source_dir, output,
                offline=True, curated_path=None,
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
                manifest, languages, places, geodata, reviews, source_dir, output,
                offline=True, curated_path=None,
            )
            self.assertEqual(approved["summary"]["approved"], 1)
            self.assertEqual(approved["approved_claims"][0]["place_id"], "place-cod-adm2-test")
            self.assertFalse(validate_presence_bundle(approved))

    def test_builds_low_confidence_caid_records_from_hxl_iso_columns(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_path = root / "caid.csv"
            source_path.write_text(
                "Admin 2,Adm 2 Pcode,Admin 1,Adm 1 Pcode,Primary language,data_confidence,notes,Lingala,Nande\n"
                "#adm2+name,#adm2+code,#adm1+name,#adm1+code,#indicator+lang+main,#meta+confidence,#meta+text,"
                "#indicator+lang+pct+iso639-3_lin,#indicator+lang+pct+iso639-3_nmb\n"
                "Example,CD1001,Province,CD10,Lingala,Low,,0.8,0.25\n"
                "Notes-only,CD1002,Province,CD10,Lingala,Low,Lingala and Nande are present.,,\n",
                encoding="utf-8",
            )
            languages = [
                {"id": "language-lin", "preferred_name": "Lingala"},
                {"id": "language-nnb", "preferred_name": "Nande"},
            ]
            places = [
                {"id": "place-cod-adm1-cd10", "name": "Province", "admin_level": "province"},
                {
                    "id": "place-cod-adm2-cd1001", "name": "Example",
                    "admin_level": "territory", "parent_id": "place-cod-adm1-cd10",
                },
                {
                    "id": "place-cod-adm2-cd1002", "name": "Notes-only",
                    "admin_level": "territory", "parent_id": "place-cod-adm1-cd10",
                },
            ]
            source = {
                "id": "clear-global-caid-drc-languages-2016",
                "version": "test", "landing_page": "https://example.org/caid",
            }

            records = _caid_documented_presence(
                source_path, source, languages, places,
                {("language-lin", "place-cod-adm2-cd1001")},
            )

            self.assertEqual(len(records), 3)
            self.assertEqual(records[0]["language_id"], "language-nnb")
            self.assertEqual(records[0]["speaker_percentage"], 25)
            self.assertEqual(records[0]["confidence"], "low")
            self.assertIn("HXL ISO mapping", records[0]["limitations"])
            qualitative = records[1:]
            self.assertEqual({record["language_id"] for record in qualitative}, {"language-lin", "language-nnb"})
            self.assertTrue(all("speaker_percentage" not in record for record in qualitative))
            self.assertTrue(all("qualitative presence only" in record["limitations"] for record in qualitative))


if __name__ == "__main__":
    unittest.main()
