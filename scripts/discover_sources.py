#!/usr/bin/env python3
"""Discover review candidates for every imported language from public indexes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from scripts.validate_catalog import ROOT, load_json


DEFAULT_CATALOG = ROOT / "data" / "generated" / "congolangbench" / "catalog"
DEFAULT_OUTPUT = ROOT / "data" / "generated" / "source-discovery.json"
DEFAULT_CACHE = ROOT / "data" / "generated" / "source-discovery-cache"
PROVIDERS = ("huggingface", "github", "openalex")
PROVIDER_LABELS = {"OLAC", "Hugging Face", "GitHub", "OpenAlex"}
CANDIDATE_KINDS = {"catalogue", "dataset", "model", "repository", "research"}
CONTEXT_TERMS = (
    "language", "linguistic", "translation", "speech", "audio", "corpus",
    "dictionary", "grammar", "orthography", "nlp", "tokenizer", "asr", "tts",
)
AMBIGUITY_EXCLUSIONS = {
    "log": ("logo design", "brand", "captioning", "graphic", "programming language", "turtle"),
    "lol": ("mongo db", "mongodb", "database", "cassandra", "mongo_orm", "mongo driver"),
    "rwm": ("amba bus", "amba-apb", "amba axi", "amba-axi", "protocol", "system on chip", "soc bridge"),
    "shr": ("mashi wentong", "chinese grammar", "assistant robot", "modern arabic", "mashi markets"),
}
AMBIGUITY_REQUIRED_SIGNALS = {
    "log": ("logoti", "democratic republic of congo", "dr congo", "african language", "central sudanic"),
    "lol": ("nkundo", "democratic republic of congo", "dr congo", "bantu language", "mongo language", "resources for mongo"),
    "rwm": ("uganda", "democratic republic of congo", "dr congo", "african language", "bantu language", "amba language"),
    "shr": ("democratic republic of congo", "dr congo", "kivu", "bantu language", "mashi language", "learning mashi", "shi verbs"),
}


class DiscoveryError(RuntimeError):
    """Raised when source discovery cannot produce a valid census."""


def _records(catalog: Path, entity_type: str) -> list[dict[str, Any]]:
    records = []
    for path in sorted(catalog.rglob("*.json")):
        record = load_json(path)
        if record.get("entity_type") == entity_type:
            records.append(record)
    return records


def _terms(language: dict[str, Any]) -> list[str]:
    values = [language["preferred_name"]]
    values.extend(item["name"] for item in language.get("alternate_names", []))
    terms: list[str] = []
    for value in values:
        cleaned = re.sub(r"\([^)]*\)", "", value)
        for part in re.split(r"\s*/\s*|\s+or\s+", cleaned):
            part = part.strip()
            if len(part) >= 3 and part.casefold() not in {item.casefold() for item in terms}:
                terms.append(part)
    return terms[:4]


def _candidate_id(provider: str, url: str) -> str:
    digest = hashlib.sha256(f"{provider}|{url}".encode()).hexdigest()[:16]
    return f"candidate-{provider}-{digest}"


def _candidate(provider: str, kind: str, title: str, url: str, **details: Any) -> dict[str, Any]:
    if url.startswith("http://"):
        url = "https://" + url.removeprefix("http://")
    return {
        "id": _candidate_id(provider, url),
        "provider": provider,
        "kind": kind,
        "title": title,
        "url": url,
        "review_status": "candidate",
        **{key: value for key, value in details.items() if value not in (None, "", [])},
    }


def _haystack(value: dict[str, Any]) -> str:
    parts = [str(value.get(key) or "") for key in ("id", "name", "full_name", "description", "display_name")]
    parts.extend(str(item) for item in value.get("tags", []))
    return " ".join(parts).casefold()


def _is_relevant(value: dict[str, Any], terms: list[str], iso: str, require_context: bool = True) -> bool:
    text = _haystack(value)
    if any(excluded in text for excluded in AMBIGUITY_EXCLUSIONS.get(iso, ())):
        return False
    required_signals = AMBIGUITY_REQUIRED_SIGNALS.get(iso)
    if required_signals and not any(signal in text for signal in required_signals):
        return False
    term_match = any(re.search(rf"(?<!\w){re.escape(term.casefold())}(?!\w)", text) for term in terms)
    iso_match = bool(re.search(rf"(?<!\w){re.escape(iso.casefold())}(?!\w)", text))
    context_match = any(term in text for term in CONTEXT_TERMS)
    return (term_match or iso_match) and (context_match or not require_context)


class CachedClient:
    def __init__(self, cache: Path, offline: bool = False) -> None:
        self.cache = cache
        self.offline = offline
        self.cache.mkdir(parents=True, exist_ok=True)

    def get(self, url: str, headers: dict[str, str] | None = None) -> Any:
        cache_path = self.cache / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
        if cache_path.exists():
            return load_json(cache_path)
        if self.offline:
            raise DiscoveryError(f"offline cache miss: {url}")
        request_headers = {"User-Agent": "CongoLangAtlas-source-discovery/0.1", **(headers or {})}
        if url.startswith("https://api.github.com/"):
            request_headers.update({
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            })
            if os.environ.get("GITHUB_TOKEN"):
                request_headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
        try:
            with urlopen(Request(url, headers=request_headers), timeout=45) as response:
                value = json.load(response)
        except (HTTPError, URLError, TimeoutError) as exc:
            raise DiscoveryError(f"request failed for {url}: {exc}") from exc
        cache_path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
        return value


def _huggingface(language: dict[str, Any], get: Callable[[str], Any]) -> list[dict[str, Any]]:
    iso = language["identifiers"]["iso_639_3"]
    terms = _terms(language)
    candidates: list[dict[str, Any]] = []
    for entity, kind in (("datasets", "dataset"), ("models", "model")):
        seen: set[str] = set()
        for term in terms[:2]:
            query = urlencode({"search": term, "limit": 30, "full": "true"})
            for item in get(f"https://huggingface.co/api/{entity}?{query}"):
                item_id = item.get("id")
                if not item_id or item_id in seen or not _is_relevant(item, terms, iso):
                    continue
                seen.add(item_id)
                tags = item.get("tags", [])
                licence = next((tag.removeprefix("license:") for tag in tags if tag.startswith("license:")), None)
                modalities = sorted({tag.removeprefix("modality:") for tag in tags if tag.startswith("modality:")})
                page_url = f"https://huggingface.co/datasets/{item_id}" if entity == "datasets" else f"https://huggingface.co/{item_id}"
                candidates.append(_candidate(
                    "Hugging Face", kind, item_id, page_url,
                    author=item.get("author"), description=(item.get("description") or "")[:500].strip(),
                    licence=licence, modalities=modalities, downloads=item.get("downloads"),
                    likes=item.get("likes"), last_updated=item.get("lastModified"),
                    access="gated" if item.get("gated") else "public-page",
                    matched_terms=[term],
                ))
    return candidates


def _github(language: dict[str, Any], get: Callable[[str], Any]) -> list[dict[str, Any]]:
    iso = language["identifiers"]["iso_639_3"]
    terms = _terms(language)
    query = f'"{terms[0]}" language'
    url = "https://api.github.com/search/repositories?" + urlencode({"q": query, "per_page": 20, "sort": "stars"})
    payload = get(url)
    candidates = []
    for item in payload.get("items", []):
        enriched = {**item, "tags": item.get("topics", [])}
        if not _is_relevant(enriched, terms, iso):
            continue
        candidates.append(_candidate(
            "GitHub", "repository", item["full_name"], item["html_url"],
            author=item.get("owner", {}).get("login"), description=item.get("description"),
            licence=(item.get("license") or {}).get("spdx_id"), stars=item.get("stargazers_count"),
            last_updated=item.get("updated_at"), matched_terms=[terms[0]],
        ))
    return candidates


def _abstract(value: dict[str, Any]) -> str:
    inverted = value.get("abstract_inverted_index") or {}
    return " ".join(inverted.keys())


def _openalex(language: dict[str, Any], get: Callable[[str], Any]) -> list[dict[str, Any]]:
    iso = language["identifiers"]["iso_639_3"]
    terms = _terms(language)
    query = f'"{terms[0]}" language'
    url = "https://api.openalex.org/works?" + urlencode({"search": query, "per-page": 20})
    candidates = []
    for item in get(url).get("results", []):
        enriched = {**item, "description": _abstract(item)}
        if not _is_relevant(enriched, terms, iso):
            continue
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        candidate_url = item.get("doi") or location.get("landing_page_url") or item.get("id")
        if not candidate_url:
            continue
        authors = [
            authorship.get("author", {}).get("display_name")
            for authorship in item.get("authorships", [])[:8]
            if authorship.get("author", {}).get("display_name")
        ]
        candidates.append(_candidate(
            "OpenAlex", "research", item.get("display_name") or "Untitled work", candidate_url,
            authors=authors, publication_year=item.get("publication_year"),
            publication_type=item.get("type"), venue=source.get("display_name"),
            open_access=(item.get("open_access") or {}).get("is_oa"),
            citations=item.get("cited_by_count"), matched_terms=[terms[0]],
        ))
    return candidates


def discover_language(
    language: dict[str, Any],
    get: Callable[[str], Any],
    providers: tuple[str, ...] = PROVIDERS,
) -> tuple[list[dict[str, Any]], list[str]]:
    iso = language["identifiers"]["iso_639_3"]
    candidates = [_candidate(
        "OLAC", "catalogue", f"OLAC resources for {language['preferred_name']}",
        f"https://www.language-archives.org/language/{iso}",
        description="Archive catalogue records indexed by ISO 639-3 code.", matched_terms=[iso],
    )]
    errors = []
    functions = {"huggingface": _huggingface, "github": _github, "openalex": _openalex}
    for provider in providers:
        try:
            candidates.extend(functions[provider](language, get))
        except DiscoveryError as exc:
            errors.append(f"{provider}: {exc}")
    deduplicated = {candidate["url"]: candidate for candidate in candidates}
    return sorted(deduplicated.values(), key=lambda item: (item["kind"], item["provider"], item["title"])), errors


def validate_discovery(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    language_ids: set[str] = set()
    for index, language in enumerate(bundle.get("languages", [])):
        prefix = f"languages[{index}]"
        language_id = language.get("language_id")
        if not language_id or language_id in language_ids:
            errors.append(f"{prefix}: missing or duplicate language_id")
        language_ids.add(language_id)
        urls: set[str] = set()
        for candidate_index, candidate in enumerate(language.get("candidates", [])):
            candidate_prefix = f"{prefix}.candidates[{candidate_index}]"
            url = candidate.get("url", "")
            if not url.startswith("https://"):
                errors.append(f"{candidate_prefix}: URL must use HTTPS")
            if url in urls:
                errors.append(f"{candidate_prefix}: duplicate URL")
            urls.add(url)
            if candidate.get("provider") not in PROVIDER_LABELS:
                errors.append(f"{candidate_prefix}: unsupported provider")
            if candidate.get("kind") not in CANDIDATE_KINDS:
                errors.append(f"{candidate_prefix}: unsupported source kind")
            if candidate.get("review_status") != "candidate":
                errors.append(f"{candidate_prefix}: discovery results must remain candidates")
    return errors


def build_discovery(
    catalog: Path = DEFAULT_CATALOG,
    output: Path = DEFAULT_OUTPUT,
    cache: Path = DEFAULT_CACHE,
    providers: tuple[str, ...] = PROVIDERS,
    offline: bool = False,
) -> dict[str, Any]:
    if not catalog.exists():
        raise DiscoveryError("generated catalogue is missing; run the CongoLangBench importer first")
    client = CachedClient(cache, offline)
    languages = sorted(_records(catalog, "language"), key=lambda item: item["preferred_name"])
    results = []
    error_count = 0
    for index, language in enumerate(languages, 1):
        candidates, errors = discover_language(language, client.get, providers)
        error_count += len(errors)
        results.append({
            "language_id": language["id"],
            "iso": language["identifiers"]["iso_639_3"],
            "name": language["preferred_name"],
            "candidates": candidates,
            "errors": errors,
        })
        print(f"[{index:02d}/{len(languages)}] {language['preferred_name']}: {len(candidates)} candidate(s)", flush=True)
        if "github" in providers and not offline and index < len(languages):
            time.sleep(6.2)
    bundle = {
        "bundle_version": 1,
        "generated_at": date.today().isoformat(),
        "review_status": "candidate",
        "providers": ["OLAC", *providers],
        "summary": {
            "languages": len(results),
            "candidates": sum(len(item["candidates"]) for item in results),
            "provider_errors": error_count,
            "languages_without_candidates": sum(not item["candidates"] for item in results),
        },
        "languages": results,
    }
    errors = validate_discovery(bundle)
    if errors:
        raise DiscoveryError("invalid discovery bundle: " + "; ".join(errors))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--providers", nargs="+", choices=PROVIDERS, default=list(PROVIDERS))
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = build_discovery(args.catalog, args.output, args.cache, tuple(args.providers), args.offline)
    except DiscoveryError as exc:
        print(f"Source discovery failed: {exc}", file=sys.stderr)
        return 1
    print(f"Discovered {bundle['summary']['candidates']} candidate source(s) for {bundle['summary']['languages']} languages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
