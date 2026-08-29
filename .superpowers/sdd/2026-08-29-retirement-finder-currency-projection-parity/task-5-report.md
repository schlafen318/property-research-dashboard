## Task 5 report

Replaced the retirement destination finder's flex-button projection with the calculator-family editorial SVG.

- Added pure `finderProjectionModel` and `finderProjectionTooltip` APIs for a target-aware scale and age-aware selected-currency labels.
- The chart now uses the closest sorted recommendation for every calculable housing plan; buy-now projections are explicitly titled for that destination.
- Added a target reference line, sparse year labels, selected-currency caption, focusable annual SVG groups, pointer/keyboard tooltips, and reduced-motion behavior.
- Added labelled SVG title/description semantics and a useful no-projection fallback.
- Matched the detailed calculator's green portfolio bars, brown target line, dark tooltip, and regular-weight disclosure summaries.
- Removed the obsolete flex-bar and mobile-width implementation without changing finder ranking or currency/result behavior.

### TDD evidence

- RED: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui` failed with two missing-function errors and two expected markup/style failures.
- GREEN focused: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui` — 35 tests passed.
- GREEN full: `python3 -m unittest` — 896 tests passed.
- `git diff --check -- src tests` passed.

### Files changed

- `src/retirement_destination_finder_page.py`
- `src/retirement_destination_finder_ui.js`
- `src/site_design_system.py`
- `tests/test_retirement_destination_finder_page.py`
- `tests/test_retirement_destination_finder_ui.py`

Generated artifacts and unrelated changes were not staged.

## Fix round 1

Addressed the projection review findings:

- Sparse visible x-axis labels now pair elapsed years with the corresponding age.
- A horizontally scrollable chart viewport and 640px SVG minimum width preserve legibility on narrow screens.
- Added pure `finderProjectionView` coverage proving non-buy-now uses the shared series while buy-now uses the closest sorted recommendation's destination-specific series, target, and heading.
- Focusable annual points now use non-button image semantics while retaining complete accessible labels and focus-triggered tooltips.

### Fix verification

- RED: the focused finder page/UI suite failed with three missing-helper errors and two expected markup/semantics failures.
- GREEN focused: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui` — 39 tests passed.
- GREEN full: `python3 -m unittest` — 900 tests passed.
- `git diff --check -- src tests` passed.
