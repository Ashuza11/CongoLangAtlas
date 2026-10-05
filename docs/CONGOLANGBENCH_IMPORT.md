# CongoLangBench metadata import plan

## Purpose

CongoLangBench is the first structured source for CongoLangAtlas, but the two
projects have different responsibilities:

- CongoLangBench curates bilingual text and evaluates models.
- CongoLangAtlas catalogues languages, places, resources, research, access,
  evidence, and gaps.

The atlas imports facts and metadata, not private evaluation content.

## Seed snapshot

At the time this plan was written, CongoLangBench reports:

- 47 structurally ready language tracks;
- 2,233,244 validated processed bitext pairs across source collections;
- 24 restricted-local tracks;
- 70,500 records in the 47-language evaluation freeze;
- national, regional, and Kivu-expansion groupings;
- per-track ISO codes, reference languages, source notes, publication
  handling, and checksums.

These totals must be regenerated and reconciled during import rather than
copied permanently into application code.

## Source files

| CongoLangBench source | Atlas use |
|---|---|
| `registry/languages.csv` | Language identity, track, region group, and curation status |
| `registry/curation_readiness.csv` | Aggregate pair counts, reference language, handling, checksum, and audit status |
| `registry/benchmark_freeze.csv` | Benchmark metadata and aggregate evaluation coverage only |
| `registry/regional_candidates.csv` | Candidate, selected, deferred, and gap claims |
| `registry/*_top5.md` | Human-readable selection rationale and limitations |
| `language_resources/*/README.md` | Resource descriptions, provenance, and caveats |
| `language_resources/*/metadata/*` | Source and licence evidence after field-level review |
| `docs/results/*` | Text-free aggregate model results and methodology links |

## Fields that may be imported

- language and variety names;
- ISO codes and explicit relationships;
- region groups as broad project categories;
- source title, URL, publisher, version, retrieval date, and licence metadata;
- access and publication handling;
- aggregate pair counts and reference languages;
- scripts and public metadata links;
- checksums of frozen benchmark manifests;
- aggregate scores with model and protocol metadata;
- limitations, gaps, and backlog status.

## Fields and artifacts that must not be imported publicly

- source or target sentence text;
- restricted raw, processed, or benchmark files;
- model prompts or outputs containing restricted source text;
- local file paths presented as public URLs;
- access credentials, private correspondence, or personal contact details;
- a geographic statement inferred only from the benchmark's regional
  organizational label.

## Import procedure

1. Pin a CongoLangBench commit and registry version.
2. Export only allow-listed metadata fields.
3. Convert each track into language, resource, source, and benchmark records.
4. Convert regional entries into evidence claims, not definitive polygons.
5. Normalize access and redistribution status separately.
6. Attach source IDs and review status to every imported field.
7. Validate schemas and scan for forbidden text fields.
8. Reconcile language count, resource count, aggregate pair totals, and
   restricted-track totals against the source snapshot.
9. Manually review cross-border resources and ambiguous varieties.
10. Publish an import report with source commit, warnings, and rejected rows.

## Known issues to preserve

- Generic Kikongo and Kikongo ya Leta are distinct tracks.
- Luba-Katanga/Kiluba and Luba-Kasai/Ciluba are distinct tracks.
- Congo Swahili must not be silently represented as generic Standard Swahili.
- Lega-Mwenga and Lega-Shabunda remain separate.
- Some Bemba, Aushi, Lunda, Zande, Alur, and other sources are cross-border;
  dataset availability does not prove DRC-specific linguistic coverage.
- A resource being authentic or useful for private evaluation does not imply
  permission to redistribute it.
