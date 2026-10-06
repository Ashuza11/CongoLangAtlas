# Atlas application

The application is a static Next.js interface over generated, public-safe
metadata. It never imports corpus text or restricted research material.

```text
src/
├── app/                # Layout, page entry point, and global visual system
├── components/         # Catalogue explorer, profiles, and MapLibre map
└── lib/                # Web bundle types
```

Run `make web-data` before starting the interface. The generated bundle lives
at `public/generated/atlas/catalog.json`; generated ADM1 and ADM2 layers live
at `public/generated/geodata/`. Both directories are reproducible and ignored
by Git.

Administrative geometry is context for navigating the DRC. It must not be
described or styled as evidence of language boundaries or presence.
Province and territory clicks filter profiles using representative-point
candidates from the pinned Glottolog source. The interface labels these as
geographic leads rather than reviewed `language_presence_claim` records and
explains that a representative point is not a complete language distribution.

Language profiles display reviewed resources separately from automatically
discovered source leads. Candidate datasets, models, repositories, research,
and archive links must always retain their candidate label until manual review
promotes them into the catalogue.

The web application will be scaffolded after the project schemas,
administrative boundary source, and first import fixture are approved. The
recommended implementation is Next.js, TypeScript, and MapLibre GL JS.
