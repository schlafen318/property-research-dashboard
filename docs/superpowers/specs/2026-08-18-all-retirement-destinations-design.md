# All-Destination Retirement Cost Ranking

## Objective

Expand the retirement cost model and ranking from eight selected destinations to all 30 destinations in `data/destinations.json`. Keep the current comparison methodology consistent, show ranks 1–10 immediately, and place ranks 11–30 in accessible, indexable expandable tables.

The result must improve coverage without mixing full models with lightweight estimates. Every destination must meet the same data contract and source standard before it appears in the ranking or calculator.

## Scope

This change will:

- Add complete retirement cost records for the 22 destinations not yet present in `data/retirement_costs.json`.
- Revalidate the existing eight records under the same shared review date and methodology.
- Include all 30 destinations in the retirement calculator and ranked guide.
- Show ranks 1–10 in the initial table and ranks 11–30 inside a native `<details>` disclosure.
- Keep concise editorial notes for the top 10 only.
- Update page copy, metadata, structured data, FAQs, internal links, and infographics from eight-destination to 30-destination coverage.
- Preserve the current static, progressively enhanced architecture and avoid a JavaScript dependency for ranking visibility.

This change will not alter the site's separate investment score, destination ordering elsewhere, retirement assumptions, or personal financial-advice limitations.

## Destination Coverage

The authoritative destination set is every ID in `data/destinations.json`. The build and tests must derive the expected set from that file instead of maintaining another hard-coded release list.

The build must fail when:

- A destination lacks a retirement cost record.
- A retirement cost record has no matching destination dossier.
- IDs are duplicated.
- A required cost, property, inflation, confidence, or source field is missing or invalid.

No destination may be silently omitted.

## Research and Data Standard

Each destination must retain the existing `retirement_costs.json` schema:

- `single` and `couple` profiles.
- Eight cost categories: food and household, utilities and communications, private healthcare, transport, dining and leisure, travel, visa and administration, and contingency.
- Annual rent and annual owner costs.
- Representative property price and acquisition-cost rate.
- General, healthcare, and property inflation assumptions.
- Overall confidence and explicit proxy categories.
- At least three dated HTTPS sources with the metric supported, access date, and limitations.

Research should prefer, in order:

1. Destination- or city-level cost and rent observations.
2. National statistical agencies for inflation context.
3. Government, major market portals, or established local property sources for acquisition costs and representative prices.

Regional or national proxies are allowed only when destination-level evidence is unavailable. Every proxy must be disclosed in `confidence.proxy_categories` and source notes. The model may use the existing representative listing evidence where it satisfies the property standard, but it must not present listing samples as market-wide medians.

All figures remain planning estimates in current USD. Research must not imply predictive accuracy or personalized financial advice.

## Ranking Method

The public guide continues to rank a couple renting under one standard scenario:

- Retirement starts today.
- 30-year planning horizon.
- 3.5% withdrawal rate.
- No pension or outside passive income.
- One year of expenses held as an emergency reserve.
- Required capital equals annual spending divided by 3.5%, plus the reserve.
- Property capital is displayed separately and does not affect rank.

The ranking function must continue to sort all eligible records by required capital in ascending order. The calculator remains the place for personalized household, retirement date, income, inflation, housing, and horizon assumptions.

## Guide Experience

The guide will use one continuous ranking with two visual segments:

1. **Ranks 1–10:** visible on initial load in the existing five-column table.
2. **Ranks 11–30:** rendered in the original HTML inside a native `<details>` element with a clear `View ranks 11–30` summary.

Both segments use the same columns:

- Rank
- Destination and country
- Annual spending
- Required retirement capital
- Property capital

The expanded table must not repeat the top 10. Search engines, screen readers, and no-JavaScript users must receive all 30 rows in the server-rendered document.

The editorial destination-note section will show the top 10 only. Each of the 30 table rows links to its destination dossier, so the guide remains useful without adding 30 large prose cards.

The introduction and methodology must explain that all Global Home Atlas destinations are included, while the cost rank is not a lifestyle or retirement-suitability endorsement.

## Calculator Experience

The calculator selector must include all 30 destinations. Its pre-rendered benchmark comparison should mirror the guide's progressive-disclosure pattern: top 10 visible and the remaining 20 expandable. Calculator calculations continue to run entirely in the browser without transmitting financial inputs.

## SEO and Structured Data

Update the title, H1, description, Open Graph copy, article text, FAQ answers, guide-hub preview, and internal-link labels to reflect 30 destinations.

Preserve the existing canonical URL. Preserve Article, FAQPage, ImageObject, BreadcrumbList, WebPage, and calculator schema. Add an `ItemList` entity containing all 30 ranked destinations, with stable positions and destination URLs.

All ranking rows, citations, methodology text, and ranks 11–30 must be present in the initial HTML. Expansion controls exist for human readability, not content loading.

## Infographics

Regenerate both retirement graphics using the new dataset. To keep labels legible, the visual charts should feature the top 10 and clearly state that they are the lowest-cost 10 of 30 ranked destinations. The HTML tables remain the authoritative complete ranking.

Image filenames and URLs remain stable to preserve existing links and image indexing. Update alt text, captions, and download labels to describe the 30-destination dataset and top-10 visual selection accurately.

## Validation

Automated tests must verify:

- Retirement cost records exactly match all IDs in `data/destinations.json`.
- Every record satisfies the complete profile, bounds, confidence, and source requirements.
- All 30 destinations appear exactly once in the guide ranking.
- Ranks are sorted by the standard required-capital result.
- Ranks 1–10 are outside the disclosure and ranks 11–30 are inside it.
- The calculator contains all 30 choices and benchmark rows.
- Metadata and copy no longer claim eight-destination coverage.
- ItemList schema contains 30 ordered entries.
- Both infographics exist, retain their expected dimensions, and use accurate alt text.
- The complete static-site verification suite passes.

Visual verification must cover desktop and 390-pixel mobile widths, including table overflow, disclosure interaction, destination links, and deferred image loading.

## Rollout

Ship the data, generator, tests, generated artifacts, and regenerated images together. Merge through the normal pull-request workflow so the existing GitHub Pages deployment rebuilds the site. After deployment, verify the canonical live guide, the calculator's 30 options, the expandable rows, structured data, and the sitemap notification job.
