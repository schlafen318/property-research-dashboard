# Calculator Demand Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a privacy-safe calculator demand funnel and honest save-intent test before investing in account infrastructure.

**Architecture:** Keep all behavior in the existing static calculator UI and shared analytics layer. Render a hidden result action in the generated page, reveal it only after a valid calculation, track the first valid result once in memory, and let the existing declarative click tracker record save intent. Pass GA4 configuration through the existing GitHub Pages build and document the go/no-go report.

**Tech Stack:** Python static generator, browser JavaScript, `unittest`, GitHub Actions, GA4.

**Spec:** `docs/superpowers/specs/2026-08-20-calculator-demand-validation-design.md`

## Global Constraints

- Do not persist or transmit calculator inputs or result values.
- Do not add authentication, accounts, a database, an email form, or a fake saved state.
- Use only plain text and one secondary action; add no pills, badges, or repeated summaries.
- Emit `retirement_calculator_result_view` once per page load after the first valid result.
- Emit `retirement_calculator_save_intent` through the existing declarative click tracker.
- Keep one canonical calculator URL and the existing static-generation architecture.

---

### Task 1: Lock the calculator demand-funnel contract

**Files:**
- Modify: `tests/test_retirement_calculator_page.py`
- Modify: `tests/test_retirement_calculator_ui.py`

**Interfaces:**
- Consumes: generated `artifacts/retirement-abroad-calculator/index.html` and `src/retirement_calculator_ui.js`.
- Produces: regression contracts for `ret-save-action`, `ret-save-intent-status`, `retirement_calculator_result_view`, and `retirement_calculator_save_intent`.

- [ ] **Step 1: Write the failing generated-page test**

Add a test asserting that the result panel contains a hidden `ret-save-action`, a button labeled `Save this plan` with `data-track="retirement_calculator_save_intent"`, and a hidden status message containing `Your figures have not been stored`. Assert there is no signup form, account modal, or password field.

- [ ] **Step 2: Run the page test and verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_page.RetirementCalculatorPageTests.test_result_card_contains_honest_save_intent_test`

Expected: FAIL because the save-intent markup is absent.

- [ ] **Step 3: Write the failing UI source contract**

Add a test asserting that the UI module contains `retirement_calculator_result_view`, an in-memory first-result guard, and code that reveals `ret-save-action` after rendering. Retain the existing forbidden checks for `localStorage`, `sessionStorage`, `fetch(`, `XMLHttpRequest`, and financial payload keys.

- [ ] **Step 4: Run the UI test and verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_ui.RetirementCalculatorUITests.test_first_valid_result_is_tracked_once_and_reveals_save_intent`

Expected: FAIL because first-result tracking and save-action reveal behavior are absent.

### Task 2: Implement the calculator save-intent experience

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `src/retirement_calculator_ui.js`
- Generated: `artifacts/retirement-abroad-calculator/index.html`

**Interfaces:**
- Consumes: `window.GHA.track(eventName, params)` and the existing calculator `render(result)` path.
- Produces: `ret-save-action`, `ret-save-intent-button`, `ret-save-intent-status`, and a single in-memory `hasTrackedResult` guard.

- [ ] **Step 1: Add the minimal hidden save-intent markup**

Place a hidden block after the key figures with one secondary button and one hidden `role="status"` message. The message must say: `Saved plans are being evaluated. Your figures have not been stored.`

- [ ] **Step 2: Add first-result and save-intent behavior**

Initialize `hasTrackedResult` to `false` inside `initRetirementCalculator`. After the first successful `render`, call `track("retirement_calculator_result_view")`, set the guard to `true`, and reveal `ret-save-action`. On save-button activation, hide the button and reveal `ret-save-intent-status`; do not manually track the click because `data-track` already does so.

- [ ] **Step 3: Run focused tests and verify GREEN**

Run: `python3 src/build_unified_app.py && python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_calculator_ui`

Expected: PASS.

### Task 3: Make acquisition measurable without adding clutter

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_retirement_calculator_page.py`
- Modify: `tests/test_static_guides.py`
- Generated: `artifacts/guides/index.html`
- Generated: relevant guide, country, and destination HTML under `artifacts/`

**Interfaces:**
- Consumes: `retirement_calculator_callout(css_class, source_label)`.
- Produces: fixed `data-track-label` values for guide hub, buying guide, country hub, and destination callouts.

- [ ] **Step 1: Write failing acquisition-route tests**

Assert every existing calculator callout includes a non-empty fixed `data-track-label`, the guide hub contains one calculator callout, and that callout appears before `guide-catalog`.

- [ ] **Step 2: Run the route tests and verify RED**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_static_guides`

Expected: FAIL because callout source labels are absent and the guide-hub callout is after the catalog.

- [ ] **Step 3: Add source labels and move the existing guide-hub callout**

Extend `retirement_calculator_callout` with a required fixed `source_label`. Pass context-specific labels at all four call sites. Move, rather than duplicate, the guide-hub callout to immediately after the buying-goal journey section.

- [ ] **Step 4: Rebuild and verify GREEN**

Run: `python3 src/build_unified_app.py && python3 -m unittest tests.test_retirement_calculator_page tests.test_static_guides`

Expected: PASS.

### Task 4: Enable aggregate production measurement

**Files:**
- Modify: `.github/workflows/deploy-pages.yml`
- Modify: `README.md`
- Create: `tests/test_deploy_analytics_config.py`

**Interfaces:**
- Consumes: GitHub Actions secret `GA4_MEASUREMENT_ID`.
- Produces: build environment variable `GA4_MEASUREMENT_ID` and documented GA4 key-event setup.

- [ ] **Step 1: Write the failing workflow contract**

Create a test that reads `.github/workflows/deploy-pages.yml` and asserts the build step maps `GA4_MEASUREMENT_ID` to `${{ secrets.GA4_MEASUREMENT_ID }}`.

- [ ] **Step 2: Run the workflow test and verify RED**

Run: `python3 -m unittest tests.test_deploy_analytics_config`

Expected: FAIL because the deployment build does not receive the secret.

- [ ] **Step 3: Wire the secret and document activation**

Add the secret to the build step's `env` map. In `README.md`, document that the repository secret must be configured and that `retirement_calculator_result_view` and `retirement_calculator_save_intent` should be marked as GA4 key events. Record the 300 visits / 100 results / 15 save-intents threshold and the four-week minimum.

- [ ] **Step 4: Run the workflow test and verify GREEN**

Run: `python3 -m unittest tests.test_deploy_analytics_config`

Expected: PASS.

### Task 5: Verify the complete validation release

**Files:**
- Verify: all source, tests, workflow, documentation, and generated artifacts changed above.

**Interfaces:**
- Consumes: the complete static build.
- Produces: a deployable calculator demand-validation release.

- [ ] **Step 1: Run the full build and test suite**

Run: `python3 src/build_unified_app.py && python3 -m unittest discover -s tests`

Expected: all tests PASS.

- [ ] **Step 2: Verify formatting and privacy boundaries**

Run: `git diff --check && rg -n "localStorage|sessionStorage|fetch\\(|XMLHttpRequest" src/retirement_calculator_ui.js`

Expected: `git diff --check` is clean, and the privacy search returns no matches.

- [ ] **Step 3: Verify in a browser**

At desktop and mobile widths, generate a valid result and confirm the save action appears, selecting it shows the honest non-storage message, the sticky card does not overlap the detailed projection, and no horizontal overflow or console errors occur.

- [ ] **Step 4: Commit the validation release**

Run: `git add .github/workflows/deploy-pages.yml README.md docs/superpowers/specs/2026-08-20-calculator-demand-validation-design.md docs/superpowers/plans/2026-08-20-calculator-demand-validation.md src/retirement_calculator_ui.js src/build_unified_app.py tests artifacts && git commit -m "feat: validate retirement calculator save demand"`

