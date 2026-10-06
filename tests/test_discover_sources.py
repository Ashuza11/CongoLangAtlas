import json
import tempfile
import unittest
from pathlib import Path

from scripts.discover_sources import _terms, build_discovery, discover_language, validate_discovery


class SourceDiscoveryTests(unittest.TestCase):
    def write_json(self, path: Path, value: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_discovers_and_filters_provider_candidates(self) -> None:
        language = {
            "id": "language-lin",
            "preferred_name": "Lingala",
            "identifiers": {"iso_639_3": "lin"},
            "alternate_names": [{"name": "Ngala"}],
        }

        def fake_get(url: str):
            if "/api/datasets" in url:
                return [
                    {"id": "team/lingala-speech", "description": "Lingala audio dataset", "tags": ["modality:audio"]},
                    {"id": "team/unrelated", "description": "Unrelated image set", "tags": []},
                ]
            if "/api/models" in url:
                return [{"id": "team/lingala-model", "description": "Lingala translation model", "tags": []}]
            if "api.github.com" in url:
                return {"items": [{
                    "full_name": "team/lingala-tools", "html_url": "https://github.com/team/lingala-tools",
                    "description": "NLP tools for the Lingala language", "topics": ["nlp"],
                    "owner": {"login": "team"}, "license": {"spdx_id": "MIT"},
                }]}
            if "api.openalex.org" in url:
                return {"results": [{
                    "display_name": "A grammar of Lingala", "doi": "https://doi.org/10.1/test",
                    "abstract_inverted_index": {"Lingala": [0], "language": [1]},
                    "authorships": [], "primary_location": {},
                }]}
            raise AssertionError(url)

        candidates, errors = discover_language(language, fake_get)
        self.assertFalse(errors)
        self.assertEqual({item["kind"] for item in candidates}, {"catalogue", "dataset", "model", "repository", "research"})
        self.assertNotIn("team/unrelated", {item["title"] for item in candidates})
        self.assertTrue(all(item["review_status"] == "candidate" for item in candidates))

    def test_rejects_unreviewed_or_insecure_candidates(self) -> None:
        errors = validate_discovery({"languages": [{
            "language_id": "language-test",
            "candidates": [{
                "provider": "Unknown", "kind": "dataset", "url": "http://example.org",
                "review_status": "approved",
            }],
        }]})
        self.assertEqual(len(errors), 3)

    def test_includes_supplemental_presence_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            catalog = root / "catalog"
            self.write_json(catalog / "language.json", {
                "entity_type": "language", "id": "language-one", "preferred_name": "One",
                "identifiers": {"iso_639_3": "one"}, "alternate_names": []
            })
            presence = root / "presence.json"
            self.write_json(presence, {"supplemental_languages": [{
                "id": "language-two", "preferred_name": "Two",
                "identifiers": {"iso_639_3": "two"}, "alternate_names": []
            }]})
            bundle = build_discovery(
                catalog, root / "output.json", root / "cache", providers=(),
                offline=True, presence=presence,
            )
            self.assertEqual(bundle["summary"]["languages"], 2)
            self.assertEqual(bundle["summary"]["candidates"], 2)
            self.assertTrue(all(item["candidates"][0]["provider"] == "OLAC" for item in bundle["languages"]))

    def test_short_language_name_falls_back_to_iso_search_term(self) -> None:
        language = {
            "id": "language-msj", "preferred_name": "Ma (Democratic Republic of Congo)",
            "identifiers": {"iso_639_3": "msj"}, "alternate_names": []
        }
        candidates, errors = discover_language(language, lambda _url: {"items": []}, providers=("github",))
        self.assertFalse(errors)
        self.assertEqual(candidates[0]["provider"], "OLAC")

    def test_country_qualified_name_stays_distinct(self) -> None:
        language = {
            "id": "language-bmy", "preferred_name": "Bemba (Democratic Republic of Congo)",
            "identifiers": {"iso_639_3": "bmy"}, "alternate_names": []
        }
        self.assertEqual(_terms(language), ["Bemba (Democratic Republic of Congo)"])


if __name__ == "__main__":
    unittest.main()
