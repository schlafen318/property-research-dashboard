# Retirement Cash-Flow Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the personalized calculator's default withdrawal-rate method with an annual cash-flow present-value model driven by retirement spending, inflation, reliable income, horizon, and a required user-entered portfolio return.

**Architecture:** Keep all timing and discounting math in the pure `src/retirement_calculator.js` engine. Keep destination defaults, monthly scaling, conditional housing controls, and presentation in `src/retirement_calculator_ui.js`; generate accessible, indexable markup and methodology from `src/build_unified_app.py`.

**Tech Stack:** JavaScript browser/CommonJS modules, Python 3.11 static-site generator, Python `unittest`, Node.js module tests, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-08-18-retirement-cashflow-model-design.md`

## Global Constraints

- No default or override withdrawal-rate input in the personalized calculator.
- Expected annual portfolio return after fees is required, blank by default, and accepts -5% through 15%.
- The model is deterministic and must not claim a safe rate or probability of success.
- Do not persist, transmit, or add financial inputs or result values to analytics.
- Static destination tables retain their separately documented 3.5% comparison method.
- Buy-now property cost is today's USD and is never added to retirement-date capital.
- Buy-at-retirement property cost is retirement-date USD and may be combined with retirement-date capital.

---

### Task 1: Annual Cash-Flow Present-Value Engine

**Files:**
- Modify: `tests/test_retirement_calculator_engine.py:32-100`
- Modify: `src/retirement_calculator.js:8-109`

**Interfaces:**
- Consumes: `calculateRetirement(input)` with ages, horizon, expense categories, income streams, `expectedPortfolioReturn`, inflation, reserve, housing, and property fields.
- Produces: `annualFundingGaps`, `expectedPortfolioReturn`, `liquidPortfolio`, `retirementCapital`, `todayDollarRetirementCapital`, and `impliedFirstYearWithdrawal`.

- [ ] **Step 1: Replace the old engine fixture**

Remove `portfolioCashYield` and withdrawal override data. Add:

```python
def level_cash_flow_payload() -> dict:
    return {
        "currentAge": 59, "retirementAge": 60, "horizonYears": 3,
        "expenseCategories": [{"amount": 12000, "inflationRate": 0}],
        "incomeStreams": [{"amount": 2000, "indexed": False, "inflationRate": 0}],
        "housingPlan": "rent", "propertyPrice": 0, "propertyInflation": 0,
        "acquisitionCostRate": 0, "generalInflation": 0,
        "emergencyReserveMonths": 0, "expectedPortfolioReturn": 0,
    }
```

- [ ] **Step 2: Write failing present-value tests**

```python
def test_zero_return_sums_annual_funding_gaps(self) -> None:
    result = calculate(level_cash_flow_payload())
    self.assertEqual([10000, 10000, 10000], result["annualFundingGaps"])
    self.assertEqual(30000, result["liquidPortfolio"])
    self.assertEqual(30000, result["retirementCapital"])
    self.assertAlmostEqual(1 / 3, result["impliedFirstYearWithdrawal"], places=8)

def test_higher_return_reduces_required_capital(self) -> None:
    payload = level_cash_flow_payload()
    payload["expectedPortfolioReturn"] = 0.10
    result = calculate(payload)
    self.assertAlmostEqual(27355.371900826444, result["liquidPortfolio"], places=6)

def test_inflation_projects_every_retirement_year(self) -> None:
    payload = level_cash_flow_payload()
    payload.update({"horizonYears": 2, "expenseCategories": [{"amount": 12000, "inflationRate": 0.10}], "incomeStreams": []})
    result = calculate(payload)
    self.assertEqual([13200, 14520], result["annualFundingGaps"])
    self.assertEqual(27720, result["liquidPortfolio"])
```

- [ ] **Step 3: Verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_engine`

Expected: FAIL because the old engine has no expected-return input or annual gap series.

- [ ] **Step 4: Implement projection and discounting**

Add these helpers:

```javascript
function boundedExpectedReturn(value) {
  const rate = Number(value);
  if (!Number.isFinite(rate) || rate < -0.05 || rate > 0.15) {
    throw new Error("Expected portfolio return must be between -5% and 15%");
  }
  return rate;
}

function projectedExpenseTotal(categories, years) {
  return categories.reduce(function (total, category) {
    return total + project(finiteNonNegative(category.amount, "Expense amount"), boundedRate(category.inflationRate, "Expense inflation", 0.15), years);
  }, 0);
}

function projectedIncomeTotal(streams, years) {
  return streams.reduce(function (total, stream) {
    const amount = finiteNonNegative(stream.amount, "Income amount");
    const inflation = boundedRate(stream.inflationRate, "Income inflation", 0.15);
    return total + (stream.indexed ? project(amount, inflation, years) : amount);
  }, 0);
}
```

Replace the first-year withdrawal division with:

```javascript
const expectedPortfolioReturn = boundedExpectedReturn(input.expectedPortfolioReturn);
const annualFundingGaps = [];
let firstYearExpenses = 0;
let outsideIncome = 0;
for (let year = 0; year < horizonYears; year += 1) {
  const projectionYears = yearsToRetirement + year;
  const expenses = projectedExpenseTotal(input.expenseCategories, projectionYears);
  const income = projectedIncomeTotal(input.incomeStreams, projectionYears);
  if (year === 0) { firstYearExpenses = expenses; outsideIncome = income; }
  annualFundingGaps.push(Math.max(0, expenses - income));
}
const liquidPortfolio = annualFundingGaps.reduce(function (total, gap, year) {
  return total + gap / Math.pow(1 + expectedPortfolioReturn, year);
}, 0);
const fundingGap = annualFundingGaps[0] || 0;
const emergencyReserve = firstYearExpenses / 12 * emergencyReserveMonths;
const retirementCapital = liquidPortfolio + emergencyReserve;
const todayDollarRetirementCapital = retirementCapital / Math.pow(1 + generalInflation, yearsToRetirement);
const impliedFirstYearWithdrawal = liquidPortfolio > 0 ? fundingGap / liquidPortfolio : null;
```

Remove `guidedWithdrawalRate`, `withdrawalRateOverride`, `portfolioCashYield`, `portfolioCashIncome`, and `assetSales` from the personalized engine.

- [ ] **Step 5: Add income and validation tests**

```python
def test_fixed_and_indexed_income_follow_different_paths(self) -> None:
    payload = level_cash_flow_payload()
    payload.update({
        "horizonYears": 2,
        "expenseCategories": [{"amount": 10000, "inflationRate": 0}],
        "incomeStreams": [
            {"amount": 1000, "indexed": True, "inflationRate": 0.10},
            {"amount": 1000, "indexed": False, "inflationRate": 0.10},
        ],
    })
    result = calculate(payload)
    self.assertEqual([7900, 7790], result["annualFundingGaps"])
    self.assertEqual(15690, result["liquidPortfolio"])

def test_expected_return_is_required_and_bounded(self) -> None:
    for value in (None, -0.051, 0.151):
        payload = level_cash_flow_payload()
        payload["expectedPortfolioReturn"] = value
        with self.assertRaises(subprocess.CalledProcessError):
            calculate(payload)

def test_each_annual_gap_floors_at_zero_independently(self) -> None:
    payload = level_cash_flow_payload()
    payload.update({
        "horizonYears": 2,
        "expenseCategories": [{"amount": 10000, "inflationRate": 0.10}],
        "incomeStreams": [{"amount": 11500, "indexed": False, "inflationRate": 0}],
    })
    result = calculate(payload)
    self.assertEqual([0, 600], result["annualFundingGaps"])
    self.assertEqual(600, result["liquidPortfolio"])
```

- [ ] **Step 6: Verify GREEN and commit**

Run: `python3 -m unittest tests.test_retirement_calculator_engine`

```bash
git add src/retirement_calculator.js tests/test_retirement_calculator_engine.py
git commit -m "Replace withdrawal rule with retirement cash flows"
```

---

### Task 2: Property Timing for Four Housing Plans

**Files:**
- Modify: `tests/test_retirement_calculator_engine.py`
- Modify: `src/retirement_calculator.js`

**Interfaces:**
- Consumes: Task 1 engine and `rent`, `own`, `buy_now`, `buy_retirement`.
- Produces: `propertyCapital`, `propertyTiming: "none" | "today" | "retirement"`, and `combinedRetirementCapital: number | null`.

- [ ] **Step 1: Write failing timing tests**

```python
def test_buy_now_uses_today_price_without_mixing_dates(self) -> None:
    payload = level_cash_flow_payload()
    payload.update({"housingPlan": "buy_now", "propertyPrice": 500000, "propertyInflation": 0.10, "acquisitionCostRate": 0.10})
    result = calculate(payload)
    self.assertEqual(550000, result["propertyCapital"])
    self.assertEqual("today", result["propertyTiming"])
    self.assertIsNone(result["combinedRetirementCapital"])

def test_buy_at_retirement_projects_property(self) -> None:
    payload = level_cash_flow_payload()
    payload.update({"currentAge": 58, "retirementAge": 60, "housingPlan": "buy_retirement", "propertyPrice": 500000, "propertyInflation": 0.10, "acquisitionCostRate": 0.10})
    result = calculate(payload)
    self.assertAlmostEqual(665500, result["propertyCapital"], places=6)
    self.assertEqual("retirement", result["propertyTiming"])
    self.assertAlmostEqual(result["retirementCapital"] + 665500, result["combinedRetirementCapital"], places=6)
```

Also assert Rent and Already own return zero property capital, `propertyTiming == "none"`, and `combinedRetirementCapital == retirementCapital`.

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_engine`

Expected: FAIL because only the old `buy` value exists.

- [ ] **Step 3: Implement timing branches**

```javascript
const HOUSING_PLANS = new Set(["rent", "own", "buy_now", "buy_retirement"]);
let propertyCapital = 0;
let propertyTiming = "none";
let combinedRetirementCapital = retirementCapital;
if (input.housingPlan === "buy_now") {
  propertyCapital = propertyPrice * (1 + acquisitionCostRate);
  propertyTiming = "today";
  combinedRetirementCapital = null;
} else if (input.housingPlan === "buy_retirement") {
  propertyCapital = project(propertyPrice, propertyInflation, yearsToRetirement) * (1 + acquisitionCostRate);
  propertyTiming = "retirement";
  combinedRetirementCapital = retirementCapital + propertyCapital;
}
```

Return the three timing fields and list all four values in validation errors.

- [ ] **Step 4: Verify GREEN and commit**

Run: `python3 -m unittest tests.test_retirement_calculator_engine`

```bash
git add src/retirement_calculator.js tests/test_retirement_calculator_engine.py
git commit -m "Add buy-now property timing"
```

---

### Task 3: UI Data Flow and Result Timing

**Files:**
- Modify: `tests/test_retirement_calculator_ui.py`
- Modify: `src/retirement_calculator_ui.js`

**Interfaces:**
- Consumes: Task 2 engine inputs/results.
- Produces: `annualBenchmark`, `housingGuidance`, `usesPropertyBudget`, cash-flow `calculatorInput()`, and timing-aware `render(result)`.

- [ ] **Step 1: Write failing housing-helper tests**

```python
def test_owner_plans_use_owner_costs(self) -> None:
    profile = {"categories_usd": {"food": 20000, "healthcare": 5000}, "annual_rent_usd": 24000, "annual_owner_costs_usd": 8000}
    self.assertEqual(49000, run_ui("annualBenchmark", {"profile": profile, "plan": "rent"}))
    for plan in ("own", "buy_now", "buy_retirement"):
        self.assertEqual(33000, run_ui("annualBenchmark", {"profile": profile, "plan": plan}))

def test_only_purchase_plans_use_property_budget(self) -> None:
    self.assertFalse(run_ui("usesPropertyBudget", "rent"))
    self.assertFalse(run_ui("usesPropertyBudget", "own"))
    self.assertTrue(run_ui("usesPropertyBudget", "buy_now"))
    self.assertTrue(run_ui("usesPropertyBudget", "buy_retirement"))
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_ui`

Expected: FAIL because `usesPropertyBudget` and two buy values are absent.

- [ ] **Step 3: Implement housing and expected-return data flow**

```javascript
function usesPropertyBudget(plan) {
  return plan === "buy_now" || plan === "buy_retirement";
}
function housingGuidance(plan) {
  if (plan === "rent") return "Monthly retirement living expenses, including rent.";
  if (plan === "own") return "Monthly retirement living expenses, including owner running costs; no new home purchase.";
  if (plan === "buy_now") return "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase.";
  return "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase at retirement.";
}
```

Use `usesPropertyBudget(plan)` for visibility. Pass `expectedPortfolioReturn: rate("ret-expected-return")`. Remove withdrawal override, cash yield, preset yields, the portfolio-style listener, and `portfolio_style` analytics. Never track the return value.

- [ ] **Step 4: Render timing-aware results**

```javascript
const headline = result.propertyTiming === "retirement" ? result.combinedRetirementCapital : result.retirementCapital;
setMoney("ret-total-capital", headline);
setMoney("ret-liquid-portfolio", result.liquidPortfolio);
setMoney("ret-emergency-reserve", result.emergencyReserve);
setMoney("ret-property-capital", result.propertyCapital);
setMoney("ret-today-total", result.todayDollarRetirementCapital);
el("ret-result-return").textContent = (result.expectedPortfolioReturn * 100).toFixed(2).replace(/\.00$/, "") + "%";
el("ret-result-implied-withdrawal").textContent = result.impliedFirstYearWithdrawal === null ? "—" : (result.impliedFirstYearWithdrawal * 100).toFixed(2) + "%";
```

Use **Combined capital at retirement** only for retirement-timed property. Otherwise use **Retirement capital needed at retirement**. Label property as **Home purchase needed now**, **Home purchase at retirement**, or **No property purchase** based on `propertyTiming`.

Replace rate-sensitivity copy with a straight-line-return and sequence-risk warning.

- [ ] **Step 5: Verify GREEN and commit**

Run: `python3 -m unittest tests.test_retirement_calculator_ui`

```bash
git add src/retirement_calculator_ui.js tests/test_retirement_calculator_ui.py
git commit -m "Connect calculator UI to cash-flow model"
```

---

### Task 4: Form, Results, and Methodology

**Files:**
- Modify: `tests/test_retirement_calculator_page.py:59-158`
- Modify: `src/build_unified_app.py:3820-3905`
- Regenerate: `artifacts/retirement-abroad-calculator/index.html`

**Interfaces:**
- Consumes: Task 3 IDs `ret-expected-return`, `ret-result-return`, `ret-result-implied-withdrawal`, `ret-headline-label`, and `ret-property-label`.
- Produces: accessible HTML controls and indexable explanation.

- [ ] **Step 1: Write failing markup tests**

```python
def test_personalized_form_uses_cash_flow_inputs(self) -> None:
    form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
    self.assertIn("Monthly retirement living expenses (today's USD)", form)
    self.assertIn('<option value="buy_now">Buy now</option>', form)
    self.assertIn('<option value="buy_retirement" selected>Buy at retirement</option>', form)
    self.assertIn("Expected annual portfolio return after fees (%)", form)
    self.assertIn('id="ret-expected-return" type="number" min="-5" max="15" step="0.1" required', form)
    for removed in ("ret-withdrawal-rate", "ret-income-preset", "ret-cash-yield"):
        self.assertNotIn(f'id="{removed}"', form)

def test_results_remove_cash_yield_breakdown(self) -> None:
    results = self.html.split('id="ret-results"', 1)[1].split("</section>", 1)[0]
    for element_id in ("ret-headline-label", "ret-property-label", "ret-result-return", "ret-result-implied-withdrawal"):
        self.assertIn(f'id="{element_id}"', results)
    self.assertNotIn('id="ret-cash-income"', results)
    self.assertNotIn('id="ret-asset-sales"', results)
```

- [ ] **Step 2: Verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_page`

Expected: FAIL on the old withdrawal, style, yield, and housing contracts.

- [ ] **Step 3: Update form markup**

Use four housing options with `buy_retirement` selected. Rename spending to **Monthly retirement living expenses (today's USD)**. Remove the Portfolio income illustration fieldset. Add:

```html
<fieldset><legend>Portfolio assumption</legend>
  <label for="ret-expected-return">Expected annual portfolio return after fees (%)</label>
  <input id="ret-expected-return" type="number" min="-5" max="15" step="0.1" required>
  <p class="hint">Required. Enter your own straight-line return assumption; this is not a guaranteed return or probability-of-success estimate.</p>
</fieldset>
```

Remove withdrawal rate and cash yield from Advanced assumptions.

- [ ] **Step 4: Simplify result markup**

Add timing-aware label IDs, expected return, and implied first-year withdrawal. Retain liquid portfolio, reserve, today's-dollar retirement capital, first-year expenses, outside income, and first-year gap. Remove cash-income and asset-sale rows.

```html
<div><span id="ret-property-label">Home purchase</span><strong id="ret-property-capital">—</strong></div>
<div><span>Expected return after fees</span><strong id="ret-result-return">—</strong></div>
<div><span>Implied first-year withdrawal</span><strong id="ret-result-implied-withdrawal">—</strong></div>
```

- [ ] **Step 5: Rewrite methodology copy**

Explain annual expense/income projection, per-year gap floors, return discounting, zero ending liquid balance, and the lack of volatility, sequence-risk, tax, and bequest modeling. Preserve the static table's 3.5% method and add: **This standardized table is separate from the personalized cash-flow calculator above.**

- [ ] **Step 6: Build, verify GREEN, and commit**

Run: `python3 src/build_unified_app.py && python3 -m unittest tests.test_retirement_calculator_page`

```bash
git add src/build_unified_app.py tests/test_retirement_calculator_page.py artifacts/retirement-abroad-calculator/index.html
git commit -m "Update calculator for personalized cash flows"
```

---

### Task 5: Full Verification and Deployment

**Files:**
- Modify: `docs/CHANGELOG.md`
- Verify: `artifacts/retirement-abroad-calculator/index.html`

**Interfaces:**
- Consumes: Tasks 1-4.
- Produces: verified static site, merged pull request, and live evidence.

- [ ] **Step 1: Add a changelog entry**

Document annual cash-flow discounting, the required expected-return input, Buy now, separated property timing, and removed portfolio-style/withdrawal controls.

- [ ] **Step 2: Run complete verification**

```bash
python3 src/build_unified_app.py
python3 -m unittest discover -s tests
python3 scripts/verify_static_site.py
git diff --check
```

Expected: build exits 0, all tests pass, static verification passes, and the diff check is silent.

- [ ] **Step 3: Browser-test locally**

Run: `python3 -m http.server 8768 --directory artifacts`

Verify all four housing plans, destination reset, custom property budget preservation, required expected return, higher-return/lower-capital behavior, separate Buy-now timing, combined Buy-at-retirement timing, and no page-level overflow at desktop and 390px.

- [ ] **Step 4: Commit documentation**

```bash
git add docs/CHANGELOG.md
git commit -m "Document retirement cash-flow model"
```

- [ ] **Step 5: Publish**

```bash
git push -u origin codex/retirement-cashflow-model
gh pr create --base main --head codex/retirement-cashflow-model --title "Calculate retirement capital from annual cash flows" --body-file /tmp/retirement-cashflow-pr.md
gh pr merge --squash --delete-branch
```

The pull-request body must state the model change, housing timing, removed controls, deterministic-return limitation, test count, static verification, and browser scenarios.

- [ ] **Step 6: Monitor and verify production**

Use `gh run list` and `gh run watch <run-id> --exit-status`. On the cache-busted production URL verify: return is blank and required; Buy now and Buy at retirement use different timing; changing return changes liquid capital; removed controls stay absent; and the sequence-risk disclosure is visible.
