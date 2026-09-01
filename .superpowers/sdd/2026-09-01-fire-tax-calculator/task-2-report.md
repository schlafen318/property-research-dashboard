# Task 2 Report: Tax-adjusted capital scenarios

## RED Evidence

- Command: `python3 -m unittest tests.test_retirement_calculator_ui -v`
- Result: failed as expected before implementation.
- Failure: 4 new tax-adjusted scenario tests failed because `ui.calculateTaxAdjustedScenarios` was not exported (`TypeError: Cannot read properties of undefined (reading 'apply')`).
- Existing UI tests continued to pass during the RED run.

## GREEN Evidence

- Command: `python3 -m unittest tests.test_retirement_calculator_ui -v`
- Result: `Ran 39 tests in 5.041s` / `OK`.
- Command: `python3 -m unittest -v`
- Result: `Ran 946 tests in 19.150s` / `OK`.
- Note: the full suite emitted existing dry-run SEO notification logs after the passing test summary.

## Files Changed

- `src/retirement_calculator_ui.js`
- `tests/test_retirement_calculator_ui.py`
- `.superpowers/sdd/2026-09-01-fire-tax-calculator/task-2-report.md`

## Implementation Summary

- Added `calculateTaxAdjustedScenarios(baseInput, taxScenario)` to the UI helper export.
- Clones calculator inputs before each engine invocation.
- Uses explicit `annualTaxExpenses`, `taxMode`, and `returnBasis: "after_fees_and_tax"` for destination tax cases.
- Uses explicit `taxMode: "user_after_tax"` and zero added annual tax for the no-tax comparison and user-after-tax bypass.
- Returns ordered favorable, central, and adverse summaries for destination estimates.
- Returns one `user_after_tax` summary for after-tax bypass mode.
- Each summary includes annual tax reserve, projected annual tax expense, first-year expenses, funding gap, required capital, required-capital difference, labeled no-tax comparison, and the pure engine result.

## Self-review

- Central scenario is tested against a direct pure-engine call using the central tax expense.
- Scenario ordering is tested by required capital.
- Existing annual tax inputs are replaced rather than accumulated, preventing double counting.
- Property tax exclusion is respected by consuming the TaxScenario case total as supplied by Task 1.
- `destination_estimate` calls use `returnBasis: "after_fees_and_tax"` explicitly.
- `user_after_tax` does not require `amountExplanations`.

## Concerns

- The helper returns calculation summaries but is not yet wired into the visible retirement calculator UI.
