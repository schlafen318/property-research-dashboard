# Codex Project Brief — Holiday & Retirement Property Destination Dashboard

## Background

The user is evaluating global destinations for developing or buying holiday/retirement properties. The ideal destination has:

- Beautiful scenery
- Airport access
- Access to global business centres
- Decent rental/profit potential
- Year-round activities
- Retirement optionality
- Foreigner / Chinese-buyer friendliness
- Good food and standard of living
- Sensible property price in USD/m²

The user already has one developed property in this cycle and wants a structured global comparison to identify the next best destinations.

## What has already been built

### 0. Unified dashboard

File: `artifacts/unified_destination_dashboard.html`

Features:

- Self-contained mobile-first HTML app
- Generated from `data/destinations.json`, `data/listings.json`, and `data/fx_rates.json`
- 25 destinations and 75 representative listings
- Real listings embedded directly inside each destination card
- Search, category filter, sort controls, and JSON export
- Current baseline for future implementation work

### 1. Main dashboard

File: `artifacts/dashboard_mobile_first_v10.html`

Features:

- Mobile-first expandable card layout
- 25 destinations
- Mountain / Water / Mountain + Water categorisation
- Scorecards by category
- Judge-style destination verdicts
- Pros / cons
- Ownership notes
- Rental/yield assumptions
- USD/m² affordability metric
- Profit drivers and red flags
- Search/filter/sort controls

### 2. Real listings appendix

File: `artifacts/listings_appendix_usd.html`

Features:

- 3 representative listing examples per destination
- 75 total examples
- USD headline prices
- Original local prices retained
- USD/m² where size data exists
- Listing source and short read

## User preferences

- Wants practical, investment-minded analysis.
- Does not want vague lifestyle fluff.
- Wants direct pros/cons and panel-style judgement.
- Strong preference for mobile-friendly outputs.
- Wants source transparency and realism around messy data.
- Wants the output to be usable by an implementation agent.

## Technical requirements for next iteration

Build a robust single-page HTML dashboard. It should be self-contained unless otherwise agreed.

Must work well on iPhone:

- No horizontal overflow
- Tap-friendly cards
- Sticky but not obstructive controls
- Readable 13–16px text
- Long URLs should wrap or be hidden behind source labels
- Avoid wide tables on mobile
- Detail sections should use cards/accordions

Data should be separated from presentation as much as possible:

- Prefer a `data/destinations.json` and `data/listings.json` model
- The app can still be compiled into a self-contained HTML if needed

## Suggested architecture

```text
/property_research_codex_project
  /artifacts
    dashboard_mobile_first_v10.html
    listings_appendix_usd.html
    legacy_scorecard.xlsx
  /src
    create_listings_appendix.py
    create_listings_appendix_usd.py
    build_unified_app.py
  /data
    destinations.json
    listings.json
    fx_rates.json
    sources.csv                     # recommended next
  /docs
    CODEX_PROJECT_BRIEF.md
    NEXT_AGENT_PROMPT.md
    DATA_SCHEMA.md
    TODO.md
```

## Highest priority next tasks

1. Re-test `artifacts/unified_destination_dashboard.html` on iPhone viewport widths: 320px, 375px, 390px, 430px.
2. Ensure no horizontal overflow.
3. Add richer source and FX timestamps where individual metric dates are available.
4. Add a data confidence badge for each yield and USD/m² metric.
5. Add editable scoring weights and CSV export.

## Important analytical standards

- Keep USD/m² conversion explicit.
- Distinguish land price from built-property price.
- Distinguish STR revenue from gross rental yield and net yield.
- Flag when data is listing-sample-based vs official/index-based.
- Do not overstate precision.
- Do not rank a destination high just because it is beautiful.
- Penalise destinations with foreign-ownership complexity, thin exit markets, or weak year-round demand.
