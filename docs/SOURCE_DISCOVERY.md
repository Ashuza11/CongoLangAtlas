# Online source discovery

The source-discovery pipeline expands every imported or supplemental language
profile with review candidates from public online indexes. Discovery is deliberately
separate from verification: a search result is a lead, not evidence that the
resource represents the intended language variety or a DRC population.

## Providers

| Provider | Candidate types | Discovery method |
|---|---|---|
| [OLAC](https://www.language-archives.org/) | Archive catalogue | Stable ISO 639-3 language page for every track |
| [Hugging Face Hub](https://huggingface.co/docs/hub/api) | Datasets and models | Public Hub API searches using reviewed names and aliases |
| [GitHub](https://docs.github.com/en/rest/search/search) | Repositories | Repository Search API using the preferred language name |
| [OpenAlex](https://docs.openalex.org/) | Papers, books, and other research | Works API full-text search using the language name |

The pipeline stores public metadata and links only. It does not download
dataset content, model weights, repository contents, or publication text.

## Run discovery

The generated CongoLangBench catalogue and presence inventory must already
exist. Run discovery after `make presence-candidates` so all supplemental DRC
profiles receive at least their stable OLAC catalogue lead.

```bash
make discover-sources
make web-data
```

GitHub applies stricter limits to unauthenticated search. Set `GITHUB_TOKEN`
to a read-only token when available; the token is used only as an HTTP header
and is never written to the cache or generated bundle.

Provider responses are cached under
`data/generated/source-discovery-cache/`. Repeat the filtering and bundle step
without network access with:

```bash
python3 -m scripts.discover_sources --offline
```

Both the cache and `data/generated/source-discovery.json` are generated files
and remain outside version control.

An offline rebuild preserves cached provider results for the original tracks
and still creates deterministic OLAC links for every supplemental profile.
Missing Hugging Face, GitHub, or OpenAlex cache entries remain recorded as
provider errors rather than silently appearing as negative search results.

## Relevance controls

Candidates must contain a reviewed language name, alias, or ISO code plus a
language-resource signal such as `linguistic`, `translation`, `speech`,
`corpus`, `grammar`, `orthography`, `NLP`, `ASR`, or `TTS`. Provider results
are deduplicated by URL.

Ambiguous names receive additional exclusions and identity signals. For
example, Logo design, MongoDB, and AMBA hardware results are excluded from the
Logo, Mongo, and Amba language tracks. These rules reduce obvious noise but do
not replace human review.

## Promotion checklist

Before a candidate becomes a reviewed catalogue record, confirm:

1. the language identity and named variety;
2. relevance to the DRC or a clearly labelled cross-border population;
3. publisher, authorship, version, and stable source URL;
4. access, licence, and redistribution terms;
5. resource type, modality, size, and known limitations; and
6. a named reviewer and review date.

Speaker estimates require additional checks for estimate year, geographic
scope, L1/L2 definition, method, and source. Discovery does not infer or copy
speaker totals from snippets.

No online search can guarantee that every existing resource has been found.
The generated summary therefore measures indexed candidate coverage, not
exhaustive coverage of the internet.
