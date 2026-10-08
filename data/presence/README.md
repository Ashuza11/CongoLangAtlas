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
ISO tags and produces 452 additional non-duplicative candidates across 165
second-level areas: 361 quantitative records and 91 qualitative records. Every
generated row retains the publisher's low confidence
rating and an exact CSV row, administrative code, column, and raw-value
locator. Qualitative primary-language and notes fields are also retained when
they mention an HXL-mapped language but provide no percentage; these records
are explicitly displayed without a speaker estimate. This includes the CAID
row identifying Swahili, Mashi, and Tembo in Kabare. Unmapped source labels are
not guessed; only the documented Nande,
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
