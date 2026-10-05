# Import configurations

Import configurations pin external or sibling-project metadata snapshots and
their expected reconciliation totals. They contain no corpus content.

`congolangbench.json` pins the first CongoLangBench registry import. Update its
commit and expected totals only after reviewing the upstream changes and
recording the new import report.

`congolangbench-resource-overrides.json` records atlas-reviewed facts from
primary dataset cards. It supplements—but never edits—the pinned registry
snapshot. Every override identifies its own source, review date, licence,
access type, redistribution state, geographic scope, and limitations.
