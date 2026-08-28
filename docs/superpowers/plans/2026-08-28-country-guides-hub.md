# Country Guides Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate a scalable `/countries/` directory that clearly connects each country’s acquisition guide, published retirement guide, and destination dossiers.

**Architecture:** Add one server-rendered hub builder to `src/build_unified_app.py`, sourcing all entries from `COUNTRY_HUBS`, `COUNTRY_RETIREMENT_GUIDES`, and the existing destination dataset. Wire the page into navigation, artifact generation, structured data, and the sitemap, with a progressive-enhancement text filter that never hides content from the initial HTML.

**Tech Stack:** Python 3 static-site generator, `unittest`, semantic HTML, inline CSS and vanilla JavaScript, JSON-LD.

**Spec:** `docs/superpowers/specs/2026-08-28-country-guides-hub-design.md`

## Global Constraints

- Use existing country and destination records; do not create a second catalogue.
- Render every country once and omit unavailable retirement-guide links without placeholders.
- Avoid decorative badges, repeated metadata, generic conversion prose, and stale counts.
- Keep all country and destination links server-rendered and usable without JavaScript.
- Preserve the current premium editorial visual language.

---

### Task 1: Define the country directory rendering contract

**Files:**
- Create: `tests/test_country_guides_hub.py`
- Modify: `src/build_unified_app.py`

**Interfaces:**
- Consumes: `COUNTRY_HUBS`, `COUNTRY_RETIREMENT_GUIDES`, `destination_slug(dest)`.
- Produces: `build_country_guides_hub_page(destinations: list[dict]) -> str` and `schema_for_country_guides_hub(canonical: str) -> list[dict]`.

- [ ] **Step 1: Write the failing rendering tests**

```python
from __future__ import annotations

import json
import re
import unittest

from src import build_unified_app


class CountryGuidesHubTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = [
            build_unified_app.consolidate_destination(item)
            for item in build_unified_app.load_json("destinations.json")
        ]
        cls.html = build_unified_app.build_country_guides_hub_page(cls.destinations)

    def test_renders_each_country_once_with_acquisition_and_destination_links(self) -> None:
        for hub in build_unified_app.COUNTRY_HUBS:
            self.assertEqual(1, self.html.count(f'data-country="{hub["slug"]}"'))
            self.assertIn(f'href="/countries/{hub["slug"]}/"', self.html)
            for destination_id in hub["destination_ids"]:
                destination = next(item for item in self.destinations if item["id"] == destination_id)
                self.assertIn(
                    f'href="/destinations/{build_unified_app.destination_slug(destination)}/"',
                    self.html,
                )

    def test_retirement_links_appear_only_for_published_guides(self) -> None:
        published = {
            slug for slug in build_unified_app.COUNTRY_RETIREMENT_GUIDES
        } | {
            "japan-retirement-property-foreign-buyers",
            "spain-retirement-property-foreign-buyers",
            "portugal-retirement-property-foreign-buyers",
        }
        for slug in published:
            self.assertIn(f'href="/{slug}/"', self.html)
        self.assertNotIn("coming soon", self.html.lower())

    def test_has_search_metadata_breadcrumbs_and_collection_schema(self) -> None:
        self.assertIn("<title>Country Property Guides for Foreign Buyers | Global Home Atlas</title>", self.html)
        self.assertIn('<link rel="canonical" href="https://globalhomeatlas.com/countries/">', self.html)
        self.assertIn('aria-label="Breadcrumb"', self.html)
        scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', self.html, re.S)
        payloads = [json.loads(script) for script in scripts]
        types = {payload.get("@type") for payload in payloads}
        self.assertIn("CollectionPage", types)
        self.assertIn("ItemList", types)
        self.assertIn("BreadcrumbList", types)
```

- [ ] **Step 2: Run the tests and confirm they fail because the builder is absent**

Run: `python3 -m unittest tests.test_country_guides_hub -v`

Expected: error containing `has no attribute 'build_country_guides_hub_page'`.

- [ ] **Step 3: Implement the minimal schema and page builder**

Add constants for the title and description, helpers that resolve retirement slugs from each hub’s existing `guide_slugs`, and a renderer with:

```python
def schema_for_country_guides_hub(canonical: str) -> list[dict]:
    items = [
        {
            "@type": "ListItem",
            "position": position,
            "name": hub["country"],
            "url": country_url(hub),
        }
        for position, hub in enumerate(sorted(COUNTRY_HUBS, key=lambda item: item["country"]), 1)
    ]
    return [
        *global_schema_entities(),
        {"@context": "https://schema.org", "@type": "CollectionPage", "name": COUNTRY_GUIDES_HUB_H1, "url": canonical},
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": SITE_NAME, "item": SITE_URL},
                {"@type": "ListItem", "position": 2, "name": "Countries", "item": canonical},
            ],
        },
        {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": items},
    ]


def build_country_guides_hub_page(destinations: list[dict]) -> str:
    destination_by_id = {item["id"]: item for item in destinations}
    rows = []
    for hub in sorted(COUNTRY_HUBS, key=lambda item: item["country"]):
        retirement_slug = next(
            (slug for slug in hub.get("guide_slugs", []) if slug.endswith("retirement-property-foreign-buyers")),
            None,
        )
        destinations_html = "".join(
            f'<a href="/destinations/{destination_slug(destination_by_id[item_id])}/">{escape(destination_by_id[item_id]["name"])}</a>'
            for item_id in hub["destination_ids"]
        )
        retirement_html = (
            f'<a href="/{escape(retirement_slug)}/">Retiring in {escape(hub["country"])}</a>'
            if retirement_slug
            else ""
        )
        rows.append(
            f'<article data-country="{escape(hub["slug"])}"><h2>{escape(hub["country"])}</h2>'
            f'<p>{escape(hub["thesis"])}</p><nav>'
            f'<a href="/countries/{escape(hub["slug"])}/">Buying property in {escape(hub["country"])}</a>'
            f'{retirement_html}{destinations_html}</nav></article>'
        )
    directory = "".join(rows)
    return f"""<!doctype html>
<html lang="en"><head>
{head_html(COUNTRY_GUIDES_HUB_TITLE, COUNTRY_GUIDES_HUB_DESCRIPTION, page_url("countries"), schema_for_country_guides_hub(page_url("countries")))}
</head><body>{primary_nav_html()}<main><h1>{COUNTRY_GUIDES_HUB_H1}</h1>
<section id="country-directory">{directory}</section></main>{analytics_event_script()}</body></html>"""
```

The final implementation must use explicit link labels: `Buying property in {country}`, `Retiring in {country}`, and the destination names.

- [ ] **Step 4: Run the focused tests until green**

Run: `python3 -m unittest tests.test_country_guides_hub -v`

Expected: all tests pass.

- [ ] **Step 5: Commit the rendering contract**

```bash
git add tests/test_country_guides_hub.py src/build_unified_app.py
git commit -m "feat: add country guides directory"
```

---

### Task 2: Wire the hub into navigation, generation, and discovery

**Files:**
- Modify: `tests/test_country_guides_hub.py`
- Modify: `src/build_unified_app.py`

**Interfaces:**
- Consumes: `build_country_guides_hub_page(destinations)` from Task 1.
- Produces: `artifacts/countries/index.html`, a `/countries/` navigation target, and a sitemap record.

- [ ] **Step 1: Write failing integration assertions**

Add tests that run the generator in the existing repository fixture context and assert:

```python
def test_navigation_and_build_publish_the_hub(self) -> None:
    self.assertIn('href="/countries/">Countries</a>', build_unified_app.primary_nav_links_html())
    self.assertIn(
        (build_unified_app.page_url("countries"), "0.90"),
        build_unified_app.sitemap_url_entries(self.destinations),
    )
```

If sitemap entries are not yet exposed through a helper, add a focused test against a new `sitemap_url_entries(destinations)` interface rather than parsing unrelated generator internals.

- [ ] **Step 2: Run the focused tests and confirm the old navigation or missing helper fails**

Run: `python3 -m unittest tests.test_country_guides_hub -v`

Expected: failure showing the old `/guides/#country-selection` link or absent sitemap entry.

- [ ] **Step 3: Implement build wiring**

Change `PRIMARY_NAV_LINKS` to use `/countries/`. During `build()`:

```python
countries_dir = ARTIFACTS / "countries"
countries_dir.mkdir(exist_ok=True)
(countries_dir / "index.html").write_text(
    clean_generated_html(build_country_guides_hub_page(destinations)),
    encoding="utf-8",
)
```

Retain the existing loop that writes individual country directories. Add `page_url("countries")` to the sitemap at priority `0.90`.

- [ ] **Step 4: Run the focused tests and build**

Run: `python3 -m unittest tests.test_country_guides_hub -v`

Run: `python3 src/build_unified_app.py`

Expected: tests pass and `artifacts/countries/index.html` exists.

- [ ] **Step 5: Commit discovery wiring**

```bash
git add tests/test_country_guides_hub.py src/build_unified_app.py
git commit -m "feat: publish country guides hub"
```

---

### Task 3: Add progressive filtering and accessibility coverage

**Files:**
- Modify: `tests/test_country_guides_hub.py`
- Modify: `src/build_unified_app.py`

**Interfaces:**
- Consumes: server-rendered country rows with `data-country` and searchable text.
- Produces: labelled `#country-filter`, live `#country-filter-status`, and a no-dependency filtering script.

- [ ] **Step 1: Write failing markup tests**

```python
def test_filter_is_accessible_and_progressive(self) -> None:
    self.assertIn('id="country-filter"', self.html)
    self.assertIn('aria-controls="country-directory"', self.html)
    self.assertIn('id="country-filter-status"', self.html)
    self.assertIn('aria-live="polite"', self.html)
    self.assertIn('data-track="country_filter_use"', self.html)
```

- [ ] **Step 2: Run the focused test and confirm it fails on missing controls**

Run: `python3 -m unittest tests.test_country_guides_hub.CountryGuidesHubTests.test_filter_is_accessible_and_progressive -v`

Expected: failure on the missing filter ID.

- [ ] **Step 3: Implement the filter**

Render a visible `<label>` and search input before the directory. The script lowercases the query, toggles each row’s `hidden` property, updates the live result text, and emits one `country_filter_use` event through `window.GHA.track` after the first non-empty input. It must not rewrite or fetch any country content.

- [ ] **Step 4: Run the focused suite**

Run: `python3 -m unittest tests.test_country_guides_hub -v`

Expected: all focused tests pass.

- [ ] **Step 5: Commit the filter**

```bash
git add tests/test_country_guides_hub.py src/build_unified_app.py
git commit -m "feat: filter country guide directory"
```

---

### Task 4: Verify the full site and presentation

**Files:**
- Verify: `artifacts/countries/index.html`
- Verify: `artifacts/sitemap.xml`

**Interfaces:**
- Consumes: completed generator and tests.
- Produces: verified desktop/mobile hub ready for deployment.

- [ ] **Step 1: Run the complete automated checks**

Run: `python3 src/build_unified_app.py`

Run: `python3 -m unittest discover -b`

Run: `git diff --check -- src tests docs`

Expected: build exits 0, all tests pass, and diff check emits no output.

- [ ] **Step 2: Start the local preview**

Run: `python3 -m http.server 8765 --directory artifacts`

Expected: the server listens on `127.0.0.1:8765`.

- [ ] **Step 3: Inspect desktop and mobile layouts**

Open `http://127.0.0.1:8765/countries/?v=country-hub` at approximately 1440px and 390px widths. Verify one H1, editorial row rhythm, legible labels, no horizontal overflow, and no console errors.

- [ ] **Step 4: Exercise interactions and links**

Filter for `Japan`, clear the input, and follow representative acquisition, retirement, destination, rankings, calculator, and methodology links. Verify keyboard focus and live result text.

- [ ] **Step 5: Review the committed diff**

Run: `git status --short`

Run: `git diff --stat HEAD~3..HEAD`

Expected: only the specification, plan, focused tests, and generator source are committed; generated artifacts remain excluded from the feature commits.
