# Geographic data source decision

## Decision

Use the matched 2017 ADM1 and ADM2 layers produced by OCHA DR Congo and the
Référentiel Géographique Commun (RGC), distributed by the World Bank Data
Catalog, as the **prototype administrative geometry source**.

The exact resource URLs and raw-file SHA-256 checksums are pinned in
`public/geodata/sources.json`. The World Bank catalogue describes the dataset
as Creative Commons Attribution 4.0.

This remains a prototype source selection rather than a claim that the 2017
boundaries and names are legally current. Administrative-currency review is
required before public launch.

## Selected layers

| Level | Meaning | Represented year | Features | Primary provenance | Licence |
|---|---|---:|---:|---|---|
| ADM1 | Provinces | 2017 | 26 | OCHA DR Congo and RGC | CC BY 4.0 |
| ADM2 | Territories, cities, and communes | 2017 | 240 | OCHA DR Congo and RGC | CC BY 4.0 |

The ADM2 description is deliberately broad. Presenting all 240 features as
territories would misrepresent the source.

## Why this pair

- Both layers share provenance and explicit parent codes.
- The distributor exposes stable resource URLs that can be checksum-pinned.
- The licence permits adaptation and redistribution with attribution.
- GeoJSON inputs support a static-first build without a spatial database.
- Full-polygon containment is materially more consistent than the previously
  evaluated mixed-source geoBoundaries ADM1/ADM2 pair.

## Reproducible processing

Run:

```bash
python3 -m scripts.build_geodata
```

The builder:

1. downloads or reuses the pinned raw resources;
2. verifies each raw-file checksum before parsing;
3. removes the distributor's exact trailing `System.IO.MemoryStream` marker
   when—and only when—the manifest permits that transformation;
4. validates feature count, IDs, names, geometry types, and polygon validity;
5. assigns ADM2 parents using source P-codes;
6. checks full-polygon parent containment and within-level overlaps;
7. performs topology-preserving simplification;
8. writes deterministic web GeoJSON and a machine-readable quality report.

Generated source files, web layers, and reports are ignored by Git and can be
recreated from the manifest.

## Quality result

The verified 2026-10-05 build found:

- 26 valid ADM1 polygons and 240 valid ADM2 polygons;
- no duplicate IDs, invalid geometries, or within-level overlaps;
- all 240 ADM2 parent relationships resolved without ambiguity;
- no parent-containment failures at the 0.01% outside-area tolerance; and
- a maximum outside-parent area ratio of approximately 0.0026%.

The build reduced ADM1 geometry from 71,060 to 6,231 vertices and ADM2 from
149,151 to 25,214 vertices while preserving topology.

## Earlier candidate rejected

The initial experiment paired geoBoundaries ADM1 geometry sourced from
OpenStreetMap/Wambacher with ADM2 geometry sourced from OCHA/RGC. Although both
files were individually valid and all representative points could be assigned,
150 ADM2 polygons extended outside their assigned ADM1 geometry; some
discrepancies were substantial. The pair was rejected rather than hiding those
differences through clipping or repair.

## Remaining publication conditions

Before these layers enter a public release:

1. Compare province and ADM2 names, classifications, and hierarchy against a
   current authoritative DRC source.
2. Review the few small parent-edge differences, especially Fizi.
3. Document future name mappings without overwriting source values.
4. Preserve attribution and the licence link in the application and exports.
5. Clearly state that administrative geometry provides map navigation and does
   not define language territories.

## Language-map constraint

The atlas will not combine administrative units into inferred language
polygons. A language presence claim may reference an administrative place, but
its geographic precision and supporting evidence remain separate metadata.
