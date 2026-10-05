# Verification and evidence policy

## Objective

Users must be able to distinguish a verified fact, a source-reported claim, an
editorial inference, an unresolved disagreement, and a missing fact. “Verified”
means the published record faithfully represents checked evidence; it does not
mean every source is complete, current, or free from error.

## Verification levels

| Level | Label | Minimum requirement |
|---|---|---|
| V0 | Draft | Submitted but not public |
| V1 | Source checked | Source opened; identity, locator, and stated claim checked |
| V2 | Corroborated | Supported by a second independent source or authoritative catalogue |
| V3 | Expert reviewed | Reviewed by a qualified linguist, archivist, dataset maintainer, or domain expert |
| V4 | Community reviewed | Reviewed by speakers or a relevant community representative with consent |
| D | Disputed | Conflicting evidence remains visible and explained |

V3 and V4 complement rather than replace one another. Not every record needs
the highest level, but the interface must show the level it has reached.

## Source hierarchy

Prefer evidence in this order while retaining relevant disagreement:

1. the primary dataset, publication, official catalogue, or community source;
2. maintained authoritative registries and institutional repositories;
3. peer-reviewed research and documented fieldwork;
4. reputable secondary catalogues with traceable references;
5. discovery-only sources that point to stronger evidence.

Search snippets, unsourced lists, model-generated text, and copied aggregator
pages are not publishable evidence.

## Claim review checklist

- Does the source actually support the displayed claim?
- Is the language or variety identity explicit?
- Does the evidence refer to the DRC, a neighbouring country, or a broad
  cross-border population?
- Is the geographic precision no stronger than the evidence?
- Are date, edition, sample, and methodology recorded?
- Are speaker estimates labelled by year, geography, and proficiency/L1/L2
  definition?
- Is uncertainty or disagreement preserved?
- Are citation and archive links complete?
- Has licence/access information been checked separately?
- Is the review date visible?

## Dataset and resource review

For each resource, verify directly from its card, repository, paper, files, or
maintainer documentation:

- exact language name, identifier, and variety;
- DRC-specific versus cross-border provenance;
- modality, format, domain, and measured size;
- whether text/audio is human-created, mined, translated, synthetic, or mixed;
- licence, terms URL, access requirements, and redistribution rights;
- current version and retrieval date;
- known quality limitations and whether claims are author- or atlas-reported.

The atlas may list a restricted resource because discoverability is valuable,
but it must not host or reproduce restricted content.

## Corrections and disputes

1. Open a correction linked to the affected record and field.
2. Preserve the existing value and its source during review.
3. Add the new evidence and reviewer notes.
4. Resolve, mark disputed, or reject with a public reason.
5. Record the decision as a review event.
6. Include the change in the next release notes.

Do not resolve identity or naming disagreements by majority vote alone.

## Release gate

A build fails if a public claim lacks a source, a resource lacks access and
licence states, an external URL is malformed, an identifier relationship is
invalid, restricted content enters an export, or required review metadata is
missing.

## Review cadence

- Automated links and schema checks: every change
- High-use dataset/access records: every six months
- General catalogue records: annually
- Speaker estimates and administrative geography: when new authoritative
  releases appear
- Corrections involving harmful or sensitive information: immediately
