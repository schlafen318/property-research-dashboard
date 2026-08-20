# Retirement Destination Discovery Calculator Design

**Date:** 2026-08-20  
**Status:** Approved for implementation planning

## Purpose

Add a second retirement-planning journey that starts with the user's current resources, projects their position at retirement, and recommends destinations that fit both their finances and a small set of meaningful preferences.

The existing `/retirement-abroad-calculator/` remains the destination-first planner. The new `/retirement-destination-finder/` answers a different question: **Given what I have today and what I can invest, where could I realistically retire?**

The two pages share the same calculation engine, destination-cost data, and housing assumptions. A restrained two-option text switch links them:

- **Plan for a destination**
- **Find destinations I can afford**

They are separate URLs rather than modes inside one changing form. This keeps each task understandable, shareable, measurable, and independently indexable.

## Goals

- Project retirement resources from current liquid capital and monthly investing.
- Evaluate the full current destination universe dynamically; never hardcode a destination count or subset.
- Model renting, buying now, and buying at retirement consistently with the destination-first calculator.
- For buying now, separate total capital into property investment and the remaining liquid portfolio without double counting.
- Model mortgage availability by destination, mortgage amortization, rental cash flow, and property equity.
- Recommend financially plausible destinations and explain every recommendation with visible numbers.
- Use a few purposeful preferences only after financial inputs.
- Keep all personal and financial inputs in the browser.

## Non-goals

- Guarantee mortgage approval or property availability.
- Provide regulated financial, mortgage, tax, legal, or immigration advice.
- Add accounts, saved plans, lender applications, or lead sharing in this release.
- Add Monte Carlo simulation, live interest rates, live foreign exchange forecasts, or tax-jurisdiction modeling.
- Create an opaque composite retirement or affordability score.

## User Journey

The page uses a single top-down reading order on desktop and mobile.

### 1. What you have today

- Current age
- Planned retirement age
- Household type
- Total liquid capital available today
- Monthly amount available for portfolio investment
- Expected annual portfolio return after fees

Monthly contributions are invested monthly. The interface states whether the contribution rises with general inflation and uses the same straight-line-return limitation as the existing calculator.

### 2. Housing plan

The selector uses the same language as the existing planner:

- **Rent:** destination retirement spending includes rent; no property capital is added.
- **Buy now:** the destination-specific purchase is financed from the user's total capital and, if selected, a mortgage. The remaining capital becomes the starting liquid portfolio.
- **Buy at retirement:** the projected purchase price and acquisition costs are added to the destination's retirement target.
- **Already own:** because the retirement property fixes the destination, the user selects the owned destination and continues in the existing destination-first planner. The discovery page does not invent a comparable owned property in every market.

When **Buy now** is selected, reveal:

- Maximum amount the user is willing to allocate to a property purchase
- Cash, mortgage, or not sure
- Intended use until retirement: rent out or personal/occasional use
- Mortgage terms when applicable
- Rental assumptions when applicable
- Mortgage treatment at retirement: pay off or continue repayments

The property allocation is a maximum, not a second pot. For each destination, actual down payment and acquisition costs are deducted from total liquid capital. Any unused allocation remains invested in the portfolio.

### 3. Mortgage profile

The default buyer profile is a non-resident foreign buyer with overseas income. Users may refine:

- Residence status in the destination country
- Income location and currency
- Optional passport country when a documented nationality restriction is relevant
- Age at proposed loan maturity
- Property use

Financial and eligibility inputs remain local to the browser and are never included in analytics events.

For a mortgage scenario, users enter:

- Down payment or desired loan-to-value ratio
- Illustrative annual interest rate
- Loan term

The first release supports principal-and-interest repayment only. User terms remain editable, but the engine constrains leverage to the researched destination limit. The page never labels illustrative terms as a lender offer.

If the user selects **Not sure**, results show an all-cash requirement and, only where research supports a standard route, a clearly labeled illustrative mortgage case.

### 4. Reliable retirement income

- Pension
- Other dependable after-tax income
- Net income from a separate rental property
- Inflation-linked or fixed treatment for each income source

Portfolio dividends and interest remain part of the expected portfolio return and cannot be entered again as outside income.

### 5. Essential preferences

Use no more than four preference questions:

- Preferred regions
- Climate
- Healthcare importance
- One existing lifestyle or access dimension supported consistently across the destination data

Preferences rank financially comparable destinations; they never conceal a funding gap or override buyer-access restrictions.

### 6. Projection and recommendations

The first result summary shows:

- Total capital available today
- Monthly portfolio contribution
- Number of destinations within reach

For rent and buy-at-retirement scenarios, one animated chart shows the shared portfolio projection by year. Hover and keyboard focus expose the year, contributions, and investment growth.

For buy-now scenarios, the projected portfolio differs by destination because purchase prices, leverage, and property cash flows differ. The page must not display one misleading universal projection. Each recommendation instead includes its destination-specific retirement portfolio and property equity.

## Destination Mortgage Evidence

Mortgage access is researched data, not a user assumption. Each destination receives a structured financing profile. Country-level evidence may be inherited by destinations, with destination overrides where local practice or property type differs.

Required fields:

- Availability: `likely_available`, `conditional`, `no_standard_nonresident_route`, or `research_incomplete`
- Eligible residency and income profiles
- Documented nationality restrictions, if any
- Typical or documented maximum loan-to-value range
- Minimum purchase or loan size, if applicable
- Supported property types and intended uses
- Loan currencies
- Local bank-account, income-history, or banking-relationship requirements
- Maximum borrower age or maturity constraint, if documented
- Short plain-language conditions
- Primary source URLs
- Evidence date
- Confidence level

The presentation labels these states as:

- **Likely available**
- **Available with conditions**
- **No standard non-resident route identified**
- **Research incomplete**

Every result says eligibility is indicative and must be verified with lenders. No destination is presented as guaranteed financing.

When mortgage funding is selected:

- Match the user profile against the destination financing profile.
- Cap leverage at the destination's supported maximum.
- If the desired leverage is higher, recalculate with the supported maximum and disclose the larger cash requirement.
- Mark unmet conditional requirements explicitly.
- Do not recommend a mortgage-funded purchase where no standard route is identified or research is incomplete; show the all-cash requirement instead.

## Buy-Now Property and Mortgage Model

Calculations run monthly from today to retirement for every eligible destination.

### Purchase allocation

For destination `d`:

1. Obtain today's representative property price and acquisition costs from the shared destination data.
2. Determine the permitted mortgage principal from the lower of user-requested and destination-supported leverage.
3. Calculate cash required as down payment plus acquisition costs.
4. Reject the financed scenario when the property exceeds the user's maximum property allocation or cash required exceeds total liquid capital.
5. Set starting portfolio to total liquid capital less cash required.

The interface displays the identity:

`total capital today = property cash required + starting portfolio`

### Mortgage amortization

Use standard monthly principal-and-interest amortization from the entered rate and term. Track payment, interest, principal, and remaining balance each month. If age-at-maturity exceeds a researched lender constraint, classify the mortgage route as conditional or unavailable rather than silently shortening the term.

### Pre-retirement use

For **personal/occasional use**:

- Rental income is zero.
- Ownership, maintenance, insurance, and other modeled running costs reduce monthly investable cash flow.

For **rent out until retirement**:

- Prefill gross rental yield from destination research and keep it editable.
- Apply editable vacancy, management, and operating-cost assumptions.
- Calculate gross rent, operating costs, mortgage payment, and net property cash flow separately.
- Add positive net property cash flow to monthly portfolio contributions.
- Subtract negative net property cash flow from monthly portfolio contributions.
- Allow net contributions to become negative; draw the shortfall from the portfolio and flag the scenario if the portfolio is exhausted before retirement.

### Property value and equity

Project property value using the shared property-inflation assumption, which remains editable. At retirement:

`property equity = projected property value - remaining mortgage balance`

Show property equity separately from the liquid portfolio. Do not use it to fund retirement spending unless the user explicitly selects a sale, which is outside this release.

### Mortgage treatment at retirement

- **Pay off at retirement:** deduct the remaining mortgage balance from the liquid portfolio and set retirement mortgage debt to zero.
- **Continue repayments:** include the scheduled mortgage payments as finite retirement cash flows until the loan ends. Do not treat them as a perpetual inflation-linked living expense.

The default is pay off at retirement because it is clearer and more conservative for destination comparison.

## Recommendation Calculation

For each destination with complete cost data:

1. Validate foreign-buyer property and mortgage access for the selected housing plan.
2. Project the destination-specific liquid portfolio and, when relevant, property equity and debt.
3. Calculate the destination retirement target using the shared retirement cash-flow engine, household, housing plan, reliable income, reserve, inflation, and return assumptions.
4. Compare liquid retirement resources with the liquid retirement target. Property equity is reported separately.
5. Classify financial feasibility:
   - **Within reach:** at least 100% funded
   - **Close:** 85% to less than 100% funded
   - **Stretch:** below 85% funded
6. Rank within each tier by preference fit, evidence completeness, and existing buyer-access rules.

The engine evaluates every destination available at runtime. Restricted or incomplete destinations remain visible only when the explanation helps the user understand why they are not recommended.

## Results Presentation

Avoid cards filled with repeated prose. Use a concise ranked list or table that remains readable on mobile.

Each destination result contains only distinct information:

- Destination
- Within reach, close, or stretch
- Projected liquid portfolio at retirement
- Retirement target
- Surplus or gap
- Property equity and mortgage remaining, when relevant
- Net rental cash flow, when relevant
- Two strongest preference matches
- Financing status and the most important condition, when relevant
- **Build a detailed plan** action

The action opens `/retirement-abroad-calculator/` with only the destination and non-sensitive categorical choices encoded in the URL. The destination-first page validates all incoming values before use. URLs must not contain passport country, precise income, capital, property budget, mortgage terms, or calculated results. Users re-enter sensitive financial values in the detailed planner rather than having them copied through storage or URLs.

The detailed result view provides mortgage evidence sources, dates, confidence, full cash-flow breakdown, and methodology without repeating the summary.

## Architecture

Keep responsibilities isolated:

- `src/retirement_calculator.js` continues to own pure retirement cash-flow and target calculations.
- Add a pure mortgage and property-cash-flow module for amortization, rental operations, equity, and buy-now allocation.
- Add a pure destination recommendation module that combines retirement projections, financing eligibility, and preference ranking.
- The new page UI module owns progressive disclosure, validation messages, chart interaction, and rendering only.
- `src/build_unified_app.py` generates the new route, embeds the complete current destination universe, adds navigation and internal links, and includes indexable explanatory content.
- Add structured mortgage profiles in a dedicated data file with schema validation, evidence dates, and sources.

The pure modules must work in both Node-based tests and the browser. UI code must not duplicate financial formulas.

## Validation and Failure Handling

- Reject retirement ages that do not exceed current age.
- Reject negative capital, contribution, price, rate, term, rent, or cost inputs where negative values are not meaningful.
- Prevent down payment plus acquisition costs from exceeding total liquid capital without an explicit infeasible result.
- Flag a portfolio exhausted before retirement rather than flooring it silently.
- Flag a mortgage extending beyond a researched age-at-maturity constraint.
- Distinguish missing financing research from a documented absence of financing.
- Fall back to the all-cash requirement when a financed recommendation cannot be supported.
- Never infer zero rent, zero operating costs, or unlimited leverage from missing data.
- Keep the last valid result visible when a non-financial UI interaction fails; show a concise actionable error near the affected field.

## Privacy and Analytics

All calculations run locally. Do not use `fetch`, `XMLHttpRequest`, local storage, session storage, cookies, or query parameters for financial and eligibility values.

Analytics may record only categorical engagement events such as:

- Discovery calculator opened
- Housing plan selected
- Mortgage section opened
- Calculation completed
- Result tier viewed
- Detailed destination plan opened

Events must not include capital, income, contribution, property budget, passport, residence, mortgage terms, destination eligibility details, or calculated results.

## SEO and Content

The new page targets destination-discovery intent rather than duplicating the existing calculator's destination-planning intent. Its title and introduction explain that it projects current savings and contributions before comparing destinations. Add contextual links from the homepage retirement path, retirement cost ranking, relevant guides, and the existing calculator.

Keep the indexable explanation concise. Detailed methodology and mortgage evidence belong behind clear links or disclosures after the results.

## Testing

### Pure calculation tests

- Monthly portfolio compounding and inflation-adjusted contributions
- Cash purchase allocation without double counting
- Mortgage payment and amortization schedule
- Destination loan-to-value cap overriding unsupported user leverage
- Rental gross income, vacancy, operating costs, and net cash flow
- Positive and negative rental cash flow affecting portfolio contributions
- Portfolio exhaustion before retirement
- Property value and equity at retirement
- Mortgage payoff versus continued repayments
- No use of property equity as liquid retirement funding
- Funding-tier boundaries at 85% and 100%

### Data tests

- Every financing profile conforms to the schema
- Enum values, dates, confidence, and source URLs are valid
- Inherited country evidence resolves deterministically
- Missing research is not treated as unavailable financing
- Destination universe is derived dynamically

### UI and generated-page tests

- Separate URLs and reciprocal mode links
- Progressive fields for each housing and use case
- Keyboard-accessible animated chart and tooltips
- Concise recommendation result contract
- Mobile reading order
- Safe detailed-plan handoff
- No sensitive analytics payloads, storage, network requests, or query parameters
- No hardcoded destination count

### Cross-calculator parity tests

For identical destination, household, housing, income, inflation, and return assumptions, the discovery page and destination-first calculator must produce the same retirement target. Buy-now property and mortgage outputs must also match once the detailed planner gains the shared property-financing module.

## Rollout

1. Add and validate mortgage evidence for a representative set of destinations covering likely, conditional, unavailable, and incomplete states.
2. Build the shared property-financing and recommendation modules with parity tests.
3. Build the discovery page behind an unlinked production route for internal QA.
4. Complete financing profiles for the full current destination universe before recommending mortgage-funded purchases broadly.
5. Add internal links and engagement analytics.
6. Compare discovery-calculator completion and detailed-plan click-through with the existing destination-first journey before considering any homepage emphasis change.
