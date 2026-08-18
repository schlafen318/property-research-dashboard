# Retirement Abroad Calculator SEO Page Design

## Context

Global Home Atlas already publishes retirement-oriented guides and destination comparisons, but it does not yet quantify the combined capital required to fund retirement spending and acquire or hold property abroad. The linked Visual Capitalist map is useful as editorial inspiration, but its country-level total-spending method is too coarse for a decision tool: it assumes a short fixed retirement, applies a flat comfort uplift, and does not integrate property capital, healthcare, tax, inflation, reliable outside income, or portfolio funding mechanics.

The new feature is an architectural addition to the static site: a dedicated, indexable SEO page with a mobile-first calculator, destination-level benchmarks, transparent methodology, and internal links into the existing retirement and property research cluster.

## Goal

Publish a useful and auditable retirement-abroad calculator that answers two related questions:

1. How much annual spending will a comfortable retirement in a selected destination require?
2. How much liquid portfolio, property capital, and emergency reserve will a single retiree or couple need?

The page should satisfy informational search intent while helping qualified users move into destination research and shortlist review.

## Audience and Lifestyle Standard

The primary audience is an affluent international buyer considering a retirement or long-stay property abroad. The default lifestyle is comfortable but not luxurious: a good neighborhood, private healthcare, regular dining out, appropriate local transport, leisure, and periodic travel, without trophy-property or luxury-consumption assumptions.

The calculator must support both:

- Single retiree
- Retired couple

## SEO Page

- **Slug:** `/retirement-abroad-calculator/`
- **Primary keyword:** `retirement abroad calculator`
- **Secondary intents:** `how much do I need to retire abroad`, `cost to retire abroad calculator`, and `international retirement calculator`
- **Title:** `Retirement Abroad Calculator: How Much Do You Need? | Global Home Atlas`
- **H1:** `Retirement Abroad Calculator`
- **Meta description:** `Estimate how much you need to retire abroad, including destination living costs, inflation, pension and passive income, property costs, and required portfolio capital.`

The page should be server-rendered by the existing static builder and remain useful before JavaScript runs. The calculator is the primary page content, followed by a concise destination benchmark table, methodology, limitations, related retirement guides, and FAQs. Do not add decorative sections or duplicate calculator outputs as editorial summaries.

### Indexable Content

The generated HTML must include:

- A direct introduction that answers what the calculator estimates.
- A pre-rendered comparison table for the initial eight destinations, with single and couple annual comfortable-spending benchmarks in today's USD.
- A concise explanation of rent, already-own, and buy-at-retirement scenarios.
- A transparent explanation of inflation, reliable income, portfolio withdrawals, property capital, and reserves.
- Source dates, confidence labels, and a research-grade-not-advice limitation.
- FAQs addressing how much is needed, how inflation is handled, how pensions and passive income are treated, whether property is included, and why portfolio dividends are not counted twice.

Use canonical, Open Graph, WebPage, WebApplication, BreadcrumbList, and FAQPage metadata consistent with the existing site helpers. Add the URL to the sitemap and guide hub.

## Initial Destination Coverage

The first release covers the same eight destinations already emphasized in the retirement guides:

- Fukuoka / Itoshima
- Valencia
- Algarve / Cascais
- Madeira
- Crete
- Hakone / Izu
- Lake Como
- Málaga / Costa del Sol

Do not launch thin programmatic calculator pages for every country or destination in this release. One strong canonical calculator page should establish search usefulness before expanding the cluster.

## Data Model

Add `data/retirement_costs.json`, keyed by `destination_id`. Each record should contain:

- Display currency and USD conversion basis.
- Data vintage and last-reviewed date.
- Single and couple annual comfortable-spending benchmarks in today's money.
- Category-level annual costs for housing, food and household spending, utilities and communications, private healthcare, transport, dining and leisure, local and home travel, visa and administration, and contingency.
- Housing scenarios for renting, already owning, and buying at retirement.
- Owner costs for property tax, insurance, maintenance, and applicable association charges.
- Representative property price, acquisition-cost percentage or range, and price basis.
- General inflation, healthcare inflation, and property-cost inflation assumptions.
- Confidence by category and an explicit proxy flag when destination-level evidence is unavailable.
- Source records containing source name, URL, metric supported, source date, access date, and notes.

Official and destination-level evidence should be preferred. Broader country data and crowdsourced cost data may be used as documented proxies, not presented as precise local facts.

## Calculator Inputs

### Guided Inputs

- Current age
- Planned retirement age
- Single or couple
- Destination
- Annual retirement spending in today's USD, pre-filled from the selected destination benchmark and editable
- Housing plan: rent, already own, or buy at retirement
- Annual pension income
- Other reliable non-portfolio passive income
- Optional net rental income from the destination property
- Inflation treatment for each income stream: indexed or fixed
- Portfolio income assumption: income-focused, balanced, or growth-focused

All income inputs should be labeled as after-tax estimates. The page should explain that gross inputs will not produce a reliable after-tax result.

### Advanced Assumptions

- General inflation
- Healthcare inflation
- Property-cost inflation
- Retirement horizon
- Planning withdrawal rate
- Estimated portfolio cash yield
- Emergency-reserve months

Ordinary users should not be required to choose a withdrawal rate. The guided default is 4.0% for a horizon of up to 25 years, 3.5% for 26–30 years, 3.25% for 31–35 years, and 3.0% for more than 35 years. Every result presents sensitivity one step above and below the guided rate where the 3.0–4.0% bounds allow it. Advanced users may override the rate.

The portfolio-income presets affect only the explanatory cash-income-versus-asset-sales breakdown: income-focused uses a 3.0% illustrative cash yield, balanced uses 2.0%, and growth-focused uses 1.0%. The user may edit this yield under advanced assumptions. These presets must be labeled as non-guaranteed illustrations and must not change the required portfolio calculation or imply personalized asset-allocation advice.

## Calculation Model

### Project Expenses to Retirement

Each expense category is projected independently so healthcare and property-related costs can use different inflation assumptions:

```text
first_year_category_cost
= today_category_cost * (1 + category_inflation_rate) ^ years_to_retirement
```

The page should show both today's-dollar and retirement-year results. Current exchange rates establish the comparison baseline; the calculator must not pretend to forecast future exchange rates.

### Project Outside Income

Each pension or passive-income stream is marked as either inflation-linked or fixed:

```text
indexed_income_at_retirement
= income_today * (1 + inflation_rate) ^ years_to_retirement

fixed_income_at_retirement
= stated_nominal_income
```

Reliable outside income includes pensions, annuities, existing net rental income, business income expected to continue, and separately underwritten net income from the destination property. Destination-property rental income defaults to zero.

### Calculate the Portfolio Requirement

```text
first_year_funding_gap
= first_year_retirement_expenses
- pension_income
- other_reliable_non_portfolio_income
- destination_property_net_rental_income

required_liquid_portfolio
= max(0, first_year_funding_gap) / planning_withdrawal_rate
```

Portfolio dividends and interest must not be subtracted as external passive income. They are part of the portfolio's total withdrawal. The result may explain the withdrawal as estimated cash yield plus asset sales, but the full amount remains the portfolio withdrawal.

### Add Property and Reserve Capital

```text
property_capital
= projected_property_price + acquisition_costs

total_capital_required
= required_liquid_portfolio
+ property_capital_if_buying
+ emergency_reserve
```

Keep liquid portfolio, property capital, and emergency reserve separate before showing their combined total. For rent and already-own scenarios, include the appropriate recurring housing or owner costs and omit new acquisition capital.

## User Experience

Use the approved mobile-first two-screen flow:

1. Guided inputs grouped into retirement, destination and housing, reliable income, and portfolio-income assumptions.
2. Decision result showing total capital, liquid portfolio, property and acquisition costs, emergency reserve, first-year spending and outside income, portfolio cash-income-versus-asset-sales explanation, and planning assumptions.

On desktop the form and result may use available width, but the information order must remain the same. On mobile, use a single column with no horizontal overflow. Results should update client-side without a page reload. The calculator must not transmit or persist user financial inputs.

## Internal Linking and Conversion

Link to the calculator from:

- `/guides/`
- `/buying-property-abroad-for-retirement/`
- `/best-places-to-buy-property-abroad-for-retirement/`
- Relevant destination and country pages in the initial coverage set

The calculator page should link back to both retirement guides, relevant destination dossiers, the methodology page, and shortlist review. Use existing tracking attributes for calculator opens, calculations, destination changes, result-guide clicks, and shortlist-review clicks. Do not record raw financial input values in analytics events.

## Error Handling

- Require retirement age to be greater than current age.
- Reject negative spending, property, income, inflation, return, reserve, and horizon values.
- Set the required portfolio to zero rather than a negative value when reliable income covers spending.
- Do not allow the same income stream to be classified as both outside income and portfolio income.
- If destination cost data is missing, disable that destination in the calculator while retaining its normal site pages.
- If a category relies on a country-level proxy, label it and reduce confidence.
- If JavaScript fails, retain the indexable benchmark table, methodology, and calculator explanation.
- Present results as planning estimates, not financial, tax, legal, immigration, healthcare, or investment advice.

## Implementation Boundaries

Use the existing Python static-generation architecture. Extend `src/build_unified_app.py` with focused page, schema, navigation, sitemap, and rendering helpers rather than introducing a framework or backend. Load calculator data from `data/retirement_costs.json` and embed only the required dataset into the generated page.

Do not add accounts, saved plans, Monte Carlo simulation, tax-jurisdiction logic, live market-return feeds, live FX forecasting, or personalized investment recommendations in this release.

## Testing and Verification

### Calculation Tests

Add deterministic tests for:

- Category-level inflation over different years to retirement.
- Fixed versus inflation-linked pensions and passive income.
- Single versus couple benchmark selection.
- Funding-gap calculation and the zero floor.
- Required portfolio at default and sensitivity withdrawal assumptions.
- Portfolio income not being double-counted.
- Rent, already-own, and buy-at-retirement housing scenarios.
- Property acquisition costs and emergency reserves.
- Today's-dollar and retirement-year conversions.

### Static and SEO Tests

Verify:

- The build succeeds and writes `artifacts/retirement-abroad-calculator/index.html`.
- Title, description, canonical, H1, structured data, and FAQ content are present.
- The page appears in `sitemap.xml` and the guide hub.
- Internal links resolve to generated pages.
- A meaningful benchmark table and methodology remain in the HTML without JavaScript.
- Analytics events exclude raw financial values.

### Visual Verification

Check 320, 375, 390, 430, 736, and 1024 pixel widths. Confirm readable controls, no horizontal overflow, visible focus treatment, and correct reflow of the input and result sections. Exercise calculator updates for both household types and all three housing plans.

## Rollout

Publish the single calculator page with the initial eight destinations. After deployment, use Search Console data and privacy-safe calculator events to assess impressions, query coverage, calculation completion, destination selection, and transitions into guides or shortlist review. Expand destination coverage only after source quality and user demand justify it.
