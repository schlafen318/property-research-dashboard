# Final broad-review fix round 1

## Changes

- Reconciled the final buy-now annual projection point with the post-retirement mortgage treatment. A payoff scenario now ends with both the recommendation's `portfolioAtRetirement` and its zero post-payoff mortgage balance.
- Added canonical USD state for every finder money control. Currency switches render from canonical values, so step-rounded presentation amounts cannot drift into engine inputs. Valid user edits update the canonical value in the currently selected currency; invalid or empty text does not.
- Limited money validation to controls active for the selected housing plan and disabled all controls inside hidden conditional groups. A stale invalid property-allocation value can no longer block a rent submission.
- Rejected missing, non-finite, zero, and negative currency rates before any value or selection mutation. The selector returns to the previous valid currency when a change is rejected.

## TDD evidence

The new regression set was run before implementation and failed for all four review findings:

- payoff projection ended before the payoff deduction;
- USD 500,000 round-tripped through the EUR display as USD 499,590;
- the hidden property allocation remained enabled and invalid;
- invalid EUR rates left the selector showing EUR.

An additional RED/GREEN refinement verified that the payoff projection's final mortgage balance reflects the post-payoff state while the preceding point still has a balance.

## Verification

Focused command:

```text
python3 -m unittest tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui tests.test_retirement_destination_finder_page tests.test_property_finance_engine
```

Result: 63 tests passed.

Full command:

```text
python3 -m unittest discover -s tests
```

Result: 904 tests passed in 29.691 seconds. The suite's SEO notifications and issue operations were dry-run output.

`git diff --check` passed with no output. Generated `artifacts/` remain unstaged and outside this fix.
