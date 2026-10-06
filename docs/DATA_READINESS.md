# Data readiness

This document records the handoff state between the evidence/data phase and
the visual application phase. It distinguishes work completed by the
repository from approvals that must come from named people or external source
owners.

## Current snapshot

The pinned CongoLangBench import at commit
`43c9a763459021d6feb7fc90c37ef13dbe4824d1` reconciles and validates:

| Record type | Count |
|---|---:|
| Languages | 47 |
| Resources | 94 |
| Sources | 26 |
| Total | 167 |

All 47 tracks have evidence-linked automated source-audit decisions. Thirty-six
pass all six technical checks. Eleven honestly retain at least one unresolved
or rejected check because the available evidence does not support a stronger
claim.

## Access and rights

| State | Tracks |
|---|---:|
| Open download | 21 |
| Gated | 2 |
| Unavailable for corpus reuse | 24 |
| Redistribution allowed | 21 |
| Redistribution restricted | 24 |
| Redistribution unknown | 2 |

Restricted source text is not imported. The public repository stores only
metadata, permitted aggregates, source links, and review decisions.

## Geographic scope

| Scope | Tracks |
|---|---:|
| DRC-labelled | 26 |
| Cross-border | 14 |
| Uncertain | 7 |

Cross-border availability is never treated as proof of a DRC-specific variety.
Uncertain scope remains visible in the generated review queue and future user
interface.

## Remaining review boundaries

Every track is deferred pending a named human reviewer. Additional blockers
are preserved for:

- 24 restricted-content tracks;
- 10 tracks needing geographic review;
- 3 tracks needing variety review;
- 3 tracks needing licence review; and
- 2 gated tracks needing access review.

Nyanga (`nyj`) has a specific evidence conflict: package metadata reports
public-domain status, while the official publisher page supplies no matching
open redistribution terms. The atlas therefore treats the text as restricted
until written permission or matching licence evidence is available.

## Administrative geography

The reproducible geodata build passes its geometry quality gate with 26 ADM1
features and 240 ADM2 features. All ADM2 parents resolve, and no invalid
geometry or within-level overlap is reported. These 2017 OCHA/RGC layers are
suitable for a clearly labelled prototype navigation map, not a claim of
current legal administrative boundaries.

The derived place-catalogue build produces 267 schema-valid records: one
country, 26 provinces, and 240 second-level areas. The pinned Glottolog 5.3
table contains 235 ISO-coded rows associated with country code `CD`. Combined
with generic Kikongo from the benchmark, this produces 236 provisional language
profiles. Of their representative points, 188 fall inside the prototype DRC
layers, 47 fall outside, and generic Kikongo has no one-to-one coordinate.
These are catalogue points—not distribution polygons or speaker locations—and
zero candidates currently have named-human approval.

A separate curated-presence bundle contributes 37 source-linked candidates.
It localizes the four national languages as broad, non-exclusive regional
contexts and adds CLEAR Global's territory-level Kinyarwanda evidence for
Masisi (15%), Nyiragongo (60%), and Rutshuru (70% Kinyabwisha, retained as a
related-variety note). The Lualaba Congo Swahili match is an explicit
administrative crosswalk from the source's former Katanga region, not a new
speaker survey; an independent secondary source also lists Lunda among the
province's principal spoken languages.
The official Kasaï-Oriental 2023–2027 development plan additionally documents
Tshiluba as the province's common language, Lingala at 10%, and Swahili at 20%,
while leaving the relevant territories and survey method unspecified. Together
with the Glottolog candidates, the public bundle now contains 225 geographic
leads across 236 language profiles. All curated records remain candidates
pending named-human review.

`make coverage-report` audits all 26 provinces against the generated bundle.
After this pass no province is empty; Kinshasa remains the only province with
fewer than three language leads, and Kasaï-Oriental remains the only province
without territory-level evidence. The report flags these gaps rather than
filling them through inference.

Source discovery now covers the same 236-profile inventory. Cached Hugging
Face, GitHub, and OpenAlex results remain available for the original reviewed
tracks; every supplemental profile receives deterministic OLAC and Glottolog
catalogue links. The public bundle contains 831 source leads in total. Offline
cache misses are recorded as provider errors and are not treated as evidence
that no resource exists.

The UN SALB catalogue identifies a validated DRC dataset from the Institut
Géographique du Congo with temporal validity beginning 2018-05-30 and a listed
update of 2024-06-13. Its downloadable artifacts and terms still require direct
inspection before the prototype boundary layer can be promoted for public
release.

## Visualization handoff rule

Frontend work may consume only generated metadata and map artifacts while
showing their draft, uncertainty, access, licence, and review states. It must
not describe any imported record as publicly verified until the named-human
review requirement is satisfied.
