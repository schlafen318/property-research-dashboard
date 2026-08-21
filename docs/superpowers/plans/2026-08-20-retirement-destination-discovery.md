# Retirement Destination Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a second retirement calculator that projects a user's current resources, models rent or destination-specific property financing, and recommends financially plausible destinations from the complete live universe.

**Architecture:** Add pure CommonJS/browser modules for property finance and destination recommendation while keeping retirement targets in `retirement_calculator.js`. Generate a separate static route with its own UI module, using structured country mortgage profiles with destination overrides and the existing retirement-cost dataset.

**Tech Stack:** Python 3.11 static-site generator and `unittest`, vanilla JavaScript tested through Node, JSON data, semantic HTML/CSS, GA4 categorical events.

**Spec:** `docs/superpowers/specs/2026-08-20-retirement-destination-discovery-design.md`

## Global Constraints

- Evaluate the complete destination universe at runtime; never hardcode its count or membership.
- Keep all personal, eligibility, and financial values in the browser and out of analytics, storage, network requests, and URLs.
- Property equity is reported separately and never treated as liquid retirement funding.
- Mortgage availability is indicative researched evidence, never approval or advice.
- Missing financing research differs from a documented absence of a standard route.
- Keep the page top-down, human-readable, and free of decorative pills, duplicated summaries, and opaque scores.
- Use only principal-and-interest mortgages in this release.

---

### Task 1: Structured Mortgage Evidence

**Files:**
- Create: `data/mortgage_profiles.json`
- Create: `tests/test_mortgage_profiles.py`
- Modify: `src/build_unified_app.py`

**Interfaces:**
- Produces: `load_mortgage_profiles() -> dict` with `as_of`, `default_buyer_profile`, `countries`, and `destination_overrides`.
- Produces: `resolve_mortgage_profile(destination: dict, payload: dict) -> dict` returning a copied country profile merged with any destination override.
- Consumes: destination `country` and `id` from `data/destinations.json`.

- [ ] **Step 1: Write failing schema and coverage tests**

Add tests that load every destination and assert its country resolves to one of `likely_available`, `conditional`, `no_standard_nonresident_route`, or `research_incomplete`; validate ISO dates, confidence, source HTTPS URLs, LTV bounds from 0 to 1, and non-empty conditions for conditional profiles.

```python
def test_every_destination_resolves_to_a_financing_profile(self):
    for destination in self.destinations:
        profile = build.resolve_mortgage_profile(destination, self.payload)
        self.assertIn(profile["availability"], self.ALLOWED_AVAILABILITY)
        self.assertTrue(profile["sources"] or profile["availability"] == "research_incomplete")
```

- [ ] **Step 2: Run the focused test and confirm the missing loader failure**

Run: `python3 -m unittest tests.test_mortgage_profiles -v`  
Expected: FAIL because the data file and loader do not exist.

- [ ] **Step 3: Add the loader, resolver, and researched country profiles**

Create one profile for every country represented in the current retirement-cost universe. Store availability, supported buyer profiles, maximum LTV, minimum size where documented, use restrictions, maturity age where documented, currency, conditions, sources, evidence date, and confidence. Use `research_incomplete` rather than inference when authoritative evidence is insufficient.

- [ ] **Step 4: Run data tests**

Run: `python3 -m unittest tests.test_mortgage_profiles -v`  
Expected: PASS.

- [ ] **Step 5: Commit the evidence foundation**

```bash
git add data/mortgage_profiles.json src/build_unified_app.py tests/test_mortgage_profiles.py
git commit -m "feat: add destination mortgage evidence"
```

### Task 2: Property Finance Engine

**Files:**
- Create: `src/property_finance.js`
- Create: `tests/test_property_finance_engine.py`

**Interfaces:**
- Produces: `monthlyMortgagePayment({principal, annualRate, termMonths}) -> number`.
- Produces: `amortizeMortgage(input) -> {monthlyPayment, remainingBalance, interestPaid, principalPaid}`.
- Produces: `evaluateBuyNow(input) -> {supported, reasons, cashRequiredToday, startingPortfolio, effectiveLtv, annualProjection, portfolioAtRetirement, propertyValueAtRetirement, mortgageBalanceAtRetirement, propertyEquityAtRetirement, netRentalCashFlowAtRetirement}`.
- Consumes: normalized mortgage profile from Task 1 and portfolio-return, inflation, property, rental, and user-allocation inputs.

- [ ] **Step 1: Write failing Node-backed tests**

Cover zero-rate amortization, standard amortization, destination LTV caps, acquisition-cost allocation, cash exceeding total capital, positive and negative rental cash flow, personal use, portfolio exhaustion, property appreciation, payoff at retirement, and continued debt.

```python
def test_supported_ltv_caps_user_request(self):
    result = run_engine("evaluateBuyNow", buy_now_payload(requestedLtv=.8, maximumLtv=.6))
    self.assertEqual(.6, result["effectiveLtv"])
    self.assertAlmostEqual(208000, result["cashRequiredToday"], places=2)
```

- [ ] **Step 2: Run the focused tests and confirm the missing module failure**

Run: `python3 -m unittest tests.test_property_finance_engine -v`  
Expected: FAIL because `src/property_finance.js` does not exist.

- [ ] **Step 3: Implement validation and mortgage amortization**

Use monthly effective portfolio return `Math.pow(1 + annualReturn, 1 / 12) - 1`. Use standard principal-and-interest payment math, with `principal / termMonths` at zero interest. Reject non-finite values and unsupported ranges with field-specific errors.

- [ ] **Step 4: Implement property allocation and monthly projection**

Set `cashRequiredToday = downPayment + acquisitionCosts`, `startingPortfolio = totalLiquidCapital - cashRequiredToday`, and monthly net contribution to user contribution plus rent after vacancy and operating costs less debt service. Allow negative contribution to draw down the portfolio; record the first exhaustion month instead of flooring silently.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m unittest tests.test_property_finance_engine -v`  
Expected: PASS.

- [ ] **Step 6: Commit the pure engine**

```bash
git add src/property_finance.js tests/test_property_finance_engine.py
git commit -m "feat: model property financing and rental cash flow"
```

### Task 3: Destination Recommendation Engine

**Files:**
- Create: `src/retirement_destination_finder.js`
- Create: `tests/test_retirement_destination_finder.py`
- Modify: `src/retirement_calculator.js`
- Modify: `tests/test_retirement_calculator_engine.py`

**Interfaces:**
- Produces from `retirement_calculator.js`: `calculateRetirementTarget(input) -> existing calculateRetirement result` as an alias preserving current API compatibility.
- Produces: `projectPortfolio(input) -> {annualProjection, portfolioAtRetirement, exhaustedMonth}` for rent and buy-at-retirement scenarios.
- Produces: `recommendDestinations({user, destinations, retirementCosts, mortgageProfiles}) -> {summary, recommendations, excluded}`.
- Recommendation item fields: `destinationId`, `name`, `tier`, `fundingRatio`, `portfolioAtRetirement`, `retirementTarget`, `surplusGap`, `propertyEquity`, `mortgageBalance`, `netRentalCashFlow`, `financingStatus`, `financingReason`, `preferenceMatches`, and `detailHref`.

- [ ] **Step 1: Write failing target-parity and ranking tests**

Assert the discovery engine returns the same target as `calculateRetirement` for identical destination assumptions; thresholds are `within_reach >= 1`, `close >= .85`, and `stretch < .85`; incomplete financing cannot produce a mortgage-funded recommendation; preference fit only sorts inside a financial tier; and all input destinations are evaluated.

```python
def test_preference_cannot_promote_stretch_above_within_reach(self):
    result = recommend(payload_with_affordable_and_preferred_stretch())
    self.assertEqual("within_reach", result["recommendations"][0]["tier"])
```

- [ ] **Step 2: Run focused tests and confirm failure**

Run: `python3 -m unittest tests.test_retirement_destination_finder tests.test_retirement_calculator_engine -v`  
Expected: FAIL because the finder module and target alias do not exist.

- [ ] **Step 3: Add the target alias and shared portfolio projection**

Keep `calculateRetirement` unchanged for current callers. Export the alias and implement monthly accumulation with inflation-adjusted contributions in the finder module.

- [ ] **Step 4: Implement per-destination evaluation and deterministic ranking**

Build destination expense categories from retirement-cost profiles, route buy-now scenarios through `evaluateBuyNow`, calculate liquid funding ratios, classify tiers, and sort by tier, preference match count, evidence completeness, existing buyer access, then destination name. Property equity must not enter the funding ratio.

- [ ] **Step 5: Run focused tests**

Run: `python3 -m unittest tests.test_retirement_destination_finder tests.test_retirement_calculator_engine -v`  
Expected: PASS.

- [ ] **Step 6: Commit recommendation logic**

```bash
git add src/retirement_calculator.js src/retirement_destination_finder.js tests/test_retirement_calculator_engine.py tests/test_retirement_destination_finder.py
git commit -m "feat: recommend fundable retirement destinations"
```

### Task 4: Discovery Page and Progressive Form

**Files:**
- Create: `src/retirement_destination_finder_ui.js`
- Create: `tests/test_retirement_destination_finder_ui.py`
- Create: `tests/test_retirement_destination_finder_page.py`
- Modify: `src/build_unified_app.py`
- Generate: `artifacts/retirement-destination-finder/index.html`

**Interfaces:**
- Consumes: `GHARetirementDestinationFinder.recommendDestinations(...)`, embedded retirement costs, destinations, and resolved mortgage profiles.
- Produces: `initRetirementDestinationFinder(rootId, payload)`.
- Route: `/retirement-destination-finder/`.

- [ ] **Step 1: Write failing generated-page contract tests**

Assert the route has reciprocal text links with the existing calculator, top-down field order, four housing-plan choices, conditional buy-now/mortgage/rental fields, result summary, accessible chart region, recommendation list, evidence disclosure, methodology, canonical URL, and no hardcoded destination count.

- [ ] **Step 2: Write failing pure UI-helper tests**

Test progressive visibility, safe non-sensitive handoff URL generation, tier labels, money formatting, and chart tooltip content. Scan the UI source for forbidden `fetch(`, `XMLHttpRequest`, `localStorage`, `sessionStorage`, and sensitive analytics keys.

- [ ] **Step 3: Run page and UI tests and confirm failure**

Run: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui -v`  
Expected: FAIL because the route and UI module do not exist.

- [ ] **Step 4: Generate minimal semantic page markup and styles**

Use one form column followed by results. Use fieldsets and native controls, plain text mode links, a three-number result summary, an SVG annual projection with focusable yearly points, and a compact results table/list that shows only the fields required by the spec.

- [ ] **Step 5: Implement UI behavior and categorical analytics**

Render only relevant nested fields. Validate near each field and in one error summary. Emit categorical events for open, housing-plan selection, mortgage-section open, completed calculation, viewed tier, and detailed-plan click; never attach entered or calculated values.

- [ ] **Step 6: Build and run focused tests**

Run: `python3 src/build_unified_app.py`  
Run: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui -v`  
Expected: PASS.

- [ ] **Step 7: Commit the page**

```bash
git add src/build_unified_app.py src/retirement_destination_finder_ui.js tests/test_retirement_destination_finder_page.py tests/test_retirement_destination_finder_ui.py artifacts/retirement-destination-finder artifacts/sitemap.xml
git commit -m "feat: add retirement destination discovery page"
```

### Task 5: Site Integration and Cross-Calculator Parity

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_retirement_calculator_page.py`
- Modify: `tests/test_static_guides.py`
- Modify: `docs/CHANGELOG.md`
- Generate: affected files under `artifacts/`

**Interfaces:**
- Existing calculator accepts only destination and non-sensitive categorical query parameters.
- Homepage retirement path, retirement ranking guide, relevant retirement guides, and both calculators link to the discovery route.

- [ ] **Step 1: Write failing integration tests**

Assert reciprocal links, sitemap inclusion, homepage and retirement-guide links, dynamic universe payload count, cross-calculator target parity, and rejection of financial query parameters.

- [ ] **Step 2: Run integration tests and confirm failure**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_static_guides -v`  
Expected: FAIL on missing integration links or handoff behavior.

- [ ] **Step 3: Add restrained internal links and safe handoff parsing**

Add one discovery link per relevant page context. Do not add badges, promotional panels, or repeated descriptions. Accept only allowlisted destination, household, and housing-plan values in the destination-first planner.

- [ ] **Step 4: Regenerate and run integration tests**

Run: `python3 src/build_unified_app.py`  
Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_static_guides -v`  
Expected: PASS.

- [ ] **Step 5: Commit integration**

```bash
git add src/build_unified_app.py tests/test_retirement_calculator_page.py tests/test_static_guides.py docs/CHANGELOG.md artifacts
git commit -m "feat: connect retirement planning journeys"
```

### Task 6: Full Verification and Human-Readable QA

**Files:**
- Modify only when verification exposes a defect: files from Tasks 1–5 and their tests.

**Interfaces:**
- Produces a clean, deployable static site on the feature branch.

- [ ] **Step 1: Run the complete build and test suite**

Run: `python3 src/build_unified_app.py`  
Run: `python3 -m unittest discover -s tests`  
Run: `git diff --check`  
Expected: all pass with no whitespace errors.

- [ ] **Step 2: Run the static-site verifier**

Run: `python3 scripts/verify_static_site.py`  
Expected: PASS with the new route linked, canonical, and included in the sitemap.

- [ ] **Step 3: Test representative browser scenarios**

Verify rent, buy at retirement, cash buy now, mortgaged rental, mortgaged personal use, unsupported financing, incomplete research, negative property cash flow, payoff at retirement, continued mortgage, mobile layout, keyboard chart tooltips, and detailed-plan handoff.

- [ ] **Step 4: Confirm privacy and dynamic coverage**

Inspect network activity and generated source to confirm no financial or eligibility values are transmitted or stored. Confirm the embedded destination count equals the live retirement-cost universe without a literal fixed count in page copy or JavaScript.

- [ ] **Step 5: Commit any verification corrections**

```bash
git add src data tests docs artifacts
git commit -m "fix: complete retirement destination finder verification"
```

