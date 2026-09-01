# Task 3 report — progressive calculator controls and results

Date: 2026-09-01

## Outcome

Implemented progressive tax controls on both retirement tools and tax-adjusted result presentation on the retirement calculator.

- The only modes are `destination_estimate` and `user_after_tax`.
- Destination estimates reveal dependable income, withdrawals, realized-gain intensity, property use when buying, and wealth band only when the jurisdiction evidence requires it.
- User-supplied figures explicitly describe the return as after fees and tax and disable the destination-tax inputs.
- The calculator calls the shared `estimateTaxScenario` and `calculateTaxAdjustedScenarios` engines. Rendering does not recompute tax.
- The central estimate is the headline. Favorable/adverse bounds and the labeled no-added-destination-tax comparison follow it.
- One disclosure contains the scenario table, assumptions, formulas, explanations, confidence/tax-year metadata, and source links.
- Missing jurisdiction evidence produces a conditional unavailable state; it does not silently fall back to a no-tax headline.
- The bypass path does not require `amountExplanations` and does not fabricate tax metadata.
- Tax and financial fields remain in memory only and are absent from URLs and analytics payloads.
- The FIRE property-use field now remains hidden and disabled for rent because `[hidden]` overrides the grid label rule.

## TDD evidence

Initial rendered-page/helper RED:

```text
$ python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_destination_finder_page tests.test_fire_abroad_page -v
Ran 67 tests in 1.672s
FAILED (failures=7)
```

The seven expected failures covered missing calculator/finder progressive visibility helpers, missing calculator tax result structure and presentation helper, missing result targets, and the FIRE `[hidden]` cascade bug.

The real 320px browser sweep exposed an intrinsic fieldset overflow. A focused regression was added first:

```text
$ python3 -m unittest tests.test_retirement_calculator_page.RetirementCalculatorPageTests.test_calculator_panels_allow_320_px_intrinsic_shrink -v
Ran 1 test
FAILED (failures=1)
```

After adding `min-width:0` to the calculator panel and fieldset:

```text
Ran 1 test
OK
```

The scripted-disabled fallback was also test-first:

```text
$ python3 -m unittest tests.test_retirement_destination_finder_page.RetirementDestinationFinderPageTests.test_script_disabled_page_keeps_context_and_warns_that_results_need_javascript -v
Ran 1 test in 0.593s
FAILED (failures=1)
```

After adding the minimal `noscript` notice:

```text
Ran 1 test in 0.580s
OK
```

The first expanded focused run correctly found two stale pre-Task-3 contract assertions (tax excluded and pre-tax return basis):

```text
Ran 126 tests in 9.460s
FAILED (failures=2)
```

The copy and assertions were aligned to the new explicit tax contract. Final focused GREEN:

```text
$ python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_calculator_ui tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui tests.test_fire_abroad_page tests.test_fire_abroad_js -v
Ran 126 tests in 9.098s
OK
```

Full-suite GREEN:

```text
$ python3 -m unittest -q 2>&1 | rg "^Ran [0-9]+ tests|^OK$|^FAILED"
Ran 956 tests in 19.853s
OK
```

Additional verification:

```text
$ node --check src/retirement_calculator_ui.js
[exit 0]
$ node --check src/retirement_destination_finder_ui.js
[exit 0]
$ python3 -m py_compile src/build_unified_app.py src/retirement_destination_finder_page.py src/fire_abroad_page.py tests/test_retirement_calculator_page.py tests/test_retirement_calculator_ui.py tests/test_retirement_destination_finder_page.py tests/test_fire_abroad_page.py
[exit 0]
$ git diff --check
[exit 0]
```

## Real-browser checks

Playwright exercised the generated HTML served locally, rather than inspecting source alone.

- Calculator, default Fukuoka scenario: central `$1,408,697`; favorable/adverse range `$1,373,182–$1,467,889`; labeled no-tax comparison `$1,349,505`.
- Valencia + buy now: property-use and conditional wealth-band inputs became available; central `$2,133,464`; range `$2,056,300–$2,320,861`; no-tax comparison `$2,034,253`.
- The expanded table rendered favorable, central, and adverse rows in that order, with official Agencia Tributaria source links.
- `user_after_tax` hid and disabled destination-tax inputs and retained the explicit “Expected annual portfolio return after fees and tax (%)” label.
- Unsupported Aspen destination evidence displayed the conditional unavailable message and hid the headline figures.
- Calculator widths `320, 375, 390, 430, 736, 1024` all had body/document widths equal to the viewport after the fieldset fix.
- Finder widths `320, 375, 390, 430, 736, 1024` all had body/document widths equal to the viewport.
- With JavaScript disabled at 320px, both pages kept their forms readable, showed their `noscript` notices, and had no horizontal overflow.

## Files changed

- `src/build_unified_app.py`
- `src/retirement_calculator_ui.js`
- `src/retirement_destination_finder_page.py`
- `src/retirement_destination_finder_ui.js`
- `src/fire_abroad_page.py`
- `tests/test_retirement_calculator_page.py`
- `tests/test_retirement_calculator_ui.py`
- `tests/test_retirement_destination_finder_page.py`
- `tests/test_fire_abroad_page.py`
- `.superpowers/sdd/2026-09-01-fire-tax-calculator/task-3-report.md`

## Self-review

- Confirmed tax rendering consumes Task 1/2 results and does not duplicate their tax calculations.
- Confirmed the only query-prefill keys remain destination, household, and housing.
- Confirmed analytics calls contain event names and existing categorical context only; tax profiles, financial inputs, tax outputs, and explanation metadata are not transmitted or persisted.
- Confirmed hidden progressive inputs are also disabled, preventing focus and constraint-validation traps.
- Confirmed source links and evidence metadata are created as DOM text/anchors rather than interpolated personalized HTML.
- Confirmed generated `artifacts/**` changes were left un-staged.

## Concerns / follow-up

- The finder now collects the progressive tax profile in memory, but Task 4 remains responsible for applying the tax-adjusted target to its ranking.
- “Refine the tax profile” is an honest unavailable hook in this task; it does not claim a workflow that has not been built.
- These are broad scenario allowances, not individualized tax or treaty advice; unsupported or stale jurisdiction evidence intentionally remains unavailable.
