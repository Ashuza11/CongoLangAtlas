import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_place_catalog import build_place_catalog
from scripts.validate_catalog import ROOT, validate_catalog


class PlaceCatalogBuildTests(unittest.TestCase):
    def write_layer(self, path: Path, properties: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": properties,
                "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
            }],
        }), encoding="utf-8")

    def test_builds_linked_country_province_and_territory_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            geodata = root / "geodata"
            output = root / "places"
            self.write_layer(geodata / "cod-adm1.geojson", {
                "id": "cod-adm1-cd10", "name": "Kinshasa", "admin_level": "ADM1",
                "source_id": "ocha-rgc-cod-adm1-2017",
            })
            self.write_layer(geodata / "cod-adm2.geojson", {
                "id": "cod-adm2-cd1000", "name": "Kinshasa", "admin_level": "ADM2",
                "parent_id": "cod-adm1-cd10", "source_id": "ocha-rgc-cod-adm2-2017",
            })

            summary = build_place_catalog(ROOT / "public/geodata/sources.json", geodata, output)

            self.assertEqual(summary["total_places"], 3)
            province = json.loads((output / "catalog/places/place-cod-adm1-cd10.json").read_text())
            territory = json.loads((output / "catalog/places/place-cod-adm2-cd1000.json").read_text())
            self.assertEqual(province["parent_id"], "place-cod")
            self.assertEqual(territory["parent_id"], province["id"])
            self.assertEqual(territory["geometry_id"], "cod-adm2-cd1000")
            self.assertFalse(validate_catalog(output / "catalog"))


if __name__ == "__main__":
    unittest.main()
