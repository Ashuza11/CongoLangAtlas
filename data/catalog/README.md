# Catalogue records

Reviewed language, place, resource, publication, source, evidence-claim, and
review-event records will live here. Records must pass schema validation and
the publication-safety checks before they are included in the website build.

The `draft/` directory contains non-public fixtures used to exercise the data
model. A draft record is not verified evidence and must pass the review policy
before a future exporter may include it in a public release.

Each JSON file contains one record and declares its schema using
`entity_type`. Identifiers are repository-wide and references must resolve to
another catalogue record.
