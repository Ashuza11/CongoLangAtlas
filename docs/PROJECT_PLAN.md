# CongoLangAtlas project plan

## 1. Goal

Build a highly interactive and trustworthy DRC language atlas that helps
researchers, communities, students, and technologists understand which
languages are documented, where they are used, what resources exist, how those
resources may be accessed, and which research gaps remain.

The project succeeds when a newcomer can explore a place or language, find
usable evidence and resources, understand their limitations, and leave with a
citable, realistic starting point for research.

## 2. Scope

### Included

- languages and named varieties documented as used in the DRC;
- province-, territory-, locality-, corridor-, and region-level evidence;
- alternate names and identifiers without collapsing distinct varieties;
- text, bitext, speech, audio, dictionaries, lexicons, grammars,
  orthographies, keyboards, fonts, educational material, and publications;
- datasets, catalogues, repositories, tools, models, and evaluation results;
- source, licence, access, provenance, version, and verification metadata;
- known gaps, unresolved claims, and requests for community confirmation;
- French and English interface content initially, with Congolese-language
  localization added through community-reviewed contributions.

### Not included in the first release

- unsupported polygon boundaries presented as exact language territories;
- private or copyrighted dataset contents;
- unverified speaker counts presented as current facts;
- automatic aggregation of related language varieties;
- a general-purpose corpus hosting service;
- claims that model scores alone measure a language's value or vitality.

## 3. Primary users and questions

### Researchers and students

- Which languages are documented in this province or territory?
- What datasets, grammars, dictionaries, or speech collections exist?
- Can I download and reuse them, and under what licence?
- Which names and identifiers refer to the same variety, and which do not?
- What has already been evaluated in NLP?

### Language communities and contributors

- Is the preferred language name and location represented correctly?
- How can I correct a claim or add a community resource?
- Which evidence is missing or outdated?

### NLP practitioners and funders

- Which languages have text, parallel text, or speech data?
- Where are resource gaps most severe?
- Which benchmarks and model results are comparable?
- What restrictions prevent reuse or publication?

## 4. Core product modules

### A. Interactive map

- Province and territory navigation
- Search by language, alternate name, identifier, or place
- Layer toggles for language presence, modality, resource count, and evidence
  confidence
- Clustered points and territory associations at national zoom
- Side panel listing languages and resources for the selected place
- Shareable URLs that preserve filters and selected entities
- Mobile, keyboard, and screen-reader accessible controls

### B. Language profiles

- Preferred and alternate names
- ISO 639-3, Glottocode, and other identifiers
- Variety and classification notes with cited sources
- Documented DRC locations and evidence precision
- Resource counts by modality and access status
- Dataset and publication cards
- NLP benchmarks, models, and evaluation summaries
- Gaps, caveats, last review date, and contribution link

### C. Resource explorer

- Filter by language, place, modality, domain, licence, access, format,
  publisher, and verification status
- Distinguish downloadable, gated, request-only, catalogue-only, and
  unavailable resources
- Display source URL, version, size, geographic provenance, and licence
- Export filtered metadata as CSV or JSON with citations

### D. Research-gap views

- Languages with no located text, speech, dictionary, or grammar resource
- Resources missing a clear licence or DRC-specific provenance
- Geographic areas with sparse documentation
- Benchmark and model coverage matrix
- Community confirmation queue

### E. Contribution and review

- Structured resource submission form
- Correction form tied to a specific claim
- GitHub issue/PR workflow for the first release
- Reviewer checklist and change history
- Named or anonymous contributor attribution according to consent

## 5. Delivery phases

### Phase 0 — Foundation and governance

1. Confirm project name, public licence, maintainers, and community advisory
   process.
2. Adopt the entity and claim schemas in `DATA_MODEL.md`.
3. Adopt the verification levels and review workflow in
   `VERIFICATION_POLICY.md`.
4. Select a DRC administrative boundary source only after verifying its
   version, licence, administrative level, and geometry quality.
5. Define accessibility, privacy, citation, and takedown policies.
6. Add schema validation and link checking to continuous integration.

**Exit criterion:** schemas validate, governance rules are public, and no
unverified record can enter the published build.

### Phase 1 — Verified metadata seed

1. Import the 47 CongoLangBench tracks as language and resource metadata.
2. Import regional assignments as claims, retaining source and confidence.
3. Exclude all sentence text and restricted source content.
4. Create profiles for the four national-language tracks and at least one
   representative language from each existing benchmark region.
5. Attach licences, access types, dates, and citations to every imported
   resource.
6. Record known benchmark limitations, including cross-border data and
   variety ambiguity.

**Exit criterion:** every seed record passes automated validation and manual
source review; imported counts reconcile with the source registry snapshot.

### Phase 2 — Minimum viable interactive atlas

1. Build the DRC map with province and territory selection. **Implemented for
   the static research preview; administrative-currency review remains.**
2. Add language search, filters, profile pages, and resource cards.
   **Implemented with reviewed resources and separately labelled source
   candidates.**
3. Add evidence and uncertainty labels directly to the interface.
   **Implemented for resource and representative-point candidate states.**
4. Implement stable, shareable URLs and metadata exports.
5. Publish source citations and a visible last-reviewed date.
6. Test on mobile devices and low-bandwidth connections.

**Exit criterion:** users can move from a place to a language to a verified
resource without losing source or licence context.

### Phase 3 — National catalogue expansion

1. Build a fuller DRC language inventory from authoritative catalogues and
   territory-level evidence.
2. Add grammars, dictionaries, orthographies, publications, speech datasets,
   and community resources.
3. Add records for languages with no available dataset so absence is visible.
4. Establish expert and community review rounds by region.
5. Track rejected, superseded, and disputed claims instead of deleting their
   history.

**Exit criterion:** national coverage is measurable, gaps are explicitly
reported, and each published geographic claim has evidence.

### Phase 4 — NLP and benchmark integration

1. Import text-free aggregate results from CongoLangBench releases.
2. Add comparable model, task, prompt, metric, and dataset-version metadata.
3. Visualize model coverage without ranking languages by intrinsic worth.
4. Link benchmarks to the exact language variety and resource version.
5. Add reproducible result exports and methodology pages.

**Exit criterion:** every displayed score is traceable to a frozen dataset,
model revision, evaluation protocol, and public methodology.

### Phase 5 — Community platform and sustainability

1. Add moderated submissions and reviewer roles if GitHub-based editing no
   longer scales.
2. Add multilingual interface translations.
3. Publish versioned catalogue releases with DOIs when appropriate.
4. Establish backups, archival exports, contributor recognition, and an annual
   review cycle.
5. Measure usefulness through research referrals, corrections, downloads, and
   documented collaborations rather than page views alone.

## 6. Recommended technical architecture

### First public release

```text
Versioned CSV/YAML records
          |
          v
JSON Schema validation + build scripts
          |
          +--> normalized JSON catalogue
          +--> GeoJSON/PMTiles map layers
          +--> generated data-quality report
                         |
                         v
              Next.js + MapLibre site
                         |
                         v
               static CDN deployment
```

This architecture keeps editorial data reviewable in Git and avoids a paid
database during the initial release. Move to PostgreSQL/PostGIS only when
authenticated editing, spatial queries, or catalogue size justify it.

## 7. Workstreams

### Data and evidence

- language identity and variety resolution;
- administrative geography and location evidence;
- resource discovery and licence review;
- source citation and archival metadata;
- import, normalization, deduplication, and quality reports.

### Product and design

- information architecture and user journeys;
- map behavior and uncertainty visualization;
- language and resource profiles;
- accessibility, responsive design, and low-bandwidth behavior;
- contribution and correction experience.

### Engineering

- schemas and validators;
- static catalogue build;
- map and search implementation;
- tests, performance budgets, deployment, and monitoring;
- versioned exports and release automation.

### Governance and community

- reviewer roles and conflict handling;
- preferred names and community corrections;
- privacy, sensitive location, and takedown rules;
- attribution and contributor consent;
- release and maintenance policy.

## 8. Initial backlog

1. Choose and verify an administrative boundary dataset.
2. Create JSON Schemas for all entities.
3. Write a deterministic CongoLangBench metadata exporter.
4. Produce the first 47-language seed catalogue and reconciliation report.
5. Design low-fidelity map, profile, and resource-explorer wireframes.
6. Build a map prototype with five representative language profiles.
7. Conduct researcher and community usability reviews.
8. Expand to speech and linguistic-publication sources.
9. Publish the first versioned metadata release.

## 9. Definition of done for a public record

A language, location claim, resource, publication, or result is publishable
only when it has:

- a stable internal identifier;
- a source citation and working source or archive URL;
- publisher/author, version or publication date, and retrieval date;
- a verification status and named review event;
- precise language identity or an explicit ambiguity note;
- DRC geographic relevance and stated precision;
- licence and access status where applicable;
- no private text, personal information, or prohibited content;
- automated schema validation; and
- a visible last-reviewed date.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| A beautiful map implies false linguistic borders | Use evidence points, territory associations, confidence, dates, and explanatory legends |
| Related varieties are merged | Keep identifiers and variety records separate; require evidence for relationships |
| A visible resource is assumed reusable | Display access and redistribution rights as separate fields |
| Old speaker figures look current | Store estimate year, method, geography, and source; show ranges or uncertainty |
| Restricted benchmark data leaks | Import metadata and aggregate statistics only; test exports for forbidden fields |
| Community knowledge is extracted without credit | Use consent-aware attribution and a correction/review process |
| The catalogue becomes stale | Show review dates, automate link checks, and publish scheduled releases |
| Map performance fails on mobile | Simplify geometry, use PMTiles, lazy-load panels, and enforce performance budgets |

## 11. Success measures

- percentage of public claims with complete citations;
- percentage of resources with resolved licence and access status;
- languages covered, including languages with explicitly documented gaps;
- provinces and territories with reviewed evidence;
- community or expert corrections resolved;
- successful referrals to original resources;
- catalogue exports and citations in research;
- accessibility and low-bandwidth performance targets met.
