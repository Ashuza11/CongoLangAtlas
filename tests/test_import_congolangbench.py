import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.import_congolangbench import (
    ImportError,
    REGISTRY_FIELDS,
    import_metadata,
    read_registry,
)


class CongoLangBenchImportTests(unittest.TestCase):
    commit = "a" * 40

    def write_csv(self, path: Path, filename: str, row: dict[str, str]) -> None:
        fields = sorted(REGISTRY_FIELDS[filename])
        with (path / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerow({field: row.get(field, "") for field in fields})

    def create_source(self, root: Path, restricted: bool = False) -> tuple[Path, Path]:
        registry = root / "source" / "registry"
        registry.mkdir(parents=True)
        handling = "restricted_local" if restricted else "publishable_or_metadata_qualified"
        self.write_csv(registry, "languages.csv", {
            "language": "Test Language", "iso_code": "tst", "variety": "Test Variety",
            "scope_region": "Test", "track": "Regional", "region_group": "Test region",
            "priority": "1", "target_pairs": "10", "current_pairs": "10",
            "status": "verified_source", "primary_next_action": "review",
        })
        self.write_csv(registry, "curation_readiness.csv", {
            "language": "Test Language", "iso_code": "tst", "track": "Regional",
            "region_group": "Test region", "target_pairs": "10", "registry_pairs": "10",
            "processed_csv": "language_resources/test-tst/data/processed/test.csv",
            "actual_pairs": "10", "reference_language": "French",
            "publication_handling": handling, "sha256": "b" * 64,
            "status": "ready_for_freeze", "issues": "",
        })
        self.write_csv(registry, "benchmark_freeze.csv", {
            "language": "Test Language", "iso_code": "tst", "track": "Regional",
            "region_group": "Test region", "reference_language": "French",
            "publication_handling": handling,
            "source_csv": "language_resources/test-tst/data/processed/test.csv",
            "source_pairs": "10", "source_sha256": "b" * 64,
            "benchmark_version": "v1", "benchmark_split": "eval", "benchmark_pairs": "2",
            "selection_algorithm": "deterministic", "benchmark_csv": "private.csv",
            "benchmark_sha256": "c" * 64, "status": "frozen_local",
        })
        config = root / "config.json"
        config.write_text(json.dumps({
            "source_commit": self.commit,
            "repository_url": "https://example.org/CongoLangBench",
            "retrieved_at": "2026-10-05",
            "expected_tracks": 1,
            "expected_processed_pairs": 10,
            "expected_restricted_tracks": 1 if restricted else 0,
            "expected_benchmark_pairs": 2,
        }), encoding="utf-8")
        return registry.parent, config

    def test_imports_allow_listed_metadata_into_valid_records(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, config = self.create_source(root)
            output = root / "output"
            report_path = root / "report.json"
            with patch("scripts.import_congolangbench.repository_commit", return_value=self.commit):
                report = import_metadata(source, config, output, report_path)

            self.assertTrue(report["passed"])
            self.assertEqual(report["generated_records"]["total"], 4)
            benchmark = json.loads(
                (output / "resources" / "resource-congolangbench-tst-benchmark-v1.json").read_text()
            )
            self.assertNotIn("benchmark_csv", benchmark)
            self.assertEqual(benchmark["access_type"], "unavailable")

    def test_preserves_restricted_publication_handling(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, config = self.create_source(root, restricted=True)
            output = root / "output"
            with patch("scripts.import_congolangbench.repository_commit", return_value=self.commit):
                import_metadata(source, config, output, root / "report.json")
            bitext = json.loads(
                (output / "resources" / "resource-congolangbench-tst-bitext.json").read_text()
            )
            self.assertEqual(bitext["redistribution"], "restricted")
            self.assertEqual(bitext["access_type"], "unavailable")

    def test_rejects_registry_fields_outside_allow_list(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            registry = Path(temporary)
            filename = "languages.csv"
            fields = sorted(REGISTRY_FIELDS[filename]) + ["source_text"]
            with (registry / filename).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
            with self.assertRaisesRegex(ImportError, "unexpected=.*source_text"):
                read_registry(registry, filename)


if __name__ == "__main__":
    unittest.main()
