# Detailed FIRE Tax Calculation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let serious users refine a planning range into an auditable, browser-local tax calculation through dynamically routed residence, income, credit, property-lifecycle, and continuing-home-country questions.

**Architecture:** Add versioned rule data and small pure engines for profile routing, residence, income, property, credits, scenarios, and explanations. Enable detailed calculation per jurisdiction only after its applicable rules and official sources pass strict validation. Keep unsupported branches visible as ranges while calculating every supported branch; never substitute a generic handoff for available calculations.

**Tech Stack:** Python 3 standard library validators and fixtures, dependency-free CommonJS/browser JavaScript engines, JSON rules, `unittest`, existing retirement engine and site UI.

**Spec:** `docs/superpowers/specs/2026-08-29-fire-abroad-design.md`

## Global Constraints

- Detailed inputs and results remain in memory only; no URL, analytics, generated personalized HTML, or persistent storage.
- A question is displayed only when its answer can change an active branch or amount.
- Every amount resolves to a formula, rule ID, tax year, taxpayer scope, effective date, confidence, source IDs, and assumptions.
- Unsupported or unknown controlling facts produce multiple calculated branches when possible.
- A jurisdiction is enabled only when all rules applicable to the selected calculation pass validation.
- The engine estimates tax; it does not recommend entities, trusts, ownership structures, residency changes, or investments.

---

### Task 1: Versioned detailed-rule schema and validator

**Files:**
- Create: `data/fire_tax_rules.json`
- Create: `src/fire_tax_rules.py`
- Create: `tests/test_fire_tax_rules.py`

**Interfaces:**
- Produces `load_fire_tax_rules(path: Path = RULES_PATH) -> dict`.
- Produces `validate_fire_tax_rules(payload: dict, as_of: date) -> list[str]`.
- Rule types: `residence_test`, `rate_band`, `allowance`, `withholding`, `credit_limit`, `property_charge`, `reporting_flag`, and `branch`.

- [ ] **Step 1: Write failing schema and mutation tests**

Remove a source, effective date, formula operand, taxpayer scope, or branch target and assert the exact rule path appears in validation errors.

- [ ] **Step 2: Run tests and verify missing-module failure**

Run: `python3 -m unittest tests.test_fire_tax_rules -v`

- [ ] **Step 3: Implement loader and validator**

Use stable rule IDs and explicit currency. Reject overlapping progressive bands, circular branches, unknown operands, unbounded rates, stale sources, and rules without an explanation template.

- [ ] **Step 4: Add synthetic complete rules for residence and one income category**

```json
{
  "id": "example-income-2026",
  "type": "rate_band",
  "tax_year": 2026,
  "taxpayer_scope": ["resident"],
  "category": "ordinary_income",
  "currency": "EUR",
  "bands": [{"up_to": 10000, "rate": 0.10}, {"up_to": null, "rate": 0.20}],
  "source_ids": ["example-authority"],
  "effective_from": "2026-01-01",
  "checked_on": "2026-09-01",
  "confidence": "high",
  "explanation": "Progressive resident ordinary-income estimate."
}
```

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: add versioned FIRE tax rule contract"`

### Task 2: Material-question router and residence engine

**Files:**
- Create: `src/fire_tax_profile.js`
- Create: `src/fire_tax_residence.js`
- Create: `tests/test_fire_tax_profile.py`
- Create: `tests/test_fire_tax_residence.py`
- Create: `tests/fixtures/fire_tax_residence.json`

**Interfaces:**
- Produces `nextQuestions(profile, rules, currentResult) -> Question[]`.
- Produces `evaluateResidence(profile, destinationRules, homeRules) -> ResidenceResult`.

- [ ] **Step 1: Write failing routing and residence tests**

Cover day thresholds, available-home tests, family/economic ties, split-year branches, dual residence, unknown facts, and a supported treaty tie-breaker.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_fire_tax_profile tests.test_fire_tax_residence -v`

- [ ] **Step 3: Implement materiality-driven routing**

Return native-control descriptors with stable IDs, plain labels, reason text, accepted values, and the rule IDs affected. Do not return questions whose possible answers produce identical active results.

- [ ] **Step 4: Implement deterministic residence branches**

Return `likely_home_resident`, `likely_destination_resident`, `possible_dual_resident`, or `conditional`, plus supported split-year periods, worldwide/source scope, unresolved facts, explanations, and rule/source IDs.

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: calculate FIRE tax residence branches"`

### Task 3: Income, withholding, and foreign-tax-credit engines

**Files:**
- Create: `src/fire_tax_income.js`
- Create: `src/fire_tax_credits.js`
- Create: `tests/test_fire_tax_income.py`
- Create: `tests/test_fire_tax_credits.py`
- Create: `tests/fixtures/fire_tax_income.json`

**Interfaces:**
- Produces `calculateIncomeTax(profile, residence, rules) -> CategoryTaxResult[]`.
- Produces `applyForeignTaxCredits(categoryResults, creditRules) -> CreditResult`.

- [ ] **Step 1: Write failing category and credit tests**

Cover private/government pension, social security, dividends, interest, realized gains, retirement-account withdrawals, rent, employment/consulting, source withholding, exemptions, allowances, and category-limited credits.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_fire_tax_income tests.test_fire_tax_credits -v`

- [ ] **Step 3: Implement progressive rates and category calculations**

Keep gross income, deductions, taxable base, domestic tax, source withholding, and net tax separate. Reject unsupported account classifications rather than mapping them to ordinary income silently.

- [ ] **Step 4: Implement credit ordering and limits**

Apply credits only to matching income categories and cap them at the supported domestic tax. Preserve unused or unsupported credits as explanatory fields rather than negative tax.

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: calculate cross-border FIRE income tax"`

### Task 4: Full property tax lifecycle engine

**Files:**
- Create: `src/fire_tax_property.js`
- Create: `tests/test_fire_tax_property.py`
- Create: `tests/fixtures/fire_tax_property.json`

**Interfaces:**
- Produces `calculatePropertyTaxes(propertyProfile, residence, rules) -> PropertyTaxResult`.

- [ ] **Step 1: Write failing lifecycle tests**

Cover purchase taxes and fixed charges; annual property, wealth, imputed-income, vacancy, and compliance charges; rental income/deductions/withholding; sale gains, recapture and withholding; inheritance/gift allowances and conditional branches.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_fire_tax_property -v`

- [ ] **Step 3: Implement lifecycle calculations with separate tax/non-tax outputs**

Use purchase price, official assessment base, ownership share, financing, use, rent, deductible expenses, acquisition basis, improvements, sale price, holding period, relationship, and transfer type only when required by active rules.

- [ ] **Step 4: Add explanation and unknown-branch behavior**

When assessment value or heir relationship is unknown, return supported branch ranges with the missing fact and controlling rule; do not return zero.

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: calculate foreign-home tax lifecycle"`

### Task 5: Explanation/audit model and retirement integration

**Files:**
- Create: `src/fire_tax_explain.js`
- Create: `src/fire_tax_detailed.js`
- Create: `tests/test_fire_tax_detailed.py`
- Modify: `src/retirement_calculator_ui.js`

**Interfaces:**
- Produces `calculateDetailedTax(profile, rules) -> DetailedTaxResult`.
- Produces `explainCalculation(result) -> ExplanationSection[]`.

- [ ] **Step 1: Write failing end-to-end fixture tests**

Require residence result, income categories, credits, property lifecycle, continuing-home overlay, total annual tax, one-time taxes, after-tax income, after-tax return basis, and tax-adjusted capital input.

- [ ] **Step 2: Run tests and verify failure**

Run: `python3 -m unittest tests.test_fire_tax_detailed -v`

- [ ] **Step 3: Compose engines and auditable explanations**

Every line contains label, amount or range, formula text, assumption text, exclusions, confidence, rule IDs, source IDs, and tax year. Totals reconcile exactly to components.

- [ ] **Step 4: Feed detailed results into the retirement engine**

Replace planning tax reserves with calculated annual tax expenses, calculated after-tax dependable income, and the selected explicit after-tax return. Preserve the planning range alongside the refined result for comparison.

- [ ] **Step 5: Run tests and commit**

Commit: `git commit -m "feat: integrate detailed tax with FIRE projections"`

### Task 6: Progressive detailed UI, jurisdiction enablement, and verification

**Files:**
- Create: `src/fire_tax_detailed_ui.js`
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_retirement_calculator_page.py`
- Create: `tests/test_fire_tax_detailed_ui.py`
- Modify: `scripts/verify_static_site.py`

**Interfaces:**
- Implements `Refine this tax estimate`, dynamic question rendering, branch comparison, and audit details.

- [ ] **Step 1: Write failing accessibility, routing, and privacy tests**

Assert applicable-question-only rendering, native labels, keyboard operation, announced updates, branch comparison, source links, no sensitive analytics/URL/storage use, and no detailed entry point for jurisdictions failing enablement validation.

- [ ] **Step 2: Implement the progressive detailed interface**

Use one question section, one reconciled result table, and expandable calculation details. Avoid a multi-card dashboard and repeated labels.

- [ ] **Step 3: Populate and enable jurisdictions incrementally**

For each jurisdiction, add official current rules, run the validator and fixtures, then set `detailed_enabled: true`. Do not infer missing rates or enable partially validated exact calculations.

- [ ] **Step 4: Run focused and full verification**

Run: `python3 -m unittest tests.test_fire_tax_rules tests.test_fire_tax_profile tests.test_fire_tax_residence tests.test_fire_tax_income tests.test_fire_tax_credits tests.test_fire_tax_property tests.test_fire_tax_detailed tests.test_fire_tax_detailed_ui -v`

Run: `python3 src/build_unified_app.py`

Run: `python3 -m unittest discover -s tests -v`

- [ ] **Step 5: Inspect all required widths and commit**

Check 320, 375, 390, 430, 736, and 1024 pixels, including long source/formula text and unknown-fact branches. Commit with `git commit -m "feat: add detailed FIRE tax calculation"`.
