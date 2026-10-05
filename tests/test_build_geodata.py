import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_geodata import BuildError, build, normalize_name


def polygon(x_min: float, y_min: float, x_max: float, y_max: float) -> dict:
    return {
        "type": "Polygon",
        "coordinates": [[
            [x_min, y_min], [x_max, y_min], [x_max, y_max],
            [x_min, y_max], [x_min, y_min]
        ]],
    }


class GeodataBuildTests(unittest.TestCase):
    def write_source(self, directory: Path, source_id: str, features: list[dict]) -> str:
        path = directory / f"{source_id}.geojson"
        content = json.dumps({"type": "FeatureCollection", "features": features}).encode()
        path.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def source(self, source_id: str, level: str, count: int, checksum: str) -> dict:
        return {
            "id": source_id,
            "admin_level": level,
            "canonical_name": "Test boundaries",
            "boundary_year": 2026,
            "provider": "Test provider",
            "source_organizations": ["Test organization"],
            "licence": {
                "name": "Test licence",
                "url": "https://example.org/licence",
                "attribution": "Test attribution"
            },
            "metadata_url": "https://example.org/metadata",
            "download_url": "https://example.org/source.geojson",
            "source_revision": "abcdef1",
            "sha256": checksum,
            "feature_count": count,
            "geometry_types": ["Polygon"],
            "fields": {
                "id": "shapeID",
                "name": "shapeName",
                "code": "shapeISO"
            },
            "preprocessing": [],
            "source_updated_at": "2026-01-01",
            "built_at": "2026-01-02",
            "review_status": "source-checked",
            "geometry_review": "structure-checked",
            "intended_use": "Offline unit test",
            "limitations": ["Synthetic geometry"]
        }

    def feature(self, feature_id: str, name: str, geometry: dict, level: str) -> dict:
        return {
            "type": "Feature",
            "properties": {
                "shapeID": feature_id,
                "shapeName": name,
                "shapeISO": "",
                "shapeGroup": "COD",
                "shapeType": level,
            },
            "geometry": geometry,
        }

    def test_builds_layers_and_assigns_parents_offline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = root / "source"
            source_dir.mkdir()
            adm1_id = "test-cod-adm1"
            adm2_id = "test-cod-adm2"
            adm1_checksum = self.write_source(
                source_dir, adm1_id,
                [self.feature("province1", " Test  Province ", polygon(0, 0, 10, 10), "ADM1")],
            )
            adm2_checksum = self.write_source(
                source_dir, adm2_id,
                [self.feature("territory1", "Territory", polygon(1, 1, 2, 2), "ADM2")],
            )
            manifest = {
                "manifest_version": 1,
                "country_iso3": "COD",
                "reviewed_at": "2026-10-05",
                "sources": [
                    self.source(adm1_id, "ADM1", 1, adm1_checksum),
                    self.source(adm2_id, "ADM2", 1, adm2_checksum),
                ],
            }
            manifest_path = root / "sources.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            output_dir = root / "output"
            report_path = root / "report.json"

            report = build(manifest_path, source_dir, output_dir, report_path, offline=True)

            self.assertTrue(report["passed"])
            self.assertEqual(report["parent_assignment"]["assigned"], 1)
            adm2 = json.loads((output_dir / "cod-adm2.geojson").read_text(encoding="utf-8"))
            self.assertEqual(adm2["features"][0]["properties"]["parent_id"], "cod-adm1-province1")
            adm1 = json.loads((output_dir / "cod-adm1.geojson").read_text(encoding="utf-8"))
            self.assertEqual(adm1["features"][0]["properties"]["name"], "Test Province")

    def test_offline_build_rejects_checksum_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_dir = root / "source"
            source_dir.mkdir()
            source_id = "test-cod-adm1"
            self.write_source(
                source_dir, source_id,
                [self.feature("province1", "Province", polygon(0, 0, 1, 1), "ADM1")],
            )
            manifest = {
                "manifest_version": 1,
                "country_iso3": "COD",
                "reviewed_at": "2026-10-05",
                "sources": [self.source(source_id, "ADM1", 1, "0" * 64)],
            }
            manifest_path = root / "sources.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(BuildError, "verified cached source is unavailable"):
                build(manifest_path, source_dir, root / "output", root / "report.json", offline=True)

    def test_name_normalization_is_conservative(self) -> None:
        self.assertEqual(normalize_name("  Kasaï   Central  "), "Kasaï Central")


if __name__ == "__main__":
    unittest.main()
