# Language-presence review

This directory stores pinned source manifests, curated source-linked presence
candidates, and named-human review decisions for geographic language evidence.
Generated candidates and cached source files remain under
`data/generated/presence/` and are excluded from Git.

Glottolog coordinates are representative catalogue points. They are useful for
finding relevant administrative context, but they do not describe a language's
full distribution, number of speakers, exclusive territory, or present-day
community boundaries.

Run:

```bash
make presence-candidates
```

Each generated candidate records the exact Glottolog row, coordinates, ISO and
Glottocode match, containing province and second-level area, and limitations.
The version-controlled `curated-presence.json` adds evidence that cannot be
represented by a single catalogue point. It currently records broad regions
for the four national languages and territory evidence for Kinyarwanda in
North Kivu. Historical-province crosswalks, speaker percentages, variety
notes, source locators, and limitations remain explicit fields.

The same build also inventories every ISO-coded Glottolog 5.3 row whose country
list contains `CD`. Existing benchmark identities remain stable; previously
missing rows become supplemental draft profiles. A country association or
representative coordinate is only a review lead, not proof of a language
boundary, current community size, or exclusive local presence.

Candidates remain unapproved until a decision file under `reviews/` names a
reviewer and approves language identity, representative location,
administrative containment, and temporal relevance.
