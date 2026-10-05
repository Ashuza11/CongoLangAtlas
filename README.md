# CongoLangAtlas

**An interactive, evidence-backed atlas of languages used in the Democratic
Republic of Congo.**

CongoLangAtlas connects language identities, geographic evidence, linguistic
resources, and NLP metadata in one explorable catalogue. It is designed for
researchers, students, language communities, technologists, and funders who
need a trustworthy starting point for work on Congolese languages.

> **Project status:** Phase 0 — data foundations and governance. The schemas,
> validation tooling, safety checks, geographic-source manifest, tests, and
> continuous integration are in place. Prototype province and territory/city
> sources are pinned; geometry review and the first metadata import come next.

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
- draft fixtures that demonstrate the catalogue format;
- unit tests and GitHub Actions validation.

Draft records are development fixtures, not verified public evidence.

## Quick start

### Requirements

- Python 3.10 or newer
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
python3 -m unittest discover -v
```

## Repository structure

```text
CongoLangAtlas/
├── data/
│   ├── catalog/        # Version-controlled metadata records
│   └── schema/         # JSON Schemas and controlled vocabularies
├── docs/               # Product, evidence, and import policies
├── public/geodata/     # Future reviewed map artifacts
├── scripts/            # Validation and safety tooling
├── src/                # Future web application
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
[verification policy](docs/VERIFICATION_POLICY.md) for the complete rules.

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
| 0 | Schemas, governance, validation, geographic-source review | In progress — source selected, geometry review pending |
| 1 | Verified CongoLangBench metadata seed | Planned |
| 2 | Interactive map, search, profiles, filters, and exports | Planned |
| 3 | Expanded national language and resource catalogue | Planned |
| 4 | Reproducible NLP benchmark and model-result integration | Planned |
| 5 | Moderated community platform and sustainable releases | Planned |

The detailed milestones and exit criteria are in the
[project plan](docs/PROJECT_PLAN.md).

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

The planned interface uses Next.js, TypeScript, and MapLibre GL JS. A
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
- [Catalogue guide](data/catalog/README.md)
- [Schema guide](data/schema/README.md)
