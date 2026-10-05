import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_geodata import DEFAULT_MANIFEST, validate_manifest


class GeodataManifestValidationTests(unittest.TestCase):
    def test_repository_manifest_is_valid(self) -> None:
        self.assertEqual(validate_manifest(DEFAULT_MANIFEST), [])

    def test_rejects_duplicate_administrative_level(self) -> None:
        manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(manifest["sources"][0])
        duplicate["id"] = "geoboundaries-cod-adm1-duplicate"
        manifest["sources"].append(duplicate)

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sources.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_manifest(path)

        self.assertIn("only one selected source is allowed per administrative level", errors)

    def test_rejects_unpinned_download(self) -> None:
        manifest = json.loads(DEFAULT_MANIFEST.read_text(encoding="utf-8"))
        manifest["sources"][0]["source_revision"] = ""

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sources.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_manifest(path)

        self.assertTrue(any("does not match" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
