# Statutory Tax Range Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace generic tax stress bands with an automatically derived withdrawal and a transparent capital range calculated from current statutory destination capital-gains rules.

**Architecture:** Add a small statutory screening engine that consumes validated, versioned jurisdiction rules and returns three disclosed gain-share cases. The calculator and finder derive destination-specific withdrawals from existing expense and income inputs, while UI code only renders the engine's estimate, range, assumptions, evidence, or unavailable state.

**Tech Stack:** Python 3 static-site builder and validators; browser-native JavaScript modules; JSON rule data; Python `unittest`; Node-based JavaScript test harness; GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-02-statutory-tax-range-design.md`

## Global Constraints

- Screening gain shares are exactly `0`, `0.5`, and `1` for lower, planning, and upper cases.
- The planning estimate is the 50% gain-share result; range endpoints are the actual minimum and maximum of all cases.
- Only current, complete, source-linked statutory rules may produce a numerical result.
- Generic `planning_bands` and `gain_intensity_modifiers` may not be runtime fallbacks.
- Initial screening assumes a full-year destination tax resident with a personal taxable listed-securities portfolio.
- Unsupported income categories, account wrappers, treaties, credits, remittance facts, or stale rules must be disclosed and must not receive invented rates.
- All financial details remain in the browser.

---

### Task 1: Derive portfolio withdrawals from existing plan inputs

**Files:**
- Modify: `src/retirement_calculator_ui.js`
- Modify: `src/retirement_destination_finder.js`
- Test: `tests/test_retirement_calculator_page.py`
- Test: `tests/test_retirement_destination_finder_ui.py`

**Interfaces:**
- Produces: `deriveAnnualPortfolioWithdrawal(expenseCategories, incomeStreams) -> number`
- Produces: `destinationTaxScenario(input, destination, cost, baseTargetInput) -> TaxRange`

- [ ] **Step 1: Write failing calculator tests**

Add tests proving that the derived withdrawal equals annual expense amounts minus annual income amounts, floors at zero, and is calculated from the selected destination's scaled expense categories rather than a form field.

```javascript
deriveAnnualPortfolioWithdrawal(
  [{ amount: 30000 }, { amount: 12000 }],
  [{ amount: 18000 }]
) === 24000
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_destination_finder_ui -q`

Expected: FAIL because the helper is absent and both UIs still require withdrawal controls.

- [ ] **Step 3: Implement the shared derivation behavior**

Calculate:

```javascript
Math.max(0,
  expenseCategories.reduce((sum, row) => sum + Number(row.amount || 0), 0) -
  incomeStreams.reduce((sum, row) => sum + Number(row.amount || 0), 0)
)
```

Use the result in `taxScenarioInput()` for the calculator and pass each finder's `baseTargetInput` to `destinationTaxScenario()` so the finder derives a different withdrawal for every destination.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_destination_finder_ui -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/retirement_calculator_ui.js src/retirement_destination_finder.js tests/test_retirement_calculator_page.py tests/test_retirement_destination_finder_ui.py
git commit -m "Derive retirement portfolio withdrawals"
```

### Task 2: Define and validate the statutory screening rule contract

**Files:**
- Modify: `data/fire_tax_rules.json`
- Modify: `src/fire_tax_rules.py`
- Test: `tests/test_fire_tax_rules.py`

**Interfaces:**
- Produces JSON records at `jurisdictions.<id>.statutory_screening`
- Produces: `load_statutory_screening_rules(path, as_of) -> dict[str, dict]`

- [ ] **Step 1: Write failing validator tests**

Require each enabled record to contain:

```json
{
  "tax_year": 2026,
  "effective_from": "2026-01-01",
  "checked_on": "2026-09-02",
  "review_interval_days": 90,
  "currency": "EUR",
  "residence_assumption": "full_year_resident",
  "portfolio_scope": "personal_taxable_listed_securities",
  "capital_gains": {
    "base": "gain",
    "calculation": "flat_rate",
    "rate": 0.12
  },
  "source_ids": ["official-source-id"]
}
```

Test rejection of missing sources, stale checked dates, invalid bands, negative rates, unknown bases, missing condition operands, and source IDs absent from the source catalog.

- [ ] **Step 2: Run validator tests and verify RED**

Run: `python3 -m unittest tests.test_fire_tax_rules -q`

Expected: FAIL because statutory screening validation does not exist.

- [ ] **Step 3: Implement the validator**

Support these calculation types and no others:

- `flat_rate` applied to realized gain;
- `progressive_rate` applied to realized gain or combined assessable income;
- `proceeds_rate` applied to sale proceeds;
- `holding_period_exemption` wrapping a gain rule;
- `remittance_progressive_rate` requiring a disclosed remittance assumption;
- `conditional_exemption` requiring a screening-safe ownership condition.

Return immutable normalized records and explicit unavailable reasons; never coerce an incomplete rule into a zero rate.

- [ ] **Step 4: Run validator tests and verify GREEN**

Run: `python3 -m unittest tests.test_fire_tax_rules -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data/fire_tax_rules.json src/fire_tax_rules.py tests/test_fire_tax_rules.py
git commit -m "Validate statutory tax screening rules"
```

### Task 3: Add official-source statutory rules for covered jurisdictions

**Files:**
- Modify: `data/fire_tax_rules.json`
- Create: `tests/fixtures/fire_tax_statutory_screening.json`
- Test: `tests/test_fire_tax_rules.py`

**Interfaces:**
- Consumes: `jurisdictions.<id>.statutory_screening` contract from Task 2
- Produces validated rules for Croatia, Greece, Indonesia, Japan, Portugal, Spain, Thailand, and Vietnam

- [ ] **Step 1: Add failing country boundary fixtures**

Fixtures must cover zero gain, a representative gain, every progressive threshold, and every modeled condition. Expected rules:

- Croatia: 12% gain tax with the statutory two-year holding exemption.
- Greece: 15% gain rate, with the listed-share participation condition represented explicitly rather than silently assumed.
- Japan: 20.315% separate taxation for supported listed-security gains.
- Portugal: 28% special rate plus the documented mandatory aggregation condition where the screening inputs support it.
- Spain: savings-base bands of 19% to EUR 6,000; 21% to EUR 50,000; 23% to EUR 200,000; 27% to EUR 300,000; and 30% thereafter.
- Thailand: foreign-source gains remitted by a resident use the supported progressive PIT bands; absence of a remittance assumption is unavailable.
- Vietnam: 0.1% of securities-transfer proceeds, modeled as a proceeds-base rule rather than a gain rate.
- Indonesia: distinguish Indonesian exchange/proceeds rules from foreign listed-security gains of a resident; return unavailable when the asset-source facts collected by screening cannot select the statutory base safely.

- [ ] **Step 2: Run country fixtures and verify RED**

Run: `python3 -m unittest tests.test_fire_tax_rules -q`

Expected: FAIL because the eight country records are absent.

- [ ] **Step 3: Add rules and primary official sources**

Record the official tax-authority or legislation URLs, supported claim, tax year/effective date, and checked date for every rate, threshold, exemption, residence/remittance condition, and tax base. Start from these primary sources and add more specific official material whenever a condition is not fully supported:

- Portugal: `https://info.portaldasfinancas.gov.pt/pt/apoio_contribuinte/Folhetos_informativos/Documents/SFP-Taxas-2025.pdf`
- Spain: `https://sede.agenciatributaria.gob.es/Sede/ayuda/manuales-videos-folletos/manuales-practicos/irpf-2025/c15-calculo-impuesto-determinacion-cuotas-integras/gravamen-aplicable-contribuyentes-irpf-residentes-extranjero/gravamen-base-liquidable-ahorro.html`
- Greece: `https://www.aade.gr/en/greeks-abroad-non-residents/income-taxation/income-categories-and-income-taxation-greece`
- Croatia: `https://narodne-novine.nn.hr/clanci/sluzbeni/2016_12_115_2525.html` plus the current amendment list at `https://investcroatia.gov.hr/en/tax-system/`
- Japan: `https://www.nta.go.jp/publication/pamph/koho/kurashi/html/04_5.htm`
- Indonesia: `https://www.pajak.go.id/en/7-things-taxpayers-need-know-about-taxes-capital-gain-otc-stock-transactions`
- Thailand: `https://www.rd.go.th/english/6045.html` and `https://www.rd.go.th/fileadmin/user_upload/porphor/GuideTaxFromAbroad_EN.pdf`
- Vietnam: the Ministry of Finance/GDT PIT law table at `https://www.gdt.gov.vn/`

- [ ] **Step 4: Run country fixtures and verify GREEN**

Run: `python3 -m unittest tests.test_fire_tax_rules -q`

Expected: PASS with eight complete or explicitly conditional country records and no generic fallback.

- [ ] **Step 5: Commit**

```bash
git add data/fire_tax_rules.json tests/fixtures/fire_tax_statutory_screening.json tests/test_fire_tax_rules.py
git commit -m "Add statutory destination gain rules"
```

### Task 4: Calculate statutory lower, estimate, and upper cases

**Files:**
- Create: `src/fire_tax_statutory.js`
- Modify: `src/fire_tax_scenarios.js`
- Create: `tests/test_fire_tax_statutory.py`
- Modify: `tests/test_fire_tax_scenarios.py`

**Interfaces:**
- Produces: `estimateStatutoryTaxRange(input, rule) -> {status, estimate, minimum, maximum, cases, explanations}`
- Consumes: `{portfolioWithdrawals, dependableIncomeByCategory, gainShares:[0,0.5,1], holdingPeriodYears, remittanceShare, asOf}`

- [ ] **Step 1: Write failing engine tests**

Test flat, progressive, proceeds, exemption, conditional, stale, and remittance calculations. A core expectation is:

```javascript
estimateStatutoryTaxRange(
  { portfolioWithdrawals: 40000, gainShares: [0, 0.5, 1] },
  { capital_gains: { base: "gain", calculation: "flat_rate", rate: 0.2 } }
).cases.map(row => row.capitalGainsTax)
// [0, 4000, 8000]
```

Also assert that the estimate is the 50% case and the range endpoints are calculated minima/maxima.

- [ ] **Step 2: Run engine tests and verify RED**

Run: `python3 -m unittest tests.test_fire_tax_statutory tests.test_fire_tax_scenarios -q`

Expected: FAIL because `fire_tax_statutory.js` is absent.

- [ ] **Step 3: Implement the statutory engine and adapter**

Keep arithmetic in `fire_tax_statutory.js`. Return dollar amounts, the statutory base, local-currency thresholds used, exact source IDs, assumptions, exclusions, and unavailable conditions. Replace `planning_bands` and `gain_intensity_modifiers` use in `fire_tax_scenarios.js`; do not retain a runtime fallback.

- [ ] **Step 4: Run engine tests and verify GREEN**

Run: `python3 -m unittest tests.test_fire_tax_statutory tests.test_fire_tax_scenarios -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/fire_tax_statutory.js src/fire_tax_scenarios.js tests/test_fire_tax_statutory.py tests/test_fire_tax_scenarios.py
git commit -m "Calculate statutory tax planning ranges"
```

### Task 5: Integrate statutory rules into the static payload and rankings

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `src/fire_abroad.py`
- Modify: `src/retirement_calculator_ui.js`
- Modify: `src/retirement_destination_finder.js`
- Test: `tests/test_build_unified_app_auto_links.py`
- Test: `tests/test_fire_abroad_data.py`
- Test: `tests/test_retirement_calculator_page.py`

**Interfaces:**
- Consumes: validated statutory rule payload and `estimateStatutoryTaxRange`
- Produces: tax-adjusted calculator cases and destination-specific ranking targets

- [ ] **Step 1: Write failing integration tests**

Assert the built payload contains only validated public screening records, embeds `fire_tax_statutory.js` before consumers, maps every covered destination to its jurisdiction rule, and returns conditional/unavailable ranking states for unsupported or stale rules.

- [ ] **Step 2: Run integration tests and verify RED**

Run: `python3 -m unittest tests.test_build_unified_app_auto_links tests.test_fire_abroad_data tests.test_retirement_calculator_page -q`

Expected: FAIL because the build does not ship statutory screening rules or the new engine.

- [ ] **Step 3: Wire build and runtime dependencies**

Load and validate rules once during build, serialize the public statutory subset, and pass it to the calculator, finder, and FIRE pages. Ensure `targetCases()` uses statutory case totals and that unavailable jurisdictions are visible but unranked.

- [ ] **Step 4: Run integration tests and verify GREEN**

Run: `python3 -m unittest tests.test_build_unified_app_auto_links tests.test_fire_abroad_data tests.test_retirement_calculator_page -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/build_unified_app.py src/fire_abroad.py src/retirement_calculator_ui.js src/retirement_destination_finder.js tests/test_build_unified_app_auto_links.py tests/test_fire_abroad_data.py tests/test_retirement_calculator_page.py
git commit -m "Integrate statutory tax ranges"
```

### Task 6: Simplify calculator and finder presentation

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `src/retirement_calculator_ui.js`
- Modify: `src/retirement_destination_finder_page.py`
- Modify: `src/retirement_destination_finder_ui.js`
- Test: `tests/test_retirement_calculator_page.py`
- Test: `tests/test_retirement_destination_finder_page.py`
- Test: `tests/test_retirement_destination_finder_ui.py`
- Test: `tests/test_fire_tax_detailed_ui.py`

**Interfaces:**
- Consumes: `{estimate, minimum, maximum, cases, explanations}`
- Produces: plain-language estimate/range UI and expandable calculation evidence

- [ ] **Step 1: Write failing UI contract tests**

Assert both initial forms omit withdrawal and realized-gain controls. Assert visible copy uses “Estimated amount needed” and “Planning range,” never “favorable/adverse,” and the expandable explanation includes calculated withdrawal, 0%/50%/100% gain amounts, tax year, destination-side scope, official sources, and last-checked date.

- [ ] **Step 2: Run UI tests and verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui tests.test_fire_tax_detailed_ui -q`

Expected: FAIL because the technical controls and scenario labels remain.

- [ ] **Step 3: Implement minimal progressive disclosure**

Remove the two technical fields and their listeners/validation. Render one estimate and one range. Keep calculation details collapsed by default and preserve the detailed calculator route for actual cost basis, source country, account wrapper, residence, treaty, and credit facts.

- [ ] **Step 4: Run UI tests and verify GREEN**

Run the command from Step 2.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/build_unified_app.py src/retirement_calculator_ui.js src/retirement_destination_finder_page.py src/retirement_destination_finder_ui.js tests/test_retirement_calculator_page.py tests/test_retirement_destination_finder_page.py tests/test_retirement_destination_finder_ui.py tests/test_fire_tax_detailed_ui.py
git commit -m "Simplify statutory tax range UX"
```

### Task 7: Remove legacy bands, verify, visually inspect, and deploy

**Files:**
- Modify: `data/fire_abroad.json`
- Modify: `scripts/verify_static_site.py`
- Modify: affected tests

**Interfaces:**
- Produces: a static production build with no runtime references to `planning_bands`, `gain_intensity_modifiers`, withdrawal controls, or gain-intensity controls

- [ ] **Step 1: Write the failing removal/static-verifier tests**

Assert legacy fields are absent from runtime data, generated HTML contains no removed controls or scenario labels, supported pages contain statutory source disclosures, and unsupported pages contain the unavailable message.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 scripts/verify_static_site.py`

Expected: FAIL while legacy fields and controls remain.

- [ ] **Step 3: Remove legacy runtime data and rebuild**

Delete `planning_bands` and `gain_intensity_modifiers` from the eight tax screens after statutory integration passes. Preserve residence, tax scope, property, wealth, compliance, eligibility, and source evidence still used elsewhere.

- [ ] **Step 4: Run complete automated verification**

Run:

```bash
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py
python3 -m unittest discover -s tests -q
git diff --check
```

Expected: every command exits zero.

- [ ] **Step 5: Perform browser QA**

At desktop and 390×844 mobile sizes, inspect and exercise:

- `/retirement-abroad-calculator/`
- `/retirement-destination-finder/`
- `/fire-abroad/`

Confirm no horizontal overflow, no console errors, removed inputs are absent, estimate/range explanations are understandable, official source links work, supported jurisdictions calculate, and unsupported jurisdictions do not fabricate numbers.

- [ ] **Step 6: Commit and deploy**

```bash
git add data/fire_abroad.json scripts/verify_static_site.py src tests
git commit -m "Complete statutory tax range rollout"
git fetch origin main
git push origin HEAD:main
gh run list --workflow "Deploy static dashboard" --branch main --limit 1
```

Watch the database ID returned by the final command with `gh run watch ID --exit-status`.

- [ ] **Step 7: Verify production**

Exercise the three live URLs with a cache-busting query, confirm the deployed statutory estimate/range and source disclosure, and record the successful commit SHA and workflow URL.
