# Changelog

## 2026-08-18 — All-destination retirement ranking

- Expanded the source-audited retirement cost model from eight destinations to all 30 destinations currently covered by Global Home Atlas.
- Kept the comparison readable by showing ranks 1–10 first and placing ranks 11–30 in accessible expandable tables on the guide and calculator.
- Added all 30 destinations to the private client-side calculator and added a complete 30-entry ItemList schema to the ranking guide.
- Regenerated both retirement graphics as lowest-cost-10-of-30 views while preserving the complete HTML ranking for readers and search engines.
- Kept the ranking limited to modeled capital requirements for a couple renting; it does not rank lifestyle quality or provide personal financial advice.

## 2026-08-18 — Retirement abroad calculator

- Added an indexable retirement-abroad calculator covering eight destination benchmarks for single retirees and couples.
- Added source-audited cost, inflation, housing, property, acquisition-cost, and confidence inputs with transparent methodology and citations.
- Added client-side projections for retirement expenses, reliable outside income, liquid portfolio capital, property capital, and emergency reserves without persisting raw financial inputs.
- Linked the calculator from the retirement guide hub, retirement guides, and covered country and destination pages.
- Added an SEO-focused capital comparison ranking all eight destinations under consistent rent, reserve, income, and withdrawal-rate assumptions, with property capital shown separately.

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
