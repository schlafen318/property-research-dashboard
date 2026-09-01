# Task 1 Report: Tax-scenario contract and calculator engine boundary

## Status

Implemented and committed-ready.

## Files Changed

- `src/fire_tax_scenarios.js`
- `src/retirement_calculator.js`
- `src/fire_abroad.py`
- `data/fire_abroad.json`
- `tests/test_fire_tax_scenarios.py`
- `tests/fixtures/fire_tax_scenarios.json`
- `tests/test_retirement_calculator_engine.py`

## Behavior Implemented

- Added `estimateTaxScenario(input, countryRecord)`.
- Returns ordered `favorable`, `central`, and `adverse` scenario cases.
- Computes planning base from `dependableIncome + portfolioWithdrawals`.
- Uses validated `planning_bands`, `gain_intensity_modifiers`, and `annual_allowances` from country tax-screen data.
- Itemizes income-tax, property-tax, wealth-tax, and compliance reserves.
- Returns source-backed explanation records and unique included source IDs.
- Treats missing/pending/stale evidence as `unavailable` with null totals, not zero.
- Explicitly excludes property tax when already included in retirement-cost owner records.
- Added validator coverage for gain-intensity and annual allowance data.
- Extended the retirement engine with `annualTaxExpenses`, `taxMode`, and `returnBasis`.
- Projects `annualTaxExpenses` with general inflation.
- Defaults legacy calculator calls to `user_after_tax`.
- Rejects `destination_estimate` without scenario expenses.
- Rejects tax-adjusted calculations unless `returnBasis === "after_fees_and_tax"`.

## RED

Command:

```bash
python3 -m unittest tests.test_fire_tax_scenarios tests.test_retirement_calculator_engine -v
```

Output summary from first RED run:

```text
test_destination_estimate_returns_ordered_data_backed_cases ... ERROR
test_fire_abroad_validation_requires_tax_scenario_assumptions ... FAIL
test_gain_intensity_modifier_changes_only_the_income_tax_reserve ... ERROR
test_missing_or_pending_scenario_evidence_is_unavailable_not_zero ... ERROR
test_property_tax_already_in_owner_costs_is_excluded_explicitly ... ERROR
test_annual_tax_expenses_are_inflated_with_general_expenses ... FAIL
test_destination_estimate_requires_scenario_expenses ... FAIL
test_tax_adjusted_expenses_require_after_tax_return_basis ... FAIL

Ran 26 tests in 2.155s

FAILED (failures=4, errors=4)
```

Expected failures:

- `src/fire_tax_scenarios.js` did not exist yet.
- `validate_fire_abroad_payload` did not reject missing scenario assumptions.
- `retirement_calculator.js` ignored `annualTaxExpenses`.
- `retirement_calculator.js` did not reject missing destination-estimate scenario expenses.
- `retirement_calculator.js` did not reject tax-adjusted results with a gross return basis.

Additional stale-evidence RED after adding that missing brief requirement:

```text
test_stale_scenario_evidence_is_unavailable_not_zero ... FAIL

AssertionError: 'unavailable' != 'available'

Ran 27 tests in 2.219s

FAILED (failures=1)
```

## GREEN

Focused command:

```bash
python3 -m unittest tests.test_fire_tax_scenarios tests.test_retirement_calculator_engine -v
```

Output:

```text
Ran 27 tests in 2.223s

OK
```

Full command:

```bash
python3 -m unittest -q
```

Output:

```text
----------------------------------------------------------------------
Ran 936 tests in 18.767s

OK
```

The full suite also emitted existing dry-run SEO notification/control logs after the unittest OK summary.

## Self-review

- Confirmed no generated artifacts were staged or changed by this task.
- Confirmed tax inputs/results are only in function payloads/return objects; no analytics, URL, HTML personalization, or storage writes were added.
- Confirmed the new data values are explicit product-defined planning allowances, not statutory rates or tax assessments.
- Confirmed source IDs support the exposure categories but the numeric allowances remain product assumptions.
- Confirmed legacy engine callers still work without specifying tax fields.

## Concerns

- `annual_allowances` values are planning reserves suitable for stress testing; they are not user-specific estimates and should be surfaced as such by later UI work.
- The scenario estimator only performs stale-date checks when `input.asOf` is supplied; callers should pass the FIRE payload review date or page as-of date when using live country data.
- Full-suite output includes noisy dry-run SEO monitor logs, including simulated GitHub unavailable/issue messages, but the unittest command exited 0 with `OK`.
