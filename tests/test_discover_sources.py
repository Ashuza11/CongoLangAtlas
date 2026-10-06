import unittest

from scripts.discover_sources import discover_language, validate_discovery


class SourceDiscoveryTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
