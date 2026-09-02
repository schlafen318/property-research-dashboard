# FIRE Tax Screen and Ranking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a concise, source-backed FIRE Abroad screen whose rankings include a non-duplicative tax reserve and whose results explain likely tax residence, economic tax impact, Tax Readiness, and the foreign-home tax lifecycle.

**Architecture:** Add a validated FIRE evidence overlay, a pure Python build-time model, and a parity-tested dependency-free JavaScript model. Render a useful default ranking at build time and rerank privately in the browser from plain-language controls. Keep tax calculations as favorable/central/adverse planning bands in this increment; exact rules belong to the detailed-engine plan.

**Tech Stack:** Python 3 standard library, `unittest`, JSON, dependency-free browser/CommonJS JavaScript, existing static builder and design system.

**Spec:** `docs/superpowers/specs/2026-08-29-fire-abroad-design.md`

## Global Constraints

- Initial controls ask no exact income, account, gain, cost-basis, wealth, or estate questions.
- Economic tax impact changes annual cost; Tax Readiness remains a separate score and explanation.
- Every tax band and property-tax statement has primary-source IDs, a checked date, confidence, and explicit inclusions.
- User tax selections and results remain browser-local and never enter URLs, analytics, generated personalized HTML, or persistent storage.
- Missing critical evidence produces an unranked or conditional state, never an implicit zero.
- The initial result uses concise text and a simple table/list with progressive details.

---

### Task 1: FIRE overlay contract and evidence skeleton

**Files:**
- Create: `data/fire_abroad.json`
- Create: `src/fire_abroad.py`
- Create: `tests/test_fire_abroad_data.py`

**Interfaces:**
- Produces `load_fire_abroad(path: Path = FIRE_ABROAD_PATH) -> dict`.
- Produces `validate_fire_abroad_payload(payload: dict, destination_ids: set[str], retirement_ids: set[str], as_of: date) -> list[str]`.
- Defines `FIRE_WEIGHTS`, `ACTIVE_LIFE_WEIGHTS`, `VALID_STAY_MODES`, `VALID_TAX_READINESS`, and the ten launch IDs.

- [ ] **Step 1: Write failing contract tests**

```python
def test_launch_tax_screen_contract_is_complete(self):
    payload = load_fire_abroad()
    errors = validate_fire_abroad_payload(
        payload,
        destination_ids=self.destination_ids,
        retirement_ids=self.retirement_ids,
        as_of=date(2026, 9, 1),
    )
    self.assertEqual([], errors)

def test_missing_tax_source_is_rejected(self):
    payload = self.payload_copy()
    payload["countries"]["Spain"]["tax_screen"]["source_ids"] = []
    errors = self.validate(payload)
    self.assertTrue(any("countries.Spain.tax_screen.source_ids" in error for error in errors))
```

- [ ] **Step 2: Run the tests and confirm the missing-module failure**

Run: `python3 -m unittest tests.test_fire_abroad_data -v`

Expected: FAIL because `src.fire_abroad` and `data/fire_abroad.json` do not exist.

- [ ] **Step 3: Implement constants, loader, and all-errors validator**

```python
FIRE_WEIGHTS = {
    "active_life": .25, "sustainable_annual_cost": .20,
    "healthcare_bridge": .15, "stay_flexibility": .10,
    "tax_readiness": .10, "global_access": .08,
    "community_fit": .07, "property_exit_flexibility": .05,
}
VALID_TAX_READINESS = frozenset({
    "straightforward", "moderate", "complex", "highly_profile_dependent"
})

def load_fire_abroad(path=FIRE_ABROAD_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))
```

Validate score bounds, weight sums, source-reference integrity, HTTPS URLs, ISO dates, review intervals, launch IDs, country inheritance, all three stay modes, tax-band ordering, explicit `included_categories`, and the five property lifecycle stages.

- [ ] **Step 4: Add the JSON skeleton and one complete synthetic Spain record**

Use this exact tax-screen shape for every country:

```json
{
  "residence": {"day_band": "183_plus", "summary": "...", "non_day_tests": ["..."], "source_ids": ["..."]},
  "scope_if_resident": "worldwide_income",
  "funding_source_notes": {"portfolio": "...", "pension": "...", "property": "...", "work_business": "...", "mixed": "..."},
  "tax_readiness": "complex",
  "tax_readiness_score": 2.5,
  "planning_bands": {
    "seasonal": {"favorable_rate": 0.00, "central_rate": 0.03, "adverse_rate": 0.08},
    "part_year": {"favorable_rate": 0.03, "central_rate": 0.12, "adverse_rate": 0.22},
    "full_relocation": {"favorable_rate": 0.12, "central_rate": 0.22, "adverse_rate": 0.35}
  },
  "included_categories": ["income_tax_reserve", "social_tax_reserve", "compliance_reserve"],
  "material_flags": ["wealth_tax", "inheritance_tax"],
  "property_lifecycle": {"purchase": {}, "annual": {}, "rental": {}, "sale": {}, "succession": {}},
  "source_ids": ["..."], "last_reviewed": "2026-09-01", "confidence": "high"
}
```

- [ ] **Step 5: Run the contract tests and commit**

Run: `python3 -m unittest tests.test_fire_abroad_data -v`

Expected: PASS.

Commit: `git commit -m "feat: add FIRE tax screen data contract"`

### Task 2: Pure screening, budget, eligibility, and ranking model

**Files:**
- Modify: `src/fire_abroad.py`
- Create: `tests/test_fire_abroad.py`
- Create: `tests/fixtures/fire_abroad_screen_contract.json`

**Interfaces:**
- Produces `normalize_fire_profile(raw: dict) -> dict`.
- Produces `screen_tax(country: dict, profile: dict) -> dict`.
- Produces `build_resilience_budget(cost: dict, profile: dict, tax_screen: dict) -> dict`.
- Produces `rank_fire_abroad_destinations(destinations: list[dict], retirement_costs: dict[str, dict], fire_payload: dict, profile: dict) -> list[dict]`.

- [ ] **Step 1: Write failing profile and tax-band tests**

```python
def test_quick_profile_defaults_do_not_require_financial_values(self):
    self.assertEqual("part_year", normalize_fire_profile({})["stay_mode"])
    self.assertIsNone(normalize_fire_profile({})["annual_income"])

def test_tax_reserve_uses_central_band_and_never_duplicates_after_tax_mode(self):
    estimated = screen_tax(self.country, {"tax_mode": "destination_estimate", "planning_base": 100_000})
    supplied = screen_tax(self.country, {"tax_mode": "user_after_tax", "planning_base": 100_000})
    self.assertEqual(12_000, estimated["central_reserve"])
    self.assertEqual(0, supplied["central_reserve"])
```

- [ ] **Step 2: Run focused tests and verify failure**

Run: `python3 -m unittest tests.test_fire_abroad -v`

- [ ] **Step 3: Implement normalized enums and ordered tax scenarios**

`screen_tax` returns:

```python
{
    "residence_outcome": "likely_resident",
    "scope_summary": "Worldwide income may enter scope.",
    "readiness": "complex",
    "favorable_reserve": 12000,
    "central_reserve": 22000,
    "adverse_reserve": 35000,
    "included_categories": [...],
    "material_flags": [...],
    "source_ids": [...],
    "confidence": "high",
}
```

- [ ] **Step 4: Implement cost composition and deterministic ranking**

Add the central tax reserve to sustainable annual cost only in `destination_estimate` mode. Return all three annual-cost and capital-impact bands. Keep Tax Readiness in its own weighted dimension. Mark results conditional when residence is unresolved or a material flag lacks required evidence.

- [ ] **Step 5: Run focused tests, save parity fixtures, and commit**

Run: `python3 -m unittest tests.test_fire_abroad tests.test_fire_abroad_data -v`

Expected: PASS.

Commit: `git commit -m "feat: rank FIRE destinations with tax reserves"`

### Task 3: JavaScript parity model and private browser controls

**Files:**
- Create: `src/fire_abroad.js`
- Create: `src/fire_abroad_ui.js`
- Create: `tests/test_fire_abroad_js.py`

**Interfaces:**
- Exposes CommonJS/browser API `normalizeProfile`, `screenTax`, `buildResilienceBudget`, and `rankDestinations`.
- Exposes UI entry point `initFireAbroad(rootId, payload)`.

- [ ] **Step 1: Write failing Node parity tests**

Execute the JS model for every record in `tests/fixtures/fire_abroad_screen_contract.json` and compare residence state, readiness, three reserves, annual costs, rank, and conditional status to the expected Python fixture.

- [ ] **Step 2: Run the JS tests and verify the missing-file failure**

Run: `python3 -m unittest tests.test_fire_abroad_js -v`

- [ ] **Step 3: Implement dependency-free model parity**

Use the same enum defaults and rounding contract as Python. Throw on unordered bands or unknown modes; never coerce missing planning bases to zero.

- [ ] **Step 4: Implement minimal controls and rendering helpers**

Bind stay mode, day band, funding source, housing, property use, and optional home-tax context. Render a concise summary with one expandable tax explanation per result. Analytics calls contain event name and destination ID only.

- [ ] **Step 5: Run parity/privacy tests and commit**

Run: `python3 -m unittest tests.test_fire_abroad_js -v`

Expected: PASS.

Commit: `git commit -m "feat: add private FIRE tax screening controls"`

### Task 4: Canonical page and static-builder integration

**Files:**
- Create: `src/fire_abroad_page.py`
- Modify: `src/build_unified_app.py`
- Create: `tests/test_fire_abroad_page.py`
- Modify: `tests/test_navigation_consistency.py`

**Interfaces:**
- Produces `render_fire_abroad_page(...) -> str`.
- Emits `artifacts/fire-abroad/index.html` and sitemap/internal links.

- [ ] **Step 1: Write failing page and integration tests**

Assert canonical metadata, H1, server-rendered default rows, native control labels, Tax Readiness text, tax-impact range, property lifecycle details, checked dates, source links, calculator link allowlist, sitemap inclusion, and absence of sensitive values in analytics.

- [ ] **Step 2: Run page tests and verify failure**

Run: `python3 -m unittest tests.test_fire_abroad_page -v`

- [ ] **Step 3: Implement the minimal server-rendered page**

Use one compact results table/list, one methodology section, and progressive `<details>` elements. Reuse the site shell and utility styles. Do not add cards, badges, duplicated summaries, or a primary-navigation item.

- [ ] **Step 4: Wire data, models, assets, links, and sitemap into the builder**

Fail the build when launch data is invalid or stale. Preserve a useful default page without JavaScript.

- [ ] **Step 5: Run focused build tests and commit**

Run: `python3 -m unittest tests.test_fire_abroad_page tests.test_navigation_consistency -v`

Expected: PASS.

Commit: `git commit -m "feat: publish FIRE Abroad tax screen"`

### Task 5: Populate all launch evidence and verify the increment

**Files:**
- Modify: `data/fire_abroad.json`
- Modify: `tests/test_fire_abroad_data.py`

**Interfaces:**
- Completes records for Portugal, Indonesia, Croatia, Greece, Vietnam, Japan, Thailand, and Spain, covering all ten launch destinations and destination-local overrides.

- [ ] **Step 1: Add completeness tests for every launch destination and country**

Require official sources for residence, worldwide/source scope, the selected funding-source summaries, planning-band basis, and every non-empty property lifecycle claim.

- [ ] **Step 2: Research and populate one country at a time**

For each country, record the official publisher, direct HTTPS URL, effective/source date, accessed date `2026-09-01`, metric supported, scope limitation, and recheck trigger. Where a defensible numerical band cannot be supported, use `tax_impact_unavailable` and make the destination conditional.

- [ ] **Step 3: Run the full build and test suite**

Run: `python3 src/build_unified_app.py`

Run: `python3 -m unittest discover -s tests -v`

Expected: build succeeds and all tests pass.

- [ ] **Step 4: Inspect the page at required widths**

Verify 320, 375, 390, 430, 736, and 1024 pixels; check no overflow, keyboard focus, concise initial rows, progressive tax details, and script-disabled usefulness.

- [ ] **Step 5: Commit the verified evidence release**

Commit: `git commit -m "data: complete FIRE tax screening evidence"`
