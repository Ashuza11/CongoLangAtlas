"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import LanguageSwitcher from "@/components/language-switcher";
import { getUi, localizeValue, type Locale } from "@/lib/i18n";
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

function resourceLabel(type: string, locale: Locale) {
  const c = getUi(locale);
  const labels: Record<string, string> = {
    bitext: c.parallelDataset,
    corpus: c.textCorpus,
    speech: c.speechDataset,
    publication: c.researchPublication,
    model: c.languageModel,
    dataset: c.datasets,
    research: c.research,
    repository: c.repository,
    catalogue: c.catalogue,
  };
  return labels[type] ?? localizeValue(type, locale);
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

function ResourceCard({ resource, locale }: { resource: AtlasResource; locale: Locale }) {
  const c = getUi(locale);
  const link = resource.download_url || resource.homepage_url;
  return (
    <article className="resource-card">
      <div className="resource-card__heading">
        <span className={`access-dot ${resourceIsOpen(resource) ? "is-open" : ""}`} />
        <div>
          <p className="eyebrow">{resourceLabel(resource.type, locale)}</p>
          <h4>{resource.title}</h4>
        </div>
      </div>
      <dl className="resource-facts">
        <div><dt>{c.access}</dt><dd>{localizeValue(resource.access, locale)}</dd></div>
        <div><dt>{c.licence}</dt><dd>{resource.licence || c.notEstablished}</dd></div>
        <div><dt>{c.scope}</dt><dd>{localizeValue(resource.geographic_scope, locale)}</dd></div>
        <div><dt>{c.size}</dt><dd>{resource.size?.toLocaleString(locale) || "—"} {resource.unit || ""}</dd></div>
      </dl>
      <p className="source-line"><strong>{resource.source.publisher}</strong> · {resource.source.citation}</p>
      {resource.limitations && <p className="limitations">{resource.limitations}</p>}
      <a href={link} target="_blank" rel="noreferrer" className="text-link">{c.openSource} {resource.type === "bitext" ? c.dataset : c.source} <span aria-hidden>↗</span></a>
    </article>
  );
}

function CandidateSourceCard({ source, locale }: { source: DiscoveredSource; locale: Locale }) {
  const c = getUi(locale);
  const details = [
    source.publication_year,
    source.licence,
    source.downloads !== undefined ? `${source.downloads.toLocaleString(locale)} ${c.downloads}` : null,
    source.stars !== undefined ? `${source.stars.toLocaleString(locale)} ${c.stars}` : null,
    source.open_access ? c.openAccess : null,
  ].filter(Boolean);
  return (
    <article className="candidate-card">
      <div className="candidate-card__meta"><span>{source.provider}</span><span>{resourceLabel(source.kind, locale)}</span><span>{c.candidate}</span></div>
      <h4>{source.title}</h4>
      {source.authors?.length ? <p className="candidate-authors">{source.authors.join(", ")}</p> : null}
      {source.description ? <p>{source.description}</p> : null}
      {details.length ? <p className="candidate-details">{details.join(" · ")}</p> : null}
      <a href={source.url} target="_blank" rel="noreferrer" className="text-link">{c.openOn} {source.provider} <span aria-hidden>↗</span></a>
    </article>
  );
}

function LanguageProfile({ language, onClose, locale }: { language: AtlasLanguage; onClose: () => void; locale: Locale }) {
  const c = getUi(locale);
  const [sourceKind, setSourceKind] = useState<"all" | DiscoveredSource["kind"]>("all");
  const [showAllSources, setShowAllSources] = useState(false);
  const unresolved = Object.entries(language.review.checks).filter(([, value]) => value !== "approved");
  const coverage = coverageCounts(language);
  const filteredSources = language.discovered_sources.filter((source) => sourceKind === "all" || source.kind === sourceKind);
  const visibleSources = showAllSources ? filteredSources : filteredSources.slice(0, 10);
  return (
    <section className="profile" role="region" aria-labelledby="language-profile-title">
      <button className="close-button" onClick={onClose} aria-label={c.closeProfile} autoFocus>×</button>
      <p className="eyebrow">{c.draftProfile}</p>
      <div className="profile__title"><h2 id="language-profile-title">{language.name}</h2><span className="iso-badge">{language.iso}</span></div>
      {language.aliases.length > 0 && <p className="aliases">{c.alsoIndexed} {language.aliases.join(", ")}</p>}
      <div className="notice notice--warm">
        <strong>{c.reviewState} : {localizeValue(language.review.status, locale)}</strong>
        <span>{c.reviewWarning}</span>
      </div>
      <div className="coverage-section">
        <h3>{c.coverageGlance}</h3>
        <div className="coverage-grid">
          <div><strong>—</strong><span>{c.speakers}</span><small>{c.noReviewedEstimate}</small></div>
          <div><strong>{coverage.sources}</strong><span>{c.digitalSources}</span><small>{c.resourceGeoLinks}</small></div>
          <div><strong>{coverage.datasets}</strong><span>{c.datasets}</span><small>{c.textSpeech}</small></div>
          <div><strong>{coverage.models}</strong><span>{c.models}</span><small>{c.verifiedRecords}</small></div>
          <div><strong>{coverage.research}</strong><span>{c.linguisticResearch}</span><small>{c.publicationsDescriptions}</small></div>
        </div>
      </div>
      <div className="profile-grid">
        <div><span>{c.projectGrouping}</span><strong>{localizeValue(language.region, locale)}</strong></div>
        <div><span>{c.reviewed}</span><strong>{language.last_reviewed_at}</strong></div>
      </div>
      <p className="classification">{language.classification_note}</p>
      {language.geographic_candidates.map((candidate) => (
        <div className="geographic-lead" key={candidate.id}>
          <div className="geographic-lead__heading"><p className="eyebrow">{candidate.evidence_type === "documented-presence" ? c.documentedPresence : c.geographicCandidate}</p><span>{localizeValue(candidate.role, locale)}</span></div>
          <strong>{candidate.territory_name ? `${candidate.territory_name}, ` : ""}{candidate.province_name}</strong>
          <div className="evidence-status"><span className={`confidence-badge confidence-badge--${candidate.confidence ?? "unspecified"}`}>{candidate.confidence ? `${localizeValue(candidate.confidence, locale)} ${c.confidence}` : c.confidenceUnstated}</span><span>{localizeValue(candidate.review_status, locale)}</span></div>
          {candidate.evidence_type === "documented-presence" ? (
            <p>
              {typeof candidate.speaker_percentage === "number"
                ? `${candidate.speaker_percentage}% — ${locale === "fr" ? c.reportedSpeaking : candidate.percentage_basis ?? c.reportedSpeaking}. `
                : ""}
              {candidate.evidence_locator}.
            </p>
          ) : candidate.point ? (
            <p>{c.glottologPrefix} {candidate.source_language_name} ({candidate.glottocode}). {c.pointAt} {candidate.point.latitude.toFixed(4)}, {candidate.point.longitude.toFixed(4)} {c.fallsContext}</p>
          ) : null}
          <p>{candidate.limitations}</p>
          <a href={candidate.source_url} target="_blank" rel="noreferrer" className="text-link">{c.openSource} {candidate.source_title} <span aria-hidden>↗</span></a>
        </div>
      ))}
      <div className="review-box">
        <h3>{c.evidenceReview}</h3>
        {unresolved.length ? (
          <p>{unresolved.map(([check]) => localizeValue(check, locale)).join(", ")} {c.requireResolution}</p>
        ) : (
          <p>{c.checksPass}</p>
        )}
        <div className="tag-row">{language.review.blockers.map((blocker) => <span className="tag" key={blocker}>{localizeValue(blocker, locale)}</span>)}</div>
      </div>
      <div className="resource-section">
        <div className="section-heading"><h3>{c.reviewedSource}</h3><span>{language.resources.length}</span></div>
        {language.resources.map((resource) => <ResourceCard resource={resource} locale={locale} key={resource.id} />)}
      </div>
      <div className="candidate-section">
        <div className="section-heading"><h3>{c.sourceLeads}</h3><span>{language.discovered_sources.length}</span></div>
        <p className="candidate-note">{c.candidateNote}</p>
        <div className="source-filters" aria-label={c.filterSources}>
          {(["all", "dataset", "model", "repository", "research", "catalogue"] as const).map((kind) => (
            <button key={kind} aria-pressed={sourceKind === kind} className={sourceKind === kind ? "active" : ""} onClick={() => { setSourceKind(kind); setShowAllSources(false); }}>
              {kind === "all" ? c.all : resourceLabel(kind, locale)}
            </button>
          ))}
        </div>
        <div className="candidate-list">
          {visibleSources.map((source) => <CandidateSourceCard source={source} locale={locale} key={source.id} />)}
          {!visibleSources.length && <p className="empty-state">{c.noCandidateSources}</p>}
        </div>
        {filteredSources.length > 10 && <button className="show-more" onClick={() => setShowAllSources((value) => !value)}>{showAllSources ? c.showFewer : `${c.showAll} ${filteredSources.length}`}</button>}
      </div>
    </section>
  );
}

export default function AtlasExplorer({ locale = "en" }: { locale?: Locale }) {
  const c = getUi(locale);
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
        if (!response.ok) throw new Error(locale === "fr" ? "Le catalogue généré n’a pas pu être chargé." : "The generated catalogue could not be loaded.");
        return response.json() as Promise<AtlasBundle>;
      })
      .then(setBundle)
      .catch((reason: Error) => setError(reason.message));
  }, [locale, reloadKey]);

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

  if (error) return <main className="state-page" role="alert"><div className="state-brand"><span>CL</span><strong>Atlas</strong></div><p className="eyebrow">{c.dataInterrupted}</p><h1>{c.catalogueUnavailable}</h1><p>{error}</p><button className="state-action" onClick={retryCatalogue}>{c.tryAgain}</button></main>;
  if (!bundle) return <main className="state-page" aria-live="polite"><div className="state-brand"><span>CL</span><strong>Atlas</strong></div><div className="loader" /><p>{c.preparing}</p><div className="loading-lines" aria-hidden><i /><i /><i /></div></main>;

  const closeProfile = () => setSelected(null);

  return (
    <main>
      <a className="skip-link" href="#atlas-catalogue">{c.skip}</a>
      <header className="site-header">
        <a href="#atlas" className="wordmark" aria-label="CL Atlas home"><span className="wordmark__mark">CL</span><span className="wordmark__name">Atlas</span></a>
        <LanguageSwitcher locale={locale} />
      </header>

      <section className="workspace" id="atlas">
        <aside className={`catalogue-panel ${selectedPlace ? "has-place-selection" : ""}`} id="atlas-catalogue">
          <div className="panel-heading"><div><p className="eyebrow">{selectedPlace ? `${localizeValue(selectedPlace.adminLevel, locale)} ${c.selected}` : c.nationalCatalogue}</p><h2>{selectedPlace?.name || c.languages}</h2></div><span>{languages.length} / {bundle.languages.length}</span></div>
          {selectedPlace && <div className="place-context">
            <div className="place-context__heading"><div><strong>{placeCounts?.candidates || 0} {placeCounts?.candidates === 1 ? c.languageLead : c.languageLeads}</strong><span>{placeCounts?.approved || 0} {placeCounts?.approved === 1 ? c.reviewedClaim : c.reviewedClaims}</span></div><button onClick={() => setSelectedPlace(null)}>{c.clearPlace}</button></div>
            <div className="place-stats" aria-label={`${c.resourceCoverage} : ${selectedPlace.name}`}>
              <div><strong>{placeCoverage.speakerEvidence || "—"}</strong><span>{c.speakerEvidence}</span></div>
              <div><strong>{placeCoverage.sources}</strong><span>{c.digitalSources}</span></div>
              <div><strong>{placeCoverage.datasets}</strong><span>{c.datasets}</span></div>
              <div><strong>{placeCoverage.models}</strong><span>{c.models}</span></div>
              <div><strong>{placeCoverage.research}</strong><span>{c.research}</span></div>
            </div>
            {selectedPlace.adminLevel === "territory" && selectedProvince && <button className="province-return" onClick={() => { setSelectedPlace(selectedProvince); setDetailLevel("provinces"); }}>← {selectedProvince.name} {c.province}</button>}
            {provinceTerritories.length > 0 && <div className="territory-browser">
              <div><strong>{selectedProvince?.name} · {c.territories}</strong><span>{c.inspectTerritory}</span></div>
              <div className="territory-list">
                {provinceTerritories.map((territory) => <button key={territory.id} className={selectedPlace.id === territory.id ? "active" : ""} onClick={() => { setSelectedPlace(territory); setDetailLevel("territories"); setSelected(null); setShowMobileFilters(false); }}><span>{territory.name}<small>{territory.sourceCode}</small></span><strong>{territory.languageCount}</strong></button>)}
              </div>
            </div>}
            <p>{c.countsDisclaimer}</p>
          </div>}
          <label className="search-field"><span className="sr-only">{c.searchLanguages}</span><span aria-hidden>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={c.searchPlaceholder} /></label>
          <div className={`filters ${showMobileFilters ? "is-open" : ""}`}>
            <button className="mobile-filter-toggle" type="button" aria-expanded={showMobileFilters} onClick={() => setShowMobileFilters((value) => !value)}>
              <span>{c.filters}</span><small>{activeFilterCount ? `${activeFilterCount} ${c.active}` : c.optional}</small><i aria-hidden>{showMobileFilters ? "−" : "+"}</i>
            </button>
            <div className="filter-content">
              <select value={region} onChange={(event) => setRegion(event.target.value)} aria-label={c.projectGroupingFilter}><option value="all">{c.allGroupings}</option>{regions.map((value) => <option value={value} key={value}>{localizeValue(value, locale)}</option>)}</select>
              <div className="segmented" aria-label={c.accessFilter}>
                {(["all", "open", "restricted"] as const).map((value) => <button aria-pressed={access === value} className={access === value ? "active" : ""} onClick={() => setAccess(value)} key={value}>{c[value]}</button>)}
              </div>
              <div className="filter-grid">
                <label><span>{c.resourceCoverage}</span><select value={coverageFilter} onChange={(event) => setCoverageFilter(event.target.value as CoverageFilter)}><option value="all">{c.anyCoverage}</option><option value="datasets">{c.hasDatasets}</option><option value="models">{c.hasModels}</option><option value="research">{c.hasResearch}</option><option value="speaker-evidence">{c.hasSpeakerEvidence}</option></select></label>
                <label><span>{c.geographicEvidence}</span><select value={evidenceFilter} onChange={(event) => setEvidenceFilter(event.target.value as EvidenceFilter)}><option value="all">{c.anyEvidence}</option><option value="documented-presence">{c.documentedPresence}</option><option value="representative-point">{c.representativePoint}</option><option value="unmapped">{c.notMapped}</option></select></label>
                <label><span>{c.evidenceConfidence}</span><select value={confidenceFilter} onChange={(event) => setConfidenceFilter(event.target.value as ConfidenceFilter)}><option value="all">{c.anyConfidence}</option><option value="high">{c.high}</option><option value="medium">{c.medium}</option><option value="low">{c.low}</option><option value="unspecified">{c.notStated}</option></select></label>
                <label><span>{c.humanReview}</span><select value={reviewFilter} onChange={(event) => setReviewFilter(event.target.value as ReviewFilter)}><option value="all">{c.anyReview}</option><option value="ready">{c.readyPromotion}</option><option value="needs-review">{c.needsReview}</option></select></label>
              </div>
              <div className="filter-actions"><span>{activeFilterCount ? `${activeFilterCount} ${activeFilterCount === 1 ? c.activeFilter : c.activeFilters}` : c.noFilters}</span><button onClick={resetLanguageFilters} disabled={!activeFilterCount}>{c.reset}</button></div>
            </div>
          </div>
          <p className="sr-only" aria-live="polite">{languages.length} {c.languageResults}</p>
          <div className="language-list" aria-label={`${languages.length} ${c.languageResults}`}>
            {languages.map((language) => {
              const hasOpen = language.resources.some(resourceIsOpen);
              const coverage = coverageCounts(language);
              const hasSpeakerEvidence = selectedPlace && language.geographic_candidates.some((candidate) =>
                (selectedPlace.adminLevel === "province" ? candidate.province_place_id : candidate.territory_place_id) === selectedPlace.id
                && typeof candidate.speaker_percentage === "number");
              return <button aria-pressed={selected?.id === language.id} className={`language-row ${selected?.id === language.id ? "selected" : ""}`} onClick={() => selectLanguage(language)} key={language.id}>
                <span className="language-row__code">{language.iso}</span><span><strong>{language.name}</strong><small>{selectedPlace ? (matchesPlace(language, selectedPlace, true) ? c.reviewedPlaceClaim : c.documentedLead) : `${localizeValue(language.region, locale)} · ${coverage.sources} ${c.sourceLinks}`}</small>{selectedPlace && <span className="language-row__coverage"><span>{hasSpeakerEvidence ? c.speakerData : c.noSpeakerEstimate}</span><span>{coverage.datasets} {c.data}</span><span>{coverage.models} {c.models}</span><span>{coverage.research} {c.research}</span></span>}</span><span className={`access-dot ${hasOpen ? "is-open" : ""}`} title={hasOpen ? c.hasOpenDownload : c.noOpenDownload} />
              </button>;
            })}
            {!languages.length && <div className="empty-state">
              <p>{activeFilterCount ? c.noFilterResults : selectedPlace ? c.noPlaceResults : c.noCatalogueResults}</p>
              {activeFilterCount > 0 && <button onClick={resetLanguageFilters}>{c.resetFilters}</button>}
            </div>}
          </div>
          <div className="export-actions catalogue-export" aria-label={c.exportMetadata}><span>{c.export} {languages.length} {languages.length === 1 ? c.result : c.results}</span><button onClick={exportCsv} disabled={!languages.length}>CSV</button><button onClick={exportJson} disabled={!languages.length}>JSON</button></div>
        </aside>

        <section className="map-panel">
          <div className="map-toolbar">
            <div><p className="eyebrow">{selectedPlace ? localizeValue(selectedPlace.adminLevel, locale) : c.map}</p><strong>{selectedPlace?.name || c.selectPlace}</strong></div>
            <div className="map-controls">
              <label className="place-picker"><span className="sr-only">{c.choosePlaceLabel}</span><select value={selectedPlace?.id ?? ""} onChange={(event) => selectPlaceById(event.target.value)}><option value="">{c.choosePlace}</option><optgroup label={c.provinces}>{provinceOptions.map((place) => <option value={place.id} key={place.id}>{place.name}</option>)}</optgroup><optgroup label={c.territoriesCities}>{territoryOptions.map((place) => <option value={place.id} key={place.id}>{place.name} · {place.sourceCode}</option>)}</optgroup></select></label>
              <div className="segmented" aria-label={c.detailLevel}><button aria-pressed={detailLevel === "provinces"} className={detailLevel === "provinces" ? "active" : ""} onClick={() => changeDetailLevel("provinces")}>{c.provinces}</button><button aria-pressed={detailLevel === "territories"} className={detailLevel === "territories" ? "active" : ""} onClick={() => changeDetailLevel("territories")}>{c.territories}</button></div>
            </div>
          </div>
          <div className="national-language-switcher" aria-label={c.locateNational}>
            <span>{c.locateNational}</span>
            {nationalLanguages.map((language) => {
              const provinceCount = new Set(language.geographic_candidates.map((candidate) => candidate.province_place_id)).size;
              return <button key={language.id} aria-pressed={selected?.id === language.id} className={selected?.id === language.id ? "active" : ""} onClick={() => { setSelectedPlace(null); setDetailLevel("provinces"); setSelected(language); }}>{language.name}<small>{provinceCount} {provinceCount === 1 ? c.province : c.provincePlural}</small></button>;
            })}
            <button className="country-view" onClick={() => { setSelected(null); setSelectedPlace(null); setDetailLevel("provinces"); }}>{c.countryView}</button>
          </div>
          <div className="map-legend" aria-label={c.mapLegendLabel}>
            <strong>{selected ? `${selected.name} · ${c.evidence}` : selectedPlace ? selectedPlace.name : c.mapLegend}</strong>
            <span><i className="legend-swatch legend-swatch--selected" />{c.selectedPlace}</span>
            <span><i className="legend-swatch legend-swatch--evidence" />{c.sourcedContext}</span>
            {detailLevel === "territories" && <span><i className="legend-swatch legend-swatch--territory" />{c.territoryNavigation}</span>}
          </div>
          <AtlasMap locale={locale} detailLevel={detailLevel} highlightedProvinceIds={highlightedProvinceIds} highlightedTerritoryIds={highlightedTerritoryIds} selectedPlaceId={selectedPlace?.id} onPlaceSelect={handlePlaceSelect} />
          {showMapGuide ? <aside className="map-disclosure" aria-label={c.mapGuidance}><span aria-hidden>◇</span><p><strong>{c.guideLead}</strong> {c.guideCaution}</p><button onClick={() => setShowMapGuide(false)} aria-label={c.dismissGuide}>×</button></aside> : <button className="map-guide-trigger" onClick={() => setShowMapGuide(true)}>{c.mapGuide}</button>}
        </section>

        {selected && <LanguageProfile key={selected.id} language={selected} locale={locale} onClose={closeProfile} />}
      </section>

      <footer className="site-footer">
        <div className="footer-brand"><span>CL</span><div><strong>Atlas</strong><p>{c.projectBy} <a href="https://kivulinguaai.org/" target="_blank" rel="noreferrer">KivuLingua AI</a></p></div></div>
        <p className="footer-note">{c.footerNote}</p>
        <nav className="footer-actions" aria-label={c.projectLinks}>
          <Link className="footer-card footer-card--primary" href={locale === "fr" ? "/fr/methodology" : "/methodology"}><span>{c.methodology}</span><small>{c.methodologyHint}</small><i aria-hidden>→</i></Link>
          <a className="footer-card" href="https://kivulinguaai.org/" target="_blank" rel="noreferrer"><span>{c.visitKivu}</span><small>{c.kivuHint}</small><i aria-hidden>↗</i></a>
        </nav>
      </footer>
    </main>
  );
}
