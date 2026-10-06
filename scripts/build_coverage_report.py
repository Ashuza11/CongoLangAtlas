#!/usr/bin/env python3
"""Build a factual province-by-province geographic coverage audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.validate_catalog import ROOT, load_json


DEFAULT_BUNDLE = ROOT / "public" / "generated" / "atlas" / "catalog.json"
DEFAULT_PLACES = ROOT / "data" / "generated" / "places" / "catalog" / "places"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "coverage" / "province-coverage.json"


def _place_records(path: Path) -> list[dict[str, Any]]:
    return [load_json(item) for item in sorted(path.glob("*.json"))]


def build_coverage_report(
    bundle_path: Path = DEFAULT_BUNDLE,
    places_path: Path = DEFAULT_PLACES,
    output: Path = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    bundle = load_json(bundle_path)
    places = _place_records(places_path)
    provinces = sorted(
        (place for place in places if place.get("admin_level") == "province"),
        key=lambda item: item["name"],
    )
    territories_by_province: dict[str, set[str]] = {}
    for place in places:
        if place.get("admin_level") == "territory":
            territories_by_province.setdefault(place["parent_id"], set()).add(place["id"])

    rows = []
    for province in provinces:
        language_ids: set[str] = set()
        language_names: set[str] = set()
        candidate_ids: set[str] = set()
        territory_ids: set[str] = set()
        documented = 0
        representative_points = 0
        approved_claims = 0
        local_documented = 0
        for language in bundle.get("languages", []):
            matched = False
            for candidate in language.get("geographic_candidates", []):
                if candidate.get("province_place_id") != province["id"]:
                    continue
                matched = True
                candidate_ids.add(candidate["id"])
                if candidate.get("territory_place_id"):
                    territory_ids.add(candidate["territory_place_id"])
                if candidate.get("evidence_type") == "documented-presence":
                    documented += 1
                    if candidate.get("role") != "national-language-region":
                        local_documented += 1
                else:
                    representative_points += 1
            for claim in language.get("place_claims", []):
                if claim.get("province_place_id") == province["id"]:
                    matched = True
                    approved_claims += 1
            if matched:
                language_ids.add(language["id"])
                language_names.add(language["name"])

        territory_total = len(territories_by_province.get(province["id"], set()))
        flags = []
        if not language_ids:
            flags.append("no-language-leads")
        if len(language_ids) < 3:
            flags.append("fewer-than-three-language-leads")
        if not territory_ids:
            flags.append("no-territory-level-evidence")
        if documented and not local_documented:
            flags.append("documented-evidence-is-national-region-only")
        if not approved_claims:
            flags.append("no-approved-place-claims")
        rows.append({
            "province_id": province["id"],
            "province_name": province["name"],
            "language_count": len(language_ids),
            "languages": sorted(language_names),
            "candidate_count": len(candidate_ids),
            "documented_presence_count": documented,
            "local_documented_presence_count": local_documented,
            "representative_point_count": representative_points,
            "approved_claim_count": approved_claims,
            "territories_with_evidence": len(territory_ids),
            "territory_count": territory_total,
            "flags": flags,
        })

    report = {
        "report_version": 1,
        "generated_at": bundle["generated_at"],
        "summary": {
            "provinces": len(rows),
            "empty_provinces": sum("no-language-leads" in row["flags"] for row in rows),
            "provinces_with_fewer_than_three_languages": sum(
                "fewer-than-three-language-leads" in row["flags"] for row in rows
            ),
            "provinces_without_territory_evidence": sum(
                "no-territory-level-evidence" in row["flags"] for row in rows
            ),
            "provinces_without_local_documented_presence": sum(
                row["local_documented_presence_count"] == 0 for row in rows
            ),
        },
        "provinces": rows,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=DEFAULT_BUNDLE)
    parser.add_argument("--places", type=Path, default=DEFAULT_PLACES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = build_coverage_report(args.bundle, args.places, args.output)
    summary = report["summary"]
    print(
        f"Audited {summary['provinces']} provinces: {summary['empty_provinces']} empty, "
        f"{summary['provinces_with_fewer_than_three_languages']} with fewer than three language leads."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
