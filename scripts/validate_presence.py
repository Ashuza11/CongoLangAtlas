#!/usr/bin/env python3
"""Validate pinned presence sources and named-human review decisions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.build_presence_candidates import DEFAULT_MANIFEST, DEFAULT_REVIEWS, _validate_document
from scripts.validate_catalog import load_json


def validate_presence(manifest_path: Path = DEFAULT_MANIFEST, review_dir: Path = DEFAULT_REVIEWS) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(manifest_path)
    except Exception as exc:
        return [f"{manifest_path}: cannot load manifest: {exc}"]
    errors.extend(
        f"{manifest_path}: {message}"
        for message in _validate_document(manifest, "presence-source-manifest.schema.json")
    )
    seen: dict[str, Path] = {}
    for path in sorted(review_dir.glob("*.json")):
        try:
            decision = load_json(path)
        except Exception as exc:
            errors.append(f"{path}: cannot load decision: {exc}")
            continue
        errors.extend(
            f"{path}: {message}"
            for message in _validate_document(decision, "presence-review-decision.schema.json")
        )
        candidate_id = decision.get("candidate_id")
        if candidate_id in seen:
            errors.append(f"{path}: duplicate decision; first declared in {seen[candidate_id]}")
        elif candidate_id:
            seen[candidate_id] = path
        if decision.get("decision") == "approve" and any(
            value != "approved" for value in decision.get("checks", {}).values()
        ):
            errors.append(f"{path}: approval requires every check to be approved")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    args = parser.parse_args(argv)
    errors = validate_presence(args.manifest, args.reviews)
    if errors:
        print(f"Presence validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Validated presence-source manifest and {len(list(args.reviews.glob('*.json')))} decision(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
