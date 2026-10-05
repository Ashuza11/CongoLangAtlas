#!/usr/bin/env python3
"""Validate catalogue records and enforce public-release safety rules."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from jsonschema import FormatChecker
from jsonschema.validators import validator_for
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA_DIR = ROOT / "data" / "schema"
DEFAULT_CATALOG_DIR = ROOT / "data" / "catalog"

SCHEMAS = {
    "source": "source.schema.json",
    "language": "language.schema.json",
    "place": "place.schema.json",
    "language_presence_claim": "language-presence-claim.schema.json",
    "resource": "resource.schema.json",
    "publication": "publication.schema.json",
    "nlp_result": "nlp-result.schema.json",
    "review_event": "review-event.schema.json",
}

FORBIDDEN_PUBLIC_FIELDS = {
    "source_text",
    "target_text",
    "source_sentence",
    "target_sentence",
    "raw_text",
    "transcript",
    "audio_data",
    "model_prompt",
    "model_output",
    "access_token",
    "api_key",
    "password",
    "private_contact",
    "local_path",
}


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains a repeated field name."""


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    counts = Counter(key for key, _ in pairs)
    duplicates = sorted(key for key, count in counts.items() if count > 1)
    if duplicates:
        raise DuplicateKeyError(f"duplicate field(s): {', '.join(duplicates)}")
    return dict(pairs)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle, object_pairs_hook=_no_duplicate_keys)


def build_registry(schema_dir: Path) -> tuple[Registry, dict[str, dict[str, Any]]]:
    registry = Registry()
    schemas: dict[str, dict[str, Any]] = {}
    for path in sorted(schema_dir.glob("*.schema.json")):
        schema = load_json(path)
        schemas[path.name] = schema
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return registry, schemas


def _format_path(parts: Iterable[Any]) -> str:
    rendered = "$"
    for part in parts:
        rendered += f"[{part}]" if isinstance(part, int) else f".{part}"
    return rendered


def _scan_forbidden(value: Any, path: tuple[Any, ...] = ()) -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = (*path, key)
            if key.lower() in FORBIDDEN_PUBLIC_FIELDS:
                errors.append(f"{_format_path(child_path)} is forbidden in public metadata")
            errors.extend(_scan_forbidden(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_scan_forbidden(child, (*path, index)))
    elif isinstance(value, str) and value.startswith(("file://", "/home/", "/Users/")):
        errors.append(f"{_format_path(path)} exposes a local filesystem path")
    return errors


def _reference_pairs(record: dict[str, Any]) -> Iterable[tuple[str, str]]:
    kind = record.get("entity_type")
    if kind == "language":
        for index, citation in enumerate(record.get("citations", [])):
            yield f"citations[{index}].source_id", citation["source_id"]
        for index, name in enumerate(record.get("alternate_names", [])):
            yield f"alternate_names[{index}].source_id", name["source_id"]
        if record.get("variety_of"):
            yield "variety_of", record["variety_of"]
    elif kind == "place":
        yield "source_id", record.get("source_id")
        if record.get("parent_id"):
            yield "parent_id", record["parent_id"]
    elif kind == "language_presence_claim":
        for field in ("language_id", "place_id", "source_id"):
            yield field, record.get(field)
    elif kind == "resource":
        yield "source_id", record.get("source_id")
        for index, language in enumerate(record.get("languages", [])):
            yield f"languages[{index}].language_id", language["language_id"]
    elif kind == "publication":
        yield "source_id", record.get("source_id")
        for index, language_id in enumerate(record.get("languages", [])):
            yield f"languages[{index}]", language_id
    elif kind == "nlp_result":
        for field in ("language_id", "benchmark_id", "result_source_id"):
            yield field, record.get(field)
    elif kind == "review_event":
        yield "record_id", record.get("record_id")
        for index, source_id in enumerate(record.get("evidence_source_ids", [])):
            yield f"evidence_source_ids[{index}]", source_id


def validate_catalog(catalog_dir: Path, schema_dir: Path = DEFAULT_SCHEMA_DIR) -> list[str]:
    registry, schemas = build_registry(schema_dir)
    errors: list[str] = []
    records: list[tuple[Path, dict[str, Any]]] = []

    for path in sorted(catalog_dir.rglob("*.json")):
        try:
            record = load_json(path)
        except (json.JSONDecodeError, DuplicateKeyError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{path}: catalogue record must be a JSON object")
            continue

        kind = record.get("entity_type")
        schema_name = SCHEMAS.get(kind)
        if schema_name is None:
            errors.append(f"{path}: unknown entity_type {kind!r}")
            continue

        schema = schemas[schema_name]
        validator_class = validator_for(schema)
        validator_class.check_schema(schema)
        validator = validator_class(schema, registry=registry, format_checker=FormatChecker())
        for error in sorted(validator.iter_errors(record), key=lambda item: list(item.absolute_path)):
            errors.append(f"{path}:{_format_path(error.absolute_path)}: {error.message}")
        errors.extend(f"{path}:{message}" for message in _scan_forbidden(record))
        records.append((path, record))

    ids: dict[str, Path] = {}
    for path, record in records:
        record_id = record.get("id")
        if not isinstance(record_id, str):
            continue
        if record_id in ids:
            errors.append(f"{path}: duplicate id {record_id!r}; first declared in {ids[record_id]}")
        else:
            ids[record_id] = path

    for path, record in records:
        for field, target in _reference_pairs(record):
            if target and target not in ids:
                errors.append(f"{path}: {field} references missing record {target!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", nargs="?", type=Path, default=DEFAULT_CATALOG_DIR)
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    args = parser.parse_args(argv)

    errors = validate_catalog(args.catalog, args.schema_dir)
    if errors:
        print(f"Catalogue validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    count = sum(1 for _ in args.catalog.rglob("*.json"))
    print(f"Validated {count} catalogue record(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
