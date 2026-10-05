# Atlas data workspace

This directory will contain public, reviewable metadata—not corpus text.

```text
data/
  schema/       JSON Schemas and controlled vocabularies
  catalog/      version-controlled language, place, resource, source, and claim records
public/geodata/ verified and optimized public map artifacts
```

Rules:

- Never copy restricted CongoLangBench text into this project.
- Every public record needs a source ID and verification status.
- Preserve raw source citations separately from normalized display values.
- Keep licence, access, and redistribution fields separate.
- Generate map files from reviewed catalogue records; do not hand-edit built
  GeoJSON or PMTiles artifacts.
- Do not commit credentials, private correspondence, or sensitive locations.
