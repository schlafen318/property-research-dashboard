# Human-Readable Market Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn destination profiles and the all-markets dashboard into calm, human-readable research pages with progressive disclosure for advanced tools.

**Architecture:** Keep the existing static-site generator and destination data model. Restructure the two generated page templates in `src/build_unified_app.py`, introduce focused markup helpers only where they prevent duplication, and protect the new reading hierarchy with behavior-level HTML tests plus browser verification.

**Tech Stack:** Python 3, `unittest`, generated HTML/CSS/JavaScript, static-file browser preview.

**Spec:** `docs/superpowers/specs/2026-08-18-human-readable-market-pages-design.md`

## Global Constraints

- Put the reader's next decision first.
- Show each fact once in the most useful location.
- Use “Overall rating,” “Price guide,” “Expected net yield,” “Ownership clarity,” “Global rank,” and “Main risk” consistently.
- Prefer whitespace and typographic hierarchy over nested cards, chips, badges, and repeated headings.
- Keep advanced research tools available through progressive disclosure.
- Preserve destination data, ranking logic, filtering, sorting, comparison calculations, saved-state behavior, analytics events, SEO metadata, and canonical top navigation.
- Do not add country pages, research sections, scoring dimensions, or marketing calls to action.

---

### Task 1: Destination hero and at-a-glance reading hierarchy

**Files:**
- Create: `tests/test_human_readable_market_pages.py`
- Modify: `src/build_unified_app.py:5000-5160`

**Interfaces:**
- Consumes: `build_destination_page(dest: dict, listings: list[dict], destinations: list[dict], pages: list[dict]) -> str`
- Produces: `first_text(items: list[str] | None, fallback: str) -> str` and destination HTML with a plain destination `h1`, plain-language metrics, a six-link reading path, one `market-summary` block, a bottom resource section, and bottom update metadata.

- [ ] **Step 1: Write the failing destination hierarchy test**

```python
from __future__ import annotations

import unittest

from src import build_unified_app


class HumanReadableDestinationPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = build_unified_app.load_json("destinations.json")
        cls.dubai = next(item for item in cls.destinations if item["id"] == "dubai")
        cls.html = build_unified_app.build_destination_page(
            cls.dubai,
            [],
            cls.destinations,
            build_unified_app.SEO_PAGES,
        )

    def test_destination_hero_uses_plain_reader_facing_labels(self) -> None:
        self.assertIn("<h1>Dubai</h1>", self.html)
        self.assertNotIn("<h1>Dubai Property Research</h1>", self.html)
        self.assertIn("City · United Arab Emirates</p>", self.html)
        self.assertNotIn("City · United Arab Emirates · updated", self.html)
        self.assertIn("<span>Overall rating</span>", self.html)
        self.assertIn("<span>Price guide</span>", self.html)
        self.assertNotIn("<span>Decision score</span>", self.html)
        self.assertNotIn("<span>Entry benchmark</span>", self.html)

    def test_destination_has_one_compact_summary_and_six_part_reading_path(self) -> None:
        self.assertEqual(self.html.count('class="market-summary"'), 1)
        self.assertNotIn("Should this destination stay on your shortlist?", self.html)
        for label in ("Overview", "Buyer fit", "Areas", "Costs and risks", "Evidence", "Compare"):
            self.assertIn(f">{label}</a>", self.html)
        self.assertEqual(self.html.count('class="sticky-jump"'), 1)
        sticky_nav = self.html.split('class="sticky-jump"', 1)[1].split("</nav>", 1)[0]
        self.assertEqual(sticky_nav.count("<a "), 6)
```

- [ ] **Step 2: Run the destination test and verify RED**

Run: `python3 -m unittest tests.test_human_readable_market_pages.HumanReadableDestinationPageTests -v`

Expected: FAIL because the visible heading includes “Property Research,” the hero uses “Decision score” and “Entry benchmark,” and the existing decision panel and ten-link jump navigation remain.

- [ ] **Step 3: Implement the destination hero and summary**

Add a small fallback helper near the other content helpers:

```python
def first_text(items: list[str] | None, fallback: str) -> str:
    return next((str(item).strip() for item in (items or []) if str(item).strip()), fallback)
```

In `build_destination_page`, retain the SEO document title but use the destination name for the visible heading. Replace the hero and decision-panel markup with:

```python
      <div class="page-hero-grid">
        <div>
          <p class="page-eyebrow">{escape(dest.get("category") or "Destination")} · {escape(dest.get("country") or "")}</p>
          <h1>{escape(dest["name"])}</h1>
          <p class="page-lede">{escape(dest.get("panel_summary") or "")}</p>
        </div>
        <aside class="page-hero-card" aria-label="Key market facts">
          <span>Global rank</span><strong>#{dest["rank"]}</strong>
          <span>Overall rating</span><strong>{dest.get("decision_score", 0):.1f}/5</strong>
          <span>Price guide</span><strong>{money(dest.get("usd_per_m2"))}/m2</strong>
        </aside>
      </div>
```

Replace the current `decision-panel` with:

```python
      <section class="market-summary" id="overview" aria-label="At a glance">
        <div class="market-summary__verdict">
          <span>At a glance</span>
          <p>{escape(dest.get("panel_verdict") or dest.get("panel_summary") or "")}</p>
        </div>
        <dl class="market-summary__facts">
          <div><dt>Best for</dt><dd>{escape(first_text(dest.get("pros"), dest.get("profit_driver") or "Long-term buyers"))}</dd></div>
          <div><dt>Ownership route</dt><dd>{escape(dest.get("ownership_notes") or "Verify locally")}</dd></div>
          <div><dt>Price guide</dt><dd>{money(dest.get("usd_per_m2"))}/m2</dd></div>
          <div><dt>Expected net yield</dt><dd>{escape(dest.get("net_yield_estimate") or "n/a")}</dd></div>
          <div><dt>Main risk</dt><dd>{escape(first_text(dest.get("cons"), dest.get("red_flags") or "Asset-level diligence required"))}</dd></div>
        </dl>
      </section>
```

Use this page navigation:

```python
sticky_page_nav([
    ("Overview", "overview"),
    ("Buyer fit", "buyer-fit"),
    ("Areas", "where-to-look"),
    ("Costs and risks", "budget"),
    ("Evidence", "evidence"),
    ("Compare", "compare"),
])
```

Replace the old `.decision-panel` CSS with `.market-summary`, `.market-summary__verdict`, and `.market-summary__facts` rules that form a two-column layout on desktop and one column at `max-width: 680px`.

- [ ] **Step 4: Run the destination test and verify GREEN**

Run: `python3 -m unittest tests.test_human_readable_market_pages.HumanReadableDestinationPageTests -v`

Expected: PASS.

- [ ] **Step 5: Commit the destination hierarchy**

```bash
git add tests/test_human_readable_market_pages.py src/build_unified_app.py
git commit -m "feat: simplify destination reading hierarchy"
```

---

### Task 2: Destination resources, actions, and update metadata

**Files:**
- Modify: `tests/test_human_readable_market_pages.py`
- Modify: `src/build_unified_app.py:5100-5160`

**Interfaces:**
- Consumes: destination HTML structure from Task 1 and existing helpers `destination_links`, `country_hub_links`, `seo_guide_links`, and `trust_page_links`.
- Produces: `continue-research` section, `destination-updated` footer line, and one action region.

- [ ] **Step 1: Add failing consolidation tests**

```python
    def test_destination_moves_supporting_links_and_date_to_the_bottom(self) -> None:
        self.assertNotIn('class="page-aside mobile-resources"', self.html)
        self.assertEqual(self.html.count('id="continue-research"'), 1)
        self.assertIn("Continue your research", self.html)
        resources_at = self.html.index('id="continue-research"')
        updated_at = self.html.index('class="destination-updated"')
        self.assertGreater(resources_at, self.html.index('id="compare"'))
        self.assertGreater(updated_at, resources_at)
        self.assertIn("Last updated 2026-08-18", self.html[updated_at:])

    def test_destination_has_one_reader_action_region(self) -> None:
        self.assertEqual(self.html.count('class="destination-actions"'), 1)
        self.assertNotIn('class="mobile-action-strip"', self.html)
```

- [ ] **Step 2: Run the consolidation tests and verify RED**

Run: `python3 -m unittest tests.test_human_readable_market_pages.HumanReadableDestinationPageTests -v`

Expected: FAIL because resources are still in `page-aside mobile-resources`, no consolidated resource/footer region exists, and the update date remains in the hero.

- [ ] **Step 3: Implement one action area and bottom resources**

Remove `details.page-aside.mobile-resources` from the destination layout. Place this after the Compare section and before the footer:

```python
      <section class="destination-actions" aria-label="Next step">
        <div>
          <h2>Compare before you decide</h2>
          <p>Use the market directory to test {escape(dest["name"])} against the alternatives that matter to you.</p>
        </div>
        <a class="page-button" href="/dashboard/">Compare markets</a>
      </section>

      <section class="continue-research" id="continue-research">
        <h2>Continue your research</h2>
        <div class="continue-research__grid">
          <div><h3>Related markets</h3><nav>{peer_links}</nav></div>
          <div><h3>Country guides</h3><nav>{country_hub_link or country_hub_links(limit=4)}</nav></div>
          <div><h3>Buying guides</h3><nav><a href="/guides/">All buying guides</a>{seo_guide_links(pages, limit=5)}</nav></div>
          <div><h3>About the research</h3><nav>{trust_page_links()}</nav></div>
        </div>
      </section>
      <p class="destination-updated">Last updated {date.today().isoformat()}</p>
```

Remove the duplicated sidebar action card, the destination `mobile_action_strip(...)` call, and any second shortlist-review call to action from the destination template. Add simple grid CSS for `continue-research__grid`; links are plain text and the section contains no nested card chrome.

- [ ] **Step 4: Run the destination tests and verify GREEN**

Run: `python3 -m unittest tests.test_human_readable_market_pages.HumanReadableDestinationPageTests -v`

Expected: PASS.

- [ ] **Step 5: Commit destination consolidation**

```bash
git add tests/test_human_readable_market_pages.py src/build_unified_app.py
git commit -m "feat: consolidate destination resources"
```

---

### Task 3: Directory-first market rows and primary filters

**Files:**
- Modify: `tests/test_compact_dashboard.py`
- Modify: `src/build_unified_app.py:680-735`
- Modify: `src/build_unified_app.py:5750-6720`

**Interfaces:**
- Consumes: `build_destination_card(dest: dict, listings: list[dict], top_retirement_ids: set[str]) -> str` and `build() -> Path`.
- Produces: a default market row with no permanent row actions, one “Markets” heading, and four primary filters including `#buyerGoal`.

- [ ] **Step 1: Replace row-action expectations with failing directory-first tests**

Update `test_market_result_is_a_compact_row_not_a_full_dossier` and add a dashboard hierarchy test:

```python
    def test_market_result_is_a_reader_first_row(self) -> None:
        available = build_unified_app.consolidate_destination({
            "id": "test-market",
            "name": "Test Market",
            "country": "Test Country",
            "category": "City",
            "rank": 1,
            "usd_per_m2": 5000,
            "net_yield_estimate": "3-4% est. net",
            "scores": {
                "ownership_clarity": {"score": 4.2},
                "retirement_suitability": {"score": 3.8},
            },
        })
        html = build_unified_app.build_destination_card(available, [], {"test-market"})
        self.assertIn('<h3><a href="/destinations/test-market/">Test Market</a></h3>', html)
        self.assertIn("Overall rating", html)
        self.assertIn("Price guide", html)
        self.assertNotIn("Shortlist", html)
        self.assertNotIn(">Compare<", html)
        self.assertNotIn(">Available<", html)

    def test_dashboard_has_one_market_heading_and_four_primary_filters(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")
        self.assertEqual(html.count("<h1>Markets</h1>"), 1)
        self.assertNotIn("<h2>Markets</h2>", html)
        for control_id in ("search", "category", "sort", "buyerGoal"):
            self.assertIn(f'id="{control_id}"', html)
        self.assertIn("Location type", html)
        self.assertIn("Buying goal", html)
```

- [ ] **Step 2: Run dashboard tests and verify RED**

Run: `python3 -m unittest tests.test_compact_dashboard -v`

Expected: FAIL because the page still uses “All markets,” Buyer Lens buttons, repeated row Compare/Shortlist actions, and an inner “Markets” heading.

- [ ] **Step 3: Simplify row markup and the default dashboard header**

Change `build_destination_card` to emit the market identity plus five facts. For normal markets omit access text; for restricted markets add:

```python
access_warning = ""
if not is_destination_recommendable(dest):
    access_warning = (
        '<p class="market-row__warning"><strong>Restricted buyer access.</strong> '
        f'{escape(dest.get("access_summary") or "Verify the current purchase route.")}</p>'
    )
```

Use `<span>` labels in each metric so mobile cards remain understandable:

```python
<div class="market-row__metric"><span>Overall rating</span><strong data-custom-score>{dest.get("decision_score", 0):.1f}</strong></div>
<div class="market-row__metric"><span>Price guide</span><strong>{money(dest.get("usd_per_m2"))}/m2</strong></div>
<div class="market-row__metric"><span>Expected net yield</span><strong>{escape(dest.get("net_yield_estimate") or "n/a")}</strong></div>
<div class="market-row__metric"><span>Ownership clarity</span><strong>{ownership_score:.1f}/5</strong></div>
{access_warning}
```

Change the dashboard hero to `<h1>Markets</h1>` and remove the inner heading from `.market-list__header`. Replace Buyer Lens buttons with:

```html
<div class="field">
  <label for="buyerGoal">Buying goal</label>
  <select id="buyerGoal">
    <option value="all">All goals</option>
    <option value="shortlist">Top rated</option>
    <option value="ownership">Clear ownership</option>
    <option value="retirement">Retirement</option>
  </select>
</div>
```

Update the filtering script to read `buyerGoal.value` where it currently reads pressed `data-quick` buttons. Rename the visible “Terrain” label to “Location type” while retaining the existing `#category` value and filter behavior.

- [ ] **Step 4: Run dashboard tests and verify GREEN**

Run: `python3 -m unittest tests.test_compact_dashboard -v`

Expected: PASS.

- [ ] **Step 5: Commit the directory-first default view**

```bash
git add tests/test_compact_dashboard.py src/build_unified_app.py
git commit -m "feat: simplify the markets directory"
```

---

### Task 4: Progressive compare mode and advanced tools

**Files:**
- Modify: `tests/test_compact_dashboard.py`
- Modify: `src/build_unified_app.py:5750-7140`

**Interfaces:**
- Consumes: simplified rows from Task 3 and existing `.compare-toggle`, memo shortlist, export, and recalculation functions.
- Produces: `#compareModeToggle`, `#compareSelectionBar`, `body.compare-mode`, and an advanced-tools section positioned after `#markets`.

- [ ] **Step 1: Add failing progressive-disclosure tests**

```python
    def test_compare_and_advanced_tools_are_progressively_disclosed(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")
        self.assertEqual(html.count('id="compareModeToggle"'), 1)
        self.assertEqual(html.count('id="compareSelectionBar"'), 1)
        self.assertIn('aria-pressed="false"', html)
        self.assertEqual(html.count('class="compare-toggle"'), 37)
        self.assertIn("Advanced research tools", html)
        self.assertGreater(html.index("Advanced research tools"), html.index('id="markets"'))
        self.assertNotIn("No saved destinations yet.", html)
        self.assertNotIn("Save markets to preview them here.", html)
```

- [ ] **Step 2: Run the progressive-disclosure test and verify RED**

Run: `python3 -m unittest tests.test_compact_dashboard.CompactDashboardTests.test_compare_and_advanced_tools_are_progressively_disclosed -v`

Expected: FAIL because compare controls are permanent row actions, there is no compare-mode toggle or selection bar, and advanced tools appear before the directory with empty-state cards.

- [ ] **Step 3: Implement compare mode and move advanced tools**

Add a single control beside the result count:

```html
<button type="button" id="compareModeToggle" aria-pressed="false">Compare markets</button>
```

Place a hidden selection bar after the filter row:

```html
<div class="compare-selection-bar hidden" id="compareSelectionBar" aria-live="polite">
  <strong id="compareSelectionCount">0 markets selected</strong>
  <div>
    <button type="button" id="openCompare">Compare</button>
    <button type="button" id="saveSelection">Save</button>
    <button type="button" id="clearCompare">Clear</button>
    <button type="button" id="exportMemo">Export</button>
  </div>
</div>
```

Keep `.compare-toggle` checkboxes in each row inside a `.market-row__select` element that is hidden by default and visible under `body.compare-mode`. Toggle mode with:

```javascript
const compareModeToggle = document.getElementById("compareModeToggle");
compareModeToggle.addEventListener("click", () => {
  const active = !document.body.classList.contains("compare-mode");
  document.body.classList.toggle("compare-mode", active);
  compareModeToggle.setAttribute("aria-pressed", String(active));
  compareModeToggle.textContent = active ? "Done comparing" : "Compare markets";
  if (!active && !selectedCompareDestinations().length) {
    document.getElementById("compareSelectionBar").classList.add("hidden");
  }
});
```

Update `renderCompare()` to set `#compareSelectionCount` and reveal `#compareSelectionBar` when at least one checkbox is selected. Point `#openCompare` to the existing comparison panel, keep `#clearCompare` and `#exportMemo` on their current handlers, and save the current IDs for the existing shortlist-review bridge:

```javascript
document.getElementById("openCompare").addEventListener("click", () => {
  if (selectedCompareDestinations().length < 2) return;
  comparePanel.scrollIntoView({ behavior: "smooth", block: "start" });
});

document.getElementById("saveSelection").addEventListener("click", () => {
  localStorage.setItem("gha_memo_shortlist", JSON.stringify([...compareSelected]));
  document.getElementById("compareSelectionCount").textContent =
    compareSelected.size + (compareSelected.size === 1 ? " market saved" : " markets saved");
  if (window.GHA) window.GHA.track("shortlist_save", { selected_count: compareSelected.size });
});
```

Move `<details class="advanced-controls">` below `#markets`, rename its summary to “Advanced research tools,” and render saved-state sections only when their associated arrays contain data. Keep score weighting and JSON/CSV export inside the collapsed section.

- [ ] **Step 4: Run dashboard tests and verify GREEN**

Run: `python3 -m unittest tests.test_compact_dashboard -v`

Expected: PASS.

- [ ] **Step 5: Commit progressive disclosure**

```bash
git add tests/test_compact_dashboard.py src/build_unified_app.py
git commit -m "feat: add progressive market comparison"
```

---

### Task 5: Responsive reading pass and full verification

**Files:**
- Modify: `src/build_unified_app.py`
- Regenerate: `artifacts/**/*.html`

**Interfaces:**
- Consumes: destination and directory markup from Tasks 1-4.
- Produces: regenerated static pages that pass automated and browser verification.

- [ ] **Step 1: Add mobile CSS for the new structures**

At `max-width: 680px`, use:

```css
.market-summary { grid-template-columns: 1fr; }
.market-summary__facts { grid-template-columns: 1fr; }
.continue-research__grid { grid-template-columns: 1fr; }
.market-row { grid-template-columns: 1fr 1fr; gap: 12px; }
.market-row__market, .market-row__warning, .market-row__select { grid-column: 1 / -1; }
.market-row__metric span { display: block; }
.market-list__labels { display: none; }
```

Ensure desktop `.market-row` uses five readable columns plus the optional compare selector, and remove obsolete styles for the old sidebar, decision panel, Buyer Lens buttons, and permanent action column when no other page consumes them.

- [ ] **Step 2: Regenerate the static site**

Run: `python3 src/build_unified_app.py && python3 scripts/seo_status_dashboard.py`

Expected: both commands exit 0 and rewrite the static artifacts.

- [ ] **Step 3: Run the complete automated suite**

Run: `python3 -m unittest discover -s tests`

Expected: all tests PASS.

- [ ] **Step 4: Run static verification after tests finish**

Run: `python3 scripts/verify_static_site.py`

Expected: `Static site verification passed`. Run this sequentially after the unit suite because dashboard tests regenerate the public asset directory.

- [ ] **Step 5: Verify representative pages in the local browser**

Check these URLs at a normal desktop viewport and at `390x844`:

```text
http://127.0.0.1:8765/destinations/dubai/
http://127.0.0.1:8765/destinations/lake-como/
http://127.0.0.1:8765/dashboard/
```

Confirm:

- Destination `h1` contains only the market name.
- Overall rating and Price guide appear in the hero.
- Updated date appears only at the bottom.
- Supporting links appear only in “Continue your research.”
- Markets has one heading and one primary filter row.
- Normal rows contain no Available, Compare, or Shortlist repetition.
- Compare mode reveals checkboxes and a selection bar.
- Mobile pages have no horizontal overflow.
- Browser console contains no errors.

- [ ] **Step 6: Commit regenerated pages and verification changes**

```bash
git add src/build_unified_app.py tests/test_human_readable_market_pages.py tests/test_compact_dashboard.py artifacts
git commit -m "feat: deliver human-readable market pages"
```
