# Schemas

This directory contains JSON Schema 2020-12 definitions for all catalogue
entities described in `docs/DATA_MODEL.md`. Shared formats and identifiers live
in `definitions.schema.json`; `catalog.schema.json` is the union schema.

`vocabularies.json` exposes important controlled values for importers and the
future web interface. The entity schemas remain the authoritative validation
source.

Run validation from the repository root:

```bash
python3 -m scripts.validate_catalog
```
