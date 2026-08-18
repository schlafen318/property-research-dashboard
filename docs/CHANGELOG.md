# Changelog

## 2026-08-18 — Retirement target and net return emphasis

- Moved the retirement capital target above today's allocation so the primary planning goal appears first.
- Added net return after withdrawal, calculated as expected return minus the first-year portfolio withdrawal rate.
- Added a plain-language warning and negative-value styling when planned withdrawals exceed the assumed return.

## 2026-08-18 — Retirement results by planning date

- Split the calculator estimate into what must be allocated today, what is needed at retirement, and first-retirement-year cash flow.
- Added the investment required today by discounting total retirement capital at the user's expected portfolio return.
- Kept a buy-now home purchase separate from the investment amount, while including a buy-at-retirement home in the future capital target.
- Renamed and explained the first-year portfolio withdrawal as funding gap divided by liquid portfolio, explicitly distinguishing it from a recommended safe withdrawal rate.

## 2026-08-18 — Personalized retirement cash-flow model

- Replaced the calculator's preset withdrawal-rate method with annual expense and reliable-income cash flows discounted by a required user-entered portfolio return after fees.
- Added separate Buy now and Buy at retirement plans so today's property cost is never mixed with retirement-year capital.
- Added the calculated first-year withdrawal as an output and removed the withdrawal override, portfolio style, cash-yield input, and asset-sale illustration.
- Added clear straight-line-return and sequence-risk limitations while retaining the separate standardized 3.5% destination comparison.

## 2026-08-18 — Retirement calculator housing inputs

- Replaced annual lifestyle spending with a monthly input while preserving annual calculations internally.
- Clarified that renting includes rent, while owning or buying includes owner running costs instead of rent.
- Added an editable home purchase budget prefilled from the selected destination and applied only to buy-at-retirement scenarios.
- Clarified that rental income should come from a separate rental property and remain zero for a self-use destination home.

## 2026-08-18 — Sortable retirement ranking

- Made every ranking column sortable across all 30 destinations while retaining the 10-row preview and 20-row expansion.
- Replaced technical table labels with plain-language titles and clarified that the home purchase estimate does not affect cost rank.
- Simplified the hero actions, removed redundant update metadata, and moved detailed cost sources into an expandable disclosure.

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
