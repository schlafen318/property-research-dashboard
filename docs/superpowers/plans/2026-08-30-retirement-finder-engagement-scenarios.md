# Retirement Finder Engagement and Scenario Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add outcome-focused match explanations, a default three-destination comparison, five indexable retirement-capital scenario pages, and privacy-conscious shared finder results.

**Architecture:** A new UMD scenario module owns the versioned public result contract and URL codec. The existing finder engine gains a projected-capital entry point that reuses destination-target evaluation and ordering. The live finder, static scenario-page builder, and build pipeline consume those shared interfaces without changing the current recommendation algorithm.

**Tech Stack:** Python 3.11 static-site build, browser-compatible CommonJS/UMD JavaScript, Node.js for engine tests and build-time scenario calculation, `unittest`, HTML/CSS, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-08-30-retirement-finder-engagement-scenarios-design.md`

## Global Constraints

- Keep the existing recommendation order and financial methodology unchanged.
- User-facing copy is informative and concise and does not describe schemas, algorithms, scoring, generation, or internal data handling.
- Use the established terms **Projected capital**, **Required capital**, **Within reach**, **Close**, **Stretch**, **Planning estimate**, and **Destination guide**.
- Shared results exclude age, current savings, contributions, salary, pension sources, and other raw financial inputs.
- Analytics never receive capital, costs, gaps, ages, income, pensions, contributions, or encoded scenarios.
- All controls and results must fit at 320 CSS pixels without page-level horizontal overflow.
- No new third-party runtime dependencies.

---

### Task 1: Versioned public scenario contract and URL codec

**Files:**
- Create: `src/retirement_finder_scenario.js`
- Create: `tests/test_retirement_finder_scenario.py`

**Interfaces:**
- Consumes: finder `user` input, `recommendDestinations(input)` output, current currency, and data-review date.
- Produces: `buildScenario(input) -> FinderScenarioV1`, `validateScenario(input, destinationIds) -> FinderScenarioV1`, `encodeScenario(scenario) -> string`, and `decodeScenario(value, destinationIds) -> FinderScenarioV1`.

- [ ] **Step 1: Write failing contract, privacy, validation, and codec tests**

```python
def test_build_scenario_keeps_outcomes_and_drops_raw_financial_inputs(self) -> None:
    scenario = run_scenario("buildScenario", scenario_input())
    self.assertEqual(1, scenario["v"])
    self.assertEqual(1_250_000, scenario["projectedCapitalUsd"])
    self.assertEqual(["fukuoka", "valencia", "madeira"], scenario["comparisonIds"])
    serialized = json.dumps(scenario)
    for forbidden in ("currentAge", "totalLiquidCapital", "monthlyPortfolioContribution", "incomeStreams"):
        self.assertNotIn(forbidden, serialized)

def test_codec_round_trips_url_safe_payload(self) -> None:
    scenario = run_scenario("buildScenario", scenario_input())
    encoded = run_scenario("encodeScenario", scenario)
    self.assertRegex(encoded, r"^[A-Za-z0-9_-]+$")
    self.assertEqual(scenario, run_scenario("decodeScenario", {"value": encoded, "destinationIds": destination_ids()}))

def test_decode_rejects_unknown_version_duplicates_and_oversized_payloads(self) -> None:
    self.assert_scenario_error({"v": 2}, "Unsupported results-link version")
    self.assert_scenario_error(duplicate_destination_scenario(), "Destination IDs must be unique")
    self.assert_scenario_error({"value": "a" * 17000, "destinationIds": destination_ids()}, "Results link is too large")
```

- [ ] **Step 2: Run the new tests to verify RED**

Run: `python3 -m unittest tests.test_retirement_finder_scenario`

Expected: FAIL because `src/retirement_finder_scenario.js` does not exist.

- [ ] **Step 3: Implement the UMD module with strict whitelisting**

```javascript
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.GHARetirementFinderScenario = api;
})(typeof window !== "undefined" ? window : null, function () {
  "use strict";
  const MAX_ENCODED_LENGTH = 16384;
  const TIERS = new Set(["within_reach", "close", "stretch"]);
  const HOUSEHOLDS = new Set(["single", "couple"]);
  const HOUSING = new Set(["rent", "own", "buy_now", "buy_retirement"]);

  function buildScenario(input) {
    const result = input.result || {};
    const user = input.user || {};
    return validateScenario({
      v: 1,
      currency: input.currency || "USD",
      projectedCapitalUsd: Number(input.projectedCapitalUsd),
      household: user.household,
      horizonYears: Number(user.horizonYears),
      housingPlan: user.housingPlan,
      preferences: Object.assign({}, user.preferences),
      results: (result.recommendations || []).map(publicResult),
      comparisonIds: (result.recommendations || []).slice(0, 3).map(item => item.destinationId),
      dataReviewed: String(input.dataReviewed || ""),
    }, new Set((result.recommendations || []).map(item => item.destinationId)));
  }
```

Implement UTF-8 base64url conversion with `TextEncoder`/`TextDecoder` in browsers and `Buffer` in Node. Validate before encoding and after decoding. Return newly constructed objects rather than the caller's references.

- [ ] **Step 4: Run contract tests to verify GREEN**

Run: `python3 -m unittest tests.test_retirement_finder_scenario`

Expected: PASS.

- [ ] **Step 5: Commit the scenario contract**

```bash
git add src/retirement_finder_scenario.js tests/test_retirement_finder_scenario.py
git commit -m "Add retirement finder scenario contract"
```

---

### Task 2: Projected-capital recommendation entry point

**Files:**
- Modify: `src/retirement_destination_finder.js`
- Modify: `tests/test_retirement_destination_finder.py`

**Interfaces:**
- Consumes: `recommendProjectedCapital(input)` with `projectedCapitalUsd`, canonical retirement assumptions, destinations, retirement costs, and mortgage profiles.
- Produces: the same `{summary, sharedProjection, recommendations, excluded}` shape as `recommendDestinations(input)`.

- [ ] **Step 1: Write failing parity and boundary tests**

```python
def test_projected_capital_entry_point_reuses_existing_target_and_ordering(self) -> None:
    accumulated = run_finder("recommendDestinations", standard_payload())
    direct = run_finder("recommendProjectedCapital", {
        **universe_payload(),
        "projectedCapitalUsd": accumulated["sharedProjection"]["portfolioAtRetirement"],
        "user": canonical_user_payload(),
    })
    self.assertEqual(
        [(item["destinationId"], item["tier"], item["retirementTarget"]) for item in accumulated["recommendations"]],
        [(item["destinationId"], item["tier"], item["retirementTarget"]) for item in direct["recommendations"]],
    )

def test_projected_capital_entry_point_rejects_buy_now(self) -> None:
    payload = projected_capital_payload(housingPlan="buy_now")
    with self.assertRaisesRegex(subprocess.CalledProcessError, "buy now"):
        run_finder("recommendProjectedCapital", payload)
```

- [ ] **Step 2: Run engine tests to verify RED**

Run: `python3 -m unittest tests.test_retirement_destination_finder`

Expected: FAIL because `recommendProjectedCapital` is not exported.

- [ ] **Step 3: Extract shared destination evaluation and implement direct capital**

Refactor the current loop and sort into an internal function:

```javascript
function evaluateDestinations(input, projectionForDestination) {
  // Existing retirement target, exclusion, mortgage, preference, tier,
  // result-shape, and sorting logic moves here without semantic changes.
}

function recommendDestinations(input) {
  const user = input.user || {};
  const sharedProjection = user.housingPlan === "buy_now" ? null : projectPortfolio({
    currentAge: user.currentAge,
    retirementAge: user.retirementAge,
    startingPortfolio: user.totalLiquidCapital,
    monthlyContribution: user.monthlyPortfolioContribution,
    contributionInflationLinked: user.contributionInflationLinked,
    generalInflation: user.generalInflation,
    expectedPortfolioReturn: user.expectedPortfolioReturn,
  });
  return evaluateDestinations(input, destination =>
    sharedProjection || buyNowProjection(input.user, destination, input)
  );
}

function recommendProjectedCapital(input) {
  if ((input.user || {}).housingPlan === "buy_now") {
    throw new Error("Projected-capital scenarios do not support buy now");
  }
  const capital = nonNegative(input.projectedCapitalUsd, "Projected capital");
  const projection = {
    portfolioAtRetirement: capital,
    annualProjection: [{year: 0, portfolio: capital, contributions: 0}],
    exhaustedMonth: null,
  };
  return evaluateDestinations(input, function () { return projection; });
}
```

Preserve every existing exclusion code, financing field, detail URL, tier boundary, preference tie-breaker, and sort order.

- [ ] **Step 4: Run engine tests to verify GREEN and no regression**

Run: `python3 -m unittest tests.test_retirement_destination_finder`

Expected: PASS.

- [ ] **Step 5: Commit the projected-capital entry point**

```bash
git add src/retirement_destination_finder.js tests/test_retirement_destination_finder.py
git commit -m "Support projected capital retirement scenarios"
```

---

### Task 3: Live recommendations, comparison, and shared results

**Files:**
- Modify: `src/retirement_destination_finder_page.py`
- Modify: `src/retirement_destination_finder_ui.js`
- Modify: `src/site_design_system.py`
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_retirement_destination_finder_page.py`
- Modify: `tests/test_retirement_destination_finder_ui.py`
- Modify: `tests/test_deploy_analytics_config.py`

**Interfaces:**
- Consumes: `GHARetirementFinderScenario`, current finder result, page payload destination guide URLs, and `FinderScenarioV1` from the query string.
- Produces: concise explanation markup, a default three-destination comparison, replacement controls, a privacy notice, share URL behavior, and read-only shared-result rendering.

- [ ] **Step 1: Write failing page-structure and copy tests**

```python
def test_page_contains_compact_comparison_and_share_controls(self) -> None:
    for marker in (
        'id="finder-comparison"',
        'id="finder-comparison-body"',
        'id="finder-share"',
        'id="finder-share-status" aria-live="polite"',
        'id="finder-shared-error" role="alert"',
    ):
        self.assertIn(marker, self.html)
    self.assertIn("Compare your three strongest matches", self.html)
    self.assertIn("This link includes your projected capital and planning choices.", self.html)
    self.assertNotIn("algorithm", self.html.lower())
```

- [ ] **Step 2: Write failing pure-UI and DOM-scenario tests**

```python
def test_comparison_defaults_to_three_and_prevents_duplicates(self) -> None:
    rows = run_ui("comparisonSelection", {"recommendations": recommendations(), "selectedIds": []})
    self.assertEqual(["fukuoka", "hakone", "valencia"], [row["destinationId"] for row in rows])
    replaced = run_ui("replaceComparisonDestination", {
        "selectedIds": ["fukuoka", "hakone", "valencia"],
        "position": 1,
        "destinationId": "fukuoka",
    })
    self.assertEqual(["fukuoka", "hakone", "valencia"], replaced)

def test_share_analytics_contains_no_financial_values(self) -> None:
    state = run_ui_dom_scenario({"submit": True, "clickShare": True, "engineResult": engine_result()})
    event = next(item for item in state["trackedEvents"] if item["name"] == "retirement_destination_finder_share")
    self.assertEqual({"housing_plan": "rent"}, event["fields"])
```

Extend the fake DOM with native-select values, clipboard success/failure, `window.location.search`, and the scenario module stub.

- [ ] **Step 3: Run focused tests to verify RED**

Run: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui tests.test_deploy_analytics_config`

Expected: FAIL for missing comparison, share, and scenario integration.

- [ ] **Step 4: Add semantic page structure and inject the scenario module**

Add the new builder argument `scenario_engine: str`, inject it before the UI script, and add:

```html
<section class="finder-comparison-section" id="finder-comparison" hidden>
  <div class="finder-comparison-heading">
    <p class="finder-landscape-kicker">Your recommended matches</p>
    <h3>Compare your three strongest matches</h3>
  </div>
  <div id="finder-comparison-body"></div>
</section>
<section class="finder-share-section" id="finder-share-section" hidden>
  <button id="finder-share" type="button">Share results</button>
  <p>This link includes your projected capital and planning choices. It does not include your age, current savings, income or pension details.</p>
  <p id="finder-share-status" aria-live="polite"></p>
</section>
<p id="finder-shared-error" role="alert" hidden>This results link cannot be opened. <a href="/retirement-destination-finder/">Start a new calculation</a>.</p>
```

- [ ] **Step 5: Implement comparison, guide paths, sharing, and shared-state rendering**

Add pure functions:

```javascript
function comparisonSelection(input) { /* strongest three or validated selected IDs */ }
function replaceComparisonDestination(input) { /* preserve three unique IDs */ }
function comparisonMarkup(input) { /* desktop table plus mobile headings */ }
function matchReasons(input) { /* affordability, preference, housing; maximum three */ }
function sharedScenarioFromLocation(search, destinationIds) { /* validated decode or null/error */ }
```

Runtime state stores `currentResult`, `currentUser`, and `comparisonIds`. Replacement rerenders only the comparison. Shared links render the scenario snapshot through the same result presenters and keep the form usable.

Use `navigator.clipboard.writeText` when available and expose a readonly text input fallback otherwise. Track only the categorical events and parameters listed in the spec.

- [ ] **Step 6: Add editorial comparison and share styles**

Desktop comparison uses a plain table with one rule between rows. Mobile below 760px renders destinations as stacked sections with the same metric order. Keep buttons square, body links regular weight, and supporting copy muted. Do not add pills, scores, or duplicated summary cards.

- [ ] **Step 7: Run focused tests to verify GREEN**

Run: `python3 -m unittest tests.test_retirement_destination_finder_page tests.test_retirement_destination_finder_ui tests.test_deploy_analytics_config`

Expected: PASS.

- [ ] **Step 8: Commit the live finder engagement features**

```bash
git add src/retirement_destination_finder_page.py src/retirement_destination_finder_ui.js src/site_design_system.py src/build_unified_app.py tests/test_retirement_destination_finder_page.py tests/test_retirement_destination_finder_ui.py tests/test_deploy_analytics_config.py
git commit -m "Add retirement finder comparison and sharing"
```

---

### Task 4: Five indexable capital-scenario pages

**Files:**
- Create: `src/retirement_capital_scenario_page.py`
- Create: `scripts/generate_retirement_capital_scenarios.js`
- Create: `tests/test_retirement_capital_scenario_page.py`
- Modify: `src/build_unified_app.py`
- Modify: `src/site_design_system.py`
- Modify: `src/retirement_destination_finder_page.py`
- Modify: `.github/workflows/deploy-pages.yml`
- Modify: `tests/test_retirement_destination_finder_page.py`
- Modify: `tests/test_seo_infrastructure_integrity.py`

**Interfaces:**
- Consumes: five canonical scenario definitions, enriched destinations, retirement costs, mortgage profiles, `recommendProjectedCapital(input)`, navigation, footer, analytics, and shared design CSS.
- Produces: five prerendered SEO pages and their sitemap/internal-link entries.

- [ ] **Step 1: Write failing route, metadata, outcome, and sitemap tests**

```python
SCENARIOS = {
    "retire-abroad-with-500k": 500_000,
    "retire-abroad-with-750k": 750_000,
    "retire-abroad-with-1-million": 1_000_000,
    "retire-abroad-with-1-5-million": 1_500_000,
    "retire-abroad-with-2-million": 2_000_000,
}

def test_every_capital_page_has_unique_outcome_copy_and_canonical_metadata(self) -> None:
    for slug, capital in SCENARIOS.items():
        html = artifact(slug)
        self.assertIn(f'<link rel="canonical" href="https://globalhomeatlas.com/{slug}/">', html)
        self.assertIn("Planning estimate", html)
        self.assertIn("Required capital", html)
        self.assertIn("Test your retirement plan", html)
        self.assertNotIn("how this page was generated", html.lower())

def test_capital_pages_are_in_sitemap_and_cross_linked(self) -> None:
    sitemap = artifact_text("sitemap.xml")
    for slug in SCENARIOS:
        self.assertIn(f"https://globalhomeatlas.com/{slug}/", sitemap)
```

- [ ] **Step 2: Write failing build-time generator parity test**

```python
def test_generated_one_million_scenario_matches_engine(self) -> None:
    generated = run_scenario_generator(1_000_000)
    expected = run_finder("recommendProjectedCapital", canonical_scenario_payload(1_000_000))
    self.assertEqual(expected["summary"], generated["summary"])
    self.assertEqual(
        [item["destinationId"] for item in expected["recommendations"]],
        [item["destinationId"] for item in generated["recommendations"]],
    )
```

- [ ] **Step 3: Run focused tests to verify RED**

Run: `python3 -m unittest tests.test_retirement_capital_scenario_page tests.test_retirement_destination_finder_page tests.test_seo_infrastructure_integrity`

Expected: FAIL because scenario routes and generator do not exist.

- [ ] **Step 4: Implement the build-time scenario generator**

`scripts/generate_retirement_capital_scenarios.js` reads one JSON object from stdin, requires `src/retirement_destination_finder.js`, runs `recommendProjectedCapital` for each requested capital value, and writes one JSON object to stdout. It emits no logs on stdout and exits nonzero with a concise stderr message on invalid input.

Add explicit Node setup to deployment:

```yaml
- name: Set up Node.js
  uses: actions/setup-node@v4
  with:
    node-version: "22"
```

- [ ] **Step 5: Implement the scenario page builder**

Expose:

```python
def build_retirement_capital_scenario_html(
    *, slug: str, capital_usd: int, result: dict, destinations_by_id: dict,
    head: str, navigation: str, footer: str, analytics: str, design_css: str,
) -> str:
    html = SCENARIO_TEMPLATE
    replacements = {
        "__HEAD__": head,
        "__NAVIGATION__": navigation,
        "__FOOTER__": footer,
        "__ANALYTICS__": analytics,
        "__DESIGN_CSS__": design_css,
        "__CONTENT__": build_scenario_content(
            slug=slug,
            capital_usd=capital_usd,
            result=result,
            destinations_by_id=destinations_by_id,
        ),
    }
    for marker, value in replacements.items():
        html = html.replace(marker, value)
    return html
```

Render a direct answer from `withinReachCount`, then Within reach rows followed by at most five closest alternatives. Every row shows destination, country, required capital, exact surplus or shortfall, and available guide links. Render the assumptions, cross-links, disclaimer, methodology link, breadcrumb JSON-LD, and visible FAQ/FAQ JSON-LD.

- [ ] **Step 6: Wire routes, sitemap, and internal links into the build**

Add one immutable scenario definition:

```python
RETIREMENT_CAPITAL_SCENARIOS = (
    ("retire-abroad-with-500k", 500_000),
    ("retire-abroad-with-750k", 750_000),
    ("retire-abroad-with-1-million", 1_000_000),
    ("retire-abroad-with-1-5-million", 1_500_000),
    ("retire-abroad-with-2-million", 2_000_000),
)
```

Call the Node generator once per build for all five amounts, write each page to `artifacts/<slug>/index.html`, and add each canonical URL to `sitemap_url_entries`. Add concise scenario links to the finder, retirement calculator, and guide hub.

- [ ] **Step 7: Add scenario-page editorial styles**

Use the same shell, header, serif heading scale, paper background, ink, accent, brass, rules, link treatment, footer, and mobile breakpoints as the finder. Use plain ruled rows, not cards or decorative badges.

- [ ] **Step 8: Run focused build and SEO tests to verify GREEN**

Run: `python3 src/build_unified_app.py`

Run: `python3 -m unittest tests.test_retirement_capital_scenario_page tests.test_retirement_destination_finder_page tests.test_seo_infrastructure_integrity`

Expected: build exits 0 and tests PASS.

- [ ] **Step 9: Commit the scenario pages**

```bash
git add src/retirement_capital_scenario_page.py scripts/generate_retirement_capital_scenarios.js src/build_unified_app.py src/site_design_system.py src/retirement_destination_finder_page.py .github/workflows/deploy-pages.yml tests/test_retirement_capital_scenario_page.py tests/test_retirement_destination_finder_page.py tests/test_seo_infrastructure_integrity.py
git commit -m "Add retirement capital scenario pages"
```

---

### Task 5: Integration, responsive QA, and final review

**Files:**
- Modify only if verification identifies a failing requirement in files already listed above.

**Interfaces:**
- Consumes: completed finder, shared result, comparison, and five scenario pages.
- Produces: verified branch ready for PR and production deployment.

- [ ] **Step 1: Run all focused retirement and SEO tests**

Run:

```bash
python3 -m unittest \
  tests.test_retirement_finder_scenario \
  tests.test_retirement_destination_finder \
  tests.test_retirement_destination_finder_ui \
  tests.test_retirement_destination_finder_page \
  tests.test_retirement_capital_scenario_page \
  tests.test_deploy_analytics_config \
  tests.test_seo_infrastructure_integrity
```

Expected: PASS.

- [ ] **Step 2: Run the full regression suite and production build**

Run: `python3 -m unittest discover -s tests`

Run: `python3 src/build_unified_app.py`

Run: `python3 -m py_compile src/build_unified_app.py src/retirement_destination_finder_page.py src/retirement_capital_scenario_page.py src/site_design_system.py`

Run: `git diff --check`

Expected: all commands exit 0.

- [ ] **Step 3: Verify browser behavior at desktop, tablet, and mobile widths**

Verify at 1280, 760, 390, and 320 CSS pixels:

- live calculation shows concise reasons and three default comparison destinations;
- replacement cannot produce duplicates;
- share confirmation and fallback work;
- a shared link opens a read-only result without exposing raw inputs;
- invalid shared links leave the calculator usable;
- each scenario page names the correct amount and outcome;
- no page-level horizontal overflow;
- keyboard focus order and visible focus styles remain intact.

- [ ] **Step 4: Verify production-output privacy and analytics**

Search built HTML and JavaScript event calls to confirm analytics parameters contain no monetary or personal fields. Decode one generated shared URL and verify it contains only the fields in `FinderScenarioV1`.

- [ ] **Step 5: Request independent code review and fix every Critical or Important finding**

Review range: `origin/main..HEAD`.

Reviewer checks financial-method parity, URL validation, privacy, SEO uniqueness, accessibility, responsive behavior, and analytics redaction.

- [ ] **Step 6: Commit verification fixes if needed**

```bash
git add src/retirement_finder_scenario.js src/retirement_destination_finder.js src/retirement_destination_finder_page.py src/retirement_destination_finder_ui.js src/retirement_capital_scenario_page.py src/site_design_system.py src/build_unified_app.py scripts/generate_retirement_capital_scenarios.js .github/workflows/deploy-pages.yml tests/test_retirement_finder_scenario.py tests/test_retirement_destination_finder.py tests/test_retirement_destination_finder_page.py tests/test_retirement_destination_finder_ui.py tests/test_retirement_capital_scenario_page.py tests/test_deploy_analytics_config.py tests/test_seo_infrastructure_integrity.py
git commit -m "Fix retirement finder engagement review findings"
```

- [ ] **Step 7: Re-run the full suite after the final change**

Run: `python3 -m unittest discover -s tests`

Run: `python3 src/build_unified_app.py`

Run: `git diff --check`

Expected: all commands exit 0 and the feature worktree is clean.
