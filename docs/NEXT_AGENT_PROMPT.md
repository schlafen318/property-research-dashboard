# Prompt for Codex / Implementation Agent

You are taking over a property-research dashboard project. The user wants an investor-grade, mobile-first dashboard comparing global holiday and retirement property-development destinations.

## Read first

1. `README.md`
2. `docs/CODEX_PROJECT_BRIEF.md`
3. `docs/DATA_SCHEMA.md`
4. Current artifacts:
   - `artifacts/unified_destination_dashboard.html`
   - `artifacts/dashboard_mobile_first_v10.html`
   - `artifacts/listings_appendix_usd.html`

## Goal

Harden the current unified dashboard as a single, self-contained, mobile-first HTML file.

The current unified dashboard already combines:

- Destination ranking and category scorecards
- Judge-style summary, pros, cons and panel verdict
- Ownership/foreigner/Chinese buyer friendliness notes
- Rental/yield economics
- USD/m² affordability
- Food quality and standard of living rankings
- Representative real listings for each destination
- Source notes and FX assumptions

## Specific requirements

### Mobile UX

- Start from a mobile-first design.
- Use expandable cards, not wide tables.
- Make destination cards tappable and readable on iPhone.
- Avoid horizontal scrolling except in very controlled source sections.
- Use readable font sizes and spacing.

### Data model

- Use the existing JSON files under `/data`.
- `data/destinations.json`, `data/listings.json`, and `data/fx_rates.json` already exist.
- Add `data/sources.csv` only if you are expanding source auditability.

### Output

Generate:

- `artifacts/unified_destination_dashboard.html`
- Optionally, `artifacts/dashboard_unified_v11.json` if useful

### Analytical rules

- Do not mix land prices with built-property prices without explicit labels.
- Do not present agent-marketing gross yields as net yield.
- Preserve original local listing prices alongside USD prices.
- Flag confidence levels.
- Include source dates where available.
- Keep the tone direct and judgement-oriented, like a panel selecting top destinations.

## Definition of done

The user should be able to open one HTML file on iPhone and:

1. Browse all destinations.
2. Filter by Mountain / Water / Mountain + Water.
3. Sort by score, USD/m², ownership, and any additional priority metrics added in the next iteration.
4. Tap a destination and see all category scores.
5. See a concise panel verdict with pros/cons.
6. See ownership and rental/yield notes.
7. See three representative listings with USD price, local price, size, USD/m² and source.
8. Understand which data is high-confidence vs rough benchmark.
