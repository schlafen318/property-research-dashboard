# Retirement Abroad Calculator SEO Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a mobile-first `/retirement-abroad-calculator/` SEO page that estimates destination spending, outside-income offsets, liquid portfolio needs, property capital, and emergency reserves for single retirees and couples.

**Architecture:** Keep the existing Python standard-library static build. Add one source-audited JSON dataset, one framework-free calculation module that works in Node and the browser, and one focused browser UI module embedded by new calculator-page helpers in `src/build_unified_app.py`. Pre-render benchmark, methodology, FAQ, and internal-link content for indexing; use JavaScript only for personalized calculations.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, vanilla JavaScript with Node-based deterministic tests, generated static HTML/CSS, JSON-LD, Playwright CLI for browser verification.

**Spec:** `docs/superpowers/specs/2026-08-18-retirement-abroad-calculator-seo-design.md`

## Global Constraints

- Publish one canonical page at `/retirement-abroad-calculator/`; do not create thin destination-specific calculator pages.
- Cover Fukuoka / Itoshima, Valencia, Algarve / Cascais, Madeira, Crete, Hakone / Izu, Lake Como, and Málaga / Costa del Sol in release one.
- Support single retirees and couples, plus rent, already-own, and buy-at-retirement housing plans.
- Treat portfolio dividends and interest as part of portfolio withdrawals, never as separate outside passive income.
- Show liquid portfolio, property capital, emergency reserve, and combined capital separately.
- Use a 3.5% guided rate for 26–30 years, with the exact horizon tiers and 3.0–4.0% bounds from the approved spec.
- Keep user financial inputs client-side; never persist or include raw financial values in analytics.
- Preserve useful pre-rendered page content when JavaScript is unavailable.
- Use only the Python standard library and existing project tooling; add no application framework or production dependency.
- Maintain readable, overflow-free layouts from 320px through 1024px.

## File Structure

- Create `data/retirement_costs.json`: source-audited destination cost, inflation, housing, property, confidence, and citation records.
- Create `src/retirement_calculator.js`: pure calculation and validation functions exported to both Node and `window.GHARetirementCalculator`.
- Create `src/retirement_calculator_ui.js`: DOM input synchronization, result rendering, disclosure controls, and privacy-safe tracking.
- Modify `src/build_unified_app.py`: dataset loader, SEO metadata and schema, calculator page HTML/CSS, static benchmark content, page output, sitemap entry, and internal links.
- Create `tests/test_retirement_cost_data.py`: dataset contract, completeness, provenance, and arithmetic checks.
- Create `tests/test_retirement_calculator_engine.py`: Node-backed formula tests.
- Create `tests/test_retirement_calculator_page.py`: generated SEO, no-JavaScript content, accessibility markers, links, and analytics-privacy checks.
- Modify `scripts/verify_static_site.py`: make the calculator a required key page and verify its essential markers.
- Modify `docs/CHANGELOG.md`: record the new indexable calculator and data surface.

---

### Task 1: Add the Source-Audited Retirement Cost Dataset

**Files:**
- Create: `data/retirement_costs.json`
- Create: `tests/test_retirement_cost_data.py`

**Interfaces:**
- Produces: JSON object with top-level `as_of`, `currency`, and `destinations` array.
- Produces: each destination record with `destination_id: str`, `display_currency: str`, `fx_to_usd: float`, `inflation: object`, `profiles: object`, `property: object`, `confidence: object`, and `sources: array`.
- Consumed by: `load_retirement_costs()` in Task 3 and browser initialization in Task 4.

- [ ] **Step 1: Write the failing dataset contract test**

Create `tests/test_retirement_cost_data.py` with exact release IDs and required numeric categories:

```python
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "retirement_costs.json"
EXPECTED_IDS = {
    "fukuoka-itoshima",
    "valencia",
    "algarve-cascais",
    "madeira",
    "crete",
    "hakone-izu",
    "lake-como",
    "m-laga-costa-del-sol",
}
CORE_CATEGORIES = {
    "food_household",
    "utilities_communications",
    "private_healthcare",
    "transport",
    "dining_leisure",
    "travel",
    "visa_admin",
    "contingency",
}


class RetirementCostDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        cls.records = {item["destination_id"]: item for item in cls.payload["destinations"]}

    def test_release_destination_set_is_complete(self) -> None:
        self.assertEqual(EXPECTED_IDS, set(self.records))

    def test_profiles_have_positive_single_and_couple_costs(self) -> None:
        for record in self.records.values():
            for household in ("single", "couple"):
                profile = record["profiles"][household]
                self.assertEqual(CORE_CATEGORIES, set(profile["categories_usd"]))
                self.assertTrue(all(value >= 0 for value in profile["categories_usd"].values()))
                self.assertGreater(profile["annual_rent_usd"], 0)
                self.assertGreater(profile["annual_owner_costs_usd"], 0)

    def test_every_record_has_dated_metric_sources(self) -> None:
        for record in self.records.values():
            self.assertGreaterEqual(len(record["sources"]), 3)
            for source in record["sources"]:
                self.assertTrue(source["name"])
                self.assertTrue(source["url"].startswith("https://"))
                self.assertTrue(source["metric_supported"])
                self.assertRegex(source["accessed_on"], r"^\d{4}-\d{2}-\d{2}$")
```

- [ ] **Step 2: Run the contract test and verify it fails**

Run: `python3 -m unittest tests.test_retirement_cost_data -v`

Expected: ERROR because `data/retirement_costs.json` does not exist.

- [ ] **Step 3: Research and create all eight records**

Create `data/retirement_costs.json` with `as_of: "2026-08-18"`, `currency: "USD"`, and exactly eight destination objects. Every object must satisfy the interface and failing tests above. Populate both household profiles with the eight exact `CORE_CATEGORIES`, `annual_rent_usd`, and `annual_owner_costs_usd`; populate `property` with `representative_price_usd`, `acquisition_cost_rate`, and a plain-language `price_basis`; populate `inflation` with `general`, `healthcare`, and `property`; and populate every source with `name`, HTTPS `url`, `metric_supported`, `source_date`, `accessed_on`, and `notes`.

Research every numeric value before writing it. Prefer official inflation and health sources, current destination-level rent and living-cost evidence, and the existing representative property/listing evidence. Use country-level or crowdsourced values only as explicit proxies in `confidence.proxy_categories`. Use `data/fx_rates.json` for the recorded USD conversion basis and keep every source directly tied to `metric_supported`. No cost, price, rate, source name, or source URL may be blank or zero merely to satisfy the schema.

- [ ] **Step 4: Strengthen tests for arithmetic and confidence**

Add tests that assert couple non-housing costs exceed single non-housing costs, acquisition rates are between `0` and `0.25`, inflation assumptions are between `0` and `0.15`, representative property prices are positive, confidence is one of `low`, `medium`, `medium-high`, or `high`, and every proxy category exists in the record.

- [ ] **Step 5: Run the dataset tests**

Run: `python3 -m unittest tests.test_retirement_cost_data -v`

Expected: all tests PASS for eight complete, source-audited records.

- [ ] **Step 6: Commit the dataset**

```bash
git add data/retirement_costs.json tests/test_retirement_cost_data.py
git commit -m "feat: add retirement destination cost dataset"
```

---

### Task 2: Implement and Test the Pure Calculation Engine

**Files:**
- Create: `src/retirement_calculator.js`
- Create: `tests/test_retirement_calculator_engine.py`

**Interfaces:**
- Produces: `guidedWithdrawalRate(horizonYears: number) -> number`.
- Produces: `calculateRetirement(input: object) -> object`.
- Consumes exact input keys: `currentAge`, `retirementAge`, `horizonYears`, `expenseCategories`, `incomeStreams`, `housingPlan`, `propertyPrice`, `propertyInflation`, `acquisitionCostRate`, `generalInflation`, `emergencyReserveMonths`, `portfolioCashYield`, and optional `withdrawalRateOverride`.
- Each `expenseCategories` item is `{ amount: number, inflationRate: number }`; each `incomeStreams` item is `{ amount: number, indexed: boolean, inflationRate: number }`.
- Produces result keys: `yearsToRetirement`, `firstYearExpenses`, `outsideIncome`, `fundingGap`, `withdrawalRate`, `liquidPortfolio`, `propertyCapital`, `emergencyReserve`, `totalCapital`, `portfolioCashIncome`, `assetSales`, and `todayDollarTotal`.
- Exports through `module.exports` in Node and `window.GHARetirementCalculator` in browsers.

- [ ] **Step 1: Write a failing Node-backed unit-test harness**

Create `tests/test_retirement_calculator_engine.py` with a helper that sends JSON to Node and invokes the module:

```python
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "retirement_calculator.js"


def calculate(payload: dict) -> dict:
    script = (
        "const engine = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(engine.calculateRetirement(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)
```

Add tests for ten years of 2.6% expense inflation, fixed versus indexed income, a zero funding gap, a 3.5% 30-year guided rate, property costs only in `buy`, and the relationship `portfolioCashIncome + assetSales == fundingGap`.

- [ ] **Step 2: Run the engine tests and verify they fail**

Run: `python3 -m unittest tests.test_retirement_calculator_engine -v`

Expected: FAIL because `src/retirement_calculator.js` is missing.

- [ ] **Step 3: Implement the UMD-style engine**

Implement a strict, side-effect-free module with these core rules:

```javascript
function guidedWithdrawalRate(horizonYears) {
  if (horizonYears <= 25) return 0.04;
  if (horizonYears <= 30) return 0.035;
  if (horizonYears <= 35) return 0.0325;
  return 0.03;
}

function project(value, rate, years) {
  return value * Math.pow(1 + rate, years);
}

function calculateRetirement(input) {
  const years = input.retirementAge - input.currentAge;
  if (!Number.isFinite(years) || years <= 0) throw new Error("Retirement age must exceed current age");
  // Validate all remaining numeric inputs as finite and non-negative.
  // Inflate each expense category with healthcare/property/general inflation.
  // Inflate indexed outside income; leave fixed income nominal.
  // Floor fundingGap and assetSales at zero.
  // Include projected purchase price and acquisition costs only for buy.
  // Keep emergencyReserve outside the liquid portfolio.
  // Deflate totalCapital with general inflation for todayDollarTotal.
  return result;
}
```

Attach `{ guidedWithdrawalRate, calculateRetirement }` to `module.exports` and `window.GHARetirementCalculator` without executing browser code during `require()`.

- [ ] **Step 4: Add invalid-input and sensitivity tests**

Test retirement age validation, negative values, overridden withdrawal rates outside the allowed `0.03–0.04` range, horizons at `25`, `26`, `30`, `31`, `35`, and `36`, and exact results for rent, own, and buy.

- [ ] **Step 5: Run engine tests and dataset tests**

Run: `python3 -m unittest tests.test_retirement_calculator_engine tests.test_retirement_cost_data -v`

Expected: all tests PASS.

- [ ] **Step 6: Commit the engine**

```bash
git add src/retirement_calculator.js tests/test_retirement_calculator_engine.py
git commit -m "feat: add retirement capital calculation engine"
```

---

### Task 3: Generate the Indexable Calculator SEO Page

**Files:**
- Modify: `src/build_unified_app.py:20-130`
- Modify: `src/build_unified_app.py:800-1020`
- Modify: `src/build_unified_app.py:3350-3720`
- Modify: `src/build_unified_app.py:7250-7375`
- Create: `tests/test_retirement_calculator_page.py`

**Interfaces:**
- Produces: `load_retirement_costs() -> list[dict]`.
- Produces: `schema_for_retirement_calculator(canonical: str) -> list[dict]`.
- Produces: `build_retirement_calculator_page(destinations: list[dict], retirement_costs: list[dict]) -> str`.
- Writes: `artifacts/retirement-abroad-calculator/index.html`.
- Consumes: `data/retirement_costs.json` and `src/retirement_calculator.js`.

- [ ] **Step 1: Write failing generated-page tests**

Create `tests/test_retirement_calculator_page.py`. In `setUpClass`, run `python3 src/build_unified_app.py`. Assert the output includes:

```python
self.assertIn("<title>Retirement Abroad Calculator: How Much Do You Need? | Global Home Atlas</title>", html)
self.assertIn('<link rel="canonical" href="https://globalhomeatlas.com/retirement-abroad-calculator/">', html)
self.assertIn("<h1>Retirement Abroad Calculator</h1>", html)
self.assertIn('"@type":"WebApplication"', compact_html)
self.assertIn('"@type":"FAQPage"', compact_html)
self.assertIn("Retirement cost benchmarks by destination", html)
self.assertIn("Fukuoka / Itoshima", html)
self.assertIn("Málaga / Costa del Sol", html)
self.assertIn("Portfolio dividends and interest", html)
```

Also parse the HTML with `html.parser` and assert labeled form controls, one result region with `aria-live="polite"`, and a no-JavaScript methodology/benchmark section.

- [ ] **Step 2: Run the page test and verify it fails**

Run: `python3 -m unittest tests.test_retirement_calculator_page -v`

Expected: FAIL because the generated page is absent.

- [ ] **Step 3: Add constants, loader, and schema helpers**

Add exact page constants beside existing guide constants:

```python
RETIREMENT_CALCULATOR_SLUG = "retirement-abroad-calculator"
RETIREMENT_CALCULATOR_TITLE = "Retirement Abroad Calculator: How Much Do You Need? | Global Home Atlas"
RETIREMENT_CALCULATOR_H1 = "Retirement Abroad Calculator"
RETIREMENT_CALCULATOR_DESCRIPTION = (
    "Estimate how much you need to retire abroad, including destination living costs, "
    "inflation, pension and passive income, property costs, and required portfolio capital."
)
RETIREMENT_COSTS_PATH = DATA_DIR / "retirement_costs.json"
RETIREMENT_ENGINE_PATH = SRC_DIR / "retirement_calculator.js"
```

Implement `load_retirement_costs()` with explicit top-level and destination-ID validation. Implement schema entities for Organization, WebSite, WebPage, WebApplication with `applicationCategory: "FinanceApplication"`, BreadcrumbList, and the five approved FAQs.

- [ ] **Step 4: Build the pre-rendered SEO body**

Implement `build_retirement_calculator_page()` using existing `head_html()`, brand header/footer, analytics helpers, and simple responsive CSS. It must include the calculator form, empty but labeled live result region, pre-rendered single/couple benchmark table, rent/own/buy explanation, methodology, source-date/confidence disclosure, related guides, and FAQs. Embed the JSON data with `json.dumps(...).replace("</", "<\\/")` and embed the calculation engine text after escaping `</script>`.

- [ ] **Step 5: Write the page and add it to the sitemap**

In `build()`, load the retirement dataset, create `artifacts/retirement-abroad-calculator/`, write `index.html`, and add `(page_url(RETIREMENT_CALCULATOR_SLUG), "0.92")` after the guide hub in `sitemap_urls`.

- [ ] **Step 6: Run page and existing static tests**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_static_guides -v`

Expected: all tests PASS.

- [ ] **Step 7: Commit the SEO page shell**

```bash
git add src/build_unified_app.py tests/test_retirement_calculator_page.py artifacts/retirement-abroad-calculator/index.html artifacts/sitemap.xml
git commit -m "feat: generate retirement abroad calculator SEO page"
```

---

### Task 4: Add the Guided Browser UI and Privacy-Safe Tracking

**Files:**
- Create: `src/retirement_calculator_ui.js`
- Modify: `src/build_unified_app.py` in `build_retirement_calculator_page()`
- Modify: `tests/test_retirement_calculator_page.py`
- Modify: `tests/test_retirement_calculator_engine.py`

**Interfaces:**
- Produces: `initRetirementCalculator(rootId: string, destinationData: object) -> void` on `window.GHARetirementCalculatorUI`.
- Consumes: `window.GHARetirementCalculator.calculateRetirement(input)`.
- Emits only: `retirement_calculator_open`, `retirement_calculator_calculate`, `retirement_calculator_destination_change`, `retirement_calculator_guide_click`, and `shortlist_review_click` with categorical labels and no financial values.

- [ ] **Step 1: Add failing interaction-contract tests**

Assert the generated page contains exact IDs for current age, retirement age, household, destination, spending, housing plan, pension, other income, destination rental income, indexed/fixed controls, portfolio-income preset, advanced assumptions, calculate button, error summary, result totals, and result assumptions. Assert `src/retirement_calculator_ui.js` contains no `localStorage`, `sessionStorage`, `fetch(`, `XMLHttpRequest`, or analytics payload keys named `spending`, `income`, `portfolio`, `property_price`, or `total_capital`.

- [ ] **Step 2: Run the contract tests and verify they fail**

Run: `python3 -m unittest tests.test_retirement_calculator_page -v`

Expected: FAIL because the UI module and required controls are missing.

- [ ] **Step 3: Implement form-to-engine input mapping**

Create `src/retirement_calculator_ui.js` as a browser-only IIFE. On destination, household, or housing changes, populate the editable annual-spending default from the selected profile and housing cost. Map healthcare to healthcare inflation, property purchase and owner costs to property inflation, and all remaining categories to general inflation. Treat the annual spending field as a proportional override of the source categories so category-specific inflation remains available.

- [ ] **Step 4: Implement guided defaults and results**

Render today's dollars and retirement-year dollars; liquid portfolio, property capital, reserve, and total; first-year expenses, outside income, and funding gap; illustrative cash income versus asset sales; guided withdrawal rate and sensitivity; data date and confidence. Use `Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 })` and never round calculation inputs before calling the engine.

- [ ] **Step 5: Implement validation and accessible disclosure behavior**

Catch engine errors, populate the error summary, focus the first invalid field, and preserve the prior valid result until the next successful calculation. Toggle advanced assumptions with a native `<details>` element. Keep the result region `aria-live="polite"`; do not announce every keystroke.

- [ ] **Step 6: Implement privacy-safe events**

Call `window.GHA.track()` only with destination ID, household type, housing plan, horizon band, and portfolio-income preset. Never include ages or any numeric spending, income, property, reserve, or capital values.

- [ ] **Step 7: Embed the UI module and run tests**

Have the builder read and embed `src/retirement_calculator_ui.js`, then initialize it after the engine and JSON data. Run:

`python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_calculator_engine -v`

Expected: all tests PASS.

- [ ] **Step 8: Commit the interactive calculator**

```bash
git add src/retirement_calculator_ui.js src/build_unified_app.py tests/test_retirement_calculator_page.py tests/test_retirement_calculator_engine.py artifacts/retirement-abroad-calculator/index.html
git commit -m "feat: add guided retirement calculator interactions"
```

---

### Task 5: Integrate the SEO Page Into Navigation and Verification

**Files:**
- Modify: `src/build_unified_app.py:1370-1450`
- Modify: `src/build_unified_app.py:3460-3700`
- Modify: `src/build_unified_app.py:4000-4300`
- Modify: `src/build_unified_app.py:5000-5350`
- Modify: `scripts/verify_static_site.py`
- Modify: `tests/test_retirement_calculator_page.py`
- Modify: `docs/CHANGELOG.md`

**Interfaces:**
- Produces valid links to `/retirement-abroad-calculator/` from the guide hub, two retirement guides, and relevant country/destination pages.
- Adds calculator page to static-site required markers and link verification.

- [ ] **Step 1: Write failing internal-link and sitemap tests**

Assert `/guides/`, `/buying-property-abroad-for-retirement/`, and `/best-places-to-buy-property-abroad-for-retirement/` each contain `/retirement-abroad-calculator/`. Assert at least one covered destination and one covered country hub link to it. Parse `sitemap.xml` and assert the canonical calculator URL appears exactly once.

- [ ] **Step 2: Run the linking tests and verify they fail**

Run: `python3 -m unittest tests.test_retirement_calculator_page -v`

Expected: FAIL for missing internal links.

- [ ] **Step 3: Add focused internal links**

Add one calculator card to the guide hub's retirement path. Add one contextual calculator link to each of the two retirement guides. Add a compact retirement-capital link only to destination/country pages represented in the release dataset; derive eligibility from destination IDs instead of duplicating a hard-coded list.

- [ ] **Step 4: Extend static verification**

Add the calculator page to `KEY_PAGES` and require these markers:

```python
ARTIFACTS / "retirement-abroad-calculator" / "index.html": [
    "Retirement Abroad Calculator",
    "Retirement cost benchmarks by destination",
    "Portfolio dividends and interest",
]
```

Keep the broken-local-link scan unchanged so the new routes participate automatically.

- [ ] **Step 5: Update the changelog**

Add a dated entry describing the indexable calculator, source-audited eight-destination data, client-side privacy, and internal-link integration. Do not claim personalized financial advice or predictive accuracy.

- [ ] **Step 6: Rebuild and run verification**

Run:

```bash
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 66
python3 -m unittest tests.test_retirement_calculator_page tests.test_static_guides -v
```

Expected: build succeeds, static verification passes, and tests pass.

- [ ] **Step 7: Commit SEO integration**

```bash
git add src/build_unified_app.py scripts/verify_static_site.py tests/test_retirement_calculator_page.py docs/CHANGELOG.md artifacts
git commit -m "feat: integrate retirement calculator into SEO routes"
```

---

### Task 6: Perform Full Regression and Mobile Visual Verification

**Files:**
- Modify only if verification exposes a defect: `src/build_unified_app.py`, `src/retirement_calculator.js`, `src/retirement_calculator_ui.js`, or related tests.
- Generate ignored evidence under: `output/playwright/retirement-calculator/`

**Interfaces:**
- Verifies the complete static deliverable without changing public interfaces.

- [ ] **Step 1: Run the full test suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests PASS.

- [ ] **Step 2: Rebuild and verify the complete site**

Run:

```bash
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 66
```

Expected: both commands exit `0` and no broken local links are reported.

- [ ] **Step 3: Exercise calculator behavior in a real browser**

Serve `artifacts/` locally and use Playwright CLI to open `/retirement-abroad-calculator/`. Verify single and couple profiles, all three housing plans, indexed and fixed income, zero funding gap, advanced assumptions, invalid age handling, and a destination change. Confirm the displayed totals match direct `calculateRetirement()` calls for the same inputs.

- [ ] **Step 4: Capture mobile and desktop screenshots**

Capture full-page screenshots at 320, 375, 390, 430, 736, and 1024 CSS pixels. Save them under `output/playwright/retirement-calculator/`. Inspect every image for horizontal overflow, clipped text, overlapping controls, unreadable tables, and poor result hierarchy.

- [ ] **Step 5: Verify metadata and analytics privacy**

Inspect the final HTML and browser events. Confirm one canonical, one H1, valid JSON-LD parse, visible benchmark content without script execution, calculator URL in sitemap, and no raw financial values in analytics calls or browser storage.

- [ ] **Step 6: Fix any discovered defects test-first and rerun verification**

For each defect, add or strengthen the narrowest failing test, reproduce the failure, implement the minimal fix, and rerun the affected test plus the full suite.

- [ ] **Step 7: Commit final verification fixes if needed**

```bash
git add src data tests scripts docs artifacts
git commit -m "fix: complete retirement calculator verification"
```

Skip this commit when verification required no tracked-file changes.
