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
represented by a single catalogue point. Its 99 records currently cover broad
regions for the four national languages; territory evidence in Équateur,
Ituri, Nord-Kivu, and Tanganyika; province evidence for Lualaba and
Kasaï-Oriental; and a sample-scoped language-use study from six Ngaliema
schools in Kinshasa.
Historical-province crosswalks, percentage denominators, variety notes, source
locators, and limitations remain explicit fields. A percentage is never shown
without its source-specific basis, such as a territory population or a school
survey sample. CAID-derived map values are retained as source-reported
language-use estimates, never reinterpreted as proficiency, first-language
identity, exclusive language areas, or complete population statistics.

The source manifest also pins CLEAR Global's open 2016 CAID territory CSV by
download URL, version, licence, and SHA-256 checksum. The build reads its HXL
ISO tags and produces 361 additional non-duplicative candidates across 128
second-level areas. Every generated row retains the publisher's low confidence
rating and an exact CSV row, administrative code, column, and raw-value
locator. Unmapped source labels are not guessed; only the documented Nande,
Tshiluba, and Tshokwe corrections are applied as explicit reviewable
overrides.

The same build also inventories every ISO-coded Glottolog 5.3 row whose country
list contains `CD`. Existing benchmark identities remain stable; previously
missing rows become supplemental draft profiles. A country association or
representative coordinate is only a review lead, not proof of a language
boundary, current community size, or exclusive local presence.

Candidates remain unapproved until a decision file under `reviews/` names a
reviewer and approves language identity, representative location,
administrative containment, and temporal relevance.
