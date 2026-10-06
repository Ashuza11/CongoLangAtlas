import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_web_data import build_web_data


class WebDataBuildTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_builds_safe_language_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = root / "catalog"
            self.write_json(catalog / "source.json", {
                "entity_type": "source", "id": "source-test", "citation": "Test source",
                "url": "https://example.org/source", "publisher": "Example", "retrieved_at": "2026-10-06",
                "source_type": "primary-dataset", "licence_id": "CC-BY-4.0",
                "verification_status": "source-checked", "last_reviewed_at": "2026-10-06"
            })
            self.write_json(catalog / "language.json", {
                "entity_type": "language", "id": "language-tst", "preferred_name": "Test",
                "identifiers": {"iso_639_3": "tst"}, "alternate_names": [], "status": "draft",
                "verification_status": "draft", "citations": [{"source_id": "source-test", "locator": "row"}],
                "classification_note": "Imported as a distinct track (Regional, Test region).",
                "last_reviewed_at": "2026-10-06"
            })
            for kind in ("bitext", "benchmark"):
                self.write_json(catalog / f"{kind}.json", {
                    "entity_type": "resource", "id": f"resource-{kind}", "title": f"Test {kind}",
                    "resource_type": kind, "modalities": ["text"],
                    "languages": [{"language_id": "language-tst", "provenance_note": "Test provenance."}],
                    "geographic_scope": "drc-labelled", "publisher": "Example", "retrieved_at": "2026-10-06",
                    "homepage_url": "https://example.org/data", "download_url": None,
                    "access_type": "catalogue-only", "licence_id": None, "redistribution": "metadata-only",
                    "source_id": "source-test", "verification_status": "draft", "last_reviewed_at": "2026-10-06",
                    "limitations": "Frozen-local evaluation metadata only; sentence text is excluded." if kind == "benchmark" else "External test source."
                })
            queue = root / "queue.json"
            self.write_json(queue, {
                "generated_at": "2026-10-06", "source_commit": "a" * 40,
                "summary": {"total": 1, "reviewed": 1, "deferred": 1, "ready_for_promotion": 0},
                "tracks": [{
                    "imported_language_id": "language-tst", "review_status": "deferred", "priority": "medium",
                    "publication_blockers": ["human-approval"],
                    "required_checks": {name: "approved" for name in (
                        "language_identity", "variety_identity", "geographic_scope", "licence", "access", "source_links"
                    )},
                    "ready_for_promotion": False
                }]
            })
            discovery = root / "discovery.json"
            self.write_json(discovery, {
                "languages": [{
                    "language_id": "language-tst",
                    "candidates": [{
                        "id": "candidate-test", "provider": "OLAC", "kind": "catalogue",
                        "title": "Test catalogue", "url": "https://example.org/catalogue",
                        "review_status": "candidate",
                    }],
                }],
            })
            presence = root / "presence.json"
            self.write_json(presence, {
                "summary": {"documented-presence": 1},
                "candidates": [{
                    "id": "presence-supplemental", "language_id": "language-sup",
                    "match_status": "documented-presence", "evidence_type": "documented-presence",
                    "place_id": "place-cod-adm2-test", "province_place_id": "place-cod-adm1-test",
                    "province_name": "Province", "territory_place_id": "place-cod-adm2-test",
                    "territory_name": "Territory", "source_id": "source-map",
                    "source_url": "https://example.org/map", "source_title": "Test map",
                    "evidence_locator": "Territory table", "role": "spoken-language",
                    "speaker_percentage": 15, "confidence": "high", "review_status": "candidate",
                    "limitations": "A test limitation."
                }],
                "approved_claims": [],
                "supplemental_languages": [{
                    "id": "language-sup", "preferred_name": "Supplemental",
                    "identifiers": {"iso_639_3": "sup"}, "alternate_names": [], "region": "Test region",
                    "classification_note": "Documented outside the benchmark.", "last_reviewed_at": "2026-10-06",
                    "review": {
                        "review_status": "deferred", "priority": "high",
                        "publication_blockers": ["human-approval"],
                        "required_checks": {"geographic_scope": "approved"},
                        "ready_for_promotion": False
                    }
                }]
            })

            bundle = build_web_data(catalog, queue, root / "web.json", discovery, presence)
            imported = next(item for item in bundle["languages"] if item["id"] == "language-tst")
            self.assertEqual(imported["region"], "Test region")
            self.assertEqual(len(imported["resources"]), 1)
            self.assertEqual(imported["resources"][0]["type"], "bitext")
            self.assertEqual(bundle["summary"]["resources"], 1)
            self.assertEqual(bundle["summary"]["discovered_sources"], 2)
            self.assertEqual(imported["discovered_sources"][0]["provider"], "OLAC")
            supplemental = next(item for item in bundle["languages"] if item["id"] == "language-sup")
            self.assertEqual(supplemental["geographic_candidates"][0]["speaker_percentage"], 15)
            self.assertEqual(bundle["summary"]["languages"], 2)
            self.assertNotIn("source_text", json.dumps(bundle))


if __name__ == "__main__":
    unittest.main()
