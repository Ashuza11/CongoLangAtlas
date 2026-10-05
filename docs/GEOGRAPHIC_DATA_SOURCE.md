# Geographic data source decision

## Decision

Use the DRC `gbOpen` ADM1 and ADM2 layers from geoBoundaries commit
`9469f09` as the **prototype administrative geometry source**. The files are
pinned by URL and SHA-256 checksum in `public/geodata/sources.json`.

This is a source selection, not final approval for public map publication.
Both layers have passed metadata, JSON structure, feature-count, geometry-type,
and checksum review. Name, hierarchy, topology, and administrative-currency
review remain required.

## Selected layers

| Level | Meaning | Represented year | Features | Primary provenance | Licence |
|---|---|---:|---:|---|---|
| ADM1 | Provinces | 2017 | 26 | OpenStreetMap and Wambacher | ODbL 1.0 |
| ADM2 | Territories and cities | 2019 | 189 | Référentiel Géographique Commun and OCHA DR Congo | CC BY 3.0 IGO |

The ADM2 label is intentionally “territories and cities.” Treating all 189
features as territories would misrepresent the source metadata.

## Why geoBoundaries

- The project exposes per-layer provenance, represented year, build date,
  feature count, licence, and pinned downloads.
- ADM1 and ADM2 are available in GeoJSON and TopoJSON, allowing a static-first
  web build without a spatial database.
- The selected layers have explicit reuse terms instead of an ambiguous or
  undocumented licence.
- Pinning the upstream commit prevents the application from changing when the
  provider updates its `current` API response.

## Verification performed

On 2026-10-05, the pinned full-resolution GeoJSON files were downloaded and
checked for:

- valid JSON `FeatureCollection` structure;
- the advertised feature counts (26 at ADM1 and 189 at ADM2);
- expected polygonal geometry types;
- consistent property keys (`shapeGroup`, `shapeID`, `shapeISO`, `shapeName`,
  and `shapeType`); and
- reproducible SHA-256 checksums.

This review did not establish that every name, border, parent relationship, or
geometry is legally current or topologically correct.

## Publication conditions

Before either layer enters a public build:

1. Compare province and ADM2 names, counts, and hierarchy against an
   independent authoritative DRC source.
2. Run geometry-validity, overlap, gap, and parent-containment checks.
3. Document every normalization or simplification step.
4. Preserve the applicable attribution and licence with downloadable outputs.
5. Record the generated artifact checksum and source-manifest version.
6. Clearly state that administrative geometry provides map navigation and does
   not define a language territory.

## Rejected shortcut

The atlas will not combine administrative units into inferred language
polygons. A language presence claim may reference an administrative place, but
its geographic precision and supporting evidence remain separate metadata.
