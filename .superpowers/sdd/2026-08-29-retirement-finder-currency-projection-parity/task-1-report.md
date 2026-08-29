# Task 1 report: Finder payload and currency-aware form markup

## Implementation

- Added `RETIREMENT_PLANNING_CURRENCIES` to the finder page payload as `planning_currencies`.
- Added the USD-default planning-currency selector with the nine specified currencies and the shared 27 August 2026 reference-rate note.
- Converted the five specified money controls to formatted, numeric-inputmode `data-money` text inputs, retaining their `min` and `step` values. Initial values are `500,000`, `2,000`, `300,000`, `0`, and `0`.
- Removed USD label suffixes, changed Step 3 to monthly income wording, and made both continuing-income indexation controls checked by default.

## Tests and results

- RED: `python3 -m unittest tests.test_retirement_destination_finder_page` failed as expected before implementation: 2 failures and 1 error for the absent currency selector, non-matching payload script/payload data, and legacy markup.
- GREEN: `python3 -m unittest tests.test_retirement_destination_finder_page` — 17 tests passed.
- Full suite: `python3 -m unittest` — 885 tests passed in 18.266 seconds.
- `git diff --check` passed for all task files.

## Files changed

- `src/build_unified_app.py`
- `src/retirement_destination_finder_page.py`
- `tests/test_retirement_destination_finder_page.py`

## Self-review

- Confirmed the generated finder payload exposes the required reference date and currency order.
- Confirmed USD is selected by default, SGD is available, each specified monetary control has the required markup, no form label retains `(USD)`, and both income checkboxes are checked.
- Generated artifacts were not staged or committed.

## Concerns

- This task deliberately supplies formatted money fields and the currency payload only. The finder runtime still requires its subsequent task to parse formatted entries and apply currency conversions before the form can calculate correctly outside USD defaults.

## Fix round 1

- Corrected the missing closing parenthesis in the main finder result-grid `grid-template-columns` declaration and removed the compensating duplicate stylesheet rule.
- Added a generated-page regression test that requires the valid three-column declaration and rejects the duplicate compensating style.
- RED: `python3 -m unittest tests.test_retirement_destination_finder_page` — 1 failure on the malformed CSS declaration.
- GREEN: focused suite — 18 tests passed; full suite — 886 tests passed in 17.205 seconds.
