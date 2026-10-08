"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useMemo, useState } from "react";
import type { AtlasBundle, AtlasLanguage, AtlasPlaceOption, AtlasPlaceSelection, AtlasResource, DiscoveredSource } from "@/lib/types";

const AtlasMap = dynamic(() => import("./atlas-map"), { ssr: false });
type AccessFilter = "all" | "open" | "restricted";
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
    <section className="profile" aria-label={`${language.name} profile`}>
      <button className="close-button" onClick={onClose} aria-label="Close language profile">×</button>
      <p className="eyebrow">Draft language profile · ISO 639-3</p>
      <div className="profile__title"><h2>{language.name}</h2><span className="iso-badge">{language.iso}</span></div>
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
          <div><p className="eyebrow">{candidate.evidence_type === "documented-presence" ? "Documented presence" : "Geographic candidate"}</p><span>{humanize(candidate.role)}</span></div>
          <strong>{candidate.territory_name ? `${candidate.territory_name}, ` : ""}{candidate.province_name}</strong>
          {candidate.evidence_type === "documented-presence" ? (
            <p>
              {candidate.speaker_percentage !== undefined
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
            <button key={kind} className={sourceKind === kind ? "active" : ""} onClick={() => { setSourceKind(kind); setShowAllSources(false); }}>
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
  const [selected, setSelected] = useState<AtlasLanguage | null>(null);
  const [selectedPlace, setSelectedPlace] = useState<AtlasPlaceSelection | null>(null);
  const [detailLevel, setDetailLevel] = useState<"provinces" | "territories">("provinces");
  const handlePlaceSelect = useCallback((place: AtlasPlaceSelection) => {
    setSelectedPlace(place);
    setSelected(null);
  }, []);
  const changeDetailLevel = (level: "provinces" | "territories") => {
    setDetailLevel(level);
    setSelectedPlace(null);
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

  const regions = useMemo(() => [...new Set(bundle?.languages.map((item) => item.region) ?? [])].sort(), [bundle]);
  const languages = useMemo(() => {
    const term = query.trim().toLowerCase();
    return (bundle?.languages ?? []).filter((language) => {
      const matchesText = !term || [language.name, language.iso, ...language.aliases].some((value) => value.toLowerCase().includes(term));
      const matchesAccess = access === "all" || (access === "open" ? language.resources.some(resourceIsOpen) : !language.resources.some(resourceIsOpen));
      const matchesGeography = !selectedPlace || matchesPlace(language, selectedPlace);
      return matchesText && matchesAccess && matchesGeography && (region === "all" || language.region === region);
    });
  }, [access, bundle, query, region, selectedPlace]);
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
      && candidate.speaker_percentage !== undefined)) total.speakerEvidence += 1;
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
  const nationalLanguages = NATIONAL_LANGUAGE_IDS
    .map((id) => bundle?.languages.find((language) => language.id === id))
    .filter((language): language is AtlasLanguage => Boolean(language));
  const highlightedProvinceIds = selected
    ? [...new Set(selected.geographic_candidates.map((candidate) => candidate.province_place_id))]
    : [];
  const highlightedTerritoryIds = selected
    ? [...new Set(selected.geographic_candidates.flatMap((candidate) => candidate.territory_place_id ? [candidate.territory_place_id] : []))]
    : [];

  if (error) return <main className="state-page" role="alert"><div className="state-brand"><span>CL</span><strong>Atlas</strong></div><p className="eyebrow">Data connection interrupted</p><h1>Catalogue unavailable</h1><p>{error}</p><button className="state-action" onClick={retryCatalogue}>Try again</button></main>;
  if (!bundle) return <main className="state-page" aria-live="polite"><div className="state-brand"><span>CL</span><strong>Atlas</strong></div><div className="loader" /><p>Preparing language and geographic evidence…</p><div className="loading-lines" aria-hidden><i /><i /><i /></div></main>;

  return (
    <main>
      <a className="skip-link" href="#atlas-catalogue">Skip to language catalogue</a>
      <header className="site-header">
        <a href="#atlas" className="wordmark" aria-label="CL Atlas home"><span className="wordmark__mark">CL</span><span className="wordmark__name">Atlas</span></a>
      </header>

      <section className="workspace" id="atlas">
        <aside className="catalogue-panel" id="atlas-catalogue">
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
                {provinceTerritories.map((territory) => <button key={territory.id} className={selectedPlace.id === territory.id ? "active" : ""} onClick={() => { setSelectedPlace(territory); setDetailLevel("territories"); setSelected(null); }}><span>{territory.name}<small>{territory.sourceCode}</small></span><strong>{territory.languageCount}</strong></button>)}
              </div>
            </div>}
            <p>Counts combine reviewed records and visible candidates. They do not define complete language distributions.</p>
          </div>}
          <label className="search-field"><span className="sr-only">Search languages</span><span aria-hidden>⌕</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Name, alias, or ISO code" /></label>
          <div className="filters">
            <select value={region} onChange={(event) => setRegion(event.target.value)} aria-label="Filter by project grouping"><option value="all">All project groupings</option>{regions.map((value) => <option key={value}>{value}</option>)}</select>
            <div className="segmented" aria-label="Filter by access">
              {(["all", "open", "restricted"] as const).map((value) => <button className={access === value ? "active" : ""} onClick={() => setAccess(value)} key={value}>{value}</button>)}
            </div>
          </div>
          <div className="language-list">
            {languages.map((language) => {
              const hasOpen = language.resources.some(resourceIsOpen);
              const coverage = coverageCounts(language);
              const hasSpeakerEvidence = selectedPlace && language.geographic_candidates.some((candidate) =>
                (selectedPlace.adminLevel === "province" ? candidate.province_place_id : candidate.territory_place_id) === selectedPlace.id
                && candidate.speaker_percentage !== undefined);
              return <button className={`language-row ${selected?.id === language.id ? "selected" : ""}`} onClick={() => selectLanguage(language)} key={language.id}>
                <span className="language-row__code">{language.iso}</span><span><strong>{language.name}</strong><small>{selectedPlace ? (matchesPlace(language, selectedPlace, true) ? "Reviewed place claim" : "Documented geographic lead") : `${language.region} · ${coverage.sources} source links`}</small>{selectedPlace && <span className="language-row__coverage"><span>{hasSpeakerEvidence ? "Speaker data" : "No speaker estimate"}</span><span>{coverage.datasets} data</span><span>{coverage.models} models</span><span>{coverage.research} research</span></span>}</span><span className={`access-dot ${hasOpen ? "is-open" : ""}`} title={hasOpen ? "Has an open download" : "No open download"} />
              </button>;
            })}
            {!languages.length && <div className="empty-state">
              <p>{selectedPlace && placeLanguages.length ? "Language evidence exists here, but the active search or filters hide it." : "No source-backed language evidence is indexed for this place yet."}</p>
              {selectedPlace && placeLanguages.length > 0 && <button onClick={() => { setQuery(""); setAccess("all"); setRegion("all"); }}>Reset language filters</button>}
            </div>}
          </div>
        </aside>

        <section className="map-panel">
          <div className="map-toolbar">
            <div><p className="eyebrow">{selectedPlace?.adminLevel || "Map"}</p><strong>{selectedPlace?.name || "Select a province or territory"}</strong></div>
            <div className="segmented"><button className={detailLevel === "provinces" ? "active" : ""} onClick={() => changeDetailLevel("provinces")}>Provinces</button><button className={detailLevel === "territories" ? "active" : ""} onClick={() => changeDetailLevel("territories")}>Territories</button></div>
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
          <div className="map-disclosure"><span aria-hidden>◇</span><p><strong>Click any area to filter geographic leads, or select a national language to locate its documented broad region.</strong> Highlights are evidence contexts—not exclusive language borders or complete distributions.</p></div>
        </section>

        {selected && <LanguageProfile key={selected.id} language={selected} onClose={() => setSelected(null)} />}
      </section>

      <footer><p>CongoLangAtlas is a research guide. Names, groupings, access, and geographic claims remain open to documented correction.</p><a href="https://github.com/Ashuza11/CongoLangAtlas" target="_blank" rel="noreferrer">View methodology and contribute ↗</a></footer>
    </main>
  );
}
