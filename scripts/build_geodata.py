#!/usr/bin/env python3
"""Build reproducible web map layers from checksum-pinned source geometry."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity

from scripts.validate_catalog import load_json
from scripts.validate_geodata import DEFAULT_MANIFEST, validate_manifest


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = ROOT / "data" / "generated" / "geodata" / "source"
DEFAULT_OUTPUT_DIR = ROOT / "public" / "generated" / "geodata"
DEFAULT_REPORT = ROOT / "data" / "generated" / "geodata" / "quality-report.json"
SIMPLIFICATION_TOLERANCE = {"ADM1": 0.01, "ADM2": 0.005}


class BuildError(RuntimeError):
    """Raised when source integrity or geometry quality blocks a build."""


@dataclass(frozen=True)
class Feature:
    atlas_id: str
    source_id: str
    source_feature_id: str
    source_name: str
    name: str
    admin_level: str
    source_code: str | None
    parent_source_code: str | None
    geometry: BaseGeometry


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_name(value: str) -> str:
    """Apply only lossless display normalization; preserve source text separately."""
    return " ".join(unicodedata.normalize("NFC", value).split())


def source_path(source: dict[str, Any], source_dir: Path) -> Path:
    return source_dir / f"{source['id']}.geojson"


def acquire_source(source: dict[str, Any], source_dir: Path, offline: bool = False) -> Path:
    destination = source_path(source, source_dir)
    if destination.exists() and sha256_file(destination) == source["sha256"]:
        return destination
    if offline:
        raise BuildError(f"{source['id']}: verified cached source is unavailable in offline mode")

    source_dir.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".geojson.tmp")
    request = urllib.request.Request(
        source["download_url"], headers={"User-Agent": "CongoLangAtlas geodata builder/0.1"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        raise BuildError(f"{source['id']}: download failed: {exc}") from exc

    actual_checksum = sha256_file(temporary)
    if actual_checksum != source["sha256"]:
        temporary.unlink(missing_ok=True)
        raise BuildError(
            f"{source['id']}: checksum mismatch; expected {source['sha256']}, got {actual_checksum}"
        )
    temporary.replace(destination)
    return destination


def load_source_document(source: dict[str, Any], path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    decoder = json.JSONDecoder()
    try:
        document, end = decoder.raw_decode(text)
    except json.JSONDecodeError as exc:
        raise BuildError(f"{source['id']}: invalid source JSON: {exc}") from exc
    trailing = text[end:].strip()
    allowed_marker = "strip-trailing-system-io-memorystream" in source["preprocessing"]
    if trailing and not (allowed_marker and trailing == "System.IO.MemoryStream"):
        raise BuildError(f"{source['id']}: unexpected trailing source content")
    return document


def load_features(source: dict[str, Any], path: Path) -> tuple[list[Feature], list[str]]:
    document = load_source_document(source, path)
    errors: list[str] = []
    if document.get("type") != "FeatureCollection" or not isinstance(document.get("features"), list):
        raise BuildError(f"{source['id']}: expected a GeoJSON FeatureCollection")
    if len(document["features"]) != source["feature_count"]:
        errors.append(
            f"feature count is {len(document['features'])}; expected {source['feature_count']}"
        )

    features: list[Feature] = []
    seen_ids: set[str] = set()
    fields = source["fields"]
    for index, raw_feature in enumerate(document["features"]):
        properties = raw_feature.get("properties") or {}
        source_feature_id = str(properties.get(fields["id"]) or "").strip()
        source_name = str(properties.get(fields["name"]) or "").strip()
        source_code = str(properties.get(fields["code"]) or "").strip() or None
        parent_field = fields.get("parent_code")
        parent_source_code = str(properties.get(parent_field) or "").strip() or None if parent_field else None
        geometry_type = (raw_feature.get("geometry") or {}).get("type")
        label = source_feature_id or f"feature-{index}"
        if not source_feature_id:
            errors.append(f"feature {index} has no shapeID")
        elif source_feature_id in seen_ids:
            errors.append(f"duplicate shapeID {source_feature_id}")
        seen_ids.add(source_feature_id)
        if not source_name:
            errors.append(f"{label} has no shapeName")
        if geometry_type not in source["geometry_types"]:
            errors.append(f"{label} has unexpected geometry type {geometry_type!r}")
            continue
        try:
            geometry = shape(raw_feature["geometry"])
        except Exception as exc:
            errors.append(f"{label} cannot be parsed as geometry: {exc}")
            continue
        if geometry.is_empty:
            errors.append(f"{label} has empty geometry")
        elif not geometry.is_valid:
            errors.append(f"{label} has invalid geometry: {explain_validity(geometry)}")

        atlas_id = f"cod-{source['admin_level'].lower()}-{source_feature_id.lower()}"
        features.append(
            Feature(
                atlas_id=atlas_id,
                source_id=source["id"],
                source_feature_id=source_feature_id,
                source_name=source_name,
                name=normalize_name(source_name),
                admin_level=source["admin_level"],
                source_code=source_code,
                parent_source_code=parent_source_code,
                geometry=geometry,
            )
        )
    return features, errors


def coordinate_count(geometry: BaseGeometry) -> int:
    if geometry.geom_type == "Polygon":
        return len(geometry.exterior.coords) + sum(len(ring.coords) for ring in geometry.interiors)
    if geometry.geom_type == "MultiPolygon":
        return sum(coordinate_count(part) for part in geometry.geoms)
    return 0


def find_overlaps(features: list[Feature], tolerance: float = 1e-12) -> list[dict[str, Any]]:
    overlaps: list[dict[str, Any]] = []
    for left_index, left in enumerate(features):
        for right in features[left_index + 1 :]:
            if not left.geometry.bounds or not right.geometry.bounds:
                continue
            if not left.geometry.intersects(right.geometry):
                continue
            intersection_area = left.geometry.intersection(right.geometry).area
            if intersection_area > tolerance:
                overlaps.append(
                    {
                        "left_id": left.atlas_id,
                        "right_id": right.atlas_id,
                        "area_square_degrees": round(intersection_area, 12),
                    }
                )
    return overlaps


def assign_parents(
    children: list[Feature], parents: list[Feature]
) -> tuple[dict[str, str], list[str], list[dict[str, Any]]]:
    assignments: dict[str, str] = {}
    unassigned: list[str] = []
    ambiguous: list[dict[str, Any]] = []
    parents_by_code = {parent.source_code: parent for parent in parents if parent.source_code}
    for child in children:
        declared_parent = parents_by_code.get(child.parent_source_code)
        if declared_parent:
            matches = [declared_parent]
        else:
            point = child.geometry.representative_point()
            matches = [parent for parent in parents if parent.geometry.covers(point)]
        if len(matches) == 1:
            assignments[child.atlas_id] = matches[0].atlas_id
        elif not matches:
            unassigned.append(child.atlas_id)
        else:
            ambiguous.append(
                {"child_id": child.atlas_id, "candidate_parent_ids": [item.atlas_id for item in matches]}
            )
    return assignments, unassigned, ambiguous


def check_parent_containment(
    children: list[Feature], parents: list[Feature], assignments: dict[str, str], tolerance: float = 0.0001
) -> tuple[list[dict[str, Any]], float]:
    parent_by_id = {parent.atlas_id: parent for parent in parents}
    issues: list[dict[str, Any]] = []
    maximum_ratio = 0.0
    for child in children:
        parent_id = assignments.get(child.atlas_id)
        if not parent_id or child.geometry.area == 0:
            continue
        outside_ratio = child.geometry.difference(parent_by_id[parent_id].geometry).area / child.geometry.area
        maximum_ratio = max(maximum_ratio, outside_ratio)
        if outside_ratio > tolerance:
            issues.append(
                {
                    "child_id": child.atlas_id,
                    "parent_id": parent_id,
                    "outside_area_ratio": round(outside_ratio, 12),
                }
            )
    return issues, maximum_ratio


def serialize_layer(
    features: list[Feature], parent_ids: dict[str, str], tolerance: float
) -> tuple[dict[str, Any], int, int]:
    output_features: list[dict[str, Any]] = []
    input_vertices = 0
    output_vertices = 0
    for feature in sorted(features, key=lambda item: item.atlas_id):
        simplified = feature.geometry.simplify(tolerance, preserve_topology=True)
        input_vertices += coordinate_count(feature.geometry)
        output_vertices += coordinate_count(simplified)
        properties: dict[str, Any] = {
            "id": feature.atlas_id,
            "name": feature.name,
            "source_name": feature.source_name,
            "source_feature_id": feature.source_feature_id,
            "source_id": feature.source_id,
            "admin_level": feature.admin_level,
            "source_code": feature.source_code,
        }
        if feature.admin_level == "ADM2":
            properties["parent_id"] = parent_ids.get(feature.atlas_id)
        output_features.append(
            {"type": "Feature", "properties": properties, "geometry": mapping(simplified)}
        )
    return {"type": "FeatureCollection", "features": output_features}, input_vertices, output_vertices


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def build(
    manifest_path: Path = DEFAULT_MANIFEST,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_path: Path = DEFAULT_REPORT,
    offline: bool = False,
) -> dict[str, Any]:
    manifest_errors = validate_manifest(manifest_path)
    if manifest_errors:
        raise BuildError("invalid source manifest: " + "; ".join(manifest_errors))
    manifest = load_json(manifest_path)

    by_level: dict[str, list[Feature]] = {}
    source_reports: list[dict[str, Any]] = []
    critical_errors: list[str] = []
    for source in manifest["sources"]:
        path = acquire_source(source, source_dir, offline=offline)
        features, errors = load_features(source, path)
        by_level[source["admin_level"]] = features
        critical_errors.extend(f"{source['id']}: {error}" for error in errors)
        source_reports.append(
            {
                "source_id": source["id"],
                "sha256": sha256_file(path),
                "feature_count": len(features),
                "geometry_errors": errors,
            }
        )

    adm1 = by_level.get("ADM1", [])
    adm2 = by_level.get("ADM2", [])
    if not adm1 or not adm2:
        critical_errors.append("both ADM1 and ADM2 sources are required")
    assignments, unassigned, ambiguous = assign_parents(adm2, adm1)
    containment_issues, maximum_outside_ratio = check_parent_containment(adm2, adm1, assignments)
    critical_errors.extend(f"unassigned ADM2 feature {item}" for item in unassigned)
    critical_errors.extend(f"ambiguous ADM2 parent for {item['child_id']}" for item in ambiguous)
    critical_errors.extend(
        f"ADM2 feature {item['child_id']} extends outside parent by {item['outside_area_ratio']:.6%}"
        for item in containment_issues
    )

    layers: dict[str, Any] = {}
    for level, features in (("ADM1", adm1), ("ADM2", adm2)):
        tolerance = SIMPLIFICATION_TOLERANCE[level]
        document, input_vertices, output_vertices = serialize_layer(features, assignments, tolerance)
        output_path = output_dir / f"cod-{level.lower()}.geojson"
        write_json(output_path, document)
        layers[level] = {
            "feature_count": len(features),
            "input_vertices": input_vertices,
            "output_vertices": output_vertices,
            "simplification_tolerance_degrees": tolerance,
            "output": display_path(output_path),
            "output_sha256": sha256_file(output_path),
            "overlaps": find_overlaps(features),
        }

    report = {
        "manifest_version": manifest["manifest_version"],
        "country_iso3": manifest["country_iso3"],
        "source_manifest": display_path(manifest_path),
        "sources": source_reports,
        "layers": layers,
        "parent_assignment": {
            "assigned": len(assignments),
            "unassigned": unassigned,
            "ambiguous": ambiguous,
            "containment_tolerance": 0.0001,
            "maximum_outside_area_ratio": round(maximum_outside_ratio, 12),
            "containment_issues": containment_issues,
        },
        "critical_errors": critical_errors,
        "passed": not critical_errors,
    }
    write_json(report_path, report)
    if critical_errors:
        raise BuildError(f"quality gate failed with {len(critical_errors)} critical error(s)")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--offline", action="store_true", help="require verified cached downloads")
    args = parser.parse_args(argv)
    try:
        report = build(args.manifest, args.source_dir, args.output_dir, args.report, args.offline)
    except BuildError as exc:
        print(f"Geodata build failed: {exc}", file=sys.stderr)
        return 1
    print(
        "Built DRC administrative layers: "
        f"{report['layers']['ADM1']['feature_count']} ADM1 and "
        f"{report['layers']['ADM2']['feature_count']} ADM2 features."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
