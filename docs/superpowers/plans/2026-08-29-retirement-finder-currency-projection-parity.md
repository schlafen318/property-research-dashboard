# Retirement Finder Currency and Projection Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the retirement destination finder the detailed calculator's planning currencies, money-entry behavior, monthly retirement-income convention, selected-currency results, and projection visual language.

**Architecture:** Keep all calculation engines normalized to annual USD. Add the existing planning-currency dataset to the finder payload, implement matching pure conversion/formatting helpers in the finder UI with parity tests against the detailed calculator, and convert only at UI boundaries. Extend finder recommendations with the relevant annual projection, then render a total-portfolio SVG chart with the closest destination's target as its reference line.

**Tech Stack:** Python static-page builders, vanilla JavaScript UMD modules, HTML/CSS/SVG, Python `unittest`, Node.js subprocess tests.

**Spec:** `docs/superpowers/specs/2026-08-29-retirement-finder-currency-projection-parity-design.md`

## Global Constraints

- USD remains the normalized engine currency and the default presentation currency.
- Supported currencies are USD, EUR, GBP, CAD, AUD, CHF, JPY, HKD, and SGD in that order.
- No live exchange-rate fetching, financial-value persistence, financial-value analytics, or financial values in URLs.
- Retirement-income controls are monthly in the UI and annual USD in engine inputs.
- The already-own route continues to hand off to the destination-specific calculator.
- Do not add pills, badges, duplicated summaries, repeated currency labels, or an annual/monthly toggle.
- Every production behavior change must be preceded by a failing automated test.

---

### Task 1: Finder payload and currency-aware form markup

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `src/retirement_destination_finder_page.py`
- Test: `tests/test_retirement_destination_finder_page.py`

**Interfaces:**
- Consumes: `RETIREMENT_PLANNING_CURRENCIES` from `src/build_unified_app.py`.
- Produces: `payload.planning_currencies`, `select#finder-currency`, and money controls marked with `data-money`.

- [ ] **Step 1: Write failing payload and form tests**

Add tests that parse the embedded finder payload and assert:

```python
payload = json.loads(
    self.html.split('<script id="retirement-finder-data" type="application/json">', 1)[1]
    .split("</script>", 1)[0]
)
self.assertEqual("2026-08-27", payload["planning_currencies"]["as_of"])
self.assertEqual(
    ["USD", "EUR", "GBP", "CAD", "AUD", "CHF", "JPY", "HKD", "SGD"],
    list(payload["planning_currencies"]["rates_to_usd"]),
)
```

Assert that `finder-currency` defaults to USD, includes SGD, and that the five monetary controls use `type="text" inputmode="numeric" data-money`. Assert labels contain no `(USD)`. Assert Step 3 reads `Income continuing after retirement (monthly)` and both indexed checkboxes are checked.

- [ ] **Step 2: Run the page tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_retirement_destination_finder_page
```

Expected: failures because the finder payload has no planning currencies, the selector is absent, and money fields still use number inputs with USD labels.

- [ ] **Step 3: Add the currency payload and form markup**

In `build_retirement_destination_finder_page`, add:

```python
"planning_currencies": RETIREMENT_PLANNING_CURRENCIES,
```

In the page template, add the same ordered currency options and reference-rate note as the detailed calculator. Convert these IDs to formatted money controls while retaining their existing `min` and `step` values:

```text
finder-liquid-capital
finder-monthly-contribution
finder-property-allocation
finder-pension
finder-other-income
```

Use initial strings `500,000`, `2,000`, `300,000`, `0`, and `0`. Rename Step 3 and check both inflation-linked checkboxes.

- [ ] **Step 4: Run the page tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_retirement_destination_finder_page
```

Expected: all finder page tests pass.

- [ ] **Step 5: Commit Task 1**

```bash
git add src/build_unified_app.py src/retirement_destination_finder_page.py tests/test_retirement_destination_finder_page.py
git commit -m "Add finder planning currency controls"
```

---

### Task 2: Money parsing, formatting, conversion, and USD engine boundary

**Files:**
- Modify: `src/retirement_destination_finder_ui.js`
- Test: `tests/test_retirement_destination_finder_ui.py`

**Interfaces:**
- Consumes: `payload.planning_currencies.rates_to_usd` and money controls from Task 1.
- Produces: pure exports `convertPlanningAmount`, `convertPlanningControlAmount`, `parseMoneyInput`, `formatMoneyInputValue`, and `formatPlanningMoney`; `collectUser()` returns USD-normalized amounts.

- [ ] **Step 1: Write failing parity tests**

Load both `src/retirement_destination_finder_ui.js` and `src/retirement_calculator_ui.js` through Node. For each function below, assert identical finder and calculator output for the same inputs:

```python
conversion = {
    "amount": 24000,
    "fromCurrency": "USD",
    "toCurrency": "SGD",
    "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
}
```

Cover:

- `convertPlanningAmount(conversion)`;
- `convertPlanningControlAmount({**conversion, "step": 100})`;
- `parseMoneyInput("2,000,000")`;
- `formatMoneyInputValue(2000000)`;
- `formatPlanningMoney({"amountUsd": 1000, "currency": "SGD", "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891}})`.

Add invalid-input assertions for `"36,3x9"`, `None`, and a missing exchange rate.

- [ ] **Step 2: Run the parity tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_retirement_destination_finder_ui
```

Expected: failures because the finder UI exports none of the currency or money helpers.

- [ ] **Step 3: Implement the matching pure helpers**

Port the detailed calculator's conversion and money functions without changing their contracts. Replace the fixed USD formatter with a selected-currency formatter created through `formatPlanningMoney`.

Inside `initRetirementDestinationFinder`:

```javascript
const ratesToUsd = payload.planning_currencies.rates_to_usd;
let selectedCurrency = "USD";
```

Add `moneyNumber(id)` that parses the displayed amount and converts it from `selectedCurrency` to USD. Use it for all five monetary fields. In `incomeStreams()`, convert monthly selected-currency income to annual USD exactly once:

```javascript
amount: moneyNumber("finder-pension") * 12
```

- [ ] **Step 4: Write failing currency-change and validation tests**

Add pure coverage for step-aware conversion and source assertions that the finder:

- formats money controls initially and on blur;
- converts populated money controls when `finder-currency` changes;
- skips empty or invalid controls;
- marks invalid money controls with `aria-invalid`;
- never sends money values in tracking calls, storage, URLs, or requests.

Run the UI tests and confirm the new assertions fail before adding event wiring.

- [ ] **Step 5: Implement currency-change and money-control events**

Add a `moneyControlIds` allowlist. On currency change, convert each valid populated amount from the previous currency to the next currency using its `step`; leave empty or invalid text unchanged. Update `selectedCurrency` only after conversion. Add blur formatting and accessible validation matching the detailed calculator.

- [ ] **Step 6: Run focused UI tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_retirement_destination_finder_ui tests.test_retirement_destination_finder_page
```

Expected: all finder UI and page tests pass.

- [ ] **Step 7: Commit Task 2**

```bash
git add src/retirement_destination_finder_ui.js tests/test_retirement_destination_finder_ui.py
git commit -m "Add finder currency conversion and money formatting"
```

---

### Task 3: Selected-currency result rendering

**Files:**
- Modify: `src/retirement_destination_finder_ui.js`
- Test: `tests/test_retirement_destination_finder_ui.py`

**Interfaces:**
- Consumes: USD-normalized finder results and Task 2's `formatPlanningMoney`.
- Produces: `resultSummaryRead(input)` and `resultMoney(input)` that format all output in the selected currency.

- [ ] **Step 1: Write failing selected-currency result tests**

Update `resultSummaryRead` tests to pass `currency` and `ratesToUsd`, and expect the closest-match gap in SGD:

```python
self.assertIn(
    "SGD\u00a0409,882",
    run_ui("resultSummaryRead", {
        "withinReachCount": 0,
        "recommendations": [{"name": "Fukuoka / Itoshima", "surplusGap": -322418}],
        "currency": "SGD",
        "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
    }),
)
```

Add `resultMoney` tests for negative gaps, property equity, and JPY formatting. Add source assertions covering every monetary result ID and recommendation value.

- [ ] **Step 2: Run result tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_retirement_destination_finder_ui
```

Expected: failures because result functions still use the fixed USD formatter.

- [ ] **Step 3: Implement selected-currency output**

Create `resultMoney({amountUsd, currency, ratesToUsd})` as a narrow wrapper over `formatPlanningMoney`. Pass the current currency configuration into `resultSummaryRead`, chart tooltip creation, recommendation rows, and summary rendering. Re-render the latest result after a currency change without recalculating rankings.

- [ ] **Step 4: Verify ranking invariance**

Add a test that renders or formats the same recommendation array under USD and SGD and asserts destination IDs and tiers remain identical while displayed money changes.

- [ ] **Step 5: Run focused tests and verify GREEN**

```bash
python3 -m unittest tests.test_retirement_destination_finder_ui tests.test_retirement_destination_finder
```

Expected: all finder UI and engine tests pass.

- [ ] **Step 6: Commit Task 3**

```bash
git add src/retirement_destination_finder_ui.js tests/test_retirement_destination_finder_ui.py
git commit -m "Format finder results in planning currency"
```

---

### Task 4: Projection data for every calculable housing plan

**Files:**
- Modify: `src/retirement_destination_finder.js`
- Test: `tests/test_retirement_destination_finder.py`

**Interfaces:**
- Consumes: `sharedProjection.annualProjection` and `propertyResult.annualProjection`.
- Produces: each recommendation includes `annualProjection: Array<{year: number, portfolio: number}>`.

- [ ] **Step 1: Write failing projection-selection tests**

For a rent scenario, assert every recommendation receives the shared projection. For a buy-now scenario with at least two eligible destinations, assert each recommendation receives its own property-finance projection and that the final point equals `portfolioAtRetirement`.

Use exact assertions:

```python
self.assertEqual(
    item["portfolioAtRetirement"],
    item["annualProjection"][-1]["portfolio"],
)
```

- [ ] **Step 2: Run finder engine tests and verify RED**

```bash
python3 -m unittest tests.test_retirement_destination_finder
```

Expected: failure because recommendations do not include `annualProjection`.

- [ ] **Step 3: Add recommendation projection data**

Initialize `annualProjection` from `sharedProjection.annualProjection` for rent and buy-at-retirement. In buy-now evaluation, replace it with `propertyResult.annualProjection`. Add the array to the recommendation object without changing sort keys, targets, ratios, or tiers.

- [ ] **Step 4: Run engine tests and verify GREEN**

```bash
python3 -m unittest tests.test_retirement_destination_finder
```

Expected: all finder engine tests pass.

- [ ] **Step 5: Commit Task 4**

```bash
git add src/retirement_destination_finder.js tests/test_retirement_destination_finder.py
git commit -m "Expose finder recommendation projections"
```

---

### Task 5: SVG projection parity and accessible interactions

**Files:**
- Modify: `src/retirement_destination_finder_page.py`
- Modify: `src/retirement_destination_finder_ui.js`
- Modify: `src/site_design_system.py`
- Test: `tests/test_retirement_destination_finder_page.py`
- Test: `tests/test_retirement_destination_finder_ui.py`

**Interfaces:**
- Consumes: recommendation `annualProjection`, `retirementTarget`, name, selected currency, current age.
- Produces: `finderProjectionModel(input)`, `finderProjectionTooltip(input)`, and an accessible SVG chart.

- [ ] **Step 1: Write failing projection-model tests**

Define the desired pure API:

```javascript
finderProjectionModel({
  series: [{year: 0, portfolio: 500000}, {year: 1, portfolio: 540000}],
  targetValue: 700000
})
```

Assert the model returns a positive maximum, a bounded target Y coordinate, and bar heights scaled to the maximum of the series and target. Add a tooltip test that expects `Year 7 · age 57`, selected-currency money, and a complete accessible label.

- [ ] **Step 2: Run UI tests and verify RED**

```bash
python3 -m unittest tests.test_retirement_destination_finder_ui
```

Expected: failures because the model and tooltip functions do not exist.

- [ ] **Step 3: Replace projection markup with SVG**

Replace the button-bar container with:

```html
<figure class="finder-projection-wrap" id="finder-projection-wrap" hidden>
  <h3 id="finder-projection-heading">Projected portfolio by year</h3>
  <div class="finder-chart-tooltip" id="finder-chart-tooltip" role="status" hidden>
    <strong id="finder-tooltip-heading"></strong>
    <span id="finder-tooltip-value"></span>
  </div>
  <svg class="finder-projection-chart" id="finder-projection" role="img"
       aria-labelledby="finder-projection-title finder-projection-desc" viewBox="0 0 640 288">
    <title id="finder-projection-title">Projected retirement portfolio</title>
    <desc id="finder-projection-desc">Complete the finder to see annual progression.</desc>
    <line class="finder-chart-target" id="finder-chart-target" x1="22" x2="618"></line>
    <text class="finder-chart-target-label" id="finder-chart-target-label" x="618" text-anchor="end"></text>
    <g id="finder-projection-bars"></g>
  </svg>
  <figcaption class="hint" id="finder-projection-caption"></figcaption>
</figure>
```

- [ ] **Step 4: Implement projection model and rendering**

Use the closest recommendation after sorting. For buy-now, set the heading to `Projection for [destination]`; otherwise retain `Projected portfolio by year`. Render SVG groups with focusable bars, sparse year labels, target line, selected-currency target text, tooltip events, and reduced-motion-safe styling. Hide the figure when recommendations or projection points are absent.

- [ ] **Step 5: Write and run page accessibility/style tests**

Assert the SVG has title/description linkage, target elements, tooltip status, figcaption, and no obsolete `.finder-projection-bars` flex-bar CSS. Assert the design CSS uses the detailed calculator's chart colors and regular-weight disclosure summaries.

Run:

```bash
python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui
```

Expected: all projection, page, and UI tests pass.

- [ ] **Step 6: Commit Task 5**

```bash
git add src/retirement_destination_finder_page.py src/retirement_destination_finder_ui.js src/site_design_system.py tests/test_retirement_destination_finder_page.py tests/test_retirement_destination_finder_ui.py
git commit -m "Standardize finder projection display"
```

---

### Task 6: End-to-end verification and quality gate

**Files:**
- Modify only if a failing verification exposes a defect in an already-scoped file.

**Interfaces:**
- Consumes: the completed finder page, UI, engine, and build pipeline.
- Produces: verified static artifacts and review-ready commits; generated artifacts remain uncommitted unless repository policy explicitly requires them.

- [ ] **Step 1: Run all focused calculator tests**

```bash
python3 -m unittest \
  tests.test_retirement_destination_finder \
  tests.test_retirement_destination_finder_ui \
  tests.test_retirement_destination_finder_page \
  tests.test_retirement_calculator_ui \
  tests.test_retirement_calculator_page
```

Expected: all focused tests pass.

- [ ] **Step 2: Rebuild the site**

```bash
python3 src/build_unified_app.py
```

Expected: the unified dashboard path is printed and the finder artifact contains the currency selector, comma-formatted defaults, monthly retirement income, and SVG projection.

- [ ] **Step 3: Run the full suite and diff checks**

```bash
python3 -m unittest discover -s tests
git diff --check
```

Expected: the full suite passes and the diff check prints nothing.

- [ ] **Step 4: Verify locally in a browser**

At desktop and 608-pixel mobile widths, verify:

1. USD loads by default with formatted values.
2. Switching to SGD converts all populated money fields once.
3. Entering invalid money text produces an accessible error without becoming zero.
4. Pension and other dependable income are monthly and inflation-linked by default.
5. Results and recommendation rows use SGD without changing order or tiers.
6. The SVG chart uses SGD in its target and tooltip.
7. Buy-now labels the closest destination-specific projection.
8. Keyboard focus reveals the complete chart tooltip.

- [ ] **Step 5: Request independent code review**

Provide the reviewer with the spec, commit range, focused/full test evidence, and the exact acceptance criteria. Resolve every Critical or Important finding, then repeat focused and full verification.

- [ ] **Step 6: Prepare integration choice**

Confirm the branch contains only scoped source, tests, spec, and plan commits. Present merge-local, push/PR, or keep-branch options to the user.
