#!/usr/bin/env python3
"""Build a deterministic manual-review queue for draft CongoLangBench records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import FormatChecker
from jsonschema.validators import validator_for

from scripts.validate_catalog import DEFAULT_CATALOG_DIR, DEFAULT_SCHEMA_DIR, ROOT, build_registry, load_json


DEFAULT_DRAFT_CATALOG = ROOT / "data" / "generated" / "congolangbench" / "catalog"
DEFAULT_IMPORT_REPORT = ROOT / "data" / "generated" / "congolangbench" / "import-report.json"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "congolangbench" / "review-queue.json"
DEFAULT_DECISIONS = ROOT / "data" / "reviews" / "congolangbench"
CHECKS = ("language_identity", "variety_identity", "geographic_scope", "licence", "access", "source_links")
CHECK_BLOCKERS = {
    "language_identity": "identity-review",
    "variety_identity": "variety-review",
    "geographic_scope": "geographic-review",
    "licence": "licence-review",
    "access": "access-review",
    "source_links": "source-link-review",
}


class ReviewQueueError(RuntimeError):
    """Raised when draft imports cannot produce a trustworthy queue."""


def records_by_type(root: Path, entity_type: str) -> list[dict[str, Any]]:
    records = []
    for path in sorted(root.rglob("*.json")):
        record = load_json(path)
        if record.get("entity_type") == entity_type:
            records.append(record)
    return records


def existing_language_ids(catalog_dir: Path) -> dict[str, str]:
    matches: dict[str, str] = {}
    for record in records_by_type(catalog_dir, "language"):
        iso = record.get("identifiers", {}).get("iso_639_3")
        if iso:
            if iso in matches:
                raise ReviewQueueError(f"public catalogue has duplicate ISO identity {iso}")
            matches[iso] = record["id"]
    return matches


def validate_queue(queue: dict[str, Any], schema_dir: Path = DEFAULT_SCHEMA_DIR) -> list[str]:
    registry, schemas = build_registry(schema_dir)
    schema = schemas["import-review-queue.schema.json"]
    validator_class = validator_for(schema)
    validator = validator_class(schema, registry=registry, format_checker=FormatChecker())
    return sorted(error.message for error in validator.iter_errors(queue))


def load_decisions(decisions_dir: Path, source_commit: str) -> dict[str, tuple[Path, dict[str, Any]]]:
    if not decisions_dir.exists():
        return {}
    registry, schemas = build_registry(DEFAULT_SCHEMA_DIR)
    schema = schemas["import-review-decision.schema.json"]
    validator_class = validator_for(schema)
    validator = validator_class(schema, registry=registry, format_checker=FormatChecker())
    decisions: dict[str, tuple[Path, dict[str, Any]]] = {}
    for path in sorted(decisions_dir.glob("*.json")):
        decision = load_json(path)
        errors = sorted(error.message for error in validator.iter_errors(decision))
        if errors:
            raise ReviewQueueError(f"{path}: invalid review decision: {'; '.join(errors)}")
        if decision["source_commit"] != source_commit:
            raise ReviewQueueError(f"{path}: review decision targets a different source commit")
        iso = decision["iso_639_3"]
        if iso in decisions:
            raise ReviewQueueError(f"duplicate review decision for {iso}")
        decisions[iso] = (path, decision)
    return decisions


def build_queue(
    draft_catalog: Path = DEFAULT_DRAFT_CATALOG,
    import_report: Path = DEFAULT_IMPORT_REPORT,
    public_catalog: Path = DEFAULT_CATALOG_DIR,
    output: Path = DEFAULT_OUTPUT,
    decisions_dir: Path = DEFAULT_DECISIONS,
) -> dict[str, Any]:
    if not draft_catalog.exists() or not import_report.exists():
        raise ReviewQueueError("draft import is missing; run the CongoLangBench importer first")
    report = load_json(import_report)
    if not report.get("passed"):
        raise ReviewQueueError("draft import report did not pass reconciliation")
    warning_isos = {warning["iso_code"] for warning in report.get("manual_review_warnings", [])}
    decisions = load_decisions(decisions_dir, report["source_commit"])
    existing = existing_language_ids(public_catalog)
    languages = records_by_type(draft_catalog, "language")
    resources = records_by_type(draft_catalog, "resource")
    resources_by_language: dict[str, list[dict[str, Any]]] = {}
    for resource in resources:
        for language in resource["languages"]:
            resources_by_language.setdefault(language["language_id"], []).append(resource)

    tracks: list[dict[str, Any]] = []
    for language in sorted(languages, key=lambda item: item["identifiers"]["iso_639_3"]):
        iso = language["identifiers"]["iso_639_3"]
        track_resources = resources_by_language.get(language["id"], [])
        if len(track_resources) != 2:
            raise ReviewQueueError(f"{iso}: expected bitext and benchmark resources")
        existing_id = existing.get(iso)
        restricted = any(resource["redistribution"] == "restricted" for resource in track_resources)
        geographic_review = iso in warning_isos or any(
            resource["geographic_scope"] == "uncertain" for resource in track_resources
        )
        variety_review = iso in warning_isos or bool(language.get("alternate_names"))
        blockers = ["identity-review", "licence-review", "access-review", "source-link-review"]
        if variety_review:
            blockers.append("variety-review")
        if geographic_review:
            blockers.append("geographic-review")
        if restricted:
            blockers.append("restricted-content")
        high_priority = restricted or geographic_review or existing_id is not None
        decision_entry = decisions.get(iso)
        checks = {check: "pending" for check in CHECKS}
        review_status = "pending"
        decision_file = None
        ready = False
        if decision_entry:
            decision_path, decision = decision_entry
            checks = decision["checks"]
            review_status = {"approve": "approved", "reject": "rejected", "defer": "deferred"}[decision["decision"]]
            decision_file = str(decision_path.relative_to(ROOT)) if decision_path.is_relative_to(ROOT) else str(decision_path)
            blockers = [blocker for blocker in blockers if blocker not in CHECK_BLOCKERS.values()]
            blockers.extend(CHECK_BLOCKERS[check] for check, status in checks.items() if status != "approved")
            if decision["decision"] != "approve":
                blockers.append("human-approval")
            ready = decision["decision"] == "approve" and all(status == "approved" for status in checks.values())
            if ready:
                blockers = []
        tracks.append({
            "iso_639_3": iso,
            "imported_language_id": language["id"],
            "preferred_name": language["preferred_name"],
            "existing_atlas_language_id": existing_id,
            "suggested_atlas_language_id": existing_id or language["id"],
            "priority": "high" if high_priority else "medium",
            "publication_blockers": sorted(set(blockers)),
            "required_checks": checks,
            "review_status": review_status,
            "decision_file": decision_file,
            "resource_ids": sorted(resource["id"] for resource in track_resources),
            "ready_for_promotion": ready,
        })

    queue = {
        "queue_version": 1,
        "source_commit": report["source_commit"],
        "generated_at": report["retrieved_at"],
        "summary": {
            "total": len(tracks),
            "high_priority": sum(track["priority"] == "high" for track in tracks),
            "medium_priority": sum(track["priority"] == "medium" for track in tracks),
            "existing_identity_matches": sum(track["existing_atlas_language_id"] is not None for track in tracks),
            "restricted_tracks": sum("restricted-content" in track["publication_blockers"] for track in tracks),
            "reviewed": sum(track["review_status"] != "pending" for track in tracks),
            "deferred": sum(track["review_status"] == "deferred" for track in tracks),
            "ready_for_promotion": sum(track["ready_for_promotion"] for track in tracks),
        },
        "tracks": tracks,
    }
    errors = validate_queue(queue)
    if errors:
        raise ReviewQueueError("generated review queue is invalid: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(queue, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return queue


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft-catalog", type=Path, default=DEFAULT_DRAFT_CATALOG)
    parser.add_argument("--import-report", type=Path, default=DEFAULT_IMPORT_REPORT)
    parser.add_argument("--public-catalog", type=Path, default=DEFAULT_CATALOG_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--decisions", type=Path, default=DEFAULT_DECISIONS)
    args = parser.parse_args(argv)
    try:
        queue = build_queue(args.draft_catalog, args.import_report, args.public_catalog, args.output, args.decisions)
    except ReviewQueueError as exc:
        print(f"Review queue build failed: {exc}", file=sys.stderr)
        return 1
    summary = queue["summary"]
    print(f"Queued {summary['total']} tracks: {summary['high_priority']} high and {summary['medium_priority']} medium priority.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
