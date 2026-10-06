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
country, 26 provinces, and 240 second-level areas. Glottolog 5.3 provides
ISO-linked representative coordinates for 46 of the 47 language tracks. Of
those, 41 points fall inside the prototype DRC layers and become geographic
review candidates. Five cross-border representative points fall outside the
DRC, and generic Kikongo has no one-to-one Glottolog language coordinate.
These are catalogue points—not distribution polygons or speaker locations—and
zero candidates currently have named-human approval.

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
