#!/usr/bin/env python3
"""Build reviewable language-place candidates from pinned Glottolog coordinates."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
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
DEFAULT_CURATED = ROOT / "data" / "presence" / "curated-presence.json"
DEFAULT_SOURCE_DIR = ROOT / "data" / "generated" / "presence" / "source"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "presence" / "candidates.json"

GLOTTOLOG_SOURCE_ID = "glottolog-5-3-languages"
CAID_SOURCE_ID = "clear-global-caid-drc-languages-2016"
CAID_LANGUAGE_OVERRIDES = {
    # The HDX HXL row either omits these well-established identifiers or, for
    # Nande, carries an identifier for an unrelated language.
    "Nande": "nnb",
    "Tshiluba": "lua",
    "Tshokwe": "cjk",
}


class PresenceBuildError(RuntimeError):
    """Raised when presence candidates cannot be built safely."""


def validate_presence_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    candidate_ids: set[str] = set()
    mapped_ids: set[str] = set()
    allowed_statuses = {
        "no-coordinate-match", "representative-point-outside-drc", "mapped-candidate", "documented-presence"
    }
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
        if candidate.get("match_status") == "documented-presence":
            for field in ("place_id", "province_place_id", "source_id", "evidence_locator", "limitations"):
                if not candidate.get(field):
                    errors.append(f"{prefix}: documented presence lacks {field}")
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
        raise PresenceBuildError(f"verified source {source['id']} is unavailable in offline mode")
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
        raise PresenceBuildError(f"{source['id']} download failed: {exc}") from exc
    actual = _sha256(temporary)
    if actual != source["sha256"]:
        temporary.unlink(missing_ok=True)
        raise PresenceBuildError(f"Glottolog checksum mismatch: expected {source['sha256']}, got {actual}")
    temporary.replace(path)
    return path


def _caid_documented_presence(
    source_path: Path,
    source: dict[str, Any],
    inventory_languages: list[dict[str, Any]],
    places: list[dict[str, Any]],
    existing_pairs: set[tuple[str, str]],
) -> list[dict[str, Any]]:
    """Convert exact HXL ISO mappings and percentages into review candidates."""
    with source_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            headers = next(reader)
            hxl_tags = next(reader)
        except StopIteration as exc:
            raise PresenceBuildError("CLEAR Global/CAID source is missing its two header rows") from exc
        rows = list(reader)

    if len(headers) != len(hxl_tags):
        raise PresenceBuildError("CLEAR Global/CAID headers and HXL tags have different lengths")
    header_index = {name.strip(): index for index, name in enumerate(headers)}
    required = {"Admin 2", "Adm 2 Pcode", "Adm 1 Pcode", "data_confidence"}
    missing = sorted(required - set(header_index))
    if missing:
        raise PresenceBuildError("CLEAR Global/CAID source lacks columns: " + ", ".join(missing))

    language_columns: list[tuple[int, str, str]] = []
    for index, (name, tag) in enumerate(zip(headers, hxl_tags, strict=True)):
        label = name.strip()
        iso = CAID_LANGUAGE_OVERRIDES.get(label)
        if not iso:
            match = re.fullmatch(r"#indicator\+lang\+pct\+iso639-3_([a-z]{3})\s*", tag)
            iso = match.group(1) if match else None
        if iso:
            language_columns.append((index, label, iso))

    language_ids = {language["id"] for language in inventory_languages}
    place_by_id = {place["id"]: place for place in places}
    candidates: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=3):
        if len(row) != len(headers):
            raise PresenceBuildError(f"CLEAR Global/CAID CSV row {row_number} has an unexpected width")
        territory_code = row[header_index["Adm 2 Pcode"]].strip().lower()
        province_code = row[header_index["Adm 1 Pcode"]].strip().lower()
        territory_id = f"place-cod-adm2-{territory_code}"
        province_id = f"place-cod-adm1-{province_code}"
        territory = place_by_id.get(territory_id)
        province = place_by_id.get(province_id)
        if not territory or not province or territory.get("parent_id") != province_id:
            raise PresenceBuildError(
                f"CLEAR Global/CAID CSV row {row_number} has an unknown administrative crosswalk "
                f"({territory_code}, {province_code})"
            )
        source_confidence = row[header_index["data_confidence"]].strip() or "Unspecified"
        for column_index, source_label, iso in language_columns:
            raw_value = row[column_index].strip()
            if not raw_value:
                continue
            try:
                fraction = float(raw_value)
            except ValueError as exc:
                raise PresenceBuildError(
                    f"CLEAR Global/CAID CSV row {row_number}, column {source_label} is not numeric"
                ) from exc
            if fraction <= 0:
                continue
            if fraction > 1:
                raise PresenceBuildError(
                    f"CLEAR Global/CAID CSV row {row_number}, column {source_label} exceeds 1"
                )
            language_id = f"language-{iso}"
            pair = (language_id, territory_id)
            if language_id not in language_ids or pair in existing_pairs:
                continue
            label_slug = re.sub(r"[^a-z0-9]+", "-", source_label.casefold()).strip("-")
            candidate_id = f"presence-caid-2016-{iso}-{territory_code}-{label_slug}"
            if candidate_id in seen_ids:
                raise PresenceBuildError(f"duplicate generated CLEAR Global/CAID candidate {candidate_id}")
            seen_ids.add(candidate_id)
            percentage = round(fraction * 100, 6)
            candidates.append({
                "id": candidate_id,
                "language_id": language_id,
                "place_id": territory_id,
                "province_place_id": province_id,
                "source_id": source["id"],
                "source_version": source["version"],
                "source_url": source["landing_page"],
                "source_title": "DRC: Languages (2016 CAID territory data)",
                "evidence_locator": (
                    f"CSV row {row_number}: Adm 2 Pcode={row[header_index['Adm 2 Pcode']]}, "
                    f"column {source_label}={raw_value}"
                ),
                "role": "spoken-language",
                "speaker_percentage": percentage,
                "percentage_basis": (
                    f"Share of the {territory['name']} administrative-area population reported "
                    f"in the 2016 CAID dataset as speaking {source_label}"
                ),
                "confidence": "low",
                "limitations": (
                    f"The source marks this row's data confidence as {source_confidence}. The value "
                    "does not measure proficiency, first-language identity, or exclusive distribution; "
                    "the HXL ISO mapping and 2017 administrative crosswalk still require human review."
                ),
                "match_status": "documented-presence",
                "evidence_type": "documented-presence",
                "province_name": province["name"],
                "territory_place_id": territory_id,
                "territory_name": territory["name"],
                "review_status": "candidate",
            })
    return candidates


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
    curated_path: Path | None = DEFAULT_CURATED,
) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    manifest_errors = _validate_document(manifest, "presence-source-manifest.schema.json")
    if manifest_errors:
        raise PresenceBuildError("invalid presence-source manifest: " + "; ".join(manifest_errors))
    source_by_id = {item["id"]: item for item in manifest["sources"]}
    source = source_by_id.get(GLOTTOLOG_SOURCE_ID)
    if not source:
        raise PresenceBuildError(f"presence-source manifest lacks {GLOTTOLOG_SOURCE_ID}")
    source_path = _acquire(source, source_dir, offline)
    with source_path.open(encoding="utf-8", newline="") as handle:
        rows = {row["ISO639P3code"]: row for row in csv.DictReader(handle) if row.get("ISO639P3code")}

    languages = sorted(_records(language_dir), key=lambda item: item["preferred_name"])
    places = _records(place_dir)
    place_by_geometry = {place.get("geometry_id"): place for place in places if place.get("geometry_id")}
    province_features = _features(geodata_dir / "cod-adm1.geojson")
    territory_features = _features(geodata_dir / "cod-adm2.geojson")
    decisions = _decision_map(review_dir)
    curated = load_json(curated_path) if curated_path and curated_path.exists() else {
        "sources": [], "supplemental_languages": [], "records": []
    }
    curated_supplemental = curated.get("supplemental_languages", [])
    reserved_isos = {language["identifiers"]["iso_639_3"] for language in [*languages, *curated_supplemental]}
    generated_supplemental = []
    for iso, row in sorted(rows.items(), key=lambda item: item[1]["Name"]):
        countries = row.get("Countries", "").split(";") if row.get("Countries") else []
        if "CD" not in countries or iso in reserved_isos:
            continue
        generated_supplemental.append({
            "id": f"language-{iso}",
            "preferred_name": row["Name"],
            "identifiers": {"iso_639_3": iso},
            "alternate_names": [],
            "region": "Unassigned",
            "classification_note": (
                "Supplemental DRC inventory candidate generated from the pinned Glottolog 5.3 "
                f"country-code row ({row['Glottocode']}). Country association and language identity "
                "still require named-human review."
            ),
            "last_reviewed_at": manifest["reviewed_at"],
            "review": {
                "review_status": "deferred",
                "priority": "medium",
                "publication_blockers": ["human-approval", "language-identity-review", "resource-review"],
                "required_checks": {
                    "language_identity": "unresolved",
                    "variety_identity": "unresolved",
                    "geographic_scope": "unresolved",
                    "licence": "approved",
                    "access": "approved",
                    "source_links": "approved",
                },
                "ready_for_promotion": False,
            },
        })
    supplemental_languages = sorted(
        [*curated_supplemental, *generated_supplemental], key=lambda item: item["preferred_name"]
    )
    inventory_languages = sorted([*languages, *supplemental_languages], key=lambda item: item["preferred_name"])
    candidates = []
    approved_claims = []

    for language in inventory_languages:
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

    curated_source_by_id = {item["id"]: item for item in curated.get("sources", [])}
    if curated.get("records"):
        language_ids = {language["id"] for language in inventory_languages}
        place_by_id = {place["id"]: place for place in places}
        for record in curated.get("records", []):
            if record["language_id"] not in language_ids:
                raise PresenceBuildError(f"{record['id']}: unknown language {record['language_id']}")
            place = place_by_id.get(record["place_id"])
            province = place_by_id.get(record["province_place_id"])
            source_record = curated_source_by_id.get(record["source_id"])
            if not place or not province:
                raise PresenceBuildError(f"{record['id']}: unknown place reference")
            if not source_record:
                raise PresenceBuildError(f"{record['id']}: unknown source {record['source_id']}")
            candidate = {
                **record,
                "match_status": "documented-presence",
                "evidence_type": "documented-presence",
                "province_name": province["name"],
                "source_url": source_record["url"],
                "source_title": source_record["title"],
                "review_status": "candidate",
            }
            if place["admin_level"] == "territory":
                candidate["territory_place_id"] = place["id"]
                candidate["territory_name"] = place["name"]
            candidates.append(candidate)

    caid_source = source_by_id.get(CAID_SOURCE_ID)
    if caid_source:
        caid_path = _acquire(caid_source, source_dir, offline)
        curated_pairs = {
            (record["language_id"], record["place_id"])
            for record in curated.get("records", [])
        }
        candidates.extend(_caid_documented_presence(
            caid_path, caid_source, inventory_languages, places, curated_pairs
        ))

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
            "languages": len(inventory_languages),
            "benchmark_languages": len(languages),
            "supplemental_languages": len(supplemental_languages),
            **status_counts,
            "reviewed": sum(candidate["review_status"] != "candidate" for candidate in candidates),
            "approved": len(approved_claims),
        },
        "candidates": candidates,
        "approved_claims": approved_claims,
        "supplemental_languages": supplemental_languages,
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
    parser.add_argument("--curated", type=Path, default=DEFAULT_CURATED)
    args = parser.parse_args(argv)
    try:
        bundle = build_presence_candidates(
            args.manifest, args.languages, args.places, args.geodata,
            args.reviews, args.source_dir, args.output, args.offline, args.curated,
        )
    except PresenceBuildError as exc:
        print(f"Presence candidate build failed: {exc}", file=sys.stderr)
        return 1
    summary = bundle["summary"]
    print(
        f"Built {summary.get('mapped-candidate', 0)} point candidate(s) and "
        f"{summary.get('documented-presence', 0)} documented presence candidate(s); "
        f"{summary['approved']} approved claim(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
