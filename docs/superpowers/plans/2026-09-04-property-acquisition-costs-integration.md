# Property Acquisition Costs Current-Main Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate sourced buyer-side acquisition costs and all-in acquisition capital into current `main` for all 37 destinations without regressing newer calculator, finder, FIRE-tax, guide, or dossier behavior.

**Architecture:** Start from current `main` and port only the legacy branch's acquisition tests, pure calculation module, schema fixtures, and researched dataset. Migrate the Málaga identifier, research seven complete new records, revalidate the historical records, then add acquisition-specific hooks to the current builder behind focused tests. The builder must validate exact 37-record parity before writing artifacts.

**Tech Stack:** Python 3.11 standard library, JSON, `unittest`, the existing static HTML/CSS/JavaScript generator, and GitHub Actions Pages deployment.

**Spec:** `docs/superpowers/specs/2026-08-19-property-acquisition-costs-design.md`

**Legacy source:** `feat/acquisition-costs`, preserved at `codex/acquisition-costs-pre-rebase-2026-09-03`.

## Global Constraints

- Work only on `codex/integrate-acquisition-costs` in `/Users/steph-tmp/Documents/GitHub/property-research-dashboard/.worktrees/acquisition-costs`.
- Never restore the legacy `src/build_unified_app.py` or `artifacts/` wholesale.
- Use the fixed rates in `data/fx_rates.json`; do not fetch live FX or round intermediate calculations.
- Model a nonresident foreign individual buying a completed resale second home for cash, without reliefs.
- Unknown or buyer-specific costs stay conditional; never encode an unknown amount as zero.
- Use authoritative, current sources for legal eligibility, taxes, government charges, and foreign-buyer surcharges.
- Preserve property-price evidence independently from acquisition-cost confidence.
- Do not publish until the acquisition dataset has exact ID parity with current `data/destinations.json`.
- Every new integration behavior follows red-green-refactor.
- Before every commit, inspect `git status --short` and stage only the active task's files.

---

### Task 1: Establish the Current-Main Test Contract

**Files:**
- Create: `tests/test_acquisition_costs.py`
- Create: `tests/test_acquisition_cost_dataset.py`
- Create: `tests/test_acquisition_cost_integration.py`
- Create: `tests/test_acquisition_cost_reconciliation.py`
- Create: `tests/fixtures/acquisition_cost_record.json`

**Interfaces:**
- Consumes: legacy versions of the five files from `feat/acquisition-costs`.
- Produces: failing tests for `validate_acquisition_dataset`, `calculate_acquisition_costs`, builder enrichment, rendered surfaces, and artifact reconciliation.

- [ ] **Step 1: Port only acquisition tests and the synthetic fixture**

Use `apply_patch` to reproduce the five files from `feat/acquisition-costs`. Do not port production code or artifacts.

- [ ] **Step 2: Update the dataset contract to current IDs**

Change exact parity from 30 to 37, replace `m-laga-costa-del-sol` with `malaga-costa-del-sol`, and assert these IDs occur exactly once:

```python
ADDED_DESTINATION_IDS = {
    "dubai",
    "gold-coast-sunshine-coast",
    "los-angeles-orange-county",
    "miami-fort-lauderdale",
    "perth-margaret-river",
    "sydney-melbourne",
    "vancouver",
}
```

- [ ] **Step 3: Verify RED**

Run:

```bash
python3 -m unittest tests.test_acquisition_costs tests.test_acquisition_cost_dataset tests.test_acquisition_cost_integration tests.test_acquisition_cost_reconciliation -v
```

Expected: import failure for missing `src.acquisition_costs`; no syntax or fixture errors.

- [ ] **Step 4: Commit the red contract**

```bash
git add tests/test_acquisition_costs.py tests/test_acquisition_cost_dataset.py tests/test_acquisition_cost_integration.py tests/test_acquisition_cost_reconciliation.py tests/fixtures/acquisition_cost_record.json
git commit -m "test: define current acquisition cost contract"
```

### Task 2: Port the Pure Engine and Historical Data

**Files:**
- Create: `src/acquisition_costs.py`
- Create: `data/acquisition_costs.json`
- Create: `data/property_comparison_methodology.json`
- Create: `tests/test_property_comparison_methodology.py`

**Interfaces:**
- Produces: `AcquisitionCostDataError`, `validate_acquisition_dataset(dataset, expected_destination_ids, fx_rates_to_usd)`, and `calculate_acquisition_costs(destination, property_price_usd, fx_rates_to_usd)`.
- Preserves: calculation types `fixed`, `rate`, `progressive`, `fixed_plus_rate`, `range_rate`, `range_fixed`, and `manual`.

- [ ] **Step 1: Port the four non-generated files**

Use `apply_patch` with the exact legacy files as the source. Do not copy the legacy builder.

- [ ] **Step 2: Migrate Málaga**

Change only the destination identifier from `m-laga-costa-del-sol` to `malaga-costa-del-sol` in the acquisition and comparison-methodology datasets. Preserve sourced values, calculations, jurisdiction notes, and confidence.

- [ ] **Step 3: Verify the pure engine GREEN**

```bash
python3 -m unittest tests.test_acquisition_costs -v
```

Expected: all pure engine tests pass. The comparison-methodology suite remains red until the current builder receives its loader and enrichment hooks in Task 5.

- [ ] **Step 4: Verify the dataset RED boundary**

```bash
python3 -m unittest tests.test_acquisition_cost_dataset -v
```

Expected: the dataset parity failure names the seven added destination IDs. Exact-price guards may also identify historical records whose current `usd_per_m2` benchmark changed after the legacy research; preserve those failures for source revalidation in Task 4 rather than weakening the guards.

- [ ] **Step 5: Commit**

```bash
git add src/acquisition_costs.py data/acquisition_costs.json data/property_comparison_methodology.json tests/test_property_comparison_methodology.py
git commit -m "feat: port acquisition cost engine and historical data"
```

### Task 3: Research the Seven Added Destinations

**Files:**
- Modify: `data/acquisition_costs.json`
- Test: `tests/test_acquisition_cost_dataset.py`

**Interfaces:**
- Each record supplies `destination_id`, `local_currency`, `jurisdiction_basis`, `purchase_route`, sourced base and conditional `components`, `confidence`, `reviewed_on`, and `review_notes`.
- Every source supplies an HTTPS URL, authority, supported metric, source date, access date, and notes.

- [ ] **Step 1: Research Dubai and write a failing record test**

Use Dubai Land Department and UAE government sources to verify designated-area eligibility, transfer/registration charges, trustee or registration-centre charges, and any buyer-specific items. Add a test requiring `dubai` to validate and reconcile at its current comparison-home price; run it before adding the record and confirm the expected missing-record failure.

- [ ] **Step 2: Add and verify Dubai**

Add the complete `dubai` record. Run:

```bash
python3 -m unittest tests.test_acquisition_cost_dataset -v
```

Expected: Dubai passes; only the six other added IDs remain missing.

Stage and commit the Dubai record and its test:

```bash
git add data/acquisition_costs.json tests/test_acquisition_cost_dataset.py
git commit -m "data: add Dubai acquisition costs"
```

- [ ] **Step 3: Research Australia and write failing record tests**

For `gold-coast-sunshine-coast`, `perth-margaret-river`, and `sydney-melbourne`, use Australian Treasury/ATO foreign-investment guidance plus Queensland, Western Australia, New South Wales, and Victoria revenue authorities. Verify whether the baseline nonresident buyer may acquire an established resale dwelling. Model unavailable or conditional routes explicitly; retain statutory duty and foreign-buyer charge context without presenting an ordinary all-in total when the route is unavailable.

- [ ] **Step 4: Add and verify the three Australian records**

Add complete records and run the dataset suite. Expected: the Australian records validate; only Los Angeles, Miami, and Vancouver remain missing.

Stage and commit the Australian records and their tests:

```bash
git add data/acquisition_costs.json tests/test_acquisition_cost_dataset.py
git commit -m "data: add Australian acquisition routes"
```

- [ ] **Step 5: Research North America and write failing record tests**

For `los-angeles-orange-county`, use California and relevant county/city recording and transfer-tax authorities. For `miami-fort-lauderdale`, use Florida and Miami-Dade/Broward official sources. For `vancouver`, use the Government of Canada foreign-buyer prohibition and British Columbia property-transfer-tax sources. Separate seller-paid, negotiable, financing, inspection, title/escrow, and buyer-specific items from mandatory baseline buyer costs.

- [ ] **Step 6: Add and verify the three North American records**

Add complete records. Run:

```bash
python3 -m unittest tests.test_acquisition_cost_dataset tests.test_acquisition_costs -v
```

Expected: 37 unique IDs, exact parity with `data/destinations.json`, and all calculations reconciled.

- [ ] **Step 7: Commit the North American batch**

```bash
git add data/acquisition_costs.json tests/test_acquisition_cost_dataset.py
git commit -m "data: add North American acquisition costs"
```

### Task 4: Revalidate the Historical Dataset

**Files:**
- Modify: `data/acquisition_costs.json`
- Test: `tests/test_acquisition_cost_dataset.py`

**Interfaces:**
- Consumes: the 30 historical records and their existing source URLs.
- Produces: 37 records reviewed for publication on 2026-09-04 with unchanged values where sources remain current and explicit edits where rules or routes changed.

- [ ] **Step 1: Validate every cited source mechanically**

Check all source URLs for HTTPS, nonempty metric/date fields, unique source IDs per destination, and resolvable component references through the dataset test.

- [ ] **Step 2: Recheck high-risk purchase routes**

Reopen authoritative sources for New Zealand, Thailand, Indonesia, Vietnam, Austria, Switzerland, and Canada. Confirm the route remains available, conditional, or unavailable for the agreed baseline buyer.

- [ ] **Step 3: Recheck progressive schedules and foreign-buyer surcharges**

Verify current official schedules for Spain, Portugal, France, Greece, British Columbia, and the representative US jurisdictions. Add a failing regression test before changing any calculation behavior.

- [ ] **Step 4: Record the review**

Set `reviewed_on` only after the corresponding record is checked. Keep original source dates and access dates; add a new source or note when current guidance differs.

- [ ] **Step 5: Verify and commit**

```bash
python3 -m unittest tests.test_acquisition_costs tests.test_acquisition_cost_dataset -v
git add data/acquisition_costs.json tests/test_acquisition_cost_dataset.py
git commit -m "data: revalidate acquisition cost research"
```

### Task 5: Integrate the Model into the Current Builder

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_acquisition_cost_integration.py`
- Modify: `tests/test_property_comparison_methodology.py`

**Interfaces:**
- Produces: `load_acquisition_costs()`, `add_comparison_home_estimate(destination, methodology)`, `add_acquisition_cost_estimate(destination, acquisition_record, fx_rates_to_usd)`, and conservative acquisition fields in `country_summary_metrics`.
- Preserves: current retirement calculator, destination finder, FIRE-tax, country-guide, premium-dossier, routing, and analytics behavior.

- [ ] **Step 1: Run builder integration tests RED**

```bash
python3 -m unittest tests.test_acquisition_cost_integration tests.test_property_comparison_methodology -v
```

Expected: missing acquisition loader/enrichment and output fields.

- [ ] **Step 2: Add loaders and validation before artifact writes**

Load FX, comparison methodology, and acquisition data. Validate exact destination parity before calculating or writing files.

- [ ] **Step 3: Add pure enrichment**

Calculate against the unrounded 100 m² comparison-home value and expose low/estimate/high cost, effective rate, all-in capital, component lists, conditional components, purchase route, confidence, jurisdiction, and review date.

- [ ] **Step 4: Add conservative country aggregation**

Exclude unavailable routes from numeric averages, return contributor/exclusion counts, and label evidence `aligned` only when all contributors have available routes and high or medium-high acquisition confidence.

- [ ] **Step 5: Run focused and regression suites GREEN**

```bash
python3 -m unittest tests.test_acquisition_cost_integration tests.test_property_comparison_methodology tests.test_retirement_calculator_page tests.test_retirement_destination_finder_page tests.test_fire_abroad -v
```

- [ ] **Step 6: Commit**

```bash
git add src/build_unified_app.py tests/test_acquisition_cost_integration.py tests/test_property_comparison_methodology.py
git commit -m "feat: integrate acquisition costs into current models"
```

### Task 6: Render Acquisition Costs Across Existing Surfaces

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_acquisition_cost_integration.py`

**Interfaces:**
- Dashboard/destination surfaces show property price, acquisition estimate/range, all-in capital, route, confidence, jurisdiction, sources, and one conditional-cost disclosure.
- Country/guide surfaces show conservative all-in figures with contributor/exclusion counts.
- JSON, CSV, and shortlist memo expose the reconciled acquisition fields.

- [ ] **Step 1: Add one failing assertion group per surface**

Cover dashboard, destination page, country comparison, country hub, guide table/cards, embedded JSON, CSV, shortlist memo, methodology, and research standards. Assert unavailable routes never show an ordinary all-in total.

- [ ] **Step 2: Implement minimal shared formatters**

Add percentage, nonduplicate range, route, and conditional-cost helpers. Reuse them; do not introduce decorative badges, repeated disclosures, or duplicate summary sections.

- [ ] **Step 3: Update destination and dashboard output**

Place acquisition information beside the existing property comparison. Add one acquisition section to destination pages with component table, conditional items, jurisdiction, buyer basis, review date, and source links.

- [ ] **Step 4: Update country, guide, export, memo, and trust output**

Add contributor/exclusion counts to aggregates. Append the specified acquisition columns after `comparison_home_evidence` in CSV output. Embed the complete acquisition methodology and calculated components in JSON.

- [ ] **Step 5: Verify focused output**

```bash
python3 -m unittest tests.test_acquisition_cost_integration -v
git diff --check
```

- [ ] **Step 6: Commit**

```bash
git add src/build_unified_app.py tests/test_acquisition_cost_integration.py
git commit -m "feat: publish all-in acquisition comparisons"
```

### Task 7: Regenerate and Verify the Entire Site

**Files:**
- Regenerate: `artifacts/`
- Verify: all source, data, tests, and output touched by Tasks 1–6.

- [ ] **Step 1: Run the full suite**

```bash
python3 -m unittest discover tests
```

Expected: zero failures.

- [ ] **Step 2: Build once from the final source**

```bash
python3 src/build_unified_app.py
```

- [ ] **Step 3: Run static and tracking verification**

```bash
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
```

- [ ] **Step 4: Reconcile all 37 embedded records**

Assert exact ID parity, finite values, low ≤ estimate ≤ high, property price plus base cost equals all-in capital, unavailable-route suppression, and resolvable HTTPS source links.

- [ ] **Step 5: Inspect representative rendered cases**

Inspect an aligned estimate, a range estimate, a conditional route, an unavailable route, a country aggregate with exclusions, CSV output, shortlist memo, methodology, and research standards.

- [ ] **Step 6: Run repository hygiene checks**

```bash
git diff --check
git status --short
```

- [ ] **Step 7: Commit generated output**

```bash
git add artifacts data/acquisition_costs.json src/acquisition_costs.py src/build_unified_app.py tests
git commit -m "feat: add comparable property acquisition costs"
```

### Task 8: Review, Merge, Deploy, and Clean Up

**Files:**
- No new source files.

- [ ] **Step 1: Review the final diff**

Review arithmetic, source traceability, base/conditional separation, route suppression, current-feature preservation, and minimal artifact presentation.

- [ ] **Step 2: Repeat full verification after review fixes**

Run the complete Task 7 verification set and require all commands to exit zero.

- [ ] **Step 3: Push and create the PR**

Push `codex/integrate-acquisition-costs`, create a PR against `main`, and include verification counts plus data review dates.

- [ ] **Step 4: Merge and deploy**

Merge the PR after checks pass. Monitor `Deploy static dashboard` through build, Pages deployment, and sitemap notification.

- [ ] **Step 5: Clean up**

Update local `main`, remove the integration worktree, and delete obsolete local and remote acquisition branches only after the merged result and deployment are verified.
