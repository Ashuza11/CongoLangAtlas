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

## Implemented draft exporter

The Phase 1 exporter is available as:

```bash
python3 -m scripts.import_congolangbench /path/to/CongoLangBench
```

It accepts only explicitly listed columns from `languages.csv`,
`curation_readiness.csv`, and `benchmark_freeze.csv`. It pins the upstream Git
commit, reconciles all documented totals, emits draft language and resource
records, runs the atlas schema and publication-safety validator, and writes an
import report under `data/generated/`.

Generated records are not public catalogue records. Every licence, geographic
scope, language-variety relationship, and source URL still requires manual
field-level review before promotion into `data/catalog/`.

Generate the deterministic manual-review queue after importing:

```bash
python3 -m scripts.build_import_review_queue
```

The queue detects existing atlas identities by ISO code and prevents imported
IDs from silently replacing stable atlas IDs. Every track remains blocked until
language and variety identity, DRC geographic scope, licence, access, and
source links receive an explicit review decision. Restricted and cross-border
tracks receive higher priority; queue generation never promotes records.

### Initial national-track source audit

The first automated evidence pass covers the four national-language tracks:

| Track | Result | Remaining blocker |
|---|---|---|
| Kikongo ya Leta (`ktu`) | All six source checks pass | Named human approval |
| Congo Swahili (`swc`) | All six source checks pass | Named human approval |
| Lingala (`lin`) | Identity, licence, access, and links pass | DRC-specific variety/geography and human approval |
| Ciluba (`lua`) | Identity, variety, and link checks pass | Gated access, licence “other,” DRC provenance, and human approval |

These are deferred source-audit decisions, not V3 expert or V4 community
reviews. Evidence URLs and notes are stored under
`data/reviews/congolangbench/`.

Reviewed source facts are applied through
`data/import/congolangbench-resource-overrides.json`. This overlay keeps the
pinned upstream registries immutable while ensuring generated resource records
represent the actual primary source. It currently corrects Ciluba to `gated`
access with unknown redistribution and no normalized licence, and records the
CC BY 4.0 open-download sources for Lingala, Kikongo ya Leta, and Congo
Swahili.

### Regional representative source audit

The second evidence pass adds one representative from each non-national region
without treating the benchmark's region label as geographic proof:

| Region | Track | Source result | Remaining blocker |
|---|---|---|---|
| Central DRC | Tetela (`tll`) | MT560 wrapper, CC BY 4.0 | Human approval; mixed OPUS provenance remains documented |
| Ituri | Alur (`alz`) | MT560 wrapper, CC BY 4.0 | Cross-border geographic review and human approval |
| Kivu | Nande (`nnb`) | CLEAR Global Gamayun, CC BY 4.0 | Cross-border geographic review and human approval |
| Maniema | Lega-Mwenga (`lgm`) | Copyrighted Africa Corpus edition | Restricted content and human approval |
| Northern DRC | Zande (`zne`) | Copyrighted, cross-border Africa Corpus edition | Restricted content and human approval |
| Northwestern Congo Basin | Ngombe (`ngc`) | Three public-domain editions | Human approval; retain cross-border and religious-domain labels |
| Southeastern DRC | Luba-Katanga (`lub`) | MT560 wrapper, CC BY 4.0 | Human approval; mixed OPUS provenance remains documented |
| Tshopo | Lengola (`lej`) | Bible in Every Language, CC BY-SA 4.0 | Human approval; attribution and ShareAlike apply |
| Western DRC | Yansi (`yns`) | Public-domain Africa Corpus edition | Human approval; retain edition-level rights evidence |

The resulting draft catalogue contains 47 language records, 94 resource
records, and 9 source records. All 13 reviewed tracks remain deferred: an
automated source audit can reduce blockers, but only a named human decision can
authorize catalogue promotion.

### High-risk open-track audit

A third evidence pass prioritizes records that look publishable in the source
registry but could still mislead users about geography, variety, or reuse:

| Track | Source result | Remaining blocker |
|---|---|---|
| Aushi (`auh`) | Open.Bible, CC BY-SA 4.0, Zambia source | DRC-specific geographic review and human approval |
| Bemba (`bem`) | MT560, CC BY 4.0, Zambia source | DRC-specific geographic review and human approval |
| Kikongo (`kon`) | `multi-open`, gated, licence “other” | Variety, geography, access, licence, and human approval |
| Lunda (`lun`) | MT560, CC BY 4.0, Zambia source | DRC-specific geographic review and human approval |
| Yaka (`yaf`) | Public-domain DRC–Angola edition | Human approval; retain cross-border scope |

After this pass the generated draft contains 47 language records, 94 resource
records, and 12 source records. Eighteen tracks have deferred automated audits;
none is ready for promotion.

### Restricted-source audit batch 1

The first restricted batch verifies five locally usable tracks without
misrepresenting official reading or download access as redistribution rights:

| Track | Source result | Remaining blocker |
|---|---|---|
| Bembe/Kibembe (`bmb`) | Matching official copyrighted EPUBs, DRC-labelled | Restricted content and human approval |
| Budu (`buu`) | Two copyrighted DRC-labelled Africa Corpus editions | Restricted content and human approval |
| Fuliiru (`flr`) | Complete all-rights-reserved eBible edition | Geography, restricted content, and human approval |
| Hunde (`hke`) | Copyrighted YouVersion edition with three available books | Restricted content and human approval |
| Holoholo (`hoo`) | Copyrighted YouVersion edition with 45 available chapters | Variety, geography, restricted content, and human approval |

The generated draft now contains 47 language records, 94 resource records, and
16 source records. Twenty-three tracks have deferred automated audits; no
restricted text, download URL, or reuse permission is emitted for this batch.

### Restricted-source audit batch 2

The second restricted batch resolves five identity and scope checks while
retaining the source's copyright restrictions:

| Track | Source result | Remaining blocker |
|---|---|---|
| Kakwa (`keo`) | Copyrighted DRC–South Sudan–Uganda edition | Restricted content and human approval |
| Kele/Lokele (`khy`) | Copyrighted DRC edition | Restricted content and human approval |
| Komo (`kmw`) | Copyrighted DRC edition | Restricted content and human approval |
| Kanyok (`kny`) | Six official copyrighted JW.org books | Restricted content and human approval |
| Lega-Shabunda (`lea`) | Complete copyrighted DRC edition | Restricted content and human approval; keep separate from Lega-Mwenga |

The generated draft now contains 47 language records, 94 resource records, and
17 source records. Twenty-eight tracks have deferred automated audits; all five
tracks in this batch pass the six technical checks but remain unpublishable at
the content layer.

### Restricted-source audit batch 3

The third restricted batch verifies five further Africa Corpus tracks and
retains their exact country scope:

| Track | Source result | Remaining blocker |
|---|---|---|
| Logo (`log`) | Two copyrighted DRC–South Sudan editions | Restricted content and human approval |
| Mongo (`lol`) | Two copyrighted DRC editions | Restricted content and human approval |
| Lobala (`loq`) | Copyrighted DRC–Republic of the Congo edition | Restricted content and human approval |
| Mayogo (`mdm`) | Copyrighted DRC edition | Restricted content and human approval |
| Ndo (`ndp`) | Copyrighted DRC–Uganda edition | Restricted content and human approval |

The generated draft remains at 158 records because all five tracks reuse the
reviewed Africa Corpus source. Thirty-three tracks now have deferred automated
audits; all five tracks in this batch pass the six technical checks but remain
unpublishable at the content layer.

### Additional open-source audit

This batch verifies five open sources whose pinned acquisitions already have
reproducible checksums and coverage totals:

| Track | Source result | Remaining blocker |
|---|---|---|
| Havu (`hav`) | DRC Havu New Testament, CC BY-SA 4.0 | Human approval; attribution, change notices, and ShareAlike apply |
| Lombo/Turumbu (`loo`) | DRC Mark and Luke documents, CC BY-SA 4.0 | Human approval; attribution and ShareAlike apply |
| Ruund (`rnd`) | DRC-labelled MT560 wrapper, CC BY 4.0 | Human approval; cross-border identity and mixed OPUS provenance remain documented |
| Mashi/Shi (`shr`) | DRC Bible edition, CC BY 4.0 | Human approval; cross-border identity remains documented |
| Songe (`sop`) | DRC-labelled MT560 wrapper, CC BY 4.0 | Human approval; mixed OPUS provenance remains documented |

The generated draft now contains 47 language records, 94 resource records, and
21 source records, for 162 records total. Thirty-eight tracks have deferred
automated audits. All five tracks in this batch pass the six technical checks,
but none can be promoted without a named human decision.

### Final source-audit batch

The final batch closes automated evidence review for every imported track:

| Track | Source result | Remaining blocker |
|---|---|---|
| Ngbaka (`nga`) | Copyrighted DRC–Central African Republic–Republic of the Congo edition | Restricted content and human approval |
| Northern Ngbandi (`ngb`) | Copyrighted DRC–Central African Republic edition | Restricted content and human approval |
| Ngiti (`niy`) | Copyrighted DRC–Uganda edition | Restricted content and human approval |
| Nyanga (`nyj`) | Official DRC four-book edition | Conflicting licence evidence, restricted content, and human approval |
| Amba (`rwm`) | Copyrighted DRC–Uganda edition | Restricted content and human approval |
| Tabwa (`tap`) | DRC edition, CC BY-SA 4.0 | Human approval; attribution, discrepancy disclosure, and ShareAlike apply |
| Tembo (`tbt`) | Copyrighted DRC New Testament | Restricted content and human approval |
| Yombe (`yom`) | DRC New Testament and Psalms, CC BY-SA 4.0 | Human approval; attribution, trademark handling, and ShareAlike apply |
| Zimba (`zmb`) | Official copyrighted DRC edition | Restricted content and human approval |

The complete generated draft contains 47 language records, 94 resource
records, and 26 source records, for 167 records total. All 47 tracks now have
deferred automated audits; 36 pass all six technical checks. No record is
promotion-ready because named human review is deliberately outside the
automated audit role. Nyanga also remains blocked by a licence conflict between
package metadata and the official publisher page.

## Known issues to preserve

- Generic Kikongo and Kikongo ya Leta are distinct tracks.
- Luba-Katanga/Kiluba and Luba-Kasai/Ciluba are distinct tracks.
- Congo Swahili must not be silently represented as generic Standard Swahili.
- Lega-Mwenga and Lega-Shabunda remain separate.
- Some Bemba, Aushi, Lunda, Zande, Alur, and other sources are cross-border;
  dataset availability does not prove DRC-specific linguistic coverage.
- A resource being authentic or useful for private evaluation does not imply
  permission to redistribute it.
