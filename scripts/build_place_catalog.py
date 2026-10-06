#!/usr/bin/env python3
"""Build catalogue place records from validated administrative GeoJSON layers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.validate_catalog import ROOT, load_json, validate_catalog
from scripts.validate_geodata import DEFAULT_MANIFEST, validate_manifest


DEFAULT_GEODATA = ROOT / "public" / "generated" / "geodata"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "places"


class PlaceBuildError(RuntimeError):
    """Raised when administrative features cannot become valid place records."""


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _source_record(source: dict[str, Any], reviewed_at: str) -> dict[str, Any]:
    organizations = source.get("source_organizations", [])
    organization_label = " and ".join(organizations) if organizations else source["provider"]
    return {
        "entity_type": "source",
        "id": source["id"],
        "citation": f"{organization_label}, {source['canonical_name']} ({source['boundary_year']})",
        "url": source["metadata_url"],
        "publisher": f"{organization_label} via {source['provider']}",
        "published_at": source["source_updated_at"],
        "retrieved_at": reviewed_at,
        "source_type": "primary-dataset",
        "licence_id": "CC-BY-4.0",
        "verification_status": source["review_status"],
        "verification_notes": "Checksum-pinned administrative geometry; suitable for navigation context, never language boundaries.",
        "last_reviewed_at": reviewed_at,
    }


def _place_id(geometry_id: str) -> str:
    return f"place-{geometry_id}"


def _load_layer(path: Path, expected_level: str) -> list[dict[str, Any]]:
    if not path.exists():
        raise PlaceBuildError(f"missing generated layer: {path}")
    document = load_json(path)
    if document.get("type") != "FeatureCollection":
        raise PlaceBuildError(f"{path}: expected a GeoJSON FeatureCollection")
    features = document.get("features", [])
    for index, feature in enumerate(features):
        properties = feature.get("properties") or {}
        if properties.get("admin_level") != expected_level:
            raise PlaceBuildError(f"{path}: feature {index} is not {expected_level}")
        if not properties.get("id") or not properties.get("name") or not properties.get("source_id"):
            raise PlaceBuildError(f"{path}: feature {index} lacks place metadata")
    return features


def build_place_catalog(
    manifest_path: Path = DEFAULT_MANIFEST,
    geodata_dir: Path = DEFAULT_GEODATA,
    output_dir: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    manifest_errors = validate_manifest(manifest_path)
    if manifest_errors:
        raise PlaceBuildError("invalid geographic-source manifest: " + "; ".join(manifest_errors))
    manifest = load_json(manifest_path)
    reviewed_at = manifest["reviewed_at"]
    adm1 = _load_layer(geodata_dir / "cod-adm1.geojson", "ADM1")
    adm2 = _load_layer(geodata_dir / "cod-adm2.geojson", "ADM2")
    source_ids = {source["id"] for source in manifest["sources"]}

    catalog_dir = output_dir / "catalog"
    source_dir = catalog_dir / "sources"
    place_dir = catalog_dir / "places"
    source_dir.mkdir(parents=True, exist_ok=True)
    place_dir.mkdir(parents=True, exist_ok=True)

    expected_paths: set[Path] = set()
    for source in manifest["sources"]:
        path = source_dir / f"{source['id']}.json"
        _write_json(path, _source_record(source, reviewed_at))
        expected_paths.add(path)

    country_source = next(source for source in manifest["sources"] if source["admin_level"] == "ADM1")
    country = {
        "entity_type": "place",
        "id": "place-cod",
        "name": "Democratic Republic of Congo",
        "admin_level": "country",
        "parent_id": None,
        "geometry_id": None,
        "source_id": country_source["id"],
        "verification_status": country_source["review_status"],
        "last_reviewed_at": reviewed_at,
    }
    country_path = place_dir / "place-cod.json"
    _write_json(country_path, country)
    expected_paths.add(country_path)

    counts = {"country": 1, "province": 0, "territory": 0}
    for feature in [*adm1, *adm2]:
        properties = feature["properties"]
        if properties["source_id"] not in source_ids:
            raise PlaceBuildError(f"{properties['id']}: unknown geographic source {properties['source_id']}")
        is_province = properties["admin_level"] == "ADM1"
        admin_level = "province" if is_province else "territory"
        parent_geometry_id = properties.get("parent_id")
        if not is_province and not parent_geometry_id:
            raise PlaceBuildError(f"{properties['id']}: ADM2 feature has no parent")
        record = {
            "entity_type": "place",
            "id": _place_id(properties["id"]),
            "name": properties["name"],
            "admin_level": admin_level,
            "parent_id": "place-cod" if is_province else _place_id(parent_geometry_id),
            "geometry_id": properties["id"],
            "source_id": properties["source_id"],
            "verification_status": "source-checked",
            "last_reviewed_at": reviewed_at,
        }
        path = place_dir / f"{record['id']}.json"
        _write_json(path, record)
        expected_paths.add(path)
        counts[admin_level] += 1

    for path in [*source_dir.glob("*.json"), *place_dir.glob("*.json")]:
        if path not in expected_paths:
            path.unlink()

    catalog_errors = validate_catalog(catalog_dir)
    if catalog_errors:
        raise PlaceBuildError("generated place catalogue is invalid: " + "; ".join(catalog_errors))
    summary = {
        "generated_at": reviewed_at,
        "source_manifest": str(manifest_path.relative_to(ROOT)) if manifest_path.is_relative_to(ROOT) else str(manifest_path),
        "sources": len(manifest["sources"]),
        **counts,
        "total_places": sum(counts.values()),
    }
    _write_json(output_dir / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--geodata", type=Path, default=DEFAULT_GEODATA)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    try:
        summary = build_place_catalog(args.manifest, args.geodata, args.output)
    except PlaceBuildError as exc:
        print(f"Place catalogue build failed: {exc}", file=sys.stderr)
        return 1
    print(
        f"Built {summary['total_places']} places: {summary['province']} provinces and "
        f"{summary['territory']} second-level areas."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
