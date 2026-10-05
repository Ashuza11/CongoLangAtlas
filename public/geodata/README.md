# Geographic data policy

Only reviewed, licence-compatible, versioned geographic artifacts belong here.
Every artifact must document its source, administrative level, release date,
licence, processing steps, and checksum.

`sources.json` records the pinned prototype sources selected for DRC province
and territory/city navigation. Validate it with:

```bash
python3 -m scripts.validate_geodata
```

The manifest is not a generated map artifact. Build the checksum-verified,
simplified layers and quality report with:

```bash
python3 -m scripts.build_geodata
```

Generated artifacts live under `public/generated/geodata/` and
`data/generated/geodata/` and are intentionally excluded from Git. The
`source-checked` layers still require the administrative-currency review
described in `docs/GEOGRAPHIC_DATA_SOURCE.md` before publication.

Language polygons must not be derived from intuition or presented as exact
boundaries. Use points, administrative associations, broad regions, or
explicit uncertainty unless a cited source supports a stronger geometry.
