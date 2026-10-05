import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_catalog import DEFAULT_CATALOG_DIR, validate_catalog


class CatalogValidationTests(unittest.TestCase):
    def write_record(self, directory: Path, name: str, record: dict) -> None:
        (directory / name).write_text(json.dumps(record), encoding="utf-8")

    def test_repository_catalog_is_valid(self) -> None:
        self.assertEqual(validate_catalog(DEFAULT_CATALOG_DIR), [])

    def test_rejects_forbidden_content_field(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.write_record(
                directory,
                "source.json",
                {
                    "entity_type": "source",
                    "id": "source-example",
                    "citation": "Example source",
                    "url": "https://example.org/source",
                    "publisher": "Example",
                    "retrieved_at": "2026-10-05",
                    "source_type": "other",
                    "licence_id": None,
                    "verification_status": "draft",
                    "last_reviewed_at": "2026-10-05",
                    "source_text": "restricted sentence"
                },
            )
            errors = validate_catalog(directory)
            self.assertTrue(any("forbidden in public metadata" in error for error in errors))

    def test_rejects_dangling_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.write_record(
                directory,
                "language.json",
                {
                    "entity_type": "language",
                    "id": "language-example",
                    "preferred_name": "Example",
                    "identifiers": {"iso_639_3": "exa"},
                    "alternate_names": [],
                    "status": "draft",
                    "verification_status": "draft",
                    "citations": [{"source_id": "source-missing", "locator": "entry"}],
                    "last_reviewed_at": "2026-10-05"
                },
            )
            errors = validate_catalog(directory)
            self.assertTrue(any("references missing record 'source-missing'" in error for error in errors))

    def test_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            base = {
                "entity_type": "source",
                "id": "source-example",
                "citation": "Example source",
                "url": "https://example.org/source",
                "publisher": "Example",
                "retrieved_at": "2026-10-05",
                "source_type": "other",
                "licence_id": None,
                "verification_status": "draft",
                "last_reviewed_at": "2026-10-05"
            }
            self.write_record(directory, "one.json", base)
            self.write_record(directory, "two.json", base)
            errors = validate_catalog(directory)
            self.assertTrue(any("duplicate id 'source-example'" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
