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

## Fix Round 1

### Reviewer findings addressed

1. `user_after_tax` now has one target and one gap only. The finder result object omits `retirementTargetRange`, `favorableGap`, and `adverseGap`; the UI labels the result as a user-supplied after-tax target and states that no destination tax scenario is added.
2. Tax freshness now uses an ISO build-date anchor (`taxPlanning.asOf`) rather than the evidence review date. Production defaults to `date.today()` and tests can pass a deterministic `date`. The runtime test proves evidence is available at 366 days and becomes conditional/unavailable at 367 days. Strict data-quality validation still rejects stale evidence by default, while the build explicitly permits structurally valid stale screens to reach the runtime conditional path.
3. The static verifier now parses the generated finder payload, runs the actual finder engine, passes every runtime recommendation through the same UI result-link builder used by rendering, rejects an empty result set or link-count mismatch, and validates every URL path, exact query-key set, enum, and destination slug. The built artifact produced 31 recommendations and 31 sanitized links with zero handoff errors.
4. The duplicate `detailHref` was removed from finder engine results. UI result rendering owns the URL and routes it through the categorical allowlist.

### TDD RED evidence

Central-only after-tax behavior:

```text
$ python3 -m unittest tests.test_retirement_destination_finder.RetirementDestinationFinderTests.test_user_after_tax_bypass_is_one_zero_added_tax_target tests.test_retirement_destination_finder_ui.RetirementDestinationFinderUITests.test_user_after_tax_presentation_has_one_target_and_gap_without_scenario_bounds -v
Ran 2 tests in 0.166s
FAILED (failures=1, errors=1)
```

Freshness/build validation:

```text
$ python3 -m unittest tests.test_retirement_destination_finder.RetirementDestinationFinderTests.test_tax_freshness_crosses_from_available_to_conditional_after_366_days tests.test_build_unified_app_auto_links.AutoInternalLinkTests.test_finder_serializes_deterministic_build_date_as_tax_freshness_anchor tests.test_fire_abroad_data.FireAbroadDataTests.test_build_validation_allows_structurally_valid_stale_tax_evidence_for_runtime_fallback -v
Ran 3 tests in 0.179s
FAILED (failures=1, errors=2)
```

Runtime handoff and duplicate engine link:

```text
$ python3 -m unittest tests.test_retirement_destination_finder.RetirementDestinationFinderTests.test_user_after_tax_bypass_is_one_zero_added_tax_target tests.test_retirement_destination_finder_ui.RetirementDestinationFinderUITests.test_result_handoff_builder_sanitizes_every_recommendation_and_ignores_engine_hrefs tests.test_build_unified_app_auto_links.AutoInternalLinkTests.test_generated_finder_runtime_handoffs_cover_every_result_and_are_private tests.test_build_unified_app_auto_links.AutoInternalLinkTests.test_static_verifier_rejects_sensitive_finder_handoff_parameters -v
Ran 4 tests in 0.179s
FAILED (failures=1, errors=3)
```

The clarified page copy also failed first because it still claimed every result had favorable/adverse bounds (`Ran 1`, `FAILED (failures=1)`).

### GREEN and final verification

Each red group passed after its minimal implementation. Fresh final commands:

```text
$ python3 -m unittest tests.test_retirement_calculator_engine tests.test_retirement_calculator_ui tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui -v
Ran 90 tests in 10.595s
OK

$ python3 -m unittest tests.test_build_unified_app_auto_links tests.test_retirement_destination_finder_page tests.test_fire_abroad_data -v
Ran 41 tests in 0.851s
OK

$ python3 src/build_unified_app.py
/Users/steph-tmp/Documents/GitHub/property-research-dashboard/artifacts/unified_destination_dashboard.html
exit 0

$ python3 -m unittest discover -s tests -q
Ran 973 tests in 21.971s
OK
```

JavaScript syntax, Python compilation, and `git diff --check` exited 0.

Runtime privacy evidence from the built artifact:

```text
{'recommendations': 31, 'links': 31, 'errors': [], 'first': '/retirement-abroad-calculator/?destination=fukuoka-itoshima&household=single&housing=rent'}
```

The full static verifier still exits 1 only for the same two Spain markers and three missing Chamonix assets documented above; it reports no finder handoff error.

At a real 390px Chrome viewport, the submitted `user_after_tax` result had document width 375, no overflow, and exactly these financial labels: `Projected portfolio`, `User-supplied after-tax target`, and `Surplus or gap`. The explanatory after-tax note was visible, favorable/adverse labels were absent, and the rendered handoff contained only destination/household/housing. Switching to destination estimates restored central target, target range, central gap, favorable gap, and adverse gap.

### Fix Round 1 files

- `.superpowers/sdd/2026-09-01-fire-tax-calculator/task-4-report.md`
- `scripts/verify_static_site.py`
- `src/build_unified_app.py`
- `src/fire_abroad.py`
- `src/retirement_destination_finder.js`
- `src/retirement_destination_finder_page.py`
- `src/retirement_destination_finder_ui.js`
- `tests/test_build_unified_app_auto_links.py`
- `tests/test_fire_abroad_data.py`
- `tests/test_retirement_destination_finder.py`
- `tests/test_retirement_destination_finder_page.py`
- `tests/test_retirement_destination_finder_ui.py`

Generated artifacts remain excluded from the commit.

## Fix Round 2

### Freshness regression addressed

The Python and browser FIRE Abroad screeners now require the same deterministic ISO `asOf` anchor used by the finder. Complete destination-estimate evidence remains usable through day 366 after review and becomes `tax_impact_unavailable` on day 367. Stale rows remain in the comparison as conditional, visibly unranked information with null score, readiness score, and tax-adjusted annual cost; they are not silently dropped or assigned an old reserve/confidence. The `user_after_tax` path remains exempt because it uses the user's supplied after-tax assumptions and adds no destination tax estimate.

`build_fire_abroad_page(..., tax_as_of=...)` uses the explicit test override or the real current build date, serializes it as `asOf`, passes it to the Python pre-render ranker, and the UI passes the same field to the JavaScript runtime ranker. The stale row copy exposes the evidence reason and says the destination remains visible but is not ranked.

### TDD RED evidence

Engine boundary tests were written first:

```text
$ python3 -m unittest tests.test_fire_abroad.FireAbroadModelTests.test_destination_tax_freshness_crosses_after_366_days_but_after_tax_mode_is_exempt tests.test_fire_abroad.FireAbroadModelTests.test_stale_destination_remains_visible_but_is_unranked tests.test_fire_abroad_js.FireAbroadJavaScriptTests.test_destination_tax_freshness_crosses_after_366_days_but_after_tax_mode_is_exempt tests.test_fire_abroad_js.FireAbroadJavaScriptTests.test_stale_destination_remains_visible_but_is_unranked -v
Ran 4 tests in 0.321s
FAILED (failures=2, errors=2)
```

Python rejected the new `as_of` argument; JavaScript left 367-day-old evidence as a rankable `planning_estimate` with numeric reserves.

Build/runtime propagation tests were then written first:

```text
$ python3 -m unittest tests.test_build_unified_app_auto_links.AutoInternalLinkTests.test_fire_page_serializes_build_date_and_retains_stale_destinations_unranked tests.test_fire_abroad_js.FireAbroadJavaScriptTests.test_ui_ranking_input_forwards_serialized_freshness_anchor -v
Ran 2 tests in 0.083s
FAILED (errors=2)
```

The page builder did not accept `tax_as_of`, and the UI had no executable ranking-input boundary that forwarded the serialized anchor.

### GREEN and verification evidence

Each RED group passed after its minimal implementation. Fresh focused runs:

```text
$ python3 -m unittest tests.test_fire_abroad tests.test_fire_abroad_js tests.test_fire_abroad_page tests.test_build_unified_app_auto_links -v
Ran 38 tests in 2.113s
OK

$ python3 -m unittest tests.test_retirement_calculator_engine tests.test_retirement_calculator_ui tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui tests.test_fire_abroad_data -v
Ran 109 tests in 10.686s
OK
```

The stale ranking tests also exercise `user_after_tax` through the full Python and JavaScript rankers and confirm it remains rankable with `user_after_tax` status.

Build and full suite:

```text
$ python3 src/build_unified_app.py
/Users/steph-tmp/Documents/GitHub/property-research-dashboard/artifacts/unified_destination_dashboard.html
exit 0

$ python3 -m unittest discover -s tests -q
Ran 979 tests in 22.764s
OK
```

`node --check` for both changed JavaScript files, Python compilation for changed Python/test modules, and `git diff --check` all exited 0.

The behavioral generated-page test builds with `tax_as_of=2027-09-03`, parses the serialized payload, and confirms all 10 launch destinations remain in the table while every stale result omits `/5` scores and calculator actions and includes the stale/unranked explanation. The JavaScript boundary tests run the real screening/ranking module and the actual UI ranking-input builder, proving the browser receives the same anchor. A fresh Playwright wrapper attempt did not return CLI help within 30 seconds in this environment, so no new visual browser session was claimed; the deterministic generated DOM/runtime checks are the proportionate fallback. Round 1's completed responsive and script-disabled browser evidence remains unchanged.

The static verifier still exits 1 only for the same unrelated dirty-artifact defects:

```text
Missing marker 'Buyer Next Step' in artifacts/countries/spain-property/index.html
Missing marker 'Turn Spain research into a shortlist' in artifacts/countries/spain-property/index.html
artifacts/destinations/chamonix/index.html -> /assets/chamonix-valley-life.webp
artifacts/destinations/chamonix/index.html -> /assets/chamonix-winter-access.webp
artifacts/destinations/chamonix/index.html -> /assets/chamonix-building-governance.webp
```

### Fix Round 2 files

- `.superpowers/sdd/2026-09-01-fire-tax-calculator/task-4-report.md`
- `src/build_unified_app.py`
- `src/fire_abroad.js`
- `src/fire_abroad.py`
- `src/fire_abroad_page.py`
- `src/fire_abroad_ui.js`
- `tests/fixtures/fire_abroad_screen_contract.json`
- `tests/test_build_unified_app_auto_links.py`
- `tests/test_fire_abroad.py`
- `tests/test_fire_abroad_js.py`
- `tests/test_fire_abroad_page.py`

### Fix Round 2 self-review and concerns

- Python and JavaScript use the same strict ISO-date contract and 366-day threshold; missing, invalid, future-dated, and stale anchors cannot create a numeric destination tax estimate.
- The production build passes one `build_date` to validation, the finder, FIRE pre-rendering, and the FIRE browser payload.
- Stale destination-estimate rows preserve visibility but cannot contribute old cost, readiness, confidence, or rank values.
- `user_after_tax` bypasses destination-evidence freshness in both engines and rankers, retaining its single zero-added-tax assumption.
- No calculator/finder privacy, equity, owner-cost, or handoff code changed in this round.
- Generated artifacts and unrelated dirty changes remain excluded. The only open repository-level concern remains the pre-existing Spain/Chamonix static-verifier failures above.

## Final calculator whole-plan fix wave

### Outcome

The normal retirement calculator now serializes a deterministic ISO build-date freshness anchor separately from the tax evidence review date. The scenario engine uses the build date only for freshness and preserves the evidence year in every amount audit. Evidence reviewed on 2026-09-01 remains usable on day 366 (2027-09-02) and becomes unavailable on day 367 (2027-09-03).

The finder and calculator now share an explicit full-year relocation assumption for the initial screen. Both pages state that assumption in concise form and tell users they can refine seasonal or part-year plans later; no additional required field was added and the calculator handoff remains limited to destination, household, and housing.

Tax totals now derive inclusions and source IDs only from active included categories. Excluded owner property tax and non-applicable property/wealth allowances carry no source IDs into the total; their excluded or not-applicable state is visible in the rendered audit. Each displayed favorable, central, and adverse tax reserve, total annual requirement, and capital requirement has its own formula, assumptions, inclusions, exclusions, evidence tax year, confidence, and active sources. The `user_after_tax` contract contains exactly one zero-added-tax case and complete zero/excluded amount explanations with user-supplied confidence and no sources.

### Strict TDD evidence

Freshness separation was RED first:

```text
$ python3 -m unittest tests.test_build_unified_app_auto_links.AutoInternalLinkTests.test_calculator_serializes_deterministic_freshness_separately_from_evidence_review tests.test_fire_tax_scenarios.FireTaxScenarioTests.test_freshness_crosses_after_day_366_while_tax_year_remains_evidence_year -v
Ran 2 tests in 0.169s
FAILED (failures=1, errors=1)
```

The builder did not accept `tax_as_of`, and the boundary audit incorrectly reported the freshness year (2027) instead of the evidence year (2026). The browser input boundary also failed first because no `taxEvidenceContext` function existed (`Ran 1 test in 0.073s`, `FAILED`). All three passed after separating `asOf` and `taxYear`.

Shared stay behavior and visible copy were RED first:

```text
$ python3 -m unittest tests.test_retirement_destination_finder.RetirementDestinationFinderTests.test_spain_finder_and_calculator_share_explicit_full_relocation_assumption tests.test_retirement_destination_finder_page.RetirementDestinationFinderPageTests.test_finder_tax_profile_explains_live_tax_adjusted_ranking tests.test_retirement_calculator_page.RetirementCalculatorPageTests.test_initial_tax_screen_states_the_shared_full_relocation_assumption -v
Ran 3 tests in 1.122s
FAILED (failures=3)
```

The same Spain profile produced an 8,000 finder reserve and a 22,000 direct calculator reserve because the finder silently defaulted to part-year. The explicit full-relocation default and matching page copy made the group pass (`Ran 3 tests in 1.017s`, `OK`).

Active-category and after-tax audit contracts were RED first:

```text
$ python3 -m unittest tests.test_fire_tax_scenarios.FireTaxScenarioTests.test_total_audit_uses_only_active_categories_and_sources tests.test_fire_tax_scenarios.FireTaxScenarioTests.test_user_after_tax_has_one_zero_case_with_complete_excluded_audits -v
Ran 2 tests in 0.166s
FAILED (failures=1, errors=1)
```

The old total hardcoded inactive property/wealth categories and their sources, component status metadata was absent, and after-tax produced three cases. Both tests passed after deriving totals from active entries and normalizing the single after-tax case (`Ran 2 tests in 0.148s`, `OK`).

Per-amount audit rendering was RED first:

```text
$ python3 -m unittest tests.test_retirement_calculator_ui.RetirementCalculatorUITests.test_each_displayed_scenario_amount_has_complete_audit_metadata tests.test_retirement_calculator_ui.RetirementCalculatorUITests.test_tax_audit_entries_cover_every_displayed_table_amount -v
Ran 2 tests in 0.321s
FAILED (errors=2)
```

Scenario results had no composed amount audits and the UI had no audit-entry rendering boundary. After implementation, all nine displayed scenario amounts had audit entries and the group passed (`Ran 2 tests in 0.336s`, `OK`).

### GREEN, build, and full-suite verification

The final focused suite, including calculator/finder engines, browser helpers, scenario contract, and page copy, passed:

```text
$ python3 -m unittest tests.test_retirement_calculator_engine tests.test_retirement_calculator_ui tests.test_retirement_destination_finder tests.test_retirement_destination_finder_ui tests.test_fire_tax_scenarios tests.test_retirement_calculator_page tests.test_retirement_destination_finder_page -q
Ran 169 tests in 14.087s
OK
```

Build and full suite:

```text
$ python3 src/build_unified_app.py
/Users/steph-tmp/Documents/GitHub/property-research-dashboard/artifacts/unified_destination_dashboard.html
exit 0

$ python3 -m unittest discover -s tests -q
Ran 988 tests in 23.906s
OK
```

`node --check` for all four changed JavaScript modules, Python compilation for changed Python/test modules, and `git diff --check` all exited 0.

### Privacy, generated DOM, and browser evidence

- The exact finder handoff test now includes the new `stayMode=full_relocation` tax profile and still returns URLs containing only destination, household, and housing.
- Existing behavioral privacy tests continue to execute the real finder result-link builder for every recommendation, reject unexpected query keys, and prove analytics/storage/network boundaries contain no tax inputs or results.
- The built calculator payload contains distinct `tax_planning.as_of=2026-09-01` and `reviewed_on=2026-09-01` fields, and both generated pages contain the shared full-year relocation/refinement copy.
- Executable Node tests run the real tax scenario, retirement composition, presentation, and audit-entry functions. They prove the rendered-entry boundary emits exactly nine entries covering the three displayed amounts in all three destination-estimate cases, with no inactive wealth source.
- A bounded Playwright CLI attempt again produced no output within 30 seconds and was stopped. No new visual-browser claim is made for this wave; deterministic executable-JavaScript and generated-page checks are the proportionate fallback. The completed 320/375/390/430/736/1024 responsive and real script-disabled Chrome evidence from Task 4/Fix Round 1 is unaffected because this wave adds only copy and content inside existing responsive containers.

The static verifier again reached its executable runtime finder handoff boundary without a Task 4 error. It exits 1 only for the same unrelated dirty-artifact defects:

```text
Missing marker 'Buyer Next Step' in artifacts/countries/spain-property/index.html
Missing marker 'Turn Spain research into a shortlist' in artifacts/countries/spain-property/index.html
artifacts/destinations/chamonix/index.html -> /assets/chamonix-valley-life.webp
artifacts/destinations/chamonix/index.html -> /assets/chamonix-winter-access.webp
artifacts/destinations/chamonix/index.html -> /assets/chamonix-building-governance.webp
```

### Final-fix files

- `.superpowers/sdd/2026-09-01-fire-tax-calculator/task-4-report.md`
- `src/build_unified_app.py`
- `src/fire_tax_scenarios.js`
- `src/retirement_calculator_ui.js`
- `src/retirement_destination_finder.js`
- `src/retirement_destination_finder_page.py`
- `src/retirement_destination_finder_ui.js`
- `tests/test_build_unified_app_auto_links.py`
- `tests/test_fire_tax_scenarios.py`
- `tests/test_retirement_calculator_page.py`
- `tests/test_retirement_calculator_ui.py`
- `tests/test_retirement_destination_finder.py`
- `tests/test_retirement_destination_finder_page.py`
- `tests/test_retirement_destination_finder_ui.py`

### Self-review and concerns

- Freshness validation uses the real/current build date in production and a deterministic override in tests; it no longer overloads evidence year metadata.
- The direct Spain parity test proves both products use full relocation, while the existing handoff privacy contract remains unchanged.
- Total sources are reduced from active component audits only. Excluded and not-applicable component states are retained in the total exclusions and rendered context, preventing an inactive wealth-tax source from appearing.
- The annual and capital audit formulas trace the actual calculator composition, retain property equity separation, and reuse the scenario result instead of duplicating tax arithmetic.
- After-tax remains one zero-added-tax result with `after_fees_and_tax`, zero/excluded component entries, `not_applicable` tax year, user-supplied confidence, and no sources.
- Generated artifacts remain intentionally uncommitted. The only open repository-level concern is the pre-existing Spain/Chamonix static-verifier failure above; the Playwright CLI limitation is recorded without overstating visual evidence.
