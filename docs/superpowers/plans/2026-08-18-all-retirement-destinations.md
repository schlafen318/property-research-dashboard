# All-Destination Retirement Ranking Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rank all 30 Global Home Atlas destinations with complete source-audited retirement cost models while showing only the first 10 rows before an accessible expansion control.

**Architecture:** Keep `data/retirement_costs.json` as the authoritative financial-model dataset and require its IDs to match `data/destinations.json` exactly. Reuse the existing capital calculation, add one shared ranking-split helper, and render the guide and calculator as server-side top-10 tables followed by native `<details>` disclosures containing ranks 11–30. Generate top-10 graphics from the same complete 30-record ranking.

**Tech Stack:** Python 3.11 static-site generator and `unittest`, JSON data, Pillow PNG generation, semantic HTML/CSS, existing vanilla-JavaScript retirement calculator.

**Spec:** `docs/superpowers/specs/2026-08-18-all-retirement-destinations-design.md`

## Global Constraints

- The authoritative destination set is every ID in `data/destinations.json`; no destination may be silently omitted.
- Every destination requires single and couple profiles, all eight existing cost categories, rent, owner costs, property inputs, inflation inputs, confidence metadata, and at least three dated HTTPS sources.
- Ranks use a couple renting today, a 30-year horizon, a 3.5% withdrawal rate, a 12-month reserve, and no outside income.
- Required capital equals annual spending divided by 3.5%, plus the reserve; property capital is separate and does not affect rank.
- Ranks 1–10 render initially; ranks 11–30 render in the original HTML inside native `<details>` elements.
- The calculator remains private and client-side; no financial input persistence or transmission may be introduced.
- The canonical guide URL and existing infographic filenames remain unchanged.
- Figures remain current-USD planning estimates and must not imply personal financial advice or predictive accuracy.

---

## File Map

- `data/retirement_costs.json`: authoritative 30-destination cost profiles, sources, confidence, and review date.
- `tests/test_retirement_cost_data.py`: exact destination-set and per-record research-contract validation.
- `src/build_unified_app.py`: shared ranking split, guide/calculator markup, copy, and structured data.
- `tests/test_retirement_destinations_article.py`: complete guide ranking, disclosure, SEO, and image contracts.
- `tests/test_retirement_calculator_page.py`: 30-option calculator and expandable benchmark contracts.
- `scripts/generate_retirement_infographics.py`: top-10-of-30 rendering from the complete ranking.
- `src/site_assets/retirement-destinations-required-capital.png`: regenerated top-10 ranking graphic.
- `src/site_assets/retirement-destinations-capital-breakdown.png`: regenerated top-10 capital-components graphic.
- `artifacts/`: generated deployable site output; never edit by hand.

### Task 1: Complete and Validate the 30-Destination Research Dataset

**Files:**
- Modify: `data/retirement_costs.json`
- Modify: `tests/test_retirement_cost_data.py`

**Interfaces:**
- Consumes: destination IDs and names from `data/destinations.json`; the existing retirement-cost record schema.
- Produces: `load_retirement_costs() -> dict` with exactly 30 complete records whose `destination_id` values match all destination dossiers.

- [ ] **Step 1: Replace the hard-coded eight-ID test with an authoritative all-destination contract**

Add `DESTINATIONS_PATH` and load the expected set independently from the production loader:

```python
DESTINATIONS_PATH = ROOT / "data" / "destinations.json"

@classmethod
def setUpClass(cls) -> None:
    cls.payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    cls.records = {item["destination_id"]: item for item in cls.payload["destinations"]}
    cls.expected_ids = {
        item["id"]
        for item in json.loads(DESTINATIONS_PATH.read_text(encoding="utf-8"))
    }

def test_release_destination_set_is_complete(self) -> None:
    self.assertEqual(30, len(self.expected_ids))
    self.assertEqual(self.expected_ids, set(self.records))
```

- [ ] **Step 2: Run the coverage test and confirm the expected failure**

Run: `python3 -m unittest tests.test_retirement_cost_data.RetirementCostDataTests.test_release_destination_set_is_complete`

Expected: FAIL because `retirement_costs.json` contains 8 records while `destinations.json` contains 30 IDs.

- [ ] **Step 3: Research the 22 missing destination models**

Research these exact IDs:

```text
costa-brava-girona
hakuba
annecy
mallorca
croatia-istria-dalmatia
niseko
queenstown
phuket-koh-samui
vancouver-island-victoria
dolomites-south-tyrol
bali
chamonix
park-city-deer-valley
da-nang-hoi-an
whistler
andermatt
innsbruck-tyrol
lake-tahoe
jackson-hole
ticino-lake-lugano
aspen-snowmass
swiss-valais-vaud-alps
```

For each destination, capture destination/city cost and rent observations, a national statistical-agency inflation reference, and government or established property-market evidence. Use the existing eight-category model for both household profiles. When destination evidence is thin, use a disclosed regional or national proxy and include the affected fields in `confidence.proxy_categories`.

Follow the complete field structure of the existing Fukuoka / Itoshima record, but derive every cost, rent, owner-cost, property, acquisition-cost, confidence, and source value independently for the destination being added. Do not copy Fukuoka values into another market. Existing tests prohibit zero rent, owner-cost, and property inputs and require at least three complete sources.

- [ ] **Step 4: Revalidate the original eight records against the same review date**

Review Fukuoka / Itoshima, Valencia, Algarve / Cascais, Madeira, Crete, Hakone / Izu, Lake Como, and Málaga / Costa del Sol using the same source hierarchy. Update `as_of` once all 30 records share a completed research pass. Preserve disclosed proxy limitations instead of increasing confidence without evidence.

- [ ] **Step 5: Strengthen source and price-basis validation**

Add assertions that prevent incomplete research records:

```python
def test_every_record_has_dated_metric_sources(self) -> None:
    for record in self.records.values():
        self.assertGreaterEqual(len(record["sources"]), 3)
        self.assertTrue(record["property"]["price_basis"].strip())
        for source in record["sources"]:
            self.assertTrue(source["name"].strip())
            self.assertTrue(source["url"].startswith("https://"))
            self.assertTrue(source["metric_supported"].strip())
            self.assertTrue(source["source_date"].strip())
            self.assertRegex(source["accessed_on"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(source["notes"].strip())
```

- [ ] **Step 6: Run the complete data tests**

Run: `python3 -m unittest tests.test_retirement_cost_data`

Expected: all tests PASS with 30 complete source-audited records.

- [ ] **Step 7: Commit the dataset**

```bash
git add data/retirement_costs.json tests/test_retirement_cost_data.py
git commit -m "Expand retirement cost data to all destinations"
```

### Task 2: Add a Shared Top-10 Ranking Split

**Files:**
- Modify: `src/build_unified_app.py`
- Create: `tests/test_retirement_ranking_helpers.py`

**Interfaces:**
- Consumes: `rankings: list[dict]` already sorted by `retirement_destination_rankings()`.
- Produces: `split_rankings(rankings: list[dict], visible_count: int = 10) -> tuple[list[dict], list[dict]]`.

- [ ] **Step 1: Write failing helper tests**

```python
import unittest

from src.build_unified_app import split_rankings


class RetirementRankingHelperTests(unittest.TestCase):
    def test_split_rankings_keeps_first_ten_visible(self) -> None:
        rankings = [{"rank": value} for value in range(1, 31)]
        visible, expandable = split_rankings(rankings)
        self.assertEqual(list(range(1, 11)), [item["rank"] for item in visible])
        self.assertEqual(list(range(11, 31)), [item["rank"] for item in expandable])

    def test_split_rankings_rejects_non_positive_visible_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "visible_count must be positive"):
            split_rankings([{"rank": 1}], visible_count=0)
```

- [ ] **Step 2: Run the helper tests and confirm the expected failure**

Run: `python3 -m unittest tests.test_retirement_ranking_helpers`

Expected: ERROR because `split_rankings` does not exist.

- [ ] **Step 3: Implement the helper beside `retirement_destination_rankings`**

```python
def split_rankings(
    rankings: list[dict], visible_count: int = 10
) -> tuple[list[dict], list[dict]]:
    if visible_count < 1:
        raise ValueError("visible_count must be positive")
    return rankings[:visible_count], rankings[visible_count:]
```

- [ ] **Step 4: Run the helper tests**

Run: `python3 -m unittest tests.test_retirement_ranking_helpers`

Expected: both tests PASS.

- [ ] **Step 5: Commit the helper**

```bash
git add src/build_unified_app.py tests/test_retirement_ranking_helpers.py
git commit -m "Add retirement ranking disclosure split"
```

### Task 3: Render the Complete Guide Ranking and ItemList Schema

**Files:**
- Modify: `src/build_unified_app.py:60-78`
- Modify: `src/build_unified_app.py:3615-3700`
- Modify: `src/build_unified_app.py:3877-4015`
- Modify: `tests/test_retirement_destinations_article.py`

**Interfaces:**
- Consumes: `retirement_destination_rankings()` and `split_rankings()` from Tasks 1–2.
- Produces: a 30-row guide, visible top 10, expandable ranks 11–30, top-10 destination notes, and a 30-entry schema.org `ItemList`.

- [ ] **Step 1: Write failing 30-destination metadata and schema tests**

Update the article metadata assertions and add an ItemList assertion:

```python
def test_article_has_indexable_metadata_and_structured_data(self) -> None:
    self.assertIn(
        '<meta name="description" content="Compare all 30 Global Home Atlas retirement destinations by required capital, annual spending, reserves, and optional property costs using one methodology.">',
        self.html,
    )
    self.assertIn(
        "<h1>30 Retirement Destinations Ranked by How Much You Need</h1>",
        self.html,
    )
    self.assertIn('"@type":"Article"', self.compact_html)
    self.assertIn('"@type":"FAQPage"', self.compact_html)
    self.assertIn('"@type":"ItemList"', self.compact_html)
    self.assertIn('"numberOfItems":30', self.compact_html)
```

- [ ] **Step 2: Write a failing disclosure-boundary test**

```python
def test_ranking_shows_top_ten_then_expands_ranks_eleven_to_thirty(self) -> None:
    ranking = self.html.split('id="ranking"', 1)[1].split("</section>", 1)[0]
    visible = ranking.split('<details class="ranking-more">', 1)[0]
    expandable = ranking.split('<details class="ranking-more">', 1)[1]
    self.assertEqual(10, visible.count('class="ranking-row"'))
    self.assertEqual(20, expandable.count('class="ranking-row"'))
    self.assertIn("View ranks 11–30", expandable)
    self.assertIn("</details>", expandable)
```

- [ ] **Step 3: Write a failing complete-ID and top-10-notes test**

```python
def test_every_destination_is_ranked_once_and_only_top_ten_have_notes(self) -> None:
    destinations = json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
    ranking = self.html.split('id="ranking"', 1)[1].split("</section>", 1)[0]
    for destination in destinations:
        href = f'href="/destinations/{destination["id"]}/"'
        self.assertEqual(1, ranking.count(href), destination["id"])
    notes = self.html.split('class="destination-notes"', 1)[1].split("</ol>", 1)[0]
    self.assertEqual(10, notes.count("<li>"))
```

- [ ] **Step 4: Run the guide tests and confirm they fail for eight-destination output**

Run: `python3 -m unittest tests.test_retirement_destinations_article`

Expected: failures for the old H1/description, absent ItemList, and absent ranking disclosure.

- [ ] **Step 5: Update guide constants and FAQ copy**

Set:

```python
RETIREMENT_DESTINATIONS_H1 = "30 Retirement Destinations Ranked by How Much You Need"
RETIREMENT_DESTINATIONS_DESCRIPTION = (
    "Compare all 30 Global Home Atlas retirement destinations by required capital, "
    "annual spending, reserves, and optional property costs using one methodology."
)
```

Change the first FAQ answer from “eight selected destinations” to “all 30 destinations currently covered by Global Home Atlas.” Update guide-hub and homepage tracking labels through the same H1 constant.

- [ ] **Step 6: Pass rankings into the article schema and append ItemList**

Change the signature to:

```python
def schema_for_retirement_destinations_article(
    canonical: str, rankings: list[dict]
) -> list[dict]:
```

Append:

```python
{
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "Retirement destinations ranked by required capital",
    "numberOfItems": len(rankings),
    "itemListOrder": "https://schema.org/ItemListOrderAscending",
    "itemListElement": [
        {
            "@type": "ListItem",
            "position": position,
            "name": item["destination"]["name"],
            "url": page_url(f'destinations/{destination_slug(item["destination"])}'),
        }
        for position, item in enumerate(rankings, start=1)
    ],
},
```

Call it as `schema_for_retirement_destinations_article(canonical, rankings)`.

- [ ] **Step 7: Render two non-overlapping guide tables**

Assign stable row classes and split before rendering:

```python
visible_rankings, expandable_rankings = split_rankings(rankings)
visible_rows = "".join(table_rows[: len(visible_rankings)])
expandable_rows = "".join(table_rows[len(visible_rankings) :])
top_destination_notes = "".join(destination_notes[: len(visible_rankings)])
```

Render the first table normally and the remaining rows in:

```html
<details class="ranking-more">
  <summary>View ranks 11–30</summary>
  <div class="table-wrap">
    <table>
      <caption>Retirement destinations ranked 11–30</caption>
      <thead><tr><th>Rank</th><th>Destination / Country</th><th>Annual spending</th><th>Required retirement capital</th><th>Property capital</th></tr></thead>
      <tbody>__EXPANDABLE_ROWS__</tbody>
    </table>
  </div>
</details>
```

Add `class="ranking-row"` to every generated `<tr>`. Use only `top_destination_notes` in the notes list. Add minimal disclosure CSS: block spacing, a clear summary focus target, and no pills or decorative badges.

- [ ] **Step 8: Run guide tests**

Run: `python3 -m unittest tests.test_retirement_destinations_article`

Expected: all guide tests PASS with 10 visible rows, 20 expandable rows, 10 notes, and 30 ItemList entries.

- [ ] **Step 9: Commit the guide and schema**

```bash
git add src/build_unified_app.py tests/test_retirement_destinations_article.py
git commit -m "Rank all retirement destinations in guide"
```

### Task 4: Expand the Calculator Selector and Benchmark Table

**Files:**
- Modify: `src/build_unified_app.py:3747-3878`
- Modify: `tests/test_retirement_calculator_page.py`

**Interfaces:**
- Consumes: all 30 retirement records and `split_rankings()`.
- Produces: 30 `<option>` elements, 10 visible benchmark rows, 20 expandable benchmark rows, and unchanged private browser calculation data.

- [ ] **Step 1: Write failing selector and benchmark-count tests**

```python
def test_calculator_contains_all_thirty_destination_options(self) -> None:
    select = self.html.split('id="ret-destination"', 1)[1].split("</select>", 1)[0]
    self.assertEqual(30, select.count("<option"))

def test_benchmarks_show_ten_rows_then_expand_twenty(self) -> None:
    section = self.html.split('<section id="benchmarks"', 1)[1].split("</section>", 1)[0]
    visible = section.split('<details class="benchmark-more">', 1)[0]
    expandable = section.split('<details class="benchmark-more">', 1)[1]
    self.assertEqual(10, visible.count('class="benchmark-row"'))
    self.assertEqual(20, expandable.count('class="benchmark-row"'))
    self.assertIn("View ranks 11–30", expandable)
```

- [ ] **Step 2: Run the calculator tests and confirm the expected failures**

Run: `python3 -m unittest tests.test_retirement_calculator_page`

Expected: failures because the calculator contains eight options and one undisclosed benchmark table.

- [ ] **Step 3: Split benchmark rows after ranking**

Add `class="benchmark-row"` to each benchmark `<tr>`, then split the rendered rows:

```python
visible_records, expandable_records = split_rankings(ranked_records)
visible_benchmark_rows = "".join(benchmark_rows[: len(visible_records)])
expandable_benchmark_rows = "".join(benchmark_rows[len(visible_records) :])
```

- [ ] **Step 4: Render the calculator benchmark disclosure**

Replace `__ROWS__` with `__VISIBLE_ROWS__` and add:

```html
<details class="benchmark-more">
  <summary>View ranks 11–30</summary>
  <div class="table-wrap">
    <table>
      <caption>Required retirement capital for ranks 11–30</caption>
      <thead><tr><th>Rank</th><th>Destination</th><th>Annual spending</th><th>Liquid portfolio</th><th>Emergency reserve</th><th>Required retirement capital</th><th>Property capital</th></tr></thead>
      <tbody>__EXPANDABLE_ROWS__</tbody>
    </table>
  </div>
</details>
```

Populate both replacement tokens. Add the same simple disclosure spacing and focus treatment used by the guide.

- [ ] **Step 5: Run calculator tests and privacy tests**

Run: `python3 -m unittest tests.test_retirement_calculator_page tests.test_retirement_calculator_engine`

Expected: all tests PASS; the selector has 30 options and calculator code still contains no persistence or transmission APIs.

- [ ] **Step 6: Commit the calculator changes**

```bash
git add src/build_unified_app.py tests/test_retirement_calculator_page.py
git commit -m "Expand retirement calculator destination coverage"
```

### Task 5: Regenerate Accurate Top-10-of-30 Infographics

**Files:**
- Modify: `scripts/generate_retirement_infographics.py`
- Modify: `tests/test_retirement_destinations_article.py`
- Modify: `src/site_assets/retirement-destinations-required-capital.png`
- Modify: `src/site_assets/retirement-destinations-capital-breakdown.png`

**Interfaces:**
- Consumes: the complete sorted 30-item ranking.
- Produces: the same two 1600×900 PNG paths, each visualizing the first 10 items and labeling them as the lowest-cost 10 of 30.

- [ ] **Step 1: Write failing image-copy tests**

Replace the eight-destination alt assertions with:

```python
self.assertIn(
    'alt="Lowest-cost 10 of 30 retirement destinations ranked by required capital for a couple renting"',
    self.html,
)
self.assertIn(
    'alt="Capital breakdown for the lowest-cost 10 of 30 retirement destinations"',
    self.html,
)
self.assertIn("lowest-cost 10 of 30", self.html.lower())
```

- [ ] **Step 2: Run the image tests and confirm the old copy fails**

Run: `python3 -m unittest tests.test_retirement_destinations_article.RetirementDestinationsArticleTests.test_two_accessible_infographics_have_downloadable_pngs`

Expected: FAIL because the HTML still describes eight destinations.

- [ ] **Step 3: Limit chart rendering to the first 10 ranked items**

In `main()` or immediately after `load_rankings()`:

```python
rankings, as_of = load_rankings()
top_rankings = rankings[:10]
draw_required_capital(top_rankings, as_of, required_output)
draw_capital_breakdown(top_rankings, as_of, breakdown_output)
```

Update the graphic eyebrow/subtitle strings to “Lowest-cost 10 of 30 retirement destinations” and “Top 10 shown; complete ranks 1–30 are available in the guide.” Adjust `row_step` only if the tenth row overlaps the footer; keep both canvases exactly 1600×900.

- [ ] **Step 4: Update guide image alt text and captions**

Use the exact alt text from Step 1. State in each caption that the chart shows the lowest-cost 10 of 30 and that the complete ranking is in the tables above.

- [ ] **Step 5: Generate the images**

Run: `python3 scripts/generate_retirement_infographics.py`

Expected: both PNGs are regenerated in `src/site_assets/` at 1600×900 and exceed 20 KB.

- [ ] **Step 6: Run the image and guide tests**

Run: `python3 -m unittest tests.test_retirement_destinations_article`

Expected: all tests PASS.

- [ ] **Step 7: Commit the graphics**

```bash
git add scripts/generate_retirement_infographics.py tests/test_retirement_destinations_article.py src/site_assets/retirement-destinations-required-capital.png src/site_assets/retirement-destinations-capital-breakdown.png
git commit -m "Update retirement graphics for full ranking"
```

### Task 6: Rebuild Artifacts and Run Complete Verification

**Files:**
- Modify: generated files under `artifacts/`
- Modify: `docs/CHANGELOG.md`

**Interfaces:**
- Consumes: all completed data, generator, schema, calculator, and image changes.
- Produces: deployable static output with 30 indexed destinations and a documented release entry.

- [ ] **Step 1: Add a changelog entry**

Add a dated entry describing the 30-destination source-audited expansion, top-10 progressive disclosure, calculator coverage, ItemList schema, and updated graphics. Do not describe the ranking as lifestyle quality or personal advice.

- [ ] **Step 2: Rebuild the site**

Run: `python3 src/build_unified_app.py`

Expected: exit 0 and regenerated guide, calculator, guide hub, homepage, assets, and sitemap artifacts.

- [ ] **Step 3: Run the focused retirement suite**

Run: `python3 -m unittest tests.test_retirement_cost_data tests.test_retirement_ranking_helpers tests.test_retirement_calculator_engine tests.test_retirement_calculator_page tests.test_retirement_destinations_article`

Expected: all focused tests PASS.

- [ ] **Step 4: Run the full suite**

Run: `python3 -m unittest discover -s tests`

Expected: all tests PASS with zero failures.

- [ ] **Step 5: Run static-site verification**

Run: `python3 scripts/verify_static_site.py`

Expected: `Static site verification passed`.

- [ ] **Step 6: Run desktop and mobile visual verification**

Serve `artifacts/` locally and inspect both `/retirement-destinations-ranked-by-cost/` and `/retirement-abroad-calculator/` at the default desktop viewport and 390×844. Confirm:

```text
10 rows visible before interaction
20 additional rows after expanding
all table overflow remains inside table wrappers
all destination links resolve
both images load when reached
no page-level horizontal overflow
calculator selector contains 30 options
```

- [ ] **Step 7: Commit generated output and release note**

```bash
git add artifacts docs/CHANGELOG.md
git commit -m "Build all-destination retirement ranking"
```

### Task 7: Publish and Verify Production

**Files:**
- No source changes expected.

**Interfaces:**
- Consumes: a clean, verified feature branch.
- Produces: a merged pull request and successful GitHub Pages deployment.

- [ ] **Step 1: Confirm final scope**

Run: `git status -sb` and `git diff origin/main...HEAD --stat`.

Expected: only the retirement dataset, generator, tests, graphics, documentation, and their generated artifacts are present.

- [ ] **Step 2: Push and open a ready pull request**

Push `codex/all-retirement-destinations`, open a PR against `main`, and summarize data coverage, disclosure behavior, SEO impact, and verification evidence.

- [ ] **Step 3: Merge after required checks pass**

Use the repository's accepted merge method. The resulting push to `main` must trigger `.github/workflows/deploy-pages.yml`.

- [ ] **Step 4: Wait for deployment and sitemap submission**

Confirm the `build`, `deploy`, and `notify-google` jobs all complete successfully for the merge commit.

- [ ] **Step 5: Verify production behavior**

On the canonical live guide and calculator, verify the same counts used in local tests: 30 ranked guide rows, 10 visible notes, 30 calculator options, 20 disclosed rows, ItemList `numberOfItems: 30`, Article and FAQ schema, canonical URLs, and updated top-10-of-30 image copy.
