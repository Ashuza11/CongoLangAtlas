#!/usr/bin/env python3
"""Build reviewable language-place candidates from pinned Glottolog coordinates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.validators import validator_for
from shapely.geometry import Point, shape

from scripts.validate_catalog import DEFAULT_SCHEMA_DIR, ROOT, build_registry, load_json


DEFAULT_MANIFEST = ROOT / "data" / "presence" / "sources.json"
DEFAULT_LANGUAGES = ROOT / "data" / "generated" / "congolangbench" / "catalog" / "languages"
DEFAULT_PLACES = ROOT / "data" / "generated" / "places" / "catalog" / "places"
DEFAULT_GEODATA = ROOT / "public" / "generated" / "geodata"
DEFAULT_REVIEWS = ROOT / "data" / "presence" / "reviews"
DEFAULT_SOURCE_DIR = ROOT / "data" / "generated" / "presence" / "source"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "presence" / "candidates.json"


class PresenceBuildError(RuntimeError):
    """Raised when presence candidates cannot be built safely."""


def validate_presence_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate_ids: set[str] = set()
    mapped_ids: set[str] = set()
    allowed_statuses = {"no-coordinate-match", "representative-point-outside-drc", "mapped-candidate"}
    for index, candidate in enumerate(bundle.get("candidates", [])):
        prefix = f"candidates[{index}]"
        candidate_id = candidate.get("id")
        if not candidate_id or candidate_id in candidate_ids:
            errors.append(f"{prefix}: missing or duplicate id")
        candidate_ids.add(candidate_id)
        if candidate.get("match_status") not in allowed_statuses:
            errors.append(f"{prefix}: unsupported match status")
        if not str(candidate.get("source_url", "")).startswith("https://"):
            errors.append(f"{prefix}: source URL must use HTTPS")
        if candidate.get("match_status") == "mapped-candidate":
            mapped_ids.add(candidate_id)
            for field in ("province_place_id", "territory_place_id", "point", "evidence_locator", "limitations"):
                if not candidate.get(field):
                    errors.append(f"{prefix}: mapped candidate lacks {field}")
    for index, claim in enumerate(bundle.get("approved_claims", [])):
        candidate_id = str(claim.get("id", "")).removeprefix("claim-")
        if candidate_id not in mapped_ids:
            errors.append(f"approved_claims[{index}]: claim has no mapped candidate")
        for field in ("language_id", "place_id", "province_place_id", "source_id", "source_url", "evidence_locator"):
            if not claim.get(field):
                errors.append(f"approved_claims[{index}]: missing {field}")
    return errors


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _validate_document(value: Any, schema_name: str) -> list[str]:
    registry, schemas = build_registry(DEFAULT_SCHEMA_DIR)
    schema = schemas[schema_name]
    validator_class = validator_for(schema)
    validator_class.check_schema(schema)
    validator = validator_class(schema, registry=registry, format_checker=FormatChecker())
    return [error.message for error in sorted(validator.iter_errors(value), key=lambda item: list(item.absolute_path))]


def _acquire(source: dict[str, Any], source_dir: Path, offline: bool) -> Path:
    path = source_dir / f"{source['id']}.csv"
    if path.exists() and _sha256(path) == source["sha256"]:
        return path
    if offline:
        raise PresenceBuildError("verified Glottolog source is unavailable in offline mode")
    source_dir.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".csv.tmp")
    request = urllib.request.Request(
        source["download_url"], headers={"User-Agent": "CongoLangAtlas presence builder/0.1"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as output:
            while block := response.read(1024 * 1024):
                output.write(block)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        raise PresenceBuildError(f"Glottolog download failed: {exc}") from exc
    actual = _sha256(temporary)
    if actual != source["sha256"]:
        temporary.unlink(missing_ok=True)
        raise PresenceBuildError(f"Glottolog checksum mismatch: expected {source['sha256']}, got {actual}")
    temporary.replace(path)
    return path


def _records(path: Path) -> list[dict[str, Any]]:
    return [load_json(item) for item in sorted(path.glob("*.json"))]


def _features(path: Path) -> list[dict[str, Any]]:
    document = load_json(path)
    if document.get("type") != "FeatureCollection":
        raise PresenceBuildError(f"{path}: expected a GeoJSON FeatureCollection")
    return document["features"]


def _decision_map(review_dir: Path) -> dict[str, dict[str, Any]]:
    decisions: dict[str, dict[str, Any]] = {}
    for path in sorted(review_dir.glob("*.json")):
        decision = load_json(path)
        errors = _validate_document(decision, "presence-review-decision.schema.json")
        if errors:
            raise PresenceBuildError(f"{path}: invalid decision: {'; '.join(errors)}")
        candidate_id = decision["candidate_id"]
        if candidate_id in decisions:
            raise PresenceBuildError(f"duplicate decision for {candidate_id}")
        decisions[candidate_id] = decision
    return decisions


def build_presence_candidates(
    manifest_path: Path = DEFAULT_MANIFEST,
    language_dir: Path = DEFAULT_LANGUAGES,
    place_dir: Path = DEFAULT_PLACES,
    geodata_dir: Path = DEFAULT_GEODATA,
    review_dir: Path = DEFAULT_REVIEWS,
    source_dir: Path = DEFAULT_SOURCE_DIR,
    output: Path = DEFAULT_OUTPUT,
    offline: bool = False,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    manifest_errors = _validate_document(manifest, "presence-source-manifest.schema.json")
    if manifest_errors:
        raise PresenceBuildError("invalid presence-source manifest: " + "; ".join(manifest_errors))
    source = manifest["sources"][0]
    source_path = _acquire(source, source_dir, offline)
    with source_path.open(encoding="utf-8", newline="") as handle:
        rows = {row["ISO639P3code"]: row for row in csv.DictReader(handle) if row.get("ISO639P3code")}

    languages = sorted(_records(language_dir), key=lambda item: item["preferred_name"])
    places = _records(place_dir)
    place_by_geometry = {place.get("geometry_id"): place for place in places if place.get("geometry_id")}
    province_features = _features(geodata_dir / "cod-adm1.geojson")
    territory_features = _features(geodata_dir / "cod-adm2.geojson")
    decisions = _decision_map(review_dir)
    candidates = []
    approved_claims = []

    for language in languages:
        iso = language["identifiers"]["iso_639_3"]
        row = rows.get(iso)
        candidate_id = f"presence-glottolog-5-3-{iso}"
        base = {
            "id": candidate_id,
            "language_id": language["id"],
            "iso": iso,
            "language_name": language["preferred_name"],
            "source_id": source["id"],
            "source_version": source["version"],
            "source_url": source["landing_page"],
            "review_status": "candidate",
        }
        if not row or not row.get("Latitude") or not row.get("Longitude"):
            candidates.append({
                **base,
                "match_status": "no-coordinate-match",
                "limitations": "No one-to-one ISO language coordinate is available in the pinned Glottolog table.",
            })
            continue

        latitude = float(row["Latitude"])
        longitude = float(row["Longitude"])
        point = Point(longitude, latitude)
        province_matches = [feature for feature in province_features if shape(feature["geometry"]).covers(point)]
        territory_matches = [feature for feature in territory_features if shape(feature["geometry"]).covers(point)]
        common = {
            **base,
            "glottocode": row["Glottocode"],
            "source_language_name": row["Name"],
            "countries": row.get("Countries", "").split(";") if row.get("Countries") else [],
            "point": {"latitude": latitude, "longitude": longitude},
            "evidence_locator": f"cldf/languages.csv ISO639P3code={iso}, Glottocode={row['Glottocode']}",
        }
        if len(province_matches) != 1 or len(territory_matches) != 1:
            candidates.append({
                **common,
                "match_status": "representative-point-outside-drc",
                "limitations": "The cross-border language's Glottolog representative point falls outside the DRC administrative layers; this does not disprove DRC use.",
            })
            continue

        province_geometry = province_matches[0]["properties"]["id"]
        territory_geometry = territory_matches[0]["properties"]["id"]
        province = place_by_geometry.get(province_geometry)
        territory = place_by_geometry.get(territory_geometry)
        if not province or not territory:
            raise PresenceBuildError(f"{candidate_id}: containing geometry has no place record")
        candidate = {
            **common,
            "match_status": "mapped-candidate",
            "province_place_id": province["id"],
            "province_name": province["name"],
            "territory_place_id": territory["id"],
            "territory_name": territory["name"],
            "geometry_type": "point",
            "role": "unspecified",
            "confidence": "medium",
            "limitations": "A Glottolog representative point is not a language boundary or complete distribution. Administrative containment is derived from the pinned 2017 navigation layers.",
        }
        decision = decisions.get(candidate_id)
        if decision:
            candidate["review_status"] = decision["decision"]
            candidate["decision"] = decision
            checks_approved = all(value == "approved" for value in decision["checks"].values())
            if decision["decision"] == "approve":
                if not checks_approved:
                    raise PresenceBuildError(f"{candidate_id}: approval requires every check to be approved")
                if decision["source_version"] != source["version"]:
                    raise PresenceBuildError(f"{candidate_id}: decision source version is stale")
                approved_claims.append({
                    "id": f"claim-{candidate_id}",
                    "language_id": language["id"],
                    "place_id": territory["id"],
                    "province_place_id": province["id"],
                    "geometry_type": "point",
                    "role": "unspecified",
                    "point": common["point"],
                    "source_id": source["id"],
                    "source_url": source["landing_page"],
                    "evidence_locator": common["evidence_locator"],
                    "confidence": "medium",
                    "verification_status": "source-checked",
                    "last_reviewed_at": decision["reviewed_at"],
                    "limitations": candidate["limitations"],
                })
        candidates.append(candidate)

    candidate_ids = {candidate["id"] for candidate in candidates}
    unknown_decisions = sorted(set(decisions) - candidate_ids)
    if unknown_decisions:
        raise PresenceBuildError("decisions reference unknown candidates: " + ", ".join(unknown_decisions))

    status_counts: dict[str, int] = {}
    for candidate in candidates:
        status = candidate["match_status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    bundle = {
        "bundle_version": 1,
        "generated_at": manifest["reviewed_at"],
        "source": source,
        "summary": {
            "languages": len(languages),
            **status_counts,
            "reviewed": sum(candidate["review_status"] != "candidate" for candidate in candidates),
            "approved": len(approved_claims),
        },
        "candidates": candidates,
        "approved_claims": approved_claims,
    }
    bundle_errors = validate_presence_bundle(bundle)
    if bundle_errors:
        raise PresenceBuildError("invalid presence bundle: " + "; ".join(bundle_errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--languages", type=Path, default=DEFAULT_LANGUAGES)
    parser.add_argument("--places", type=Path, default=DEFAULT_PLACES)
    parser.add_argument("--geodata", type=Path, default=DEFAULT_GEODATA)
    parser.add_argument("--reviews", type=Path, default=DEFAULT_REVIEWS)
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = build_presence_candidates(
            args.manifest, args.languages, args.places, args.geodata,
            args.reviews, args.source_dir, args.output, args.offline,
        )
    except PresenceBuildError as exc:
        print(f"Presence candidate build failed: {exc}", file=sys.stderr)
        return 1
    summary = bundle["summary"]
    print(
        f"Built {summary.get('mapped-candidate', 0)} mapped candidate(s); "
        f"{summary['approved']} approved claim(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
