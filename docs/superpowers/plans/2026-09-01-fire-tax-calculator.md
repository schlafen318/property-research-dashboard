# FIRE Tax-Aware Calculator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an approachable destination tax estimate to the normal FIRE and retirement calculators, showing favorable/central/adverse annual tax reserves and their effect on required capital while preserving a user-supplied after-tax mode.

**Architecture:** Build a focused tax-scenario module on the validated FIRE overlay, then feed its outputs into the existing pure cash-flow engine as explicit tax expenses and after-tax income/return assumptions. Add equivalent Python and JavaScript fixtures, progressive calculator controls, and expandable explanations. Do not implement exact residence, treaty, or account-level rules here.

**Tech Stack:** Python 3 standard library, `unittest`, JSON fixtures, dependency-free CommonJS/browser JavaScript, existing calculator engine and static builder.

**Spec:** `docs/superpowers/specs/2026-08-29-fire-abroad-design.md`

## Global Constraints

- Calculator modes are exactly `destination_estimate` and `user_after_tax`.
- `destination_estimate` uses explicit planning inputs and shows favorable, central, and adverse results.
- `user_after_tax` adds no income-tax reserve and labels portfolio return “after fees and tax.”
- Property tax and income tax are never counted both in retirement costs and the tax scenario.
- Every amount expands to formula, assumptions, included categories, exclusions, tax year, confidence, and source IDs.
- No tax or financial input/result enters analytics, URLs, generated personalized HTML, or persistent storage.

---

### Task 1: Tax-scenario contract and calculator engine boundary

**Files:**
- Create: `src/fire_tax_scenarios.js`
- Create: `tests/test_fire_tax_scenarios.py`
- Create: `tests/fixtures/fire_tax_scenarios.json`
- Modify: `src/retirement_calculator.js`
- Modify: `tests/test_retirement_calculator_engine.py`

**Interfaces:**
- Produces `estimateTaxScenario(input, countryRecord) -> TaxScenario`.
- Extends calculator input with `annualTaxExpenses`, `taxMode`, and `returnBasis`.
- `TaxScenario` contains ordered `favorable`, `central`, and `adverse` cases plus explanations.

- [ ] **Step 1: Write failing scenario tests**

```javascript
const result = scenarios.estimateTaxScenario({
  taxMode: "destination_estimate",
  stayMode: "full_relocation",
  dependableIncome: 40000,
  portfolioWithdrawals: 60000,
  realizedGainIntensity: "moderate",
  propertyPrice: 500000,
  propertyUse: "personal",
  wealthBand: "under_threshold"
}, country);
assert.deepStrictEqual(Object.keys(result.cases), ["favorable", "central", "adverse"]);
assert.ok(result.cases.favorable.total <= result.cases.central.total);
assert.ok(result.cases.central.total <= result.cases.adverse.total);
```

- [ ] **Step 2: Run focused tests and confirm failure**

Run: `python3 -m unittest tests.test_fire_tax_scenarios tests.test_retirement_calculator_engine -v`

- [ ] **Step 3: Implement scenario calculation and explanation records**

Compute the planning base from dependable income plus portfolio withdrawals. Apply the selected stay-mode and gain-intensity modifiers from validated data. Add applicable annual property/wealth/compliance reserves separately. Return integer USD amounts with source-backed explanation records.

- [ ] **Step 4: Extend the retirement engine without breaking legacy inputs**

Treat `annualTaxExpenses` as an expense category with general inflation. Reject `destination_estimate` when scenarios are missing. Reject a tax-adjusted result unless `returnBasis === "after_fees_and_tax"`. Legacy callers default to `user_after_tax` only when their UI labels already state after-tax inputs.

- [ ] **Step 5: Run tests and commit**

Run: `python3 -m unittest tests.test_fire_tax_scenarios tests.test_retirement_calculator_engine -v`

Commit: `git commit -m "feat: add FIRE tax planning scenarios"`

### Task 2: Tax-adjusted capital scenarios

**Files:**
- Modify: `src/retirement_calculator_ui.js`
- Modify: `tests/test_retirement_calculator_ui.py`

**Interfaces:**
- Produces `calculateTaxAdjustedScenarios(baseInput, taxScenario) -> {favorable, central, adverse}`.

- [ ] **Step 1: Write failing UI-helper tests**

Assert that the central result equals the normal calculator result with the central tax expense, bands remain ordered, and `user_after_tax` yields one result with zero added tax reserve.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_retirement_calculator_ui -v`

- [ ] **Step 3: Implement scenario composition**

Clone the base input three times, add the matching tax expense category, and invoke the pure retirement engine. Return annual tax, first-year spending, funding gap, and required-capital differences against the no-tax comparison.

- [ ] **Step 4: Add tests for no double counting and return basis**

Cover owner-cost records that already include property tax, zero outside income, zero withdrawals, and after-tax bypass mode.

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: calculate tax-adjusted FIRE capital ranges"`

### Task 3: Progressive calculator controls and results

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `src/retirement_calculator_ui.js`
- Modify: `src/retirement_destination_finder_page.py`
- Modify: `src/retirement_destination_finder_ui.js`
- Modify: `tests/test_retirement_calculator_page.py`
- Modify: `tests/test_retirement_destination_finder_page.py`

**Interfaces:**
- Adds tax-mode controls and `Refine this tax estimate` hook without implementing the detailed drawer.

- [ ] **Step 1: Write failing rendered-page tests**

Require both tax modes, plain-language planning inputs, conditional wealth-band control, explicit “after fees and tax” return copy, favorable/central/adverse result rows, and expandable assumptions/sources.

- [ ] **Step 2: Run page tests and verify failure**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_destination_finder_page -v`

- [ ] **Step 3: Add minimal progressive controls**

Show dependable income, withdrawals, gain intensity, property use, and conditional wealth band only in destination-estimate mode. Preserve the existing concise calculator layout and native form controls.

- [ ] **Step 4: Render tax-adjusted results and explanations**

Show central result first, a simple range beneath it, and one expandable table containing tax reserve, total annual requirement, and capital requirement. Keep the no-tax figure as a labelled comparison, not the headline.

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: add tax-aware retirement calculator controls"`

### Task 4: Cross-tool integration, privacy, and verification

**Files:**
- Modify: `tests/test_retirement_destination_finder.py`
- Modify: `tests/test_retirement_destination_finder_ui.py`
- Modify: `tests/test_build_unified_app_auto_links.py`
- Modify: `scripts/verify_static_site.py`

**Interfaces:**
- Finder affordability tiers consume the central tax-adjusted target and expose favorable/adverse gaps.

- [ ] **Step 1: Write failing integration and privacy tests**

Assert ranking can change after tax, tax inputs/results never reach analytics or query strings, and invalid/stale tax data makes a destination conditional rather than silently reverting to zero.

- [ ] **Step 2: Implement finder integration and safe fallbacks**

Use central tax-adjusted capital for `within_reach`, `close`, and `stretch`; display the range alongside the tier. Preserve property equity separation.

- [ ] **Step 3: Run focused suites**

Run: `python3 -m unittest tests.test_retirement_calculator_engine tests.test_retirement_calculator_ui tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui -v`

- [ ] **Step 4: Run full build and suite**

Run: `python3 src/build_unified_app.py`

Run: `python3 -m unittest discover -s tests -v`

- [ ] **Step 5: Inspect responsive and script-disabled behavior, then commit**

Check 320, 375, 390, 430, 736, and 1024 pixels and commit with `git commit -m "feat: integrate tax-adjusted FIRE planning"`.
