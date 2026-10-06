#!/usr/bin/env python3
"""Build the public-safe static data bundle consumed by the atlas UI."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from scripts.validate_catalog import ROOT, load_json, validate_catalog
from scripts.discover_sources import validate_discovery
from scripts.build_presence_candidates import validate_presence_bundle


DEFAULT_CATALOG = ROOT / "data" / "generated" / "congolangbench" / "catalog"
DEFAULT_QUEUE = ROOT / "data" / "generated" / "congolangbench" / "review-queue.json"
DEFAULT_OUTPUT = ROOT / "public" / "generated" / "atlas" / "catalog.json"
DEFAULT_DISCOVERY = ROOT / "data" / "generated" / "source-discovery.json"
DEFAULT_PRESENCE = ROOT / "data" / "generated" / "presence" / "candidates.json"


class WebDataError(RuntimeError):
    """Raised when a safe, complete web bundle cannot be produced."""


def _records(catalog: Path, entity_type: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in sorted(catalog.rglob("*.json")):
        record = load_json(path)
        if record.get("entity_type") == entity_type:
            records.append(record)
    return records


def _region(classification_note: str | None) -> str:
    match = re.search(r"\(Regional, ([^)]+)\)", classification_note or "")
    if match:
        return match.group(1)
    match = re.search(r"\((National)\)", classification_note or "")
    return match.group(1) if match else "Unassigned"


def _display_resources(resources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Prefer external resources over internal frozen-evaluation metadata."""
    external = [
        resource for resource in resources
        if not (
            resource["resource_type"] == "benchmark"
            and (resource.get("limitations") or "").startswith("Frozen-local evaluation metadata only")
        )
    ]
    return external or resources


def build_web_data(
    catalog: Path = DEFAULT_CATALOG,
    queue_path: Path = DEFAULT_QUEUE,
    output: Path = DEFAULT_OUTPUT,
    discovery_path: Path | None = DEFAULT_DISCOVERY,
    presence_path: Path | None = DEFAULT_PRESENCE,
) -> dict[str, Any]:
    if not catalog.exists() or not queue_path.exists():
        raise WebDataError("generated import is missing; run the importer and review queue first")
    catalog_errors = validate_catalog(catalog)
    if catalog_errors:
        raise WebDataError("generated catalogue is invalid: " + "; ".join(catalog_errors))

    queue = load_json(queue_path)
    summary = queue.get("summary", {})
    if summary.get("reviewed") != summary.get("total"):
        raise WebDataError("every imported track must have a review decision before web export")

    sources = {record["id"]: record for record in _records(catalog, "source")}
    resources = _records(catalog, "resource")
    resources_by_language: dict[str, list[dict[str, Any]]] = {}
    for resource in resources:
        for language in resource["languages"]:
            resources_by_language.setdefault(language["language_id"], []).append(resource)
    reviews = {track["imported_language_id"]: track for track in queue["tracks"]}
    discovery_by_language: dict[str, dict[str, Any]] = {}
    if discovery_path and discovery_path.exists():
        discovery = load_json(discovery_path)
        discovery_errors = validate_discovery(discovery)
        if discovery_errors:
            raise WebDataError("source discovery is invalid: " + "; ".join(discovery_errors))
        discovery_by_language = {item["language_id"]: item for item in discovery.get("languages", [])}
    presence_candidates_by_language: dict[str, list[dict[str, Any]]] = {}
    approved_claims_by_language: dict[str, list[dict[str, Any]]] = {}
    presence_summary: dict[str, Any] = {}
    presence: dict[str, Any] = {}
    if presence_path and presence_path.exists():
        presence = load_json(presence_path)
        presence_errors = validate_presence_bundle(presence)
        if presence_errors:
            raise WebDataError("presence candidates are invalid: " + "; ".join(presence_errors))
        presence_summary = presence.get("summary", {})
        for candidate in presence.get("candidates", []):
            if candidate.get("match_status") in {"mapped-candidate", "documented-presence"}:
                presence_candidates_by_language.setdefault(candidate["language_id"], []).append(candidate)
        for claim in presence.get("approved_claims", []):
            approved_claims_by_language.setdefault(claim["language_id"], []).append(claim)

    catalog_languages = _records(catalog, "language")
    supplemental_languages = presence.get("supplemental_languages", [])
    supplemental_language_ids = {language["id"] for language in supplemental_languages}
    languages = []
    for language in sorted([*catalog_languages, *supplemental_languages], key=lambda item: item["preferred_name"]):
        review = reviews.get(language["id"])
        if review is None and language["id"] not in supplemental_language_ids:
            raise WebDataError(f"{language['id']}: missing review queue entry")
        if review is None:
            review = language["review"]
        language_resources = []
        display_resources = _display_resources(resources_by_language.get(language["id"], []))
        for resource in sorted(display_resources, key=lambda item: item["resource_type"]):
            source = sources[resource["source_id"]]
            language_resources.append({
                "id": resource["id"],
                "title": resource["title"],
                "type": resource["resource_type"],
                "modalities": resource["modalities"],
                "size": resource.get("size"),
                "unit": resource.get("unit"),
                "format": resource.get("format"),
                "access": resource["access_type"],
                "licence": resource.get("licence_id"),
                "redistribution": resource["redistribution"],
                "geographic_scope": resource["geographic_scope"],
                "homepage_url": resource["homepage_url"],
                "download_url": resource.get("download_url"),
                "limitations": resource.get("limitations"),
                "source": {
                    "citation": source["citation"],
                    "publisher": source["publisher"],
                    "url": source["url"],
                },
            })
        discovered_sources = discovery_by_language.get(language["id"], {}).get("candidates", [])
        if language["id"] in supplemental_language_ids:
            glottolog_source = presence.get("source", {})
            discovered_sources = [
                {
                    "id": f"candidate-glottolog-{language['identifiers']['iso_639_3']}",
                    "provider": "Glottolog",
                    "kind": "catalogue",
                    "title": f"Glottolog catalogue record for {language['preferred_name']}",
                    "url": glottolog_source.get("landing_page", "https://glottolog.org/"),
                    "review_status": "candidate",
                    "licence": glottolog_source.get("licence_id"),
                },
                *discovered_sources,
            ]
        geographic_candidates = [
            {
                "id": candidate["id"],
                "province_place_id": candidate["province_place_id"],
                "province_name": candidate["province_name"],
                "place_id": candidate.get("place_id", candidate.get("territory_place_id")),
                "territory_place_id": candidate.get("territory_place_id"),
                "territory_name": candidate.get("territory_name"),
                "point": candidate.get("point"),
                "glottocode": candidate.get("glottocode"),
                "source_language_name": candidate.get("source_language_name"),
                "source_url": candidate["source_url"],
                "source_title": candidate.get("source_title", "Glottolog 5.3"),
                "evidence_locator": candidate["evidence_locator"],
                "evidence_type": candidate.get("evidence_type", "representative-point"),
                "role": candidate.get("role", "unspecified"),
                "speaker_percentage": candidate.get("speaker_percentage"),
                "percentage_basis": candidate.get("percentage_basis"),
                "confidence": candidate.get("confidence"),
                "review_status": candidate["review_status"],
                "limitations": candidate["limitations"],
            }
            for candidate in presence_candidates_by_language.get(language["id"], [])
        ]
        languages.append({
            "id": language["id"],
            "name": language["preferred_name"],
            "iso": language["identifiers"]["iso_639_3"],
            "aliases": [item["name"] for item in language.get("alternate_names", [])],
            "region": language.get("region") or _region(language.get("classification_note")),
            "classification_note": language.get("classification_note"),
            "last_reviewed_at": language["last_reviewed_at"],
            "review": {
                "status": review["review_status"],
                "priority": review["priority"],
                "blockers": review["publication_blockers"],
                "checks": review["required_checks"],
                "ready_for_promotion": review["ready_for_promotion"],
            },
            "resources": language_resources,
            "discovered_sources": discovered_sources,
            "geographic_candidates": geographic_candidates,
            "place_claims": approved_claims_by_language.get(language["id"], []),
        })

    displayed_resource_count = sum(len(language["resources"]) for language in languages)
    displayed_source_count = len({resource["source"]["url"] for language in languages for resource in language["resources"]})
    bundle = {
        "bundle_version": 1,
        "generated_at": queue["generated_at"],
        "source_commit": queue["source_commit"],
        "status": "draft",
        "summary": {
            **summary,
            "languages": len(languages),
            "resources": displayed_resource_count,
            "sources": displayed_source_count,
            "open_download_tracks": sum(any(item["access"] == "open-download" for item in language["resources"]) for language in languages),
            "discovered_sources": sum(len(language["discovered_sources"]) for language in languages),
            "mapped_geographic_candidates": sum(len(language["geographic_candidates"]) for language in languages),
            "approved_place_claims": sum(len(language["place_claims"]) for language in languages),
            "unmapped_language_tracks": (
                presence_summary.get("no-coordinate-match", 0)
                + presence_summary.get("representative-point-outside-drc", 0)
            ),
        },
        "languages": languages,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--queue", type=Path, default=DEFAULT_QUEUE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--discovery", type=Path, default=DEFAULT_DISCOVERY)
    parser.add_argument("--presence", type=Path, default=DEFAULT_PRESENCE)
    args = parser.parse_args(argv)
    try:
        bundle = build_web_data(args.catalog, args.queue, args.output, args.discovery, args.presence)
    except WebDataError as exc:
        print(f"Web data build failed: {exc}", file=sys.stderr)
        return 1
    print(f"Built web bundle with {len(bundle['languages'])} languages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
