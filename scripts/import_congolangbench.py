#!/usr/bin/env python3
"""Export allow-listed CongoLangBench registry metadata as draft atlas records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.validate_catalog import ROOT, load_json, validate_catalog


DEFAULT_CONFIG = ROOT / "data" / "import" / "congolangbench.json"
DEFAULT_OVERRIDES = ROOT / "data" / "import" / "congolangbench-resource-overrides.json"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "congolangbench" / "catalog"
DEFAULT_REPORT = ROOT / "data" / "generated" / "congolangbench" / "import-report.json"

REGISTRY_FIELDS = {
    "languages.csv": {
        "language", "iso_code", "variety", "scope_region", "track", "region_group",
        "priority", "target_pairs", "current_pairs", "status", "primary_next_action",
    },
    "curation_readiness.csv": {
        "language", "iso_code", "track", "region_group", "target_pairs", "registry_pairs",
        "processed_csv", "actual_pairs", "reference_language", "publication_handling",
        "sha256", "status", "issues",
    },
    "benchmark_freeze.csv": {
        "language", "iso_code", "track", "region_group", "reference_language",
        "publication_handling", "source_csv", "source_pairs", "source_sha256",
        "benchmark_version", "benchmark_split", "benchmark_pairs", "selection_algorithm",
        "benchmark_csv", "benchmark_sha256", "status",
    },
}


class ImportError(RuntimeError):
    """Raised when pinned input or reconciliation rules fail."""


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_registry(registry_dir: Path, filename: str) -> list[dict[str, str]]:
    path = registry_dir / filename
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        actual_fields = set(reader.fieldnames or [])
        if actual_fields != REGISTRY_FIELDS[filename]:
            missing = sorted(REGISTRY_FIELDS[filename] - actual_fields)
            unexpected = sorted(actual_fields - REGISTRY_FIELDS[filename])
            raise ImportError(f"{filename}: field mismatch; missing={missing}, unexpected={unexpected}")
        return list(reader)


def repository_commit(source_root: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def require_integer(row: dict[str, str], field: str, filename: str) -> int:
    try:
        value = int(row[field])
    except (KeyError, ValueError) as exc:
        raise ImportError(f"{filename}: invalid integer {field}={row.get(field)!r}") from exc
    if value < 0:
        raise ImportError(f"{filename}: {field} cannot be negative")
    return value


def record_url(repository_url: str, commit: str, relative_path: str) -> str:
    return f"{repository_url}/blob/{commit}/{relative_path}"


def directory_url(repository_url: str, commit: str, relative_path: str) -> str:
    return f"{repository_url}/tree/{commit}/{relative_path}"


def resource_root(path: str) -> str:
    marker = "/data/"
    return path.split(marker, 1)[0] if marker in path else str(Path(path).parent)


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def import_metadata(
    source_root: Path,
    config_path: Path = DEFAULT_CONFIG,
    output_dir: Path = DEFAULT_OUTPUT,
    report_path: Path = DEFAULT_REPORT,
    overrides_path: Path | None = DEFAULT_OVERRIDES,
) -> dict[str, Any]:
    config = load_json(config_path)
    overrides = load_json(overrides_path) if overrides_path and overrides_path.exists() else {"sources": {}, "tracks": {}}
    actual_commit = repository_commit(source_root)
    if actual_commit != config["source_commit"]:
        raise ImportError(
            f"source commit mismatch; expected {config['source_commit']}, got {actual_commit}"
        )

    registry_dir = source_root / "registry"
    languages = read_registry(registry_dir, "languages.csv")
    readiness = read_registry(registry_dir, "curation_readiness.csv")
    freezes = read_registry(registry_dir, "benchmark_freeze.csv")
    languages_by_iso = {row["iso_code"]: row for row in languages}
    readiness_by_iso = {row["iso_code"]: row for row in readiness}
    freezes_by_iso = {row["iso_code"]: row for row in freezes}
    if len(languages_by_iso) != len(languages):
        raise ImportError("languages.csv contains duplicate ISO codes")
    if set(readiness_by_iso) != set(freezes_by_iso):
        raise ImportError("curation and benchmark registries cover different ISO codes")
    missing_languages = sorted(set(readiness_by_iso) - set(languages_by_iso))
    if missing_languages:
        raise ImportError(f"ready tracks missing from languages.csv: {missing_languages}")

    ready_isos = sorted(readiness_by_iso)
    processed_total = sum(require_integer(readiness_by_iso[iso], "actual_pairs", "curation_readiness.csv") for iso in ready_isos)
    benchmark_total = sum(require_integer(freezes_by_iso[iso], "benchmark_pairs", "benchmark_freeze.csv") for iso in ready_isos)
    restricted_total = sum(
        readiness_by_iso[iso]["publication_handling"] == "restricted_local" for iso in ready_isos
    )
    checks = {
        "tracks": (len(ready_isos), config["expected_tracks"]),
        "processed_pairs": (processed_total, config["expected_processed_pairs"]),
        "restricted_tracks": (restricted_total, config["expected_restricted_tracks"]),
        "benchmark_pairs": (benchmark_total, config["expected_benchmark_pairs"]),
    }
    mismatches = [f"{name}: actual={actual}, expected={expected}" for name, (actual, expected) in checks.items() if actual != expected]
    if mismatches:
        raise ImportError("reconciliation failed: " + "; ".join(mismatches))

    if output_dir.exists():
        shutil.rmtree(output_dir)
    source_id = f"source-congolangbench-{actual_commit[:12]}"
    source_record = {
        "entity_type": "source",
        "id": source_id,
        "citation": f"CongoLangBench registry snapshot, commit {actual_commit}",
        "url": f"{config['repository_url']}/tree/{actual_commit}/registry",
        "publisher": "CongoLangBench",
        "authors": [],
        "retrieved_at": config["retrieved_at"],
        "source_type": "primary-dataset",
        "licence_id": None,
        "verification_status": "draft",
        "verification_notes": "Automated allow-listed metadata import; manual field-level review is required before publication.",
        "last_reviewed_at": config["retrieved_at"],
    }
    write_json(output_dir / "sources" / f"{source_id}.json", source_record)

    referenced_override_sources = {
        override["source_id"]
        for iso, override in overrides.get("tracks", {}).items()
        if iso in ready_isos
    }
    missing_override_sources = sorted(referenced_override_sources - set(overrides.get("sources", {})))
    if missing_override_sources:
        raise ImportError(f"resource overrides reference missing sources: {missing_override_sources}")
    for override_source_id in sorted(referenced_override_sources):
        item = overrides["sources"][override_source_id]
        write_json(output_dir / "sources" / f"{override_source_id}.json", {
            "entity_type": "source",
            "id": override_source_id,
            "citation": item["citation"],
            "url": item["url"],
            "publisher": item["publisher"],
            "authors": [],
            "retrieved_at": overrides["reviewed_at"],
            "source_type": item["source_type"],
            "licence_id": item["licence_id"],
            "verification_status": "source-checked",
            "verification_notes": item["verification_notes"],
            "last_reviewed_at": overrides["reviewed_at"],
        })

    warnings: list[dict[str, str]] = []
    for iso in ready_isos:
        language_row = languages_by_iso[iso]
        ready_row = readiness_by_iso[iso]
        freeze_row = freezes_by_iso[iso]
        language_id = f"language-{iso}"
        alternate_names = []
        variety = language_row["variety"].strip()
        if variety and variety.casefold() != language_row["language"].strip().casefold():
            alternate_names.append(
                {"name": variety, "source_id": source_id, "usage_note": "CongoLangBench variety label; requires identity review."}
            )
        language_record = {
            "entity_type": "language",
            "id": language_id,
            "preferred_name": language_row["language"].strip(),
            "identifiers": {"iso_639_3": iso},
            "alternate_names": alternate_names,
            "variety_of": None,
            "classification_note": (
                f"Imported as a distinct CongoLangBench track ({language_row['track']}, "
                f"{language_row['region_group']}). Project groupings are not geographic evidence."
            ),
            "status": "draft",
            "verification_status": "draft",
            "citations": [{"source_id": source_id, "locator": f"registry/languages.csv; ISO {iso}"}],
            "last_reviewed_at": config["retrieved_at"],
        }
        write_json(output_dir / "languages" / f"{language_id}.json", language_record)

        restricted = ready_row["publication_handling"] == "restricted_local"
        handling_note = (
            "Restricted-local track: corpus contents and local paths are excluded from the atlas export."
            if restricted
            else "Metadata-only import; original source licences require field-level review before any reuse claim."
        )
        bitext_id = f"resource-congolangbench-{iso}-bitext"
        override = overrides.get("tracks", {}).get(iso)
        bitext_record = {
            "entity_type": "resource",
            "id": bitext_id,
            "title": f"CongoLangBench {language_row['language']} curated bitext track",
            "resource_type": "bitext",
            "modalities": ["text", "tabular"],
            "languages": [{
                "language_id": language_id,
                "provenance_note": f"CongoLangBench track paired with {ready_row['reference_language']}; DRC provenance requires manual review."
            }],
            "geographic_scope": "uncertain" if "cross_border" in language_row["status"] else "drc-labelled",
            "publisher": "CongoLangBench",
            "creators": [],
            "version": actual_commit,
            "published_at": None,
            "retrieved_at": config["retrieved_at"],
            "homepage_url": directory_url(config["repository_url"], actual_commit, resource_root(ready_row["processed_csv"])),
            "download_url": None,
            "access_type": "unavailable" if restricted else "catalogue-only",
            "licence_id": None,
            "terms_url": None,
            "terms_checked_at": None,
            "redistribution": "restricted" if restricted else "metadata-only",
            "size": require_integer(ready_row, "actual_pairs", "curation_readiness.csv"),
            "unit": "parallel-pairs",
            "format": "CSV",
            "domain": None,
            "source_id": source_id,
            "verification_status": "draft",
            "limitations": handling_note,
            "last_reviewed_at": config["retrieved_at"],
        }
        if override:
            bitext_record.update({
                "geographic_scope": override["geographic_scope"],
                "homepage_url": override["homepage_url"],
                "download_url": override["download_url"],
                "access_type": override["access_type"],
                "licence_id": override["licence_id"],
                "terms_url": override["terms_url"],
                "terms_checked_at": overrides["reviewed_at"],
                "redistribution": override["redistribution"],
                "source_id": override["source_id"],
                "verification_status": "source-checked",
                "limitations": override["limitations"],
                "last_reviewed_at": overrides["reviewed_at"],
            })
        write_json(output_dir / "resources" / f"{bitext_id}.json", bitext_record)

        benchmark_id = f"resource-congolangbench-{iso}-benchmark-{freeze_row['benchmark_version']}"
        benchmark_record = {
            "entity_type": "resource",
            "id": benchmark_id,
            "title": f"CongoLangBench {language_row['language']} evaluation freeze {freeze_row['benchmark_version']}",
            "resource_type": "benchmark",
            "modalities": ["text", "tabular"],
            "languages": [{"language_id": language_id, "provenance_note": f"Frozen {freeze_row['benchmark_split']} split paired with {freeze_row['reference_language']}."}],
            "geographic_scope": bitext_record["geographic_scope"],
            "publisher": "CongoLangBench",
            "creators": [],
            "version": freeze_row["benchmark_version"],
            "published_at": None,
            "retrieved_at": config["retrieved_at"],
            "homepage_url": record_url(config["repository_url"], actual_commit, "registry/benchmark_freeze.csv"),
            "download_url": None,
            "access_type": "unavailable",
            "licence_id": None,
            "terms_url": None,
            "terms_checked_at": None,
            "redistribution": "restricted" if restricted else "metadata-only",
            "size": require_integer(freeze_row, "benchmark_pairs", "benchmark_freeze.csv"),
            "unit": "parallel-pairs",
            "format": "CSV",
            "domain": None,
            "source_id": source_id,
            "verification_status": "draft",
            "limitations": "Frozen-local evaluation metadata only; sentence text, prompts, and outputs are excluded.",
            "last_reviewed_at": config["retrieved_at"],
        }
        write_json(output_dir / "resources" / f"{benchmark_id}.json", benchmark_record)
        if "cross_border" in language_row["status"] or "unspecified" in language_row["status"]:
            warnings.append({"iso_code": iso, "status": language_row["status"], "review": "geographic provenance or variety identity"})

    validation_errors = validate_catalog(output_dir)
    if validation_errors:
        raise ImportError("generated catalogue validation failed: " + "; ".join(validation_errors))

    report = {
        "source_commit": actual_commit,
        "retrieved_at": config["retrieved_at"],
        "inputs": {
            filename: {"sha256": sha256_file(registry_dir / filename), "allow_listed_fields": sorted(fields)}
            for filename, fields in REGISTRY_FIELDS.items()
        },
        "reconciliation": {name: {"actual": actual, "expected": expected, "matches": actual == expected} for name, (actual, expected) in checks.items()},
        "metadata_overrides": {
            "path": str(overrides_path.relative_to(ROOT)) if overrides_path and overrides_path.is_relative_to(ROOT) else None,
            "sha256": sha256_file(overrides_path) if overrides_path and overrides_path.exists() else None,
            "applied_tracks": sorted(set(ready_isos) & set(overrides.get("tracks", {}))),
        },
        "generated_records": {
            "sources": 1 + len(referenced_override_sources),
            "languages": len(ready_isos),
            "resources": len(ready_isos) * 2,
            "total": 1 + len(referenced_override_sources) + len(ready_isos) * 3,
        },
        "excluded_language_candidates": sorted(set(languages_by_iso) - set(ready_isos)),
        "manual_review_warnings": warnings,
        "forbidden_content_imported": False,
        "passed": True,
    }
    write_json(report_path, report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="path to the pinned CongoLangBench repository")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--overrides", type=Path, default=DEFAULT_OVERRIDES)
    args = parser.parse_args(argv)
    try:
        report = import_metadata(args.source.resolve(), args.config, args.output, args.report, args.overrides)
    except (ImportError, subprocess.CalledProcessError) as exc:
        print(f"CongoLangBench import failed: {exc}", file=sys.stderr)
        return 1
    counts = report["generated_records"]
    print(f"Imported {counts['languages']} tracks into {counts['total']} validated draft records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
