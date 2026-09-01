# Task 4 report: cross-tool integration, privacy, and verification

## Outcome

The retirement destination finder now derives affordability from the central tax-adjusted target produced by the existing tax scenario engine and calculator composition helper. Results expose favorable, central, and adverse targets/gaps; unsupported, invalid, or stale evidence is conditional and unavailable rather than treated as zero tax. Property equity remains separate and owner property tax is excluded from the tax reserve when already present in retirement costs.

The `user_after_tax` path remains a single zero-added-tax result with the explicit `after_fees_and_tax` return basis. Finder-to-calculator links still carry only `destination`, `household`, and `housing`. Tax values are written into result nodes with `textContent`, and analytics receives only categorical housing fields.

## Strict TDD evidence

### RED

Initial integration/privacy run:

```text
$ python3 -m unittest tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui tests.test_build_unified_app_auto_links -v
Ran 25 tests
FAILED (failures=2, errors=6)
```

The failures were the intended missing behavior: no tax-adjusted finder targets/ranking, no conditional tax fallback, no safe result-field writer or categorical analytics helper, and no executable handoff verifier.

Copy/integration status test:

```text
$ python3 -m unittest tests.test_retirement_destination_finder_page.RetirementDestinationFinderPageTests.test_finder_tax_profile_explains_live_tax_adjusted_ranking tests.test_retirement_destination_finder_page.RetirementDestinationFinderPageTests.test_results_include_financial_tiers_and_decision_outputs -v
Ran 2 tests
FAILED (failures=1)
```

Additional focused red/green cycles:

- Mutating owner-cost handling to add property tax twice made `test_owner_costs_exclude_property_tax_from_the_integrated_tax_target` fail (`0 != 5000`); restoring the exclusion passed.
- Adding the cross-cap evidence-summary test first errored because `finderEvidenceSummary` did not exist; its first implementation then failed the singular grammar case (`1 destinations`), which was corrected.
- Conditional-field tests initially failed because a null central gap was omitted from the safe sink and could become `$0`; all conditional tax values now render `Unavailable`.

### GREEN

Required focused suite:

```text
$ python3 -m unittest tests.test_retirement_calculator_engine tests.test_retirement_calculator_ui tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui -v
Ran 87 tests in 10.521s
OK
```

Page/build boundary tests:

```text
$ python3 -m unittest tests.test_build_unified_app_auto_links tests.test_retirement_destination_finder_page -v
Ran 21 tests in 0.705s
OK
```

## Build and full-suite verification

```text
$ python3 src/build_unified_app.py
/Users/steph-tmp/Documents/GitHub/property-research-dashboard/artifacts/unified_destination_dashboard.html
exit 0

$ python3 -m unittest discover -s tests -q
Ran 968 tests in 21.616s
OK
```

The required verbose full-suite command was also run and exited 0; the quiet run above is the fresh, untruncated confirmation. JavaScript syntax checks for both finder files, Python compilation for the changed Python source/verifier, and `git diff --check` all exited 0.

The static site verifier was exercised at its behavioral boundary:

```text
$ python3 scripts/verify_static_site.py --min-sitemap-urls 65
Missing marker 'Buyer Next Step' in artifacts/countries/spain-property/index.html
Missing marker 'Turn Spain research into a shortlist' in artifacts/countries/spain-property/index.html
artifacts/destinations/chamonix/index.html -> /assets/chamonix-valley-life.webp
artifacts/destinations/chamonix/index.html -> /assets/chamonix-winter-access.webp
artifacts/destinations/chamonix/index.html -> /assets/chamonix-building-governance.webp
exit 1
```

These are pre-existing unrelated dirty generated-artifact defects. The verifier reached the new finder marker and query-parameter checks without reporting Task 4 failures. Executable unit tests also prove generated handoffs pass and injected `taxMode`/`wealthBand` query parameters fail.

## Privacy evidence

- `finderAnalyticsPayload` returns only `housing_plan` and `purchase_method`, even when passed tax inputs/results.
- The generated finder calculator handoffs were parsed as URLs and contained only `destination`, `household`, and `housing`.
- The static verifier rejects any other calculator handoff query key.
- Tax target/range/gap fields are populated through `textContent`; a test installs throwing `innerHTML` setters and passes.
- Searches and review found no finder storage or fetch/network persistence additions.
- Conditional null results render `Unavailable`, never `$0`.

## Responsive and JavaScript-disabled evidence

The built finder page was inspected in a real browser at actual CSS viewport widths 320, 375, 390, 430, 736, and 1024 pixels. At every width, `document.documentElement.scrollWidth <= innerWidth`; no horizontal page overflow was present. Observed pairs were 320/320, 358/375, 373/390, 413/430, 720/736, and 1007/1024.

At 1024px the interactive default run completed without page or console errors. The first Fukuoka result displayed:

- projected portfolio `$1,662,594`
- central target `$2,085,917`
- favorable-adverse range `$2,025,374–$2,186,821`
- central/favorable/adverse gaps `−$423,323`, `−$362,780`, and `−$524,227`
- handoff `/retirement-abroad-calculator/?destination=fukuoka-itoshima&household=couple&housing=rent`

For the real script-disabled check, Chrome was launched with an isolated profile and `--blink-settings=scriptEnabled=false`, then inspected through the DevTools protocol after applying a 320px viewport. The observed state was:

```json
{"viewport":320,"documentWidth":320,"overflow":false,"fallbackVisible":true,"resultsHidden":true,"resultCards":0,"finderEngineType":"undefined"}
```

The visible fallback states that the interactive comparison requires JavaScript and keeps the tax controls as a planning checklist. The static page test for this fallback also passes.

## Files changed

- `scripts/verify_static_site.py`
- `src/build_unified_app.py`
- `src/retirement_destination_finder.js`
- `src/retirement_destination_finder_page.py`
- `src/retirement_destination_finder_ui.js`
- `tests/test_build_unified_app_auto_links.py`
- `tests/test_retirement_destination_finder.py`
- `tests/test_retirement_destination_finder_page.py`
- `tests/test_retirement_destination_finder_ui.py`
- `.superpowers/sdd/2026-09-01-fire-tax-calculator/task-4-report.md`

Generated artifacts and unrelated existing changes are intentionally excluded from the commit.

## Self-review

- Re-read the engine flow to confirm all tax arithmetic remains in `fire_tax_scenarios.js` and `retirement_calculator_ui.js`; the finder only supplies inputs and composes existing results.
- Confirmed central target drives funding ratio, tier, and sorting, while favorable/adverse values are disclosure bounds.
- Confirmed missing, malformed, and stale tax evidence all take the same unavailable/conditional path and sort after evaluated tiers.
- Confirmed mortgage liability is added consistently to all three target cases and property equity never enters liquid portfolio funding.
- Confirmed owner housing plans set the existing property-tax-in-costs flag, preventing the tax allowance from being counted twice.
- Confirmed `user_after_tax` produces one repeated target range, zero annual tax reserve, and an after-fees-and-tax basis.
- Confirmed dynamic personalized tax output uses DOM text nodes and safe fixed-path links.
- Reviewed the exact task-file diff and found no unrelated source changes.

## Concerns

The only open repository-level concern is the unrelated static-verifier failure from the already dirty Spain and Chamonix generated artifacts listed above. Task 4 does not modify or commit those artifacts.
