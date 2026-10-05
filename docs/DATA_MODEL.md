# Data model

## Design rule: store claims, not just conclusions

The atlas must separate an entity from claims made about it. For example, a
language record identifies Mashi, while separate evidence records state where
Mashi is documented, which alternate names a source uses, or how many speakers
a publication estimated in a given year. This makes contradictions and older
evidence visible rather than silently overwriting them.

## Core entities

### `language`

| Field | Purpose |
|---|---|
| `id` | Stable atlas identifier, independent of external catalogues |
| `preferred_name` | Current display name and the authority/review behind it |
| `iso_639_3` | ISO identifier when applicable |
| `glottocode` | Glottolog identifier when applicable |
| `alternate_names` | Searchable names with source and usage notes |
| `variety_of` | Optional explicit relationship, never inferred from spelling |
| `classification_note` | Cited note for unresolved or disputed classification |
| `status` | Draft, reviewed, disputed, or retired |
| `last_reviewed_at` | Most recent substantive review date |

### `place`

| Field | Purpose |
|---|---|
| `id` | Stable place identifier |
| `name` | Display name |
| `admin_level` | Country, province, territory, locality, or custom region |
| `parent_id` | Administrative hierarchy |
| `geometry_id` | Reference to versioned geometry, not embedded editorial truth |
| `source_id` | Boundary source and version |

### `language_presence_claim`

| Field | Purpose |
|---|---|
| `id` | Stable claim identifier |
| `language_id` | Language or variety asserted |
| `place_id` | Associated place when applicable |
| `geometry_type` | Point, territory association, corridor, or supported area |
| `role` | L1, L2, lingua franca, heritage, educational, or unspecified |
| `time_start` / `time_end` | Time relevance when known |
| `source_id` | Evidence for the claim |
| `evidence_quote_or_locator` | Short permitted excerpt or page/table locator |
| `confidence` | High, medium, low, or disputed |
| `review_status` | Workflow state |

### `resource`

| Field | Purpose |
|---|---|
| `id` | Stable resource identifier |
| `title` | Source title |
| `resource_type` | Dataset, corpus, bitext, speech, dictionary, grammar, orthography, publication, tool, model, benchmark, or other |
| `modalities` | Text, tabular, audio, image, video, multimodal |
| `languages` | Language IDs plus exact variety/provenance notes |
| `geographic_scope` | DRC-only, DRC-labelled, cross-border, generic, or uncertain |
| `publisher` / `creators` | Attribution |
| `version` | Resource release or edition |
| `published_at` / `retrieved_at` | Time metadata |
| `homepage_url` / `download_url` | Discovery and access links |
| `access_type` | Open download, gated, registration, request-only, catalogue-only, unavailable, or unknown |
| `licence_id` | Normalized licence record |
| `redistribution` | Allowed, metadata-only, restricted, prohibited, or unknown |
| `size` / `unit` | Count with a clear unit such as sentences, tokens, hours, or entries |
| `format` | CSV, JSONL, Parquet, WAV, PDF, etc. |
| `domain` | News, religious, conversational, educational, health, etc. |
| `source_id` | Evidence for this metadata |
| `verification_status` | Draft, source-checked, expert-reviewed, community-reviewed, disputed |
| `limitations` | Free-text caveats shown to users |

### `publication`

Stores bibliographic metadata for papers, books, theses, grammars, surveys,
and reports. A publication can be both a source of claims and a discoverable
research resource.

### `nlp_result`

| Field | Purpose |
|---|---|
| `id` | Stable result identifier |
| `language_id` | Exact evaluated variety |
| `task` / `direction` | Translation, ASR, classification, etc. |
| `model_id` / `model_revision` | Reproducible model identity |
| `benchmark_id` / `benchmark_version` | Frozen evaluation input |
| `metric` / `value` | Named metric and score |
| `protocol_url` | Public method and prompt/decoding details |
| `result_source_id` | Result artifact or publication |
| `limitations` | Comparability and interpretation caveats |

### `source`

| Field | Purpose |
|---|---|
| `id` | Stable citation identifier |
| `citation` | Human-readable citation |
| `url` / `archive_url` | Original and preserved links |
| `publisher` / `authors` | Responsibility |
| `published_at` / `retrieved_at` | Dates |
| `source_type` | Primary dataset, official catalogue, paper, community review, etc. |
| `licence_id` | Licence of the source itself |
| `verification_notes` | What was checked and by whom |

### `review_event`

Records reviewer, date, decision, changed fields, evidence examined, and
conflict-of-interest or community-consent notes. Public exports may use a role
or contributor ID when personal attribution is not desired.

## Licence and access are separate

Never encode availability in the licence field. A resource may have an open
licence but require registration, or be publicly viewable without permission
to redistribute. At minimum store:

- normalized licence or `unknown`;
- access type;
- redistribution status;
- terms URL;
- date the terms were checked;
- notes about derived metadata or aggregates.

## Geographic representation

Use the least precise geometry supported by evidence:

1. an exact documented locality point;
2. a territory/province association;
3. a documented corridor or approximate area;
4. a broad region label;
5. `unknown`.

Do not generate a language polygon merely by combining administrative units.
If a scholarly or community-reviewed polygon is used, preserve its source,
date, method, precision, and licence.

## Required identifiers

External identifiers aid interoperability but are not permanent internal
primary keys. Keep the atlas ID stable even if ISO, Glottolog, catalogue, or
administrative identifiers change.

## Publication-safe exports

The public build must exclude:

- sentence-level benchmark text;
- restricted audio or transcripts;
- credentials, access tokens, and private contact details;
- sensitive community locations where disclosure creates risk;
- copyrighted extracts beyond permitted citation;
- fields explicitly marked internal.
