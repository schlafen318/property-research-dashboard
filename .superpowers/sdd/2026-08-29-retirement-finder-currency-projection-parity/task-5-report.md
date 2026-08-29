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
