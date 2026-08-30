# FIRE Abroad Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish `/fire-abroad/`, a source-backed and interactive destination ranking for active financial independence abroad that distinguishes seasonal, part-year, and full-relocation scenarios.

**Architecture:** Add one FIRE-specific evidence overlay and a pure Python model for validation, build-time scoring, and server-rendered default results. Add an equivalent dependency-free JavaScript model and UI controller for private browser-side reranking, with a shared fixture contract to prevent Python/JavaScript drift. Render the canonical page through a focused page module and connect it to the existing builder, retirement tools, guides, sitemap, analytics, and design system.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, dependency-free browser/CommonJS JavaScript, existing static-site builder and design-system helpers.

**Spec:** `docs/superpowers/specs/2026-08-29-fire-abroad-design.md`

## Global Constraints

- The public name is **FIRE Abroad** and the canonical URL is `/fire-abroad/`.
- Support `seasonal`, `part_year`, and `full_relocation`; permanent residence and property purchase are never universal requirements.
- Default profile: age 50, single household, renting, part-year base.
- Overall weights are Active Life 25%, Sustainable annual cost 20%, Healthcare Bridge 15%, Stay Flexibility 10%, Tax Compatibility 10%, Global Access 8%, Community Fit 7%, and Property and Exit Flexibility 5%.
- Active Life subweights are everyday movement 30%, active-pursuit access 30%, year-round continuity 25%, and activity ecosystem 15%.
- Tax Compatibility measures clarity and administrative complexity; never calculate a personal tax liability or label a destination universally low-tax.
- Keep precise income, balances, citizenship, health, age, tax-home, annual-days, and income-category values out of URLs, analytics, storage, and generated personalized HTML.
- The calculator handoff may contain only validated `destination`, `household`, and `housing` query parameters already accepted by `retirementPrefill()`.
- Use primary or official sources for volatile immigration, tax, healthcare, and financial-infrastructure claims wherever available; every critical claim needs a checked date.
- Missing launch-critical evidence makes the affected destination/mode unranked; missing numerical inputs never become zero.
- Do not add a primary-navigation item, backend, framework, account system, or destination-specific FIRE pages.
- Keep the existing retirement calculator's after-tax-input model unchanged.

## File Structure

- Create `data/fire_abroad.json`: FIRE-specific country evidence, destination overrides, launch coverage, scores, source records, and freshness metadata.
- Create `src/fire_abroad.py`: data contract validation, inheritance resolution, eligibility, resilience budget, scoring, warnings, and deterministic ranking.
- Create `src/fire_abroad.js`: browser/CommonJS implementation of the same normalized profile, eligibility, budget, scoring, and sorting contract.
- Create `src/fire_abroad_ui.js`: DOM binding, accessible rendering, safe calculator links, activity filtering, and privacy-safe analytics payloads.
- Create `src/fire_abroad_page.py`: server-rendered page structure and minimal page-specific styles using the shared site shell.
- Modify `src/build_unified_app.py`: constants, loaders, page builder adapter, asset embedding, route output, sitemap, and contextual links.
- Modify `src/site_design_system.py`: only the small shared utility selectors required by the FIRE page, if existing utility styles cannot express them.
- Create `tests/fixtures/fire_abroad_contract.json`: fixed cross-runtime scoring cases.
- Create `tests/test_fire_abroad_data.py`: schema, coverage, source, freshness, and identifier integrity.
- Create `tests/test_fire_abroad.py`: Python model behavior and error cases.
- Create `tests/test_fire_abroad_js.py`: JavaScript model parity, safe links, privacy, and UI helper behavior.
- Create `tests/test_fire_abroad_page.py`: generated HTML, metadata, accessibility, static fallback, links, and analytics contract.
- Modify `tests/test_site_design_system.py`: only if `src/site_design_system.py` changes.

---

### Task 1: FIRE Evidence Contract and Launch Dataset

**Files:**
- Create: `data/fire_abroad.json`
- Create: `src/fire_abroad.py`
- Create: `tests/test_fire_abroad_data.py`

**Interfaces:**
- Produces: `FIRE_WEIGHTS: dict[str, float]`, `ACTIVE_LIFE_WEIGHTS: dict[str, float]`, `VALID_STAY_MODES: frozenset[str]`, `load_fire_abroad(path: Path) -> dict`, and `validate_fire_abroad_payload(payload: dict, *, destination_ids: set[str], retirement_ids: set[str], as_of: date) -> list[str]`.
- Produces data keys consumed later: `launch_destination_ids`, `countries`, `destination_overrides`, `weights`, `active_life_weights`, and `review_policy`.

- [ ] **Step 1: Write failing data-contract tests**

Create `tests/test_fire_abroad_data.py` with a helper that loads `data/destinations.json`, `data/retirement_costs.json`, and the new overlay. Assert the exact ten launch IDs, weight sums, required country/destination sections, accepted enums, HTTPS sources, ISO dates, source-reference integrity, and no unsupported destination IDs.

```python
from datetime import date
from pathlib import Path
import json
import unittest

from src.fire_abroad import (
    ACTIVE_LIFE_WEIGHTS,
    FIRE_WEIGHTS,
    load_fire_abroad,
    validate_fire_abroad_payload,
)

ROOT = Path(__file__).resolve().parents[1]
LAUNCH_IDS = {
    "algarve-cascais", "bali", "croatia-istria-dalmatia", "crete",
    "da-nang-hoi-an", "fukuoka-itoshima", "madeira",
    "malaga-costa-del-sol", "phuket-koh-samui", "valencia",
}

class FireAbroadDataTests(unittest.TestCase):
    def test_launch_contract_is_complete_and_valid(self) -> None:
        payload = load_fire_abroad()
        destination_rows = json.loads((ROOT / "data/destinations.json").read_text())
        destination_ids = {row["id"] for row in destination_rows}
        retirement_ids = {
            row["destination_id"]
            for row in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
        }
        self.assertEqual(LAUNCH_IDS, set(payload["launch_destination_ids"]))
        self.assertEqual(1.0, sum(FIRE_WEIGHTS.values()))
        self.assertEqual(1.0, sum(ACTIVE_LIFE_WEIGHTS.values()))
        self.assertEqual(
            [],
            validate_fire_abroad_payload(
                payload,
                destination_ids=destination_ids,
                retirement_ids=retirement_ids,
                as_of=date(2026, 8, 29),
            ),
        )
```

Add mutation tests that remove a tax source, set `everyday_movement` to `None`, introduce a dangling source ID, and make a volatile review date exceed its interval. Assert that every error contains the destination or country ID plus the offending field path.

- [ ] **Step 2: Run the data tests to verify they fail**

Run: `python3 -m unittest tests.test_fire_abroad_data -v`

Expected: FAIL because `src.fire_abroad` and `data/fire_abroad.json` do not exist.

- [ ] **Step 3: Implement constants, loader, and strict validator**

Start `src/fire_abroad.py` with the exact contract below. Return all validation errors rather than failing at the first one; `load_fire_abroad()` raises `ValueError("Invalid FIRE Abroad data:\n- ...")` when validation is requested by the builder in Task 4.

```python
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIRE_ABROAD_PATH = ROOT / "data" / "fire_abroad.json"

FIRE_WEIGHTS = {
    "active_life": 0.25,
    "sustainable_annual_cost": 0.20,
    "healthcare_bridge": 0.15,
    "stay_flexibility": 0.10,
    "tax_compatibility": 0.10,
    "global_access": 0.08,
    "community_fit": 0.07,
    "property_exit_flexibility": 0.05,
}
ACTIVE_LIFE_WEIGHTS = {
    "everyday_movement": 0.30,
    "active_pursuits": 0.30,
    "year_round_continuity": 0.25,
    "activity_ecosystem": 0.15,
}
VALID_STAY_MODES = frozenset({"seasonal", "part_year", "full_relocation"})
VALID_ELIGIBILITY = frozenset({"eligible", "conditional", "needs_verification", "not_eligible"})
VALID_WORK_PERMISSIONS = frozenset({"passive_only", "remote_permitted", "local_permitted", "unclear"})
VALID_CONFIDENCE = frozenset({"low", "medium", "medium_high", "high"})

def load_fire_abroad(path: Path = FIRE_ABROAD_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
```

The validator must enforce scores from 0 through 5, unique source IDs, every referenced source present, `https://` URLs, `YYYY-MM-DD` dates, positive review intervals, all three stay modes, all four Active Life subcomponents, and every launch ID's presence in both shared datasets.

- [ ] **Step 4: Research and populate the ten-destination overlay**

Create `data/fire_abroad.json` with this top-level shape and exact enums:

```json
{
  "schema_version": 1,
  "reviewed_on": "2026-08-29",
  "review_policy": {
    "immigration_days": 90,
    "tax_days": 90,
    "healthcare_days": 180,
    "financial_infrastructure_days": 180,
    "active_life_days": 365
  },
  "weights": {
    "active_life": 0.25,
    "sustainable_annual_cost": 0.20,
    "healthcare_bridge": 0.15,
    "stay_flexibility": 0.10,
    "tax_compatibility": 0.10,
    "global_access": 0.08,
    "community_fit": 0.07,
    "property_exit_flexibility": 0.05
  },
  "active_life_weights": {
    "everyday_movement": 0.30,
    "active_pursuits": 0.30,
    "year_round_continuity": 0.25,
    "activity_ecosystem": 0.15
  },
  "launch_destination_ids": [],
  "countries": {},
  "destination_overrides": {}
}
```

Populate the exact launch IDs from Step 1. Country records cover Croatia, Greece, Indonesia, Japan, Portugal, Spain, Thailand, and Vietnam. Each country record contains `stay_routes` for all three modes, `tax`, `healthcare`, `financial_infrastructure`, and `sources`. Each destination override contains `country`, `active_life`, `activity_tags`, `rent_flexibility_score`, `one_time_relocation_usd`, `risk_warnings`, `source_ids`, `confidence`, and `last_reviewed`. `activity_tags` is a non-empty subset of `walking`, `cycling`, `hiking`, `water`, `winter_sports`, and `fitness_social`.

For each stay route record use:

```json
{
  "status": "conditional",
  "base_score": 3.5,
  "max_days": 180,
  "minimum_age": null,
  "summary": "Plain-language route and duration condition.",
  "work_permission": "passive_only",
  "source_ids": ["country-immigration-1"],
  "last_reviewed": "2026-08-29",
  "confidence": "high"
}
```

Use `max_days: null` only when no single standard cap accurately represents the route. Record tax `standard_day_threshold`, `non_day_tests`, `scope_if_resident`, `category_flags`, `treaty_reporting_note`, `compatibility_score`, `source_ids`, `last_reviewed`, and `confidence`. A higher `compatibility_score` means clearer rules and lower administrative friction, never a lower personal tax rate. Record healthcare mode-specific `bridge_score`, eligibility, waiting-period, age-limit, pre-existing-condition, and evacuation summaries. Do not copy marketing claims or infer legal permission from property ownership.

Use official immigration, tax-authority, health-system, central-bank, government, airport/transit, and municipal sources first. If a primary source cannot support a launch-critical field, set the relevant status to `needs_verification`; do not invent a score to keep the destination ranked.

- [ ] **Step 5: Run the data tests and inspect validation output**

Run: `python3 -m unittest tests.test_fire_abroad_data -v`

Expected: PASS with ten launch destinations, eight country records, valid sources, and no stale critical evidence as of 2026-08-29.

- [ ] **Step 6: Commit the evidence contract**

```bash
git add data/fire_abroad.json src/fire_abroad.py tests/test_fire_abroad_data.py
git commit -m "feat: add FIRE Abroad evidence contract"
```

---

### Task 2: Python Eligibility, Budget, and Ranking Model

**Files:**
- Modify: `src/fire_abroad.py`
- Create: `tests/fixtures/fire_abroad_contract.json`
- Create: `tests/test_fire_abroad.py`

**Interfaces:**
- Consumes: the validated overlay from Task 1 plus consolidated destination and retirement-cost dictionaries.
- Produces: `normalize_fire_profile(raw: dict) -> dict`, `resolve_country_record(destination: dict, payload: dict) -> dict`, `active_life_score(record: dict) -> float`, `build_resilience_budget(cost: dict, profile: dict) -> dict`, `eligibility_for_mode(country: dict, profile: dict) -> dict`, and `rank_fire_abroad_destinations(destinations: list[dict], retirement_costs: dict[str, dict], fire_payload: dict, profile: dict) -> list[dict]`.

- [ ] **Step 1: Write failing normalization and eligibility tests**

Create tests for defaults, boundary ages, all stay modes, missing mobility rights, and a missing full-relocation route. Use small synthetic country records so the tests isolate behavior.

```python
def test_profile_defaults_are_the_static_page_defaults(self) -> None:
    self.assertEqual(
        {
            "stay_mode": "part_year", "age": 50, "household": "single",
            "housing": "rent", "mobility_rights": "prefer_not_to_say",
            "home_tax_context": "prefer_not_to_say", "annual_days": None,
            "income_type": "prefer_not_to_say", "activity_priority": "balanced",
        },
        normalize_fire_profile({}),
    )

def test_no_long_term_route_blocks_full_relocation_only(self) -> None:
    country = self.country_fixture(full_relocation_status="not_eligible")
    seasonal = eligibility_for_mode(country, normalize_fire_profile({"stay_mode": "seasonal"}))
    relocation = eligibility_for_mode(country, normalize_fire_profile({"stay_mode": "full_relocation"}))
    self.assertEqual("eligible", seasonal["status"])
    self.assertEqual("not_eligible", relocation["status"])
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python3 -m unittest tests.test_fire_abroad.FireProfileTests -v`

Expected: FAIL because the profile and eligibility functions are undefined.

- [ ] **Step 3: Implement normalization and eligibility**

Validate against fixed allowlists. Clamp age to 18–100; treat invalid values as the documented defaults. Never convert an absent nationality-dependent condition into eligibility. Apply `minimum_age` inclusively. Return:

- `stay_mode`: `seasonal`, `part_year`, or `full_relocation`;
- `household`: `single` or `couple`;
- `housing`: `rent`, `own`, `buy_now`, or `buy_retirement`;
- `mobility_rights`: `local_free_movement`, `general_nonlocal`, or `prefer_not_to_say`;
- `home_tax_context`: `us_person`, `other`, or `prefer_not_to_say`;
- `annual_days`: `None` or an integer from 1 through 366;
- `income_type`: `portfolio`, `pension`, `property`, `business_consulting`, `mixed`, or `prefer_not_to_say`; and
- `activity_priority`: `balanced`, `walking`, `cycling`, `hiking`, `water`, `winter_sports`, or `fitness_social`.

```python
{
    "status": "eligible",  # eligible | conditional | needs_verification | not_eligible
    "reason": "Plain-language route summary",
    "work_permission": "remote_permitted",
    "stay_score": 4.0,
}
```

If the user's income type is `business_consulting`, subtract 0.5 from `stay_score` for `passive_only` and 1.0 for `unclear`, clamped to 0–5. Do not penalize work permission for portfolio, pension, property, mixed, or prefer-not-to-say profiles; display the flag instead.

- [ ] **Step 4: Write failing resilience-budget tests**

Cover rent, already-own, buy-now, and buy-at-retirement. Assert that shared healthcare, travel, visa/admin, and contingency categories appear once. The currency/inflation buffer is 10% of recurring categories excluding `contingency`, and one-time relocation cost is returned separately.

```python
def test_resilience_budget_does_not_double_count_shared_categories(self) -> None:
    budget = build_resilience_budget(self.cost_fixture(), normalize_fire_profile({"housing": "rent"}))
    self.assertEqual(1000, budget["categories"]["private_healthcare"])
    self.assertEqual(600, budget["categories"]["travel"])
    self.assertEqual(200, budget["categories"]["visa_admin"])
    recurring_without_contingency = sum(
        value for key, value in budget["categories"].items() if key != "contingency"
    )
    self.assertEqual(round(recurring_without_contingency * 0.10), budget["currency_inflation_buffer"])
```

- [ ] **Step 5: Implement resilience budgeting and fixed cost-score anchors**

For `rent`, add `annual_rent_usd`; for `own` and `buy_now`, add `annual_owner_costs_usd`; for `buy_retirement`, use rent for the current screening budget and report acquisition capital separately. Return `annual_total_usd`, `categories`, `currency_inflation_buffer`, `property_capital_usd`, and `one_time_relocation_usd`.

Convert annual cost to a stable 0–5 score using linear anchors, not launch-set percentiles:

```python
COST_SCORE_ANCHORS = {
    "single": {"five": 30_000, "zero": 90_000},
    "couple": {"five": 45_000, "zero": 135_000},
}

def annual_cost_score(annual_total_usd: float, household: str) -> float:
    anchors = COST_SCORE_ANCHORS[household]
    ratio = (annual_total_usd - anchors["five"]) / (anchors["zero"] - anchors["five"])
    return round(max(0.0, min(5.0, 5.0 * (1.0 - ratio))), 2)
```

- [ ] **Step 6: Write failing score-composition and ordering tests**

Assert Active Life composition, overall weighting, score bounds, destination-dimension mapping, eligibility ordering, confidence tie-break, alphabetical final tie-break, US-person warning, tax-residence day warning, and unranked missing evidence.

Use these exact mappings:

- `global_access`: existing destination dimension `global_access`.
- `community_fit`: existing destination dimension `foreigner_fit`.
- `property_exit_flexibility`: mean of existing `exit_liquidity`, existing `ownership_clarity`, and overlay `rent_flexibility_score`.
- `healthcare_bridge`: overlay country mode score.
- `stay_flexibility`: eligibility result `stay_score`.
- `tax_compatibility`: overlay `compatibility_score` for the selected mode; a day warning changes explanatory flags but not the score.

- [ ] **Step 7: Implement ranking and warnings**

Round component and total scores to two decimal places. Sort status groups in this order: eligible, conditional, needs_verification, not_eligible. Within eligible/conditional groups sort score descending, confidence rank `high > medium_high > medium > low`, then display name ascending. Return view models with the exact keys used by both runtimes:

```python
{
    "destination_id": "valencia",
    "name": "Valencia",
    "status": "eligible",
    "status_reason": "...",
    "score": 4.12,
    "components": {"active_life": 4.3, "sustainable_annual_cost": 3.8},
    "resilience_budget": {"annual_total_usd": 48000},
    "work_permission": "remote_permitted",
    "warnings": ["Tax residence likely at the selected day count."],
    "strongest_activity_reason": "Daily cycling and year-round park access.",
    "confidence": "high",
    "last_reviewed": "2026-08-29"
}
```

Add the US worldwide-filing reminder when `home_tax_context == "us_person"`. Add a local tax-residence warning when `annual_days` meets or exceeds `standard_day_threshold`; always append non-day-test language when present.

- [ ] **Step 8: Add the shared contract fixture and pass the Python suite**

Create `tests/fixtures/fire_abroad_contract.json` with at least six cases: default, seasonal under 50, exact minimum age, full relocation unavailable, consulting with passive-only work permission, and US person over the tax day threshold. Store normalized inputs plus expected ordered IDs, statuses, scores, annual budgets, and warning substrings.

Run: `python3 -m unittest tests.test_fire_abroad -v`

Expected: PASS.

- [ ] **Step 9: Commit the Python model**

```bash
git add src/fire_abroad.py tests/test_fire_abroad.py tests/fixtures/fire_abroad_contract.json
git commit -m "feat: rank FIRE Abroad destinations"
```

---

### Task 3: Browser Ranking Parity and Privacy-Safe UI Helpers

**Files:**
- Create: `src/fire_abroad.js`
- Create: `src/fire_abroad_ui.js`
- Create: `tests/test_fire_abroad_js.py`

**Interfaces:**
- Consumes: the embedded normalized destination, cost, and overlay payload from Task 4.
- Produces from `src/fire_abroad.js`: `normalizeProfile(raw)`, `activeLifeScore(record)`, `buildResilienceBudget(cost, profile)`, `eligibilityForMode(country, profile)`, and `rankDestinations(payload, rawProfile)`.
- Produces from `src/fire_abroad_ui.js`: `safeCalculatorHref(destinationId, profile)`, `safeAnalyticsPayload(eventName, details)`, `resultRowsForDisplay(results, activityPriority)`, and `initFireAbroad(root)`.

- [ ] **Step 1: Write failing cross-runtime contract tests**

In `tests/test_fire_abroad_js.py`, invoke CommonJS exports with Node using the established subprocess pattern from `tests/test_retirement_destination_finder_ui.py`. Load every case from `tests/fixtures/fire_abroad_contract.json` and compare normalized profiles, ordered IDs, statuses, rounded scores, budgets, and warning substrings.

```python
def run_js(module: Path, function_name: str, payload: object) -> object:
    script = (
        "const mod=require(process.argv[1]);"
        "const value=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(mod.{function_name}(value)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(module), json.dumps(payload)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)
```

- [ ] **Step 2: Run the JavaScript tests to verify they fail**

Run: `python3 -m unittest tests.test_fire_abroad_js -v`

Expected: FAIL because both JavaScript modules are absent.

- [ ] **Step 3: Implement the dependency-free ranking module**

Use a UMD/CommonJS wrapper consistent with existing browser engines:

```javascript
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.GHAFireAbroad = api;
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  // Pure functions only; no DOM, storage, network, or analytics here.
  return { normalizeProfile, activeLifeScore, buildResilienceBudget, eligibilityForMode, rankDestinations };
});
```

Port the Python formulas exactly, including 10% currency/inflation buffer, fixed cost anchors, work-permission modifiers, status ordering, confidence ordering, two-decimal rounding, and alphabetical tie-break. Never use truthiness to replace a valid zero or a missing score.

- [ ] **Step 4: Write failing privacy and link-helper tests**

Assert the handoff contains only the allowlisted values and that invalid slugs or enums fall back safely.

```python
def test_calculator_href_excludes_fire_profile_and_financial_details(self) -> None:
    href = run_js(UI, "safeCalculatorHref", {
        "destinationId": "valencia",
        "profile": {
            "household": "couple", "housing": "buy_now", "age": 52,
            "homeTaxContext": "us_person", "annualDays": 190,
            "incomeType": "business_consulting", "netWorth": 2500000,
        },
    })
    self.assertEqual(
        "/retirement-abroad-calculator/?destination=valencia&household=couple&housing=buy_now",
        href,
    )
```

Read the source and reject `fetch(`, `XMLHttpRequest`, `localStorage`, `sessionStorage`, precise sensitive analytics keys, or DOM HTML insertion from unescaped data.

- [ ] **Step 5: Implement UI helpers and DOM controller**

`safeAnalyticsPayload()` accepts only `page_view`, `stay_mode_change`, `activity_filter_use`, `destination_guide_click`, and `calculator_handoff`. It may return event name plus non-sensitive destination ID, stay-mode category, or activity-filter category; it must drop age, mobility rights, tax context, days, income type, costs, and scores.

`initFireAbroad(root)` must:

1. parse the embedded JSON payload;
2. bind labeled controls once;
3. normalize the profile and rerank on explicit form submission or control change;
4. render text with `textContent` and build links through safe helpers;
5. keep eligibility and warnings textual rather than color-only;
6. update an `aria-live="polite"` result summary;
7. retain unranked conditional/verification items after ranked results; and
8. call `window.GHA.track` only with `safeAnalyticsPayload()` output.

- [ ] **Step 6: Run the JavaScript suite and parity contract**

Run: `python3 -m unittest tests.test_fire_abroad_js -v`

Expected: PASS for all shared fixtures, safe URL behavior, privacy scans, and UI helpers.

- [ ] **Step 7: Commit browser behavior**

```bash
git add src/fire_abroad.js src/fire_abroad_ui.js tests/test_fire_abroad_js.py
git commit -m "feat: add interactive FIRE Abroad ranking"
```

---

### Task 4: Server-Rendered FIRE Abroad Page

**Files:**
- Create: `src/fire_abroad_page.py`
- Create: `tests/test_fire_abroad_page.py`
- Modify: `src/build_unified_app.py:1-175`
- Modify: `src/build_unified_app.py:6011-6075`

**Interfaces:**
- Consumes: default result view models from `rank_fire_abroad_destinations()`, normalized embedded payload JSON, shared header/footer HTML, shared design CSS, engine source, UI source, metadata, and analytics script.
- Produces: `build_fire_abroad_html(*, head: str, navigation: str, default_results: list[dict], payload_json: str, engine_js: str, ui_js: str, design_css: str, analytics: str, footer: str) -> str` and builder adapter `build_fire_abroad_page(destinations: list[dict], retirement_costs: dict, fire_payload: dict) -> str`.

- [ ] **Step 1: Write failing page-structure tests**

Generate the page through `build_fire_abroad_page()` in the test and assert:

- exact title, canonical, H1, and primary search answer;
- `WebPage` or `CollectionPage` plus `BreadcrumbList`, with no rating/review schema;
- default profile controls with labels and exact values;
- ten valid launch IDs in embedded data;
- server-rendered default ranking, score methodology, resilience budget, tax/immigration distinction, and evidence dates;
- `aria-live="polite"`, visible textual statuses, keyboard-operable native controls, and a useful `noscript` explanation;
- only destination/household/housing in calculator links; and
- no primary-navigation expansion.

```python
def test_default_page_answers_the_query_without_javascript(self) -> None:
    self.assertIn("<h1>FIRE Abroad</h1>", self.html)
    self.assertIn("financial independence", self.html.lower())
    self.assertIn('data-default-stay-mode="part_year"', self.html)
    self.assertIn('id="fire-results" aria-live="polite"', self.html)
    self.assertIn("Immigration status and tax residence are separate", self.html)
    self.assertIn("Active Life", self.html)
    self.assertIn("Resilience budget", self.html)
```

- [ ] **Step 2: Run page tests to verify they fail**

Run: `python3 -m unittest tests.test_fire_abroad_page -v`

Expected: FAIL because the page module and builder adapter do not exist.

- [ ] **Step 3: Add builder constants, imports, and paths**

Add exact constants beside the retirement routes:

```python
FIRE_ABROAD_SLUG = "fire-abroad"
FIRE_ABROAD_TITLE = "FIRE Abroad: Best Places for an Active Life Overseas | Global Home Atlas"
FIRE_ABROAD_DESCRIPTION = (
    "Compare FIRE Abroad destinations for active living, sustainable costs, healthcare, "
    "legal stay options, tax complexity, global access, and long-term flexibility."
)
FIRE_ABROAD_PATH = DATA / "fire_abroad.json"
FIRE_ABROAD_ENGINE_PATH = ROOT / "src" / "fire_abroad.js"
FIRE_ABROAD_UI_PATH = ROOT / "src" / "fire_abroad_ui.js"
```

Import `build_fire_abroad_html` and the Python model in both package and direct-execution branches. Add `load_fire_abroad_for_build()` that validates against current destination and retirement IDs and raises one actionable error list before rendering.

- [ ] **Step 4: Implement the focused page template**

Use the existing `site_header_html()`, `site_footer_html()`, metadata helpers, and `top_level_page_design_css()`. Keep page-specific markup minimal: hero answer, compact profile form, result table/list, methodology, evidence disclosure, and visible FAQs only when they add distinct search value.

Required form values:

```html
<select id="fire-stay-mode">
  <option value="seasonal">Seasonal</option>
  <option value="part_year" selected>Part-year base</option>
  <option value="full_relocation">Full relocation</option>
</select>
<input id="fire-age" type="number" min="18" max="100" value="50">
<select id="fire-household"><option value="single" selected>Single</option><option value="couple">Couple</option></select>
<select id="fire-housing">
  <option value="rent" selected>Rent</option><option value="own">Already own</option>
  <option value="buy_now">Buy now</option><option value="buy_retirement">Buy at retirement</option>
</select>
```

Add optional mobility-rights, home-tax-context, annual-days, income-type, and activity-priority controls using the enums from Tasks 1–3. Keep detailed sources in native `<details>` elements. Use a simple responsive table when space permits and a linear labeled list below 760px; do not use decorative score pills or duplicate summaries.

- [ ] **Step 5: Implement the builder adapter and static default**

Normalize `{}` to the default profile and generate default results in Python. Embed only the ten launch destinations, their shared cost records, the validated FIRE overlay, and the static default profile in `<script id="fire-abroad-data" type="application/json">`. Escape `<`, `>`, and `&` in embedded JSON before inserting it.

Render default result rows directly into HTML. Then embed the pure engine, UI module, and an initializer that runs `GHAFireAbroadUI.initFireAbroad(window)` after the DOM is available. The static HTML must remain coherent when that initializer never runs.

- [ ] **Step 6: Run page and model tests**

Run: `python3 -m unittest tests.test_fire_abroad_page tests.test_fire_abroad tests.test_fire_abroad_js -v`

Expected: PASS.

- [ ] **Step 7: Commit the page component**

```bash
git add src/fire_abroad_page.py src/build_unified_app.py tests/test_fire_abroad_page.py
git commit -m "feat: render the FIRE Abroad page"
```

---

### Task 5: Build Route, Sitemap, Contextual Links, and Analytics

**Files:**
- Modify: `src/build_unified_app.py:4470-4485`
- Modify: `src/build_unified_app.py:6011-6075`
- Modify: `src/build_unified_app.py:6450-6535`
- Modify: `src/build_unified_app.py:7110-7590`
- Modify: `src/build_unified_app.py:10195-10220`
- Modify: `src/build_unified_app.py:11580-11625`
- Modify: `tests/test_fire_abroad_page.py`
- Modify: `tests/test_country_content_link_graph.py`

**Interfaces:**
- Consumes: `build_fire_abroad_page()` from Task 4.
- Produces: `artifacts/fire-abroad/index.html`, sitemap entry, and contextual inbound links from the approved planning and guide surfaces.

- [ ] **Step 1: Extend failing integration tests**

Make `tests/test_fire_abroad_page.py.setUpClass()` run the complete builder. Assert the artifact exists and that the sitemap contains exactly one canonical FIRE URL. Assert contextual links from:

- `artifacts/guides/index.html`;
- `artifacts/retirement-abroad-calculator/index.html`;
- `artifacts/retirement-destination-finder/index.html`;
- `artifacts/best-places-to-buy-property-abroad-for-retirement/index.html`; and
- `artifacts/buying-property-abroad-for-retirement/index.html`.

In `tests/test_country_content_link_graph.py`, assert launch destination/country pages include `/fire-abroad/` only where the destination is in `launch_destination_ids`. Assert `PRIMARY_NAV_LINKS` is unchanged.

- [ ] **Step 2: Run integration tests to verify they fail**

Run: `python3 -m unittest tests.test_fire_abroad_page tests.test_country_content_link_graph -v`

Expected: FAIL because the builder does not emit or link the route.

- [ ] **Step 3: Emit the route and sitemap entry**

Load and validate the overlay once in `build()`. After the retirement finder output, write:

```python
fire_abroad_dir = ARTIFACTS / FIRE_ABROAD_SLUG
fire_abroad_dir.mkdir(parents=True, exist_ok=True)
(fire_abroad_dir / "index.html").write_text(
    clean_generated_html(build_fire_abroad_page(destinations, retirement_costs, fire_payload)),
    encoding="utf-8",
)
```

Add `(page_url(FIRE_ABROAD_SLUG), "0.92")` once to `sitemap_url_entries()`.

- [ ] **Step 4: Add restrained contextual links**

Add one distinct FIRE Abroad link to each approved planning surface. Use copy appropriate to context, for example `Compare active FIRE Abroad destinations`, and `data-track="fire_abroad_open"` with a non-sensitive surface label.

For destination and country pages, add a shared helper:

```python
def fire_abroad_context_link(destination_ids: set[str], fire_ids: set[str]) -> str:
    if not destination_ids.intersection(fire_ids):
        return ""
    return (
        f'<p class="context-link"><a href="/{FIRE_ABROAD_SLUG}/" '
        'data-track="fire_abroad_open">Compare this market for FIRE Abroad</a></p>'
    )
```

Call it only with the launch set; do not add a nav item or site-wide footer link.

- [ ] **Step 5: Wire privacy-safe analytics**

Track only page view, stay-mode category, activity-filter category, destination-guide destination ID, and calculator-handoff destination ID. Add a source scan assertion that generated analytics never includes `age`, `home_tax_context`, `annual_days`, `income_type`, `mobility_rights`, `annual_total_usd`, or component scores.

- [ ] **Step 6: Run integration and regression tests**

Run: `python3 -m unittest tests.test_fire_abroad_page tests.test_country_content_link_graph tests.test_retirement_calculator_page tests.test_retirement_destination_finder_page tests.test_navigation_consistency -v`

Expected: PASS with one FIRE route, required contextual links, unchanged primary navigation, and unchanged calculator query allowlist.

- [ ] **Step 7: Commit route integration**

```bash
git add src/build_unified_app.py tests/test_fire_abroad_page.py tests/test_country_content_link_graph.py
git commit -m "feat: connect FIRE Abroad to retirement research"
```

---

### Task 6: Accessibility, Responsive Layout, and Failure-State Hardening

**Files:**
- Modify: `src/fire_abroad_page.py`
- Modify: `src/fire_abroad_ui.js`
- Modify: `src/site_design_system.py` only if a reusable utility rule is necessary
- Modify: `tests/test_fire_abroad_page.py`
- Modify: `tests/test_fire_abroad_js.py`
- Modify: `tests/test_site_design_system.py` only if the design system changes

**Interfaces:**
- Consumes: the complete generated page and browser controller.
- Produces: accessible small-screen rendering, script-disabled fallback, clear invalid/stale states, and no horizontal overflow.

- [ ] **Step 1: Add failing accessibility and failure-state tests**

Use `HTMLParser` as in `tests/test_retirement_calculator_page.py` to assert every input/select has a matching label, the results summary has `aria-live="polite"`, warnings are text, and the page includes a `<noscript>` block. Add UI tests for invalid age/day values, missing critical fields, conditional eligibility, and `needs_verification` ordering.

Assert the page CSS includes a breakpoint at 760px or below that changes the comparison table into a labeled linear layout and preserves 44px control targets without hiding status text.

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python3 -m unittest tests.test_fire_abroad_page tests.test_fire_abroad_js -v`

Expected: FAIL on the newly asserted failure and responsive behaviors.

- [ ] **Step 3: Implement accessible state updates and responsive rules**

On every rerank, update one concise live-region sentence such as `10 destinations evaluated; 6 eligible, 2 conditional, 2 need verification.` Do not move keyboard focus automatically. For validation failure, place a visible text error beside the control and preserve the last valid results.

At small widths, use CSS grid labels or `data-label` plus accessible headers; never require horizontal scrolling to understand a result. Maintain 44px minimum height for controls and links. Use the existing design tokens and square/restrained surfaces; do not add badges, chips, duplicate summary cards, or ornamental sections.

- [ ] **Step 4: Verify static and script-disabled behavior**

Run: `python3 src/build_unified_app.py`

Expected: exits 0 and creates `artifacts/fire-abroad/index.html` containing populated default rows, methodology, source disclosures, and `<noscript>` guidance.

Serve locally:

```bash
python3 -m http.server 4173 --directory artifacts
```

Inspect `/fire-abroad/` at 320, 375, 390, 430, 736, and 1024 CSS pixels. Exercise all stay modes; ages 49, 50, 59, and 60; both households; all housing modes; absent optional context; a US-person profile above a recorded tax threshold; and an activity filter. Confirm no overflow, clear focus, stable ordering, textual warnings, and safe calculator URLs.

- [ ] **Step 5: Run focused tests and commit hardening**

Run: `python3 -m unittest tests.test_fire_abroad_page tests.test_fire_abroad_js tests.test_site_design_system -v`

Expected: PASS.

```bash
git add src/fire_abroad_page.py src/fire_abroad_ui.js src/site_design_system.py tests/test_fire_abroad_page.py tests/test_fire_abroad_js.py tests/test_site_design_system.py
git commit -m "fix: harden FIRE Abroad responsive states"
```

If `src/site_design_system.py` and its test are unchanged, omit them from `git add`.

---

### Task 7: Full Verification and Deployment Readiness

**Files:**
- Modify only files required to correct failures found by the commands below.

**Interfaces:**
- Consumes: all completed tasks.
- Produces: a clean, tested build ready for the repository's normal deployment workflow.

- [ ] **Step 1: Run all FIRE Abroad tests from a clean build**

Run:

```bash
python3 -m unittest \
  tests.test_fire_abroad_data \
  tests.test_fire_abroad \
  tests.test_fire_abroad_js \
  tests.test_fire_abroad_page -v
```

Expected: PASS.

- [ ] **Step 2: Run the complete unit-test suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: PASS with no existing retirement, destination, SEO, navigation, or design-system regressions.

- [ ] **Step 3: Build and run static-site verification**

Run:

```bash
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
```

Expected: both commands exit 0; the verifier reports no broken internal links, missing canonical page, invalid sitemap entry, or missing artifact.

- [ ] **Step 4: Inspect privacy and generated-output invariants**

Run:

```bash
rg -n 'netWorth|home_tax_context|annual_days|income_type|mobility_rights|localStorage|sessionStorage|XMLHttpRequest|fetch\(' artifacts/fire-abroad/index.html src/fire_abroad.js src/fire_abroad_ui.js
rg -n 'fire-abroad' artifacts/sitemap.xml artifacts/guides/index.html artifacts/retirement-abroad-calculator/index.html artifacts/retirement-destination-finder/index.html
```

Expected: the first command shows only declared local control identifiers or privacy tests, never personalized values, storage, or network calls; the second shows one sitemap URL and the required contextual links.

- [ ] **Step 5: Review the diff against the approved spec**

Run: `git diff --check && git status --short && git log --oneline --decorate -8`

Expected: no whitespace errors, only scoped implementation files, and the planned incremental commits.

- [ ] **Step 6: Commit any verification-only corrections**

If Step 1–5 required corrections:

```bash
git add data/fire_abroad.json src/fire_abroad.py src/fire_abroad.js src/fire_abroad_ui.js src/fire_abroad_page.py src/build_unified_app.py src/site_design_system.py tests
git commit -m "fix: complete FIRE Abroad verification"
```

If no corrections were needed, do not create an empty commit. Deployment is a separate explicit execution step using the repository's existing workflow after branch review.
