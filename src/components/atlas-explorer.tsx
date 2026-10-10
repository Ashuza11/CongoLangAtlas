"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { AtlasBundle, AtlasLanguage, AtlasPlaceOption, AtlasPlaceSelection, AtlasResource, DiscoveredSource } from "@/lib/types";

const AtlasMap = dynamic(() => import("./atlas-map"), { ssr: false });
type AccessFilter = "all" | "open" | "restricted";
type CoverageFilter = "all" | "datasets" | "models" | "research" | "speaker-evidence";
type EvidenceFilter = "all" | "documented-presence" | "representative-point" | "unmapped";
type ConfidenceFilter = "all" | "high" | "medium" | "low" | "unspecified";
type ReviewFilter = "all" | "ready" | "needs-review";
const NATIONAL_LANGUAGE_IDS = ["language-ktu", "language-lin", "language-swc", "language-lua"];

function resourceIsOpen(resource: AtlasResource) {
  return resource.access === "open-download";
}

function humanize(value: string) {
  return value.replaceAll("-", " ");
}

function resourceLabel(type: string) {
  const labels: Record<string, string> = {
    bitext: "Parallel dataset",
    corpus: "Text corpus",
    speech: "Speech dataset",
    publication: "Research publication",
    model: "Language model",
  };
  return labels[type] ?? humanize(type);
}

function matchesPlace(language: AtlasLanguage, place: AtlasPlaceSelection, approvedOnly = false) {
  const claimMatches = language.place_claims.some((claim) =>
    place.adminLevel === "province" ? claim.province_place_id === place.id : claim.place_id === place.id,
  );
  if (claimMatches || approvedOnly) return claimMatches;
  return language.geographic_candidates.some((candidate) =>
    place.adminLevel === "province"
      ? candidate.province_place_id === place.id
      : candidate.territory_place_id === place.id,
  );
}

function coverageCounts(language: AtlasLanguage) {
  const datasets = language.resources.filter((resource) => ["dataset", "corpus", "bitext", "speech"].includes(resource.type)).length
    + language.discovered_sources.filter((source) => source.kind === "dataset").length;
  const models = language.resources.filter((resource) => resource.type === "model").length
    + language.discovered_sources.filter((source) => source.kind === "model").length;
  const research = language.resources.filter((resource) => ["publication", "grammar", "dictionary", "orthography"].includes(resource.type)).length
    + language.discovered_sources.filter((source) => source.kind === "research").length;
  const geographicSources = new Set(language.geographic_candidates.map((candidate) => candidate.source_url)).size;
  return {
    datasets,
    models,
    research,
    sources: language.resources.length + language.discovered_sources.length + geographicSources,
  };
}

function evidenceForPlace(language: AtlasLanguage, place: AtlasPlaceSelection | null) {
  if (!place) return language.geographic_candidates;
  return language.geographic_candidates.filter((candidate) =>
    place.adminLevel === "province" ? candidate.province_place_id === place.id : candidate.territory_place_id === place.id,
  );
}

function csvCell(value: string | number) {
  const text = String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function downloadFile(filename: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function ResourceCard({ resource }: { resource: AtlasResource }) {
  const link = resource.download_url || resource.homepage_url;
  return (
    <article className="resource-card">
      <div className="resource-card__heading">
        <span className={`access-dot ${resourceIsOpen(resource) ? "is-open" : ""}`} />
        <div>
          <p className="eyebrow">{resourceLabel(resource.type)}</p>
          <h4>{resource.title}</h4>
        </div>
      </div>
      <dl className="resource-facts">
        <div><dt>Access</dt><dd>{humanize(resource.access)}</dd></div>
        <div><dt>Licence</dt><dd>{resource.licence || "Not established"}</dd></div>
        <div><dt>Scope</dt><dd>{humanize(resource.geographic_scope)}</dd></div>
        <div><dt>Size</dt><dd>{resource.size?.toLocaleString() || "—"} {resource.unit || ""}</dd></div>
      </dl>
      <p className="source-line"><strong>{resource.source.publisher}</strong> · {resource.source.citation}</p>
      {resource.limitations && <p className="limitations">{resource.limitations}</p>}
      <a href={link} target="_blank" rel="noreferrer" className="text-link">Open {resource.type === "bitext" ? "dataset" : "source"} <span aria-hidden>↗</span></a>
    </article>
  );
}

function CandidateSourceCard({ source }: { source: DiscoveredSource }) {
  const details = [
    source.publication_year,
    source.licence,
    source.downloads !== undefined ? `${source.downloads.toLocaleString()} downloads` : null,
    source.stars !== undefined ? `${source.stars.toLocaleString()} stars` : null,
    source.open_access ? "open access" : null,
  ].filter(Boolean);
  return (
    <article className="candidate-card">
      <div className="candidate-card__meta"><span>{source.provider}</span><span>{resourceLabel(source.kind)}</span><span>Candidate</span></div>
      <h4>{source.title}</h4>
      {source.authors?.length ? <p className="candidate-authors">{source.authors.join(", ")}</p> : null}
      {source.description ? <p>{source.description}</p> : null}
      {details.length ? <p className="candidate-details">{details.join(" · ")}</p> : null}
      <a href={source.url} target="_blank" rel="noreferrer" className="text-link">Open on {source.provider} <span aria-hidden>↗</span></a>
    </article>
  );
}

function LanguageProfile({ language, onClose }: { language: AtlasLanguage; onClose: () => void }) {
  const [sourceKind, setSourceKind] = useState<"all" | DiscoveredSource["kind"]>("all");
  const [showAllSources, setShowAllSources] = useState(false);
  const unresolved = Object.entries(language.review.checks).filter(([, value]) => value !== "approved");
  const coverage = coverageCounts(language);
  const filteredSources = language.discovered_sources.filter((source) => sourceKind === "all" || source.kind === sourceKind);
  const visibleSources = showAllSources ? filteredSources : filteredSources.slice(0, 10);
  return (
    <section className="profile" role="region" aria-labelledby="language-profile-title">
      <button className="close-button" onClick={onClose} aria-label="Close language profile" autoFocus>×</button>
      <p className="eyebrow">Draft language profile · ISO 639-3</p>
      <div className="profile__title"><h2 id="language-profile-title">{language.name}</h2><span className="iso-badge">{language.iso}</span></div>
      {language.aliases.length > 0 && <p className="aliases">Also indexed as {language.aliases.join(", ")}</p>}
      <div className="notice notice--warm">
        <strong>Review state: {humanize(language.review.status)}</strong>
        <span>Not promoted to verified public evidence. Named human approval is still required.</span>
      </div>
      <div className="coverage-section">
        <h3>Coverage at a glance</h3>
        <div className="coverage-grid">
          <div><strong>—</strong><span>Speakers</span><small>No reviewed estimate</small></div>
          <div><strong>{coverage.sources}</strong><span>Digital sources</span><small>Resource and geographic evidence links</small></div>
          <div><strong>{coverage.datasets}</strong><span>Datasets</span><small>Text or speech</small></div>
          <div><strong>{coverage.models}</strong><span>Models</span><small>Verified records</small></div>
          <div><strong>{coverage.research}</strong><span>Linguistic research</span><small>Publications and descriptions</small></div>
        </div>
      </div>
      <div className="profile-grid">
        <div><span>Project grouping</span><strong>{language.region}</strong></div>
        <div><span>Reviewed</span><strong>{language.last_reviewed_at}</strong></div>
      </div>
      <p className="classification">{language.classification_note}</p>
      {language.geographic_candidates.map((candidate) => (
        <div className="geographic-lead" key={candidate.id}>
          <div className="geographic-lead__heading"><p className="eyebrow">{candidate.evidence_type === "documented-presence" ? "Documented presence" : "Geographic candidate"}</p><span>{humanize(candidate.role)}</span></div>
          <strong>{candidate.territory_name ? `${candidate.territory_name}, ` : ""}{candidate.province_name}</strong>
          <div className="evidence-status"><span className={`confidence-badge confidence-badge--${candidate.confidence ?? "unspecified"}`}>{candidate.confidence ? `${candidate.confidence} confidence` : "Confidence not stated"}</span><span>{humanize(candidate.review_status)}</span></div>
          {candidate.evidence_type === "documented-presence" ? (
            <p>
              {typeof candidate.speaker_percentage === "number"
                ? `${candidate.speaker_percentage}% — ${candidate.percentage_basis ?? "reported speaking the language"}. `
                : ""}
              {candidate.evidence_locator}.
            </p>
          ) : candidate.point ? (
            <p>Glottolog identifies this row as {candidate.source_language_name} ({candidate.glottocode}). The point at {candidate.point.latitude.toFixed(4)}, {candidate.point.longitude.toFixed(4)} falls inside this administrative context.</p>
          ) : null}
          <p>{candidate.limitations}</p>
          <a href={candidate.source_url} target="_blank" rel="noreferrer" className="text-link">Open {candidate.source_title} <span aria-hidden>↗</span></a>
        </div>
      ))}
      <div className="review-box">
        <h3>Evidence review</h3>
        {unresolved.length ? (
          <p>{unresolved.map(([check]) => humanize(check)).join(", ")} require resolution.</p>
        ) : (
          <p>All automated checks pass; human approval remains outstanding.</p>
        )}
        <div className="tag-row">{language.review.blockers.map((blocker) => <span className="tag" key={blocker}>{humanize(blocker)}</span>)}</div>
      </div>
      <div className="resource-section">
        <div className="section-heading"><h3>Reviewed source</h3><span>{language.resources.length}</span></div>
        {language.resources.map((resource) => <ResourceCard resource={resource} key={resource.id} />)}
      </div>
      <div className="candidate-section">
        <div className="section-heading"><h3>Source leads</h3><span>{language.discovered_sources.length}</span></div>
        <p className="candidate-note">Automatically discovered links. Check language identity, variety, geography, licence, and access before treating them as verified.</p>
        <div className="source-filters" aria-label="Filter source leads">
          {(["all", "dataset", "model", "repository", "research", "catalogue"] as const).map((kind) => (
            <button key={kind} aria-pressed={sourceKind === kind} className={sourceKind === kind ? "active" : ""} onClick={() => { setSourceKind(kind); setShowAllSources(false); }}>
              {kind === "all" ? "All" : resourceLabel(kind)}
            </button>
          ))}
        </div>
        <div className="candidate-list">
          {visibleSources.map((source) => <CandidateSourceCard source={source} key={source.id} />)}
          {!visibleSources.length && <p className="empty-state">No candidate sources in this category yet.</p>}
        </div>
        {filteredSources.length > 10 && <button className="show-more" onClick={() => setShowAllSources((value) => !value)}>{showAllSources ? "Show fewer" : `Show all ${filteredSources.length}`}</button>}
      </div>
    </section>
  );
}

export default function AtlasExplorer() {
  const [bundle, setBundle] = useState<AtlasBundle | null>(null);
  const [places, setPlaces] = useState<AtlasPlaceOption[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);
  const [query, setQuery] = useState("");
  const [access, setAccess] = useState<AccessFilter>("all");
  const [region, setRegion] = useState("all");
  const [coverageFilter, setCoverageFilter] = useState<CoverageFilter>("all");
  const [evidenceFilter, setEvidenceFilter] = useState<EvidenceFilter>("all");
  const [confidenceFilter, setConfidenceFilter] = useState<ConfidenceFilter>("all");
  const [reviewFilter, setReviewFilter] = useState<ReviewFilter>("all");
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  const [showMapGuide, setShowMapGuide] = useState(true);
  const [selected, setSelected] = useState<AtlasLanguage | null>(null);
  const [selectedPlace, setSelectedPlace] = useState<AtlasPlaceSelection | null>(null);
  const [detailLevel, setDetailLevel] = useState<"provinces" | "territories">("provinces");
  const handlePlaceSelect = useCallback((place: AtlasPlaceSelection) => {
    setSelectedPlace(place);
    setSelected(null);
    setShowMobileFilters(false);
  }, []);
  const changeDetailLevel = (level: "provinces" | "territories") => {
    setDetailLevel(level);
    setSelectedPlace(null);
  };
  const selectPlaceById = (placeId: string) => {
    if (!placeId) {
      setSelectedPlace(null);
      return;
    }
    const place = places.find((item) => item.id === placeId);
    if (!place) return;
    setSelectedPlace(place);
    setDetailLevel(place.adminLevel === "territory" ? "territories" : "provinces");
    setSelected(null);
    setShowMobileFilters(false);
  };
  const selectLanguage = (language: AtlasLanguage) => {
    setSelected(language);
    if (language.geographic_candidates.some((candidate) => candidate.territory_place_id)) {
      setDetailLevel("territories");
    }
  };

  useEffect(() => {
    fetch("/generated/atlas/catalog.json")
      .then((response) => {
        if (!response.ok) throw new Error("The generated catalogue could not be loaded.");
        return response.json() as Promise<AtlasBundle>;
      })
      .then(setBundle)
      .catch((reason: Error) => setError(reason.message));
  }, [reloadKey]);

  const retryCatalogue = () => {
    setError(null);
    setBundle(null);
    setReloadKey((value) => value + 1);
  };

  useEffect(() => {
    Promise.all([
      fetch("/generated/geodata/cod-adm1.geojson").then((response) => response.json()),
      fetch("/generated/geodata/cod-adm2.geojson").then((response) => response.json()),
    ]).then(([provinces, territories]) => {
      const provinceOptions: AtlasPlaceOption[] = provinces.features.map((feature: { properties: Record<string, string> }) => ({
        id: `place-${feature.properties.id}`,
        name: feature.properties.name,
        adminLevel: "province",
        sourceCode: feature.properties.source_code,
      }));
      const territoryOptions: AtlasPlaceOption[] = territories.features.map((feature: { properties: Record<string, string> }) => ({
        id: `place-${feature.properties.id}`,
        name: feature.properties.name,
        adminLevel: "territory",
        parentId: `place-${feature.properties.parent_id}`,
        sourceCode: feature.properties.source_code,
      }));
      setPlaces([...provinceOptions, ...territoryOptions]);
    }).catch(() => setPlaces([]));
  }, []);

  useEffect(() => {
    if (!selected) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelected(null);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [selected]);

  useEffect(() => {
    if (!showMapGuide) return;
    const timer = window.setTimeout(() => setShowMapGuide(false), 9000);
    return () => window.clearTimeout(timer);
  }, [showMapGuide]);

  const regions = useMemo(() => [...new Set(bundle?.languages.map((item) => item.region) ?? [])].sort(), [bundle]);
  const languages = useMemo(() => {
    const term = query.trim().toLowerCase();
    return (bundle?.languages ?? []).filter((language) => {
      const coverage = coverageCounts(language);
      const relevantEvidence = evidenceForPlace(language, selectedPlace);
      const matchesText = !term || [language.name, language.iso, ...language.aliases].some((value) => value.toLowerCase().includes(term));
      const matchesAccess = access === "all" || (access === "open" ? language.resources.some(resourceIsOpen) : !language.resources.some(resourceIsOpen));
      const matchesGeography = !selectedPlace || matchesPlace(language, selectedPlace);
      const matchesCoverage = coverageFilter === "all"
        || (coverageFilter === "datasets" && coverage.datasets > 0)
        || (coverageFilter === "models" && coverage.models > 0)
        || (coverageFilter === "research" && coverage.research > 0)
        || (coverageFilter === "speaker-evidence" && relevantEvidence.some((candidate) => typeof candidate.speaker_percentage === "number"));
      const matchesEvidence = evidenceFilter === "all"
        || (evidenceFilter === "unmapped" && relevantEvidence.length === 0)
        || relevantEvidence.some((candidate) => candidate.evidence_type === evidenceFilter);
      const matchesConfidence = confidenceFilter === "all"
        || (confidenceFilter === "unspecified" && relevantEvidence.some((candidate) => !candidate.confidence))
        || relevantEvidence.some((candidate) => candidate.confidence === confidenceFilter);
      const matchesReview = reviewFilter === "all"
        || (reviewFilter === "ready" && language.review.ready_for_promotion)
        || (reviewFilter === "needs-review" && !language.review.ready_for_promotion);
      return matchesText && matchesAccess && matchesGeography && matchesCoverage && matchesEvidence && matchesConfidence && matchesReview && (region === "all" || language.region === region);
    });
  }, [access, bundle, confidenceFilter, coverageFilter, evidenceFilter, query, region, reviewFilter, selectedPlace]);
  const placeCounts = useMemo(() => {
    if (!selectedPlace || !bundle) return null;
    return {
      approved: bundle.languages.filter((language) => matchesPlace(language, selectedPlace, true)).length,
      candidates: bundle.languages.filter((language) => matchesPlace(language, selectedPlace)).length,
    };
  }, [bundle, selectedPlace]);
  const placeLanguages = useMemo(
    () => selectedPlace ? (bundle?.languages ?? []).filter((language) => matchesPlace(language, selectedPlace)) : [],
    [bundle, selectedPlace],
  );
  const placeCoverage = useMemo(() => placeLanguages.reduce((total, language) => {
    const coverage = coverageCounts(language);
    total.sources += coverage.sources;
    total.datasets += coverage.datasets;
    total.models += coverage.models;
    total.research += coverage.research;
    if (language.geographic_candidates.some((candidate) =>
      (selectedPlace?.adminLevel === "province" ? candidate.province_place_id : candidate.territory_place_id) === selectedPlace?.id
      && typeof candidate.speaker_percentage === "number")) total.speakerEvidence += 1;
    return total;
  }, { sources: 0, datasets: 0, models: 0, research: 0, speakerEvidence: 0 }), [placeLanguages, selectedPlace]);
  const selectedProvince = selectedPlace?.adminLevel === "province"
    ? selectedPlace
    : places.find((place) => place.id === selectedPlace?.parentId);
  const provinceTerritories = useMemo(() => selectedProvince
    ? places
      .filter((place) => place.adminLevel === "territory" && place.parentId === selectedProvince.id)
      .map((place) => ({
        ...place,
        languageCount: (bundle?.languages ?? []).filter((language) => matchesPlace(language, place)).length,
      }))
      .sort((left, right) => right.languageCount - left.languageCount || left.name.localeCompare(right.name))
    : [], [bundle, places, selectedProvince]);
  const provinceOptions = useMemo(() => places.filter((place) => place.adminLevel === "province").sort((left, right) => left.name.localeCompare(right.name)), [places]);
  const territoryOptions = useMemo(() => places.filter((place) => place.adminLevel === "territory").sort((left, right) => left.name.localeCompare(right.name) || left.sourceCode.localeCompare(right.sourceCode)), [places]);
  const nationalLanguages = NATIONAL_LANGUAGE_IDS
    .map((id) => bundle?.languages.find((language) => language.id === id))
    .filter((language): language is AtlasLanguage => Boolean(language));
  const highlightedProvinceIds = selected
    ? [...new Set(selected.geographic_candidates.map((candidate) => candidate.province_place_id))]
    : [];
  const highlightedTerritoryIds = selected
    ? [...new Set(selected.geographic_candidates.flatMap((candidate) => candidate.territory_place_id ? [candidate.territory_place_id] : []))]
    : [];
  const activeFilterCount = Number(Boolean(query.trim())) + Number(access !== "all") + Number(region !== "all")
    + Number(coverageFilter !== "all") + Number(evidenceFilter !== "all") + Number(confidenceFilter !== "all")
    + Number(reviewFilter !== "all");
  const resetLanguageFilters = () => {
    setQuery("");
    setAccess("all");
    setRegion("all");
    setCoverageFilter("all");
    setEvidenceFilter("all");
    setConfidenceFilter("all");
    setReviewFilter("all");
  };
  const exportJson = () => {
    const exported = languages.map((language) => ({
      id: language.id,
      name: language.name,
      iso_639_3: language.iso,
      aliases: language.aliases,
      project_grouping: language.region,
      review: language.review,
      coverage: coverageCounts(language),
      resources: language.resources,
      discovered_sources: language.discovered_sources,
      geographic_evidence: evidenceForPlace(language, selectedPlace),
    }));
    downloadFile("congo-lang-atlas-filtered.json", `${JSON.stringify({
      bundle_version: bundle?.bundle_version,
      data_generated_at: bundle?.generated_at,
      selected_place: selectedPlace,
      language_count: exported.length,
      languages: exported,
    }, null, 2)}\n`, "application/json");
  };
  const exportCsv = () => {
    const header = ["name", "iso_639_3", "aliases", "project_grouping", "review_status", "digital_sources", "datasets", "models", "research", "geographic_evidence", "selected_place"];
    const rows = languages.map((language) => {
      const coverage = coverageCounts(language);
      return [language.name, language.iso, language.aliases.join("; "), language.region, language.review.status, coverage.sources, coverage.datasets, coverage.models, coverage.research, evidenceForPlace(language, selectedPlace).length, selectedPlace?.name ?? "National catalogue"];
    });
    downloadFile("congo-lang-atlas-filtered.csv", `${[header, ...rows].map((row) => row.map(csvCell).join(",")).join("\n")}\n`, "text/csv;charset=utf-8");
  };

  if (error) return <main className="state-page" role="alert"><div className="state-brand"><span>CL</span><strong>Atlas</strong></div><p className="eyebrow">Data connection interrupted</p><h1>Catalogue unavailable</h1><p>{error}</p><button className="state-action" onClick={retryCatalogue}>Try again</button></main>;
  if (!bundle) return <main className="state-page" aria-live="polite"><div className="state-brand"><span>CL</span><strong>Atlas</strong></div><div className="loader" /><p>Preparing language and geographic evidence…</p><div className="loading-lines" aria-hidden><i /><i /><i /></div></main>;

  const closeProfile = () => setSelected(null);

  return (
    <main>
      <a className="skip-link" href="#atlas-catalogue">Skip to language catalogue</a>
      <header className="site-header">
        <a href="#atlas" className="wordmark" aria-label="CL Atlas home"><span className="wordmark__mark">CL</span><span className="wordmark__name">Atlas</span></a>
      </header>

      <section className="workspace" id="atlas">
        <aside className={`catalogue-panel ${selectedPlace ? "has-place-selection" : ""}`} id="atlas-catalogue">
          <div className="panel-heading"><div><p className="eyebrow">{selectedPlace ? `${selectedPlace.adminLevel} selected` : "National catalogue"}</p><h2>{selectedPlace?.name || "Languages"}</h2></div><span>{languages.length} / {bundle.languages.length}</span></div>
          {selectedPlace && <div className="place-context">
            <div className="place-context__heading"><div><strong>{placeCounts?.candidates || 0} language lead{placeCounts?.candidates === 1 ? "" : "s"}</strong><span>{placeCounts?.approved || 0} reviewed geographic claim{placeCounts?.approved === 1 ? "" : "s"}</span></div><button onClick={() => setSelectedPlace(null)}>Clear place</button></div>
            <div className="place-stats" aria-label={`Resource coverage for ${selectedPlace.name}`}>
              <div><strong>{placeCoverage.speakerEvidence || "—"}</strong><span>Speaker evidence</span></div>
              <div><strong>{placeCoverage.sources}</strong><span>Digital sources</span></div>
              <div><strong>{placeCoverage.datasets}</strong><span>Datasets</span></div>
              <div><strong>{placeCoverage.models}</strong><span>Models</span></div>
              <div><strong>{placeCoverage.research}</strong><span>Research</span></div>
            </div>
            {selectedPlace.adminLevel === "territory" && selectedProvince && <button className="province-return" onClick={() => { setSelectedPlace(selectedProvince); setDetailLevel("provinces"); }}>← {selectedProvince.name} province</button>}
            {provinceTerritories.length > 0 && <div className="territory-browser">
              <div><strong>{selectedProvince?.name} territories</strong><span>Select a territory to inspect its language evidence</span></div>
              <div className="territory-list">
                {provinceTerritories.map((territory) => <button key={territory.id} className={selectedPlace.id === territory.id ? "active" : ""} onClick={() => { setSelectedPlace(territory); setDetailLevel("territories"); setSelected(null); setShowMobileFilters(false); }}><span>{territory.name}<small>{territory.sourceCode}</small></span><strong>{territory.languageCount}</strong></button>)}
              </div>
            </div>}
            <p>Counts combine reviewed records and visible candidates. They do not define complete language distributions.</p>
          </div>}
          <label className="search-field"><span className="sr-only">Search languages</span><span aria-hidden>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, alias, or ISO code" /></label>
          <div className={`filters ${showMobileFilters ? "is-open" : ""}`}>
            <button className="mobile-filter-toggle" type="button" aria-expanded={showMobileFilters} onClick={() => setShowMobileFilters((value) => !value)}>
              <span>Filters</span><small>{activeFilterCount ? `${activeFilterCount} active` : "Optional"}</small><i aria-hidden>{showMobileFilters ? "−" : "+"}</i>
            </button>
            <div className="filter-content">
              <select value={region} onChange={(event) => setRegion(event.target.value)} aria-label="Filter by project grouping"><option value="all">All project groupings</option>{regions.map((value) => <option key={value}>{value}</option>)}</select>
              <div className="segmented" aria-label="Filter by access">
                {(["all", "open", "restricted"] as const).map((value) => <button aria-pressed={access === value} className={access === value ? "active" : ""} onClick={() => setAccess(value)} key={value}>{value}</button>)}
              </div>
              <div className="filter-grid">
                <label><span>Resource coverage</span><select value={coverageFilter} onChange={(event) => setCoverageFilter(event.target.value as CoverageFilter)}><option value="all">Any coverage</option><option value="datasets">Has datasets</option><option value="models">Has models</option><option value="research">Has research</option><option value="speaker-evidence">Has speaker evidence</option></select></label>
                <label><span>Geographic evidence</span><select value={evidenceFilter} onChange={(event) => setEvidenceFilter(event.target.value as EvidenceFilter)}><option value="all">Any evidence</option><option value="documented-presence">Documented presence</option><option value="representative-point">Representative point</option><option value="unmapped">Not mapped</option></select></label>
                <label><span>Evidence confidence</span><select value={confidenceFilter} onChange={(event) => setConfidenceFilter(event.target.value as ConfidenceFilter)}><option value="all">Any confidence</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option><option value="unspecified">Not stated</option></select></label>
                <label><span>Human review</span><select value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value as ReviewFilter)}><option value="all">Any review state</option><option value="ready">Ready for promotion</option><option value="needs-review">Needs human review</option></select></label>
              </div>
              <div className="filter-actions"><span>{activeFilterCount ? `${activeFilterCount} active filter${activeFilterCount === 1 ? "" : "s"}` : "No language filters"}</span><button onClick={resetLanguageFilters} disabled={!activeFilterCount}>Reset</button></div>
            </div>
          </div>
          <p className="sr-only" aria-live="polite">{languages.length} language results</p>
          <div className="language-list" aria-label={`${languages.length} language results`}>
            {languages.map((language) => {
              const hasOpen = language.resources.some(resourceIsOpen);
              const coverage = coverageCounts(language);
              const hasSpeakerEvidence = selectedPlace && language.geographic_candidates.some((candidate) =>
                (selectedPlace.adminLevel === "province" ? candidate.province_place_id : candidate.territory_place_id) === selectedPlace.id
                && typeof candidate.speaker_percentage === "number");
              return <button aria-pressed={selected?.id === language.id} className={`language-row ${selected?.id === language.id ? "selected" : ""}`} onClick={() => selectLanguage(language)} key={language.id}>
                <span className="language-row__code">{language.iso}</span><span><strong>{language.name}</strong><small>{selectedPlace ? (matchesPlace(language, selectedPlace, true) ? "Reviewed place claim" : "Documented geographic lead") : `${language.region} · ${coverage.sources} source links`}</small>{selectedPlace && <span className="language-row__coverage"><span>{hasSpeakerEvidence ? "Speaker data" : "No speaker estimate"}</span><span>{coverage.datasets} data</span><span>{coverage.models} models</span><span>{coverage.research} research</span></span>}</span><span className={`access-dot ${hasOpen ? "is-open" : ""}`} title={hasOpen ? "Has an open download" : "No open download"} />
              </button>;
            })}
            {!languages.length && <div className="empty-state">
              <p>{activeFilterCount ? "No languages match the active search and filters." : selectedPlace ? "No source-backed language evidence is indexed for this place yet." : "No languages are available in the public catalogue."}</p>
              {activeFilterCount > 0 && <button onClick={resetLanguageFilters}>Reset language filters</button>}
            </div>}
          </div>
          <div className="export-actions catalogue-export" aria-label="Export filtered metadata"><span>Export {languages.length} result{languages.length === 1 ? "" : "s"}</span><button onClick={exportCsv} disabled={!languages.length}>CSV</button><button onClick={exportJson} disabled={!languages.length}>JSON</button></div>
        </aside>

        <section className="map-panel">
          <div className="map-toolbar">
            <div><p className="eyebrow">{selectedPlace?.adminLevel || "Map"}</p><strong>{selectedPlace?.name || "Select a province or territory"}</strong></div>
            <div className="map-controls">
              <label className="place-picker"><span className="sr-only">Choose a province or territory</span><select value={selectedPlace?.id ?? ""} onChange={(event) => selectPlaceById(event.target.value)}><option value="">Choose a place</option><optgroup label="Provinces">{provinceOptions.map((place) => <option value={place.id} key={place.id}>{place.name}</option>)}</optgroup><optgroup label="Territories and cities">{territoryOptions.map((place) => <option value={place.id} key={place.id}>{place.name} · {place.sourceCode}</option>)}</optgroup></select></label>
              <div className="segmented" aria-label="Administrative detail level"><button aria-pressed={detailLevel === "provinces"} className={detailLevel === "provinces" ? "active" : ""} onClick={() => changeDetailLevel("provinces")}>Provinces</button><button aria-pressed={detailLevel === "territories"} className={detailLevel === "territories" ? "active" : ""} onClick={() => changeDetailLevel("territories")}>Territories</button></div>
            </div>
          </div>
          <div className="national-language-switcher" aria-label="Locate a national language">
            <span>Locate a national language</span>
            {nationalLanguages.map((language) => {
              const provinceCount = new Set(language.geographic_candidates.map((candidate) => candidate.province_place_id)).size;
              return <button key={language.id} aria-pressed={selected?.id === language.id} className={selected?.id === language.id ? "active" : ""} onClick={() => { setSelectedPlace(null); setDetailLevel("provinces"); setSelected(language); }}>{language.name}<small>{provinceCount} province{provinceCount === 1 ? "" : "s"}</small></button>;
            })}
            <button className="country-view" onClick={() => { setSelected(null); setSelectedPlace(null); setDetailLevel("provinces"); }}>Country view</button>
          </div>
          <div className="map-legend" aria-label="Map evidence legend">
            <strong>{selected ? `${selected.name} evidence` : selectedPlace ? selectedPlace.name : "Map legend"}</strong>
            <span><i className="legend-swatch legend-swatch--selected" />Selected place</span>
            <span><i className="legend-swatch legend-swatch--evidence" />Sourced language context</span>
            {detailLevel === "territories" && <span><i className="legend-swatch legend-swatch--territory" />Territory navigation</span>}
          </div>
          <AtlasMap detailLevel={detailLevel} highlightedProvinceIds={highlightedProvinceIds} highlightedTerritoryIds={highlightedTerritoryIds} selectedPlaceId={selectedPlace?.id} onPlaceSelect={handlePlaceSelect} />
          {showMapGuide ? <aside className="map-disclosure" aria-label="Map guidance"><span aria-hidden>◇</span><p><strong>Click any area to filter geographic leads, or select a national language to locate its documented broad region.</strong> Highlights are evidence contexts, not exclusive language borders or complete distributions.</p><button onClick={() => setShowMapGuide(false)} aria-label="Dismiss map guidance">×</button></aside> : <button className="map-guide-trigger" onClick={() => setShowMapGuide(true)}>Map guide</button>}
        </section>

        {selected && <LanguageProfile key={selected.id} language={selected} onClose={closeProfile} />}
      </section>

      <footer className="site-footer">
        <div className="footer-brand"><span>CL</span><div><strong>Atlas</strong><p>A project by <a href="https://kivulinguaai.org/" target="_blank" rel="noreferrer">KivuLingua AI</a></p></div></div>
        <p className="footer-note">CongoLangAtlas is a research guide. Names, groupings, access, and geographic claims remain open to documented correction.</p>
        <nav className="footer-actions" aria-label="Project links">
          <Link className="footer-card footer-card--primary" href="/methodology"><span>Methodology & contributions</span><small>Review the evidence process or improve the atlas</small><i aria-hidden>→</i></Link>
          <a className="footer-card" href="https://kivulinguaai.org/" target="_blank" rel="noreferrer"><span>Visit KivuLingua AI</span><small>Community-led African language technology</small><i aria-hidden>↗</i></a>
        </nav>
      </footer>
    </main>
  );
}
