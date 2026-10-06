# Language-presence review

This directory stores pinned source manifests and named-human review decisions
for geographic language evidence. Generated candidates and cached source files
remain under `data/generated/presence/` and are excluded from Git.

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
Candidates remain unapproved until a decision file under `reviews/` names a
reviewer and approves language identity, representative location,
administrative containment, and temporal relevance.
