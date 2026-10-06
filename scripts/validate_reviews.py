#!/usr/bin/env python3
"""Validate version-controlled CongoLangBench review decisions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.validators import validator_for

from scripts.validate_catalog import (
    DEFAULT_SCHEMA_DIR,
    DuplicateKeyError,
    ROOT,
    build_registry,
    load_json,
)


DEFAULT_DECISIONS_DIR = ROOT / "data" / "reviews" / "congolangbench"
DEFAULT_IMPORT_CONFIG = ROOT / "data" / "import" / "congolangbench.json"


def validate_reviews(
    decisions_dir: Path = DEFAULT_DECISIONS_DIR,
    import_config: Path = DEFAULT_IMPORT_CONFIG,
    schema_dir: Path = DEFAULT_SCHEMA_DIR,
) -> list[str]:
    errors: list[str] = []
    try:
        config = load_json(import_config)
    except (OSError, json.JSONDecodeError, DuplicateKeyError) as exc:
        return [f"{import_config}: invalid import configuration: {exc}"]

    registry, schemas = build_registry(schema_dir)
    schema = schemas["import-review-decision.schema.json"]
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    validator = validator_class(schema, registry=registry, format_checker=FormatChecker())
    seen_isos: dict[str, Path] = {}
    decisions: list[tuple[Path, dict[str, Any]]] = []

    for path in sorted(decisions_dir.glob("*.json")):
        try:
            decision = load_json(path)
        except (json.JSONDecodeError, DuplicateKeyError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(decision, dict):
            errors.append(f"{path}: review decision must be a JSON object")
            continue
        for error in sorted(validator.iter_errors(decision), key=lambda item: list(item.absolute_path)):
            location = ".".join(str(part) for part in error.absolute_path)
            errors.append(f"{path}{':' + location if location else ''}: {error.message}")
        decisions.append((path, decision))

        iso = decision.get("iso_639_3")
        if not isinstance(iso, str):
            continue
        if path.stem != iso:
            errors.append(f"{path}: filename must match ISO code {iso!r}")
        if iso in seen_isos:
            errors.append(f"{path}: duplicate review decision for {iso}; first declared in {seen_isos[iso]}")
        else:
            seen_isos[iso] = path

    expected_commit = config.get("source_commit")
    for path, decision in decisions:
        if decision.get("source_commit") != expected_commit:
            errors.append(f"{path}: source_commit does not match the pinned import")

    expected_tracks = config.get("expected_tracks")
    if isinstance(expected_tracks, int) and len(seen_isos) != expected_tracks:
        errors.append(
            f"{decisions_dir}: expected {expected_tracks} unique review decisions, found {len(seen_isos)}"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decisions", nargs="?", type=Path, default=DEFAULT_DECISIONS_DIR)
    parser.add_argument("--import-config", type=Path, default=DEFAULT_IMPORT_CONFIG)
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    args = parser.parse_args(argv)

    errors = validate_reviews(args.decisions, args.import_config, args.schema_dir)
    if errors:
        print(f"Review validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    count = sum(1 for _ in args.decisions.glob("*.json"))
    print(f"Validated {count} review decision(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
