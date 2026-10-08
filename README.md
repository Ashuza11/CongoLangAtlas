# CongoLangAtlas

**An interactive, evidence-backed atlas of languages used in the Democratic
Republic of Congo.**

CongoLangAtlas connects language identities, geographic evidence, linguistic
resources, and NLP metadata in one explorable catalogue. It is designed for
researchers, students, language communities, technologists, and funders who
need a trustworthy starting point for work on Congolese languages.

CongoLangAtlas is a project by [KivuLingua AI](https://kivulinguaai.org/), a
community-led African language technology initiative.

> **Project status:** Phase 2 research preview. The complete 47-track resource
> audit and a 236-language Glottolog-backed DRC inventory now feed a static
> Next.js and MapLibre interface with catalogue search,
> evidence filters, clickable province and territory context, and resource
> profiles. The map can filter 188 representative-point candidates while
> distinguishing them from the current zero human-approved place claims. All
> records remain visibly marked as drafts: none can be promoted without named
> human approval and all unresolved licence, access, variety, and geographic
> questions being closed.

## What the atlas will provide

| Explore | Evaluate | Contribute |
|---|---|---|
| Browse languages by province, territory, locality, or region | Check evidence quality, geographic precision, access, and licence terms | Submit a resource, correction, preferred name, or community review |
| Search names, aliases, ISO codes, and Glottocodes | Compare text, speech, dictionary, grammar, model, and benchmark coverage | Preserve attribution, uncertainty, and review history |
| Open language profiles and resource records | Identify documentation and NLP-resource gaps | Help resolve disputed or outdated claims |

The atlas is a research guide, not a claim that languages occupy hard borders.
Language use is multilingual, mobile, and often crosses provincial and
national boundaries. Maps therefore use the least precise geography supported
by the available evidence.

## Why this project exists

Information about Congolese languages is scattered across catalogues, papers,
archives, community knowledge, datasets, and NLP repositories. Even when a
resource can be found, it may be unclear whether it:

- represents the DRC or a cross-border population;
- refers to the intended language variety;
- can be downloaded, reused, or redistributed;
- has a current and verifiable source; or
- contains limitations that affect research use.

CongoLangAtlas makes those distinctions explicit and keeps citations and
verification history attached to every public claim.

## Current foundation

The repository currently provides:

- JSON Schema 2020-12 definitions for languages, places, presence claims,
  resources, publications, NLP results, sources, and review events;
- controlled vocabularies for verification, access, redistribution, language
  roles, and geographic precision;
- cross-record identifier and reference validation;
- publication-safety checks that reject restricted content, credentials, and
  local filesystem paths;
- a checksum-pinned manifest for prototype ADM1 and ADM2 geographic sources,
  with licence, provenance, intended use, and review limitations;
- deterministic downloading, geometry validation, parent assignment,
  topology-preserving simplification, and quality reporting;
- a generated catalogue of one country, 26 provinces, and 240 second-level
  administrative places linked to their source geometry;
- an allow-listed, commit-pinned CongoLangBench metadata exporter that excludes
  sentence text and reconciles source totals before producing draft records;
- a deterministic public-safe web bundle containing metadata only;
- a responsive static atlas with language search, access and project-grouping
  filters, province-to-territory drill-down, place-level coverage summaries,
  synchronized map selection, evidence-aware profiles, keyboard-visible
  controls, and compact mobile map navigation;
- resource-coverage and geographic-evidence filters plus public-safe JSON and
  CSV exports that preserve the currently selected place and visible results;
- confidence and human-review filters, visible evidence-status badges, Escape
  handling for language profiles, and a keyboard-accessible administrative
  place picker that provides an alternative to direct map interaction;
- profile coverage summaries for speaker evidence, digital sources, datasets,
  models, and linguistic research, with missing evidence shown explicitly;
- a cached, reproducible candidate-source census across OLAC, Hugging Face,
  GitHub, and OpenAlex, with ambiguous-name filtering and review labels;
- a checksum-pinned Glottolog 5.3 inventory workflow that exposes 235
  ISO-coded DRC-associated rows and maps 188 representative-point candidates
  into administrative context without presenting them as language boundaries;
- 551 source-linked documented-presence candidates: 99 individually curated
  records plus 452 non-duplicative territory records generated from CLEAR
  Global's checksum-pinned 2016 CAID dataset;
- 236 language profiles: the original 47 benchmark tracks plus 189 provisional
  DRC inventory profiles whose identities and geographic evidence remain
  visibly reviewable;
- a reproducible province coverage audit that flags empty, thin, national-only,
  territory-missing, and unapproved coverage without inventing data;
- draft fixtures that demonstrate the catalogue format;
- unit tests and GitHub Actions validation.

Draft records are development fixtures, not verified public evidence.

## Quick start

### Requirements

- Python 3.10 or newer
- Node.js 20.9 or newer and `npm`
- `pip`
- `make` (optional)

Create an isolated environment and run all checks:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
make check
```

Without `make`:

```bash
python3 -m scripts.validate_catalog
python3 -m scripts.validate_geodata
python3 -m scripts.validate_reviews
python3 -m unittest discover -v
```

Build the generated map layers from their pinned sources:

```bash
make geodata
make places
```

This command requires network access the first time. Verified downloads are
cached under `data/generated/`; generated sources, web layers, and quality
reports are excluded from Git and remain reproducible from the manifest.
The place build emits 267 schema-valid catalogue records derived from those
layers, including the country and complete parent hierarchy.

Import the pinned CongoLangBench registry metadata from a sibling checkout:

```bash
make import-congolangbench
```

Override `CONGOLANGBENCH=/path/to/CongoLangBench` when the checkout is located
elsewhere. The generated draft catalogue and reconciliation report are written
under `data/generated/` and excluded from Git.

Create the manual-review queue:

```bash
make review-congolangbench
```

The queue detects existing atlas identities and prioritizes restricted,
cross-border, and variety-ambiguous tracks. Structural validation alone never
promotes a draft record into the public catalogue.

Current review status: all 47 tracks have automated source audits. Thirty-six
tracks pass all six technical checks but still require a named human reviewer.
Aushi, Alur, Bemba, Fuliiru, Lunda, and Nande retain geographic questions;
Holoholo and Lingala retain variety/geography questions; Ciluba and generic
Kikongo remain blocked by gated access, licence “other,” and unresolved
provenance; and Nyanga retains a conflict between package public-domain
metadata and the absence of matching publisher terms. Every copyrighted track
also remains restricted regardless of later identity approval.

The web bundle prefers the external dataset or repository for each language
and omits the internal frozen-evaluation metadata card when that external
record exists. This keeps the interface focused on sources users can actually
investigate while retaining the complete audit trail in generated research
records.

The original 47-track discovery pass identifies 453 candidate links. The
expanded cached census now contains 1,149 candidates across all 236 profiles:
217 Hugging Face datasets or models, 40 GitHub repositories, 656 OpenAlex
research records, and 236 OLAC catalogue pages. Each of the 189 supplemental
profiles also links back to its pinned Glottolog catalogue source, bringing the
public bundle to 1,338 source leads. The 189 uncached GitHub searches and 92
OpenAlex searches blocked by the current provider quota remain explicit
provider errors. All links are displayed as candidates—not verified
records—and
must pass language, variety, geographic, licence, and access review before
promotion.

Reviewed source metadata is applied as a separate overlay, leaving the pinned
CongoLangBench registries unchanged. The generated records now link directly
to CLEAR Global, Google SMOL, `multi-open`, MT560 wrappers, AfriSpeech Africa
Corpus, eBible.org, or Bible in Every Language and preserve their actual
access, licence, redistribution, and geographic-scope states.

Build the metadata-only bundle used by the interface, install frontend
dependencies, and start the research preview:

```bash
make presence-candidates
make discover-sources
make web-data
make coverage-report
npm install
npm run dev
```

Open `http://localhost:3000`. The importer and review queue must already have
been generated as described above. The map also expects the reproducible ADM1
and ADM2 layers created by `make geodata`. Administrative polygons provide
navigation context only and are never presented as language boundaries.
Selecting a province or territory updates the catalogue context immediately.
The map guidance appears briefly when the atlas loads, dismisses automatically,
and remains available through the **Map guide** control.
Province selections expose their complete territory list, ordered by current
language-evidence coverage, so users can move from a province to a territory
without searching the map. The place panel summarizes speaker evidence,
digital sources, datasets, models, and research linked to the visible language
leads; each language row exposes the same categories before its full profile is
opened. These are evidence counts, not demographic totals or completeness
claims. Qualitative CAID notes are preserved even when a territory has no
statistical percentages. For example, Kabare exposes the source's Swahili,
Mashi, and Tembo presence statements while clearly showing that no speaker
estimate was reported.
The map combines labelled Glottolog representative-point candidates with a
separate documented-presence layer. A national-language switcher highlights
the broad sourced regions for Kikongo ya Leta, Lingala, Congo Swahili, and
Ciluba, reports the number of provinces currently linked to each language, and
zooms to the selected evidence context. A persistent legend separates a
selected administrative place from language evidence and territory navigation;
hover labels identify the province or territory before selection. Lualaba now
resolves to both a Congo Swahili regional candidate through
an explicit former-Katanga-to-current-province crosswalk and a separately
sourced Lunda presence candidate. At territory level,
the CLEAR Global North Kivu source adds Kinyarwanda in Masisi and Nyiragongo,
and preserves the source's Kinyabwisha note for Rutshuru. These highlights are
not language borders or complete distributions. CLEAR Global maps now also
add source-linked, CAID-derived language-use estimates for seven Équateur
territories, five Ituri territories, and seven Tanganyika territories, plus
Nande and Swahili evidence for Beni Territory. The interface preserves each
map's warning that these percentages do not measure proficiency or exclusive
language identity. Broad labels such as Luba and Hemba remain explicit review
candidates rather than silently resolved varieties. A separate 2026 Ngaliema
school study adds explicit Kinshasa candidates for Lingala, Kikongo,
Kiswahili, and Tshiluba; its percentages are labelled as shares of 500
surveyed students rather than citywide speaker estimates. Together with 188
catalogue points, the public bundle contains 739 geographic leads. The pinned
CLEAR Global/CAID import contributes low-confidence quantitative or qualitative
evidence across 165 territories, 25 provinces, and 71 ISO-matched language identities. With
the separate Kinshasa evidence, every province now has locally grounded
documentary evidence and at least one territory-level record. This is coverage
of evidence availability, not proof that every language or territory has been
fully documented. Forty-seven cross-border catalogue points fall outside the
DRC layers, generic Kikongo has
no one-to-one Glottolog coordinate, and no place claim has named-human approval
yet.
Online discovery requires network access; cached results can be rebuilt with
`python3 -m scripts.discover_sources --offline`. See the
[source-discovery guide](docs/SOURCE_DISCOVERY.md) for providers, relevance
controls, rate limits, and the promotion checklist.

Verify a production-ready static export:

```bash
npm run lint
npm run typecheck
npm run build
```

The export is written to `out/`. Browser-ready catalogue and map snapshots
under `public/generated/` are versioned so deployment builds reproduce the
reviewed public state. Internal caches, source downloads, review reports, and
build artifacts under `data/generated/`, `.next/`, and `out/` remain excluded.

## Continuous integration and deployment

GitHub Actions provides continuous integration. The workflow at
`.github/workflows/validate.yml` runs catalogue validation, all Python tests,
ESLint, TypeScript checks, and a production Next.js build for every pull
request and every push to `main`.

Vercel provides continuous deployment through its Git integration:

- `main` is the production environment;
- every pull request and non-production branch receives an isolated preview
  deployment; and
- a commit is promoted only after Vercel completes its production build.

For the one-time setup, import `Ashuza11/CongoLangAtlas` from the Vercel New
Project screen, keep the detected **Next.js** framework preset and default
`npm run build` command, and deploy. The current static export needs no runtime
environment variables or deployment secrets. Vercel assigns the initial
production domain; a custom domain can be added later from the project
settings without changing application code.

Before committing a data update, regenerate `public/generated/atlas/catalog.json`
and the two public GeoJSON layers. Keeping these three deployment snapshots in
the same commit as their source and code changes ensures the live site always
matches the reviewed repository state.

## Repository structure

```text
CongoLangAtlas/
├── data/
│   ├── catalog/        # Version-controlled metadata records
│   ├── presence/       # Geographic source pins and human review decisions
│   └── schema/         # JSON Schemas and controlled vocabularies
├── docs/               # Product, evidence, and import policies
├── public/geodata/     # Geographic source manifest and guidance
├── scripts/            # Validation and safety tooling
├── src/                # Next.js atlas interface
└── tests/              # Automated validation tests
```

## Data principles

1. **Evidence before appearance.** Every public claim must have a traceable
   source.
2. **Claims remain separate from entities.** Conflicting or historical claims
   are preserved instead of silently overwritten.
3. **Language varieties stay explicit.** Similar names are never treated as
   proof that two varieties are identical.
4. **Uncertainty remains visible.** Approximate locations, old estimates, and
   unresolved classifications are labelled.
5. **Metadata is not permission.** Licence, access, and redistribution are
   recorded separately.
6. **Communities are collaborators.** Preferred names, corrections, consent,
   and attribution are part of the review process.
7. **Restricted content stays private.** The public repository contains
   metadata and permitted aggregates—not protected corpus text or audio.

See the [data model](docs/DATA_MODEL.md) and
[verification policy](docs/VERIFICATION_POLICY.md) for the complete rules. The
[data-readiness report](docs/DATA_READINESS.md) summarizes the current handoff
state and the external approvals that automation cannot replace.

## Initial metadata seed

The first planned import is metadata from CongoLangBench. Its current project
snapshot describes 47 DRC language tracks, 2,233,244 structurally validated
bitext pairs, and a 70,500-pair evaluation freeze. These figures will be
regenerated and reconciled during import rather than embedded in application
code.

Only allow-listed metadata and legally publishable aggregates will be
imported. Sentence-level text, restricted audio, credentials, private
correspondence, and copyrighted content remain outside this repository. See
the [CongoLangBench import plan](docs/CONGOLANGBENCH_IMPORT.md).

## Roadmap

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Schemas, governance, validation, geographic-source review | Automated gate complete — administrative review pending |
| 1 | Verified CongoLangBench metadata seed | Automated audit complete — named human review pending |
| 2 | Interactive map, search, profiles, filters, and exports | Deployed research preview complete — field testing and iterative polish ongoing |
| 3 | Expanded national language and resource catalogue | Draft nationwide inventory complete — human review and gap resolution ongoing |
| 4 | Reproducible NLP benchmark and model-result integration | Planned |
| 5 | Moderated community platform and sustainable releases | Planned |

The detailed milestones and exit criteria are in the
[project plan](docs/PROJECT_PLAN.md).

The next implementation priorities are stable shareable catalogue URLs,
field testing on low-bandwidth mobile devices, and citation-ready release
snapshots. Research work remains for named-human verification, ambiguous CAID
labels, provider searches blocked by quotas, and community-reviewed names and
locations. NLP result integration and moderated contributions remain later
phases rather than blockers for the deployed research preview.

## Planned architecture

```text
Version-controlled CSV/YAML records
                 │
                 ▼
      Schema and safety validation
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      JSON    GeoJSON   Quality report
        └────────┼────────┘
                 ▼
       Next.js + MapLibre application
                 ▼
          Static CDN deployment
```

The interface uses Next.js, TypeScript, and MapLibre GL JS. A
static-first build keeps early releases affordable, reproducible, and easy to
audit. PostgreSQL/PostGIS will be introduced only if authenticated editing or
spatial query requirements justify it.

## Contributing

Contributions may add resources, correct claims, improve validation, review a
language profile, or help build the application. Data contributions must
include a source, geographic scope, licence and access information, relevant
dates, and known uncertainty.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change. Never
submit restricted corpus content, credentials, personal information, private
correspondence, or sensitive community locations.

## Documentation

- [Project plan](docs/PROJECT_PLAN.md)
- [Data model](docs/DATA_MODEL.md)
- [Verification and evidence policy](docs/VERIFICATION_POLICY.md)
- [CongoLangBench import plan](docs/CONGOLANGBENCH_IMPORT.md)
- [Geographic data source decision](docs/GEOGRAPHIC_DATA_SOURCE.md)
- [Online source discovery](docs/SOURCE_DISCOVERY.md)
- [Catalogue guide](data/catalog/README.md)
- [Schema guide](data/schema/README.md)
