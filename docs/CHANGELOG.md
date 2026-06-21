# Changelog

## Production publish setup

- Updated `src/build_unified_app.py` to emit `artifacts/index.html`.
- Added a GitHub Pages deployment workflow.
- Added static-site and repo hygiene files for production publishing.

## Mobile hardening pass

- Added quick-view filtering for priority shortlist, ownership clarity, and top retirement destinations.
- Added CSV export alongside JSON export.
- Added visible confidence badges for USD/m² and yield metrics.
- Added original local listing prices and listing confidence in each real-listing card.
- Changed mobile toolbar behavior to avoid a tall sticky control stack on narrow screens.
- Regenerated `artifacts/unified_destination_dashboard.html`.

## Unified app scaffold

- Added `src/build_unified_app.py`.
- Generated `artifacts/unified_destination_dashboard.html` from structured JSON data.
- Integrated representative listings directly into each destination card.
- Added search, category filter, sort controls, and JSON export.
- Updated README and TODO to reflect the current handoff state.

## v10

- Rebuilt dashboard as a mobile-first expandable-card layout.
- Preserved 25-destination universe.
- Preserved category scoring and judge-style verdicts.
- Improved iPhone rendering by removing desktop-table dependency.

## Listings appendix USD

- Added 3 representative listings per destination.
- Converted headline prices into USD.
- Retained original local prices for auditability.
- Added USD/m² calculations where size data is available.

## Earlier iterations

- v6 expanded European destinations and added Switzerland.
- v7 added panel/judge-style evaluation summaries.
- v8/v9 attempted responsive improvements but still had desktop-table architecture issues.
- v10 replaced that with a mobile-first structure.
