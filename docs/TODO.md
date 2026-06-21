# Project TODO

## Critical

- [x] Extract dashboard destination data from `dashboard_mobile_first_v10.html` into `data/destinations.json`.
- [x] Extract listings data from `listings_appendix_usd.html` or source scripts into `data/listings.json`.
- [x] Build a unified HTML dashboard that integrates real listings into each destination detail card.
- [ ] Re-test on iPhone viewport widths: 320px, 375px, 390px, 430px.
- [ ] Ensure no horizontal overflow with browser screenshot QA.

## Data quality

- [ ] Add date accessed and source date for each property price metric.
- [x] Add data-confidence badge to each yield and USD/m² metric.
- [ ] Separate built-property price, condo price, villa price, and land price.
- [ ] Separate STR revenue, gross yield, and estimated net yield.
- [ ] Refresh representative listings before any investment decision.

## Product features

- [x] Add “show only priority shortlist” filter.
- [x] Add “hide low ownership clarity” filter.
- [x] Add “show top 5 by retirement suitability” quick view.
- [x] Add export to JSON.
- [x] Add export to CSV.
- [ ] Add editable scoring weights.
- [ ] Add source drawer per destination.

## Analytical additions

- [ ] Add climate/disaster risk score.
- [ ] Add healthcare score explicitly, not just retirement suitability.
- [ ] Add travel-time matrix from Hong Kong, Singapore, Tokyo and London.
- [ ] Add tax/transaction-cost estimates by country.
- [ ] Add build-cost and development-execution score.
