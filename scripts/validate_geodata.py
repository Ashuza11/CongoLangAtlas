#!/usr/bin/env python3
"""Validate the pinned geographic-source manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from jsonschema import FormatChecker
from jsonschema.validators import validator_for

from scripts.validate_catalog import DEFAULT_SCHEMA_DIR, build_registry, load_json


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "public" / "geodata" / "sources.json"


def validate_manifest(manifest_path: Path, schema_dir: Path = DEFAULT_SCHEMA_DIR) -> list[str]:
    registry, schemas = build_registry(schema_dir)
    schema = schemas["geodata-manifest.schema.json"]
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    validator = validator_class(schema, registry=registry, format_checker=FormatChecker())
    manifest = load_json(manifest_path)

    errors = [
        f"{'.'.join(str(part) for part in error.absolute_path) or '$'}: {error.message}"
        for error in validator.iter_errors(manifest)
    ]

    ids = [source.get("id") for source in manifest.get("sources", [])]
    if len(ids) != len(set(ids)):
        errors.append("source ids must be unique")
    levels = [source.get("admin_level") for source in manifest.get("sources", [])]
    if len(levels) != len(set(levels)):
        errors.append("only one selected source is allowed per administrative level")
    return sorted(errors)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--schema-dir", type=Path, default=DEFAULT_SCHEMA_DIR)
    args = parser.parse_args(argv)
    errors = validate_manifest(args.manifest, args.schema_dir)
    if errors:
        print(f"Geodata manifest validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Validated geographic-source manifest.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
