# Japan Foreign-Buyer Country Guide Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the legacy Japan country hub with an acquisition-first, source-grounded guide titled “Buying Property in Japan as a Foreigner,” ready for local user review before any other country is migrated.

**Architecture:** Add a focused country-guide data and validation module, then route only the Japan hub through a new semantic renderer in the existing static builder. Keep non-migrated country hubs on the legacy renderer. Reuse the established site header/footer and premium editorial design language while giving the acquisition guide its own small CSS contract.

**Tech Stack:** Python 3 static-site generator, dictionary-backed editorial content, `unittest`, HTML/JSON-LD generation, CSS, local HTTP preview, in-app browser QA.

**Spec:** `docs/superpowers/specs/2026-08-27-foreign-buyer-country-guides-design.md`

## Global Constraints

- Migrate Japan only; do not change the rendered structure of the other 16 country hubs.
- Preserve `/countries/japan-property/` as the canonical route.
- H1 must be `Buying Property in Japan as a Foreigner`.
- Do not render sample listings, listing images, retirement-capital blocks, premium briefs, shortlist-review panels, generic `Country Thesis`, or generic `Buyer Fit` sections.
- Render exactly one compact destination comparison.
- Keep substantive factual guidance; remove generic, self-referential, and process-description prose.
- References must be the final article section.
- Legal and administrative claims require current authoritative sources reviewed on 2026-08-27 or later.
- The Japan acquisition guide and Japan retirement guide must link to each other contextually.
- Use open semantic sections, not `<details>` accordions, for the core article.
- Use one existing scenic image; do not create a montage or duplicate listing imagery.
- Normal text must meet WCAG AA contrast and mobile actions must have at least 44px targets.
- Generated `artifacts/**` are preview output and must not be included in feature commits.

## File Map

- Create `src/foreign_buyer_country_guides.py`: migrated-guide data, required-field constants, lookup, and validation.
- Modify `src/build_unified_app.py`: import the guide module, select the new renderer for Japan, render semantic article HTML and JSON-LD, and add the reciprocal link to the Japan retirement guide.
- Modify `src/site_design_system.py`: provide `foreign_buyer_country_guide_css()` for the acquisition-guide layout.
- Create `tests/test_foreign_buyer_country_guide.py`: data, validation, content, schema, routing, link, and exclusion contracts.
- Create `docs/research/japan-foreign-buyer-country-guide-evidence.md`: claim-to-source ledger and review triggers.
- Modify `docs/UX_UI_PREMIUM_REVAMP_HANDOFF.md`: document the local pilot route and explicitly note that the other country hubs remain legacy until approval.

---

### Task 1: Add the Migrated-Guide Contract and Fail-Closed Validation

**Files:**
- Create: `src/foreign_buyer_country_guides.py`
- Create: `tests/test_foreign_buyer_country_guide.py`

**Interfaces:**
- Produces: `FOREIGN_BUYER_COUNTRY_GUIDES: dict[str, dict]`
- Produces: `get_foreign_buyer_country_guide(country_hub_slug: str) -> dict | None`
- Produces: `validate_foreign_buyer_country_guide(country_hub_slug: str, guide: dict, expected_destination_ids: list[str]) -> None`
- Validation raises `ValueError` with the country slug and missing or inconsistent field.

- [ ] **Step 1: Write failing lookup and validation tests**

```python
from __future__ import annotations

from copy import deepcopy
import json
import re
import unittest

from src.foreign_buyer_country_guides import (
    FOREIGN_BUYER_COUNTRY_GUIDES,
    get_foreign_buyer_country_guide,
    validate_foreign_buyer_country_guide,
)


def valid_guide_fixture() -> dict:
    sourced = {"heading": "Heading", "body": "Body", "source_urls": ["https://example.gov/source"]}
    return {
        "country": "Japan",
        "title": "Title",
        "description": "Description",
        "h1": "H1",
        "summary": "Summary",
        "date_published": "2026-08-27",
        "date_reviewed": "2026-08-27",
        "hero_image": {"src": "/assets/example.webp", "alt": "Alt", "caption": "Caption"},
        "direct_answers": {
            key: {"answer": "Answer", "source_urls": ["https://example.gov/source"]}
            for key in ("ownership", "residency", "financing", "short_rentals")
        },
        "eligibility_sections": [deepcopy(sourced)],
        "purchase_steps": [
            {"heading": f"Step {index}", "body": "Body", "source_urls": ["https://example.gov/source"]}
            for index in range(1, 6)
        ],
        "cost_rows": [
            {"cost": f"Cost {index}", "when": "When", "buyer_read": "Read", "source_urls": ["https://example.gov/source"]}
            for index in range(1, 5)
        ],
        "ownership_rules": [deepcopy(sourced)],
        "destination_reads": {
            destination_id: {"best_for": "Best", "verify_first": "Verify"}
            for destination_id in ("fukuoka-itoshima", "hakone-izu", "hakuba", "niseko")
        },
        "buyer_checklist": ["Check"],
        "faqs": [
            {"question": f"Question {index}", "answer": "Answer", "source_urls": ["https://example.gov/source"]}
            for index in range(1, 4)
        ],
        "primary_sources": [{"label": "Source", "url": "https://example.gov/source"}],
        "retirement_guide_slug": "japan-retirement-property-foreign-buyers",
    }


class ForeignBuyerCountryGuideContractTests(unittest.TestCase):
    def test_only_japan_is_migrated_for_the_pilot(self) -> None:
        self.assertEqual(["japan-property"], sorted(FOREIGN_BUYER_COUNTRY_GUIDES))
        self.assertIsNotNone(get_foreign_buyer_country_guide("japan-property"))
        self.assertIsNone(get_foreign_buyer_country_guide("spain-property"))

    def test_validator_rejects_missing_required_content(self) -> None:
        guide = valid_guide_fixture()
        guide.pop("purchase_steps")

        with self.assertRaisesRegex(ValueError, "japan-property.*purchase_steps"):
            validate_foreign_buyer_country_guide(
                "japan-property",
                guide,
                ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"],
            )

    def test_validator_requires_four_named_direct_answers(self) -> None:
        guide = valid_guide_fixture()
        guide["direct_answers"].pop("financing")

        with self.assertRaisesRegex(ValueError, "direct_answers.*financing"):
            validate_foreign_buyer_country_guide(
                "japan-property",
                guide,
                ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"],
            )

    def test_validator_requires_one_read_for_every_destination(self) -> None:
        guide = valid_guide_fixture()
        guide["destination_reads"].pop("niseko")

        with self.assertRaisesRegex(ValueError, "destination_reads.*niseko"):
            validate_foreign_buyer_country_guide(
                "japan-property",
                guide,
                ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"],
            )
```

- [ ] **Step 2: Run the tests and verify the red state**

Run:

```bash
python3 -m unittest tests.test_foreign_buyer_country_guide
```

Expected: import failure because `src.foreign_buyer_country_guides` does not exist.

- [ ] **Step 3: Implement the contract, lookup, and validator**

Create the module with these required keys and checks:

```python
"""Structured content and validation for migrated foreign-buyer country guides."""

from __future__ import annotations

from copy import deepcopy


REQUIRED_GUIDE_KEYS = {
    "country",
    "title",
    "description",
    "h1",
    "summary",
    "date_published",
    "date_reviewed",
    "hero_image",
    "direct_answers",
    "eligibility_sections",
    "purchase_steps",
    "cost_rows",
    "ownership_rules",
    "destination_reads",
    "buyer_checklist",
    "faqs",
    "primary_sources",
    "retirement_guide_slug",
}
REQUIRED_DIRECT_ANSWERS = {"ownership", "residency", "financing", "short_rentals"}

FOREIGN_BUYER_COUNTRY_GUIDES: dict[str, dict] = {
    "japan-property": {"country": "Japan"},
}


def get_foreign_buyer_country_guide(country_hub_slug: str) -> dict | None:
    guide = FOREIGN_BUYER_COUNTRY_GUIDES.get(country_hub_slug)
    return deepcopy(guide) if guide else None


def validate_foreign_buyer_country_guide(
    country_hub_slug: str,
    guide: dict,
    expected_destination_ids: list[str],
) -> None:
    missing = sorted(REQUIRED_GUIDE_KEYS - set(guide))
    if missing:
        raise ValueError(f"{country_hub_slug}: missing {', '.join(missing)}")
    missing_answers = sorted(REQUIRED_DIRECT_ANSWERS - set(guide["direct_answers"]))
    if missing_answers:
        raise ValueError(
            f"{country_hub_slug}: direct_answers missing {', '.join(missing_answers)}"
        )
    missing_destinations = sorted(
        set(expected_destination_ids) - set(guide["destination_reads"])
    )
    if missing_destinations:
        raise ValueError(
            f"{country_hub_slug}: destination_reads missing {', '.join(missing_destinations)}"
        )
    if set(guide["destination_reads"]) != set(expected_destination_ids):
        raise ValueError(f"{country_hub_slug}: destination_reads must match destination_ids")
    if len(guide["purchase_steps"]) < 5:
        raise ValueError(f"{country_hub_slug}: purchase_steps requires at least five steps")
    if len(guide["cost_rows"]) < 4:
        raise ValueError(f"{country_hub_slug}: cost_rows requires at least four rows")
    if len(guide["faqs"]) < 3:
        raise ValueError(f"{country_hub_slug}: faqs requires at least three questions")
    if not guide["primary_sources"]:
        raise ValueError(f"{country_hub_slug}: primary_sources is required")
```

Task 2 replaces the pilot registration stub with the complete, reviewed Japan record before the build imports or validates it.

- [ ] **Step 4: Add one test per remaining fail-closed condition**

Test fewer than five purchase steps, fewer than four cost rows, fewer than three FAQs, empty sources, an extra destination read, and missing dates. Each test must assert the exact `ValueError` message.

- [ ] **Step 5: Run the contract tests**

Run:

```bash
python3 -m unittest tests.test_foreign_buyer_country_guide.ForeignBuyerCountryGuideContractTests
```

Expected: all contract tests pass.

- [ ] **Step 6: Commit the contract**

```bash
git add src/foreign_buyer_country_guides.py tests/test_foreign_buyer_country_guide.py
git commit -m "feat: define foreign-buyer country guide contract"
```

---

### Task 2: Build the Japan Evidence Ledger and Acquisition Copy

**Files:**
- Create: `docs/research/japan-foreign-buyer-country-guide-evidence.md`
- Modify: `src/foreign_buyer_country_guides.py`
- Modify: `tests/test_foreign_buyer_country_guide.py`

**Interfaces:**
- Consumes: the validated guide structure from Task 1.
- Produces: complete `FOREIGN_BUYER_COUNTRY_GUIDES["japan-property"]` reader content and authoritative source URLs.

- [ ] **Step 1: Verify the official source set before writing copy**

Open and review these official sources, recording the exact page title, current rule, review date, caveat, and change trigger in the evidence ledger:

```text
https://www.mof.go.jp/english/policy/international_policy/real_property/index.html
https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html
https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html
https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf
https://www.mlit.go.jp/report/press/totikensangyo13_hh_000269.html
https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html
https://disaportal.gsi.go.jp/
https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf
https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html
https://www.mofa.go.jp/ca/fna/page22e_000738.html
```

Do not infer a legal conclusion from a page that does not state it. If a URL has moved, use the current official replacement and update both the ledger and guide data.

- [ ] **Step 2: Write failing reader-copy tests**

Add tests that require these reader-facing conclusions and prohibit generic prose:

```python
class JapanForeignBuyerContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guide = FOREIGN_BUYER_COUNTRY_GUIDES["japan-property"]

    def test_direct_answers_are_short_and_decisive(self) -> None:
        self.assertIn("generally buy and register", self.guide["direct_answers"]["ownership"]["answer"])
        self.assertIn("does not create", self.guide["direct_answers"]["residency"]["answer"])
        self.assertIn("lender-specific", self.guide["direct_answers"]["financing"]["answer"])
        self.assertIn("180 days", self.guide["direct_answers"]["short_rentals"]["answer"])

    def test_purchase_sequence_covers_offer_through_registration(self) -> None:
        headings = [step["heading"] for step in self.guide["purchase_steps"]]
        self.assertEqual(
            [
                "Confirm the buyer and intended use",
                "Appoint independent advisers",
                "Check the property before offering",
                "Review the contract and Important Matters Explanation",
                "Settle and register the transfer",
                "Complete non-resident reporting and owner administration",
            ],
            headings,
        )

    def test_copy_avoids_generic_process_language(self) -> None:
        rendered_data = repr(self.guide).lower()
        for phrase in (
            "this guide helps",
            "use this page",
            "country thesis",
            "buyer fit",
            "research read",
            "research inputs",
            "same ten-dimension model",
        ):
            self.assertNotIn(phrase, rendered_data)
```

- [ ] **Step 3: Run the content tests and verify they fail**

Run:

```bash
python3 -m unittest tests.test_foreign_buyer_country_guide.JapanForeignBuyerContentTests
```

Expected: failures against the minimal Task 1 values.

- [ ] **Step 4: Replace the temporary Japan record with reviewed content**

Use these fixed metadata and structural values:

```python
"country": "Japan",
"title": "Buying Property in Japan as a Foreigner | Global Home Atlas",
"description": "Learn how foreigners can buy property in Japan, including ownership rights, the purchase process, taxes, financing, reporting, rental rules, and four markets.",
"h1": "Buying Property in Japan as a Foreigner",
"summary": "Foreigners can generally own Japanese land and buildings, but the purchase creates no residence rights and non-resident buyers face reporting, financing, tax, management, and property-specific checks.",
"date_published": "2026-08-27",
"date_reviewed": "2026-08-27",
"hero_image": {
    "src": "/assets/fukuoka-itoshima-coast.webp",
    "alt": "Fukuoka and Itoshima coastline in Japan",
    "caption": "Fukuoka / Itoshima · City access and coastal living",
},
"retirement_guide_slug": "japan-retirement-property-foreign-buyers",
```

Write concise factual entries for the four direct answers, the six purchase steps specified by the test, at least four cost rows, ongoing-owner rules, checklist, and FAQs. Every legal or administrative entry includes `source_urls` that appear in `primary_sources`.

The cost table must distinguish:

- Purchase price from acquisition and registration taxes
- Brokerage and professional costs from taxes
- Annual fixed-asset, insurance, management, and repair costs
- Withholding or tax-administration issues involving non-resident parties
- Eventual sale and registration costs from acquisition costs

Do not state one universal closing-cost percentage. Explain that the exact amount depends on the asset, assessment, buyer, seller, finance, and date.

Use these destination reads:

```python
"destination_reads": {
    "fukuoka-itoshima": {
        "best_for": "Year-round city life with coastal access and broad domestic demand",
        "verify_first": "Rail or car dependence, building condition, flood exposure, management and resale depth",
    },
    "hakone-izu": {
        "best_for": "Personal use near Tokyo, onsen life and repeat weekend stays",
        "verify_first": "Slope, seismic condition, renovation scope, access, permitted use and thin comparable evidence",
    },
    "hakuba": {
        "best_for": "Active alpine use with a lower entry point than Niseko",
        "verify_first": "Snow load, winter access, staffing, building condition, operating permissions and exit depth",
    },
    "niseko": {
        "best_for": "Premium international resort use for buyers comfortable with high carrying costs",
        "verify_first": "Service charges, operator contract, construction quality, owner-use limits and resale depth",
    },
},
```

- [ ] **Step 5: Add source-integrity tests**

Test that every URL referenced by a direct answer, eligibility section, purchase step, cost row, ownership rule, or FAQ appears exactly once in `primary_sources`. Test that every `primary_sources` URL uses HTTPS and an approved official domain from `mof.go.jp`, `moj.go.jp`, `mlit.go.jp`, `nta.go.jp`, `gsi.go.jp`, or `mofa.go.jp`.

- [ ] **Step 6: Run content and contract tests**

Run:

```bash
python3 -m unittest tests.test_foreign_buyer_country_guide
```

Expected: all data, copy, and source-integrity tests pass.

- [ ] **Step 7: Commit the reviewed Japan content**

```bash
git add docs/research/japan-foreign-buyer-country-guide-evidence.md src/foreign_buyer_country_guides.py tests/test_foreign_buyer_country_guide.py
git commit -m "content: add Japan foreign-buyer acquisition guide"
```

---

### Task 3: Render the Acquisition Guide and Preserve Legacy Country Hubs

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_foreign_buyer_country_guide.py`

**Interfaces:**
- Consumes: `get_foreign_buyer_country_guide()` and `validate_foreign_buyer_country_guide()` from Task 1.
- Produces: `build_foreign_buyer_country_guide_page(hub: dict, guide: dict, destinations: list[dict], pages: list[dict], content_overrides: list[dict] | None = None) -> str`
- Produces: `schema_for_foreign_buyer_country_guide(guide: dict, selected: list[dict], canonical: str) -> list[dict]`
- `build_country_hub_page()` delegates to the new renderer only when lookup returns a migrated guide.

- [ ] **Step 1: Write failing renderer-selection and section-order tests**

```python
from src import build_unified_app


def render_country(slug: str) -> str:
    hub = next(item for item in build_unified_app.COUNTRY_HUBS if item["slug"] == slug)
    destinations = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.build_country_hub_page(
        hub, destinations, build_unified_app.SEO_PAGES
    )


class ForeignBuyerCountryGuideRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.japan = render_country("japan-property")
        cls.spain = render_country("spain-property")

    def test_japan_uses_the_acquisition_renderer_only(self) -> None:
        self.assertIn('<body class="foreign-buyer-country-guide">', self.japan)
        self.assertNotIn('<body class="foreign-buyer-country-guide">', self.spain)
        self.assertIn("Spain Property Guide for Foreign Buyers", self.spain)

    def test_japan_sections_follow_the_approved_order(self) -> None:
        section_ids = [
            "ownership-answer",
            "purchase-process",
            "costs-financing",
            "after-purchase",
            "destinations",
            "buyer-checklist",
            "faq",
            "sources",
        ]
        positions = [self.japan.index(f'id="{section_id}"') for section_id in section_ids]
        self.assertEqual(positions, sorted(positions))

    def test_core_article_uses_open_sections(self) -> None:
        article = self.japan.split('<article class="foreign-buyer-article">', 1)[1].split("</article>", 1)[0]
        self.assertNotIn("<details", article)
        self.assertNotIn("<summary", article)
```

- [ ] **Step 2: Run the renderer tests and verify they fail**

Run:

```bash
python3 -m unittest tests.test_foreign_buyer_country_guide.ForeignBuyerCountryGuideRenderingTests
```

Expected: Japan still uses the legacy country-hub HTML.

- [ ] **Step 3: Import and route the migrated guide**

Extend both package and direct-execution import branches:

```python
from src.foreign_buyer_country_guides import (
    get_foreign_buyer_country_guide,
    validate_foreign_buyer_country_guide,
)
```

At the beginning of `build_country_hub_page()`:

```python
migrated_guide = get_foreign_buyer_country_guide(hub["slug"])
if migrated_guide:
    validate_foreign_buyer_country_guide(
        hub["slug"], migrated_guide, hub["destination_ids"]
    )
    return build_foreign_buyer_country_guide_page(
        hub,
        migrated_guide,
        destinations,
        pages,
        content_overrides=content_overrides,
    )
```

- [ ] **Step 4: Implement small rendering helpers**

Add focused helpers immediately before the new page renderer:

```python
def source_links_html(labels_by_url: dict[str, str], urls: list[str]) -> str:
    return " ".join(
        f'<a href="{escape(url)}" rel="noopener noreferrer">{escape(labels_by_url[url])}</a>'
        for url in urls
    )


def foreign_buyer_direct_answers_html(
    guide: dict, source_labels: dict[str, str]
) -> str:
    labels = {
        "ownership": "Can foreigners buy?",
        "residency": "Does ownership create residency?",
        "financing": "Is financing practical?",
        "short_rentals": "What limits short-term rentals?",
    }
    return "".join(
        f'<article><h2>{escape(labels[key])}</h2>'
        f'<p>{escape(guide["direct_answers"][key]["answer"])}</p>'
        f'<p class="foreign-buyer-source-links">{source_links_html(source_labels, guide["direct_answers"][key]["source_urls"])}</p></article>'
        for key in ("ownership", "residency", "financing", "short_rentals")
    )


def foreign_buyer_eligibility_html(
    guide: dict, source_labels: dict[str, str]
) -> str:
    return "".join(
        f'<section><h3>{escape(item["heading"])}</h3><p>{escape(item["body"])}</p>'
        f'<p class="foreign-buyer-source-links">{source_links_html(source_labels, item["source_urls"])}</p></section>'
        for item in guide["eligibility_sections"]
    )


def foreign_buyer_purchase_steps_html(
    guide: dict, source_labels: dict[str, str]
) -> str:
    return "".join(
        f'<li><span>{index}</span><div><h3>{escape(step["heading"])}</h3>'
        f'<p>{escape(step["body"])}</p><p class="foreign-buyer-source-links">'
        f'{source_links_html(source_labels, step["source_urls"])}</p></div></li>'
        for index, step in enumerate(guide["purchase_steps"], start=1)
    )


def foreign_buyer_cost_table_html(
    guide: dict, source_labels: dict[str, str]
) -> str:
    rows = "".join(
        f'<tr><th scope="row">{escape(row["cost"])}</th><td>{escape(row["when"])}</td>'
        f'<td>{escape(row["buyer_read"])} <span class="foreign-buyer-source-links">'
        f'{source_links_html(source_labels, row["source_urls"])}</span></td></tr>'
        for row in guide["cost_rows"]
    )
    return (
        '<table class="foreign-buyer-cost-table"><thead><tr>'
        '<th scope="col">Cost</th><th scope="col">When</th><th scope="col">What matters</th>'
        f'</tr></thead><tbody>{rows}</tbody></table>'
    )


def foreign_buyer_rules_html(
    guide: dict, source_labels: dict[str, str]
) -> str:
    return "".join(
        f'<section><h3>{escape(rule["heading"])}</h3><p>{escape(rule["body"])}</p>'
        f'<p class="foreign-buyer-source-links">{source_links_html(source_labels, rule["source_urls"])}</p></section>'
        for rule in guide["ownership_rules"]
    )


def foreign_buyer_destination_comparison_html(
    guide: dict, selected: list[dict]
) -> tuple[str, str]:
    rows = []
    cards = []
    for destination in selected:
        destination_id = destination["id"]
        read = guide["destination_reads"][destination_id]
        href = f'/destinations/{escape(destination_slug(destination))}/'
        name = escape(destination["name"])
        rows.append(
            f'<tr><th scope="row"><a href="{href}">{name}</a></th>'
            f'<td>{escape(read["best_for"])}</td><td>{escape(read["verify_first"])}</td></tr>'
        )
        cards.append(
            f'<article><h3><a href="{href}">{name}</a></h3>'
            f'<p><strong>Best for:</strong> {escape(read["best_for"])}</p>'
            f'<p><strong>Verify first:</strong> {escape(read["verify_first"])}</p></article>'
        )
    table = (
        '<table class="foreign-buyer-destination-table"><thead><tr>'
        '<th scope="col">Destination</th><th scope="col">Best for</th>'
        f'<th scope="col">Verify first</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
    )
    return table, f'<div class="foreign-buyer-destination-cards">{"".join(cards)}</div>'


def foreign_buyer_faq_html(
    guide: dict, source_labels: dict[str, str]
) -> str:
    return "".join(
        f'<article class="foreign-buyer-faq-item"><h3>{escape(item["question"])}</h3>'
        f'<p>{escape(item["answer"])}</p><p class="foreign-buyer-source-links">'
        f'{source_links_html(source_labels, item["source_urls"])}</p></article>'
        for item in guide["faqs"]
    )


def foreign_buyer_sources_html(guide: dict) -> str:
    return "".join(
        f'<li><a href="{escape(item["url"])}" rel="noopener noreferrer">{escape(item["label"])}</a></li>'
        for item in guide["primary_sources"]
    )
```

Each helper renders one approved content unit and depends only on its arguments. Source links use meaningful labels or a compact `Official source` link; they never expose internal confidence or research-process language.

- [ ] **Step 5: Implement the semantic page renderer**

The renderer must compute the comparison variants once and emit this exact semantic shell:

```python
destination_table, destination_cards = foreign_buyer_destination_comparison_html(
    guide, selected
)
source_labels = {item["url"]: item["label"] for item in guide["primary_sources"]}
eligibility_html = foreign_buyer_eligibility_html(guide, source_labels)
checklist = "".join(f"<li>{escape(item)}</li>" for item in guide["buyer_checklist"])
retirement_link = (
    '<p class="foreign-buyer-retirement-link">Planning to live in Japan long term? '
    '<a href="/japan-retirement-property-foreign-buyers/">Read the Japan retirement property guide</a> '
    'for residence, healthcare and retirement-life planning.</p>'
)
section_links = [
    ("Can foreigners buy?", "ownership-answer"),
    ("Purchase process", "purchase-process"),
    ("Costs and financing", "costs-financing"),
    ("After purchase", "after-purchase"),
    ("Where to buy", "destinations"),
    ("Buyer checklist", "buyer-checklist"),
    ("FAQ", "faq"),
    ("References", "sources"),
]
rail_links = "".join(
    f'<a href="#{escape(section_id)}">{escape(label)}</a>'
    for label, section_id in section_links
)

return f"""<!doctype html>
<html lang="en">
<head>
{head_html(guide["title"], guide["description"], canonical, schema_for_foreign_buyer_country_guide(guide, selected, canonical))}
<style>{foreign_buyer_country_guide_css()}</style>
</head>
<body class="foreign-buyer-country-guide">
{site_header_html()}
<header class="foreign-buyer-hero">
  <div class="foreign-buyer-shell foreign-buyer-hero-grid">
    <div><h1>{escape(guide["h1"])}</h1><p>{escape(guide["summary"])}</p>
      <p class="foreign-buyer-byline">By Global Home Atlas Research Team · Published {escape(guide["date_published"])} · Reviewed {escape(guide["date_reviewed"])}</p>
    </div>
    <figure><img src="{escape(guide["hero_image"]["src"])}" alt="{escape(guide["hero_image"]["alt"])}"><figcaption>{escape(guide["hero_image"]["caption"])}</figcaption></figure>
  </div>
  <div class="foreign-buyer-shell foreign-buyer-answers">{foreign_buyer_direct_answers_html(guide, source_labels)}</div>
</header>
<main><div class="foreign-buyer-shell foreign-buyer-layout">
  <article class="foreign-buyer-article">
    <section id="ownership-answer"><h2>Can foreigners buy property in Japan?</h2>{eligibility_html}{retirement_link}</section>
    <section id="purchase-process"><h2>How the purchase works</h2><ol class="foreign-buyer-steps">{foreign_buyer_purchase_steps_html(guide, source_labels)}</ol></section>
    <section id="costs-financing"><h2>Costs and financing</h2>{foreign_buyer_cost_table_html(guide, source_labels)}</section>
    <section id="after-purchase"><h2>Rules after purchase</h2>{foreign_buyer_rules_html(guide, source_labels)}</section>
    <section id="destinations"><h2>Where to buy</h2>{destination_table}{destination_cards}</section>
    <section id="buyer-checklist"><h2>Before making an offer</h2><ul class="foreign-buyer-checklist">{checklist}</ul></section>
    <section id="faq"><h2>Frequently asked questions</h2>{foreign_buyer_faq_html(guide, source_labels)}</section>
    <section id="sources"><h2>References and update policy</h2><p>Rules can change. Recheck every linked source and obtain current professional advice before signing.</p><ul>{foreign_buyer_sources_html(guide)}</ul></section>
  </article>
  <aside class="foreign-buyer-rail"><p>In this guide</p><nav aria-label="In this guide">{rail_links}</nav><a class="foreign-buyer-atlas-link" href="/dashboard/#destinations">Compare every destination</a></aside>
</div></main>
{site_footer_html()}
{analytics_event_script()}
</body></html>"""
```

The hero contains the four direct answers immediately below the summary. The rail repeats only section links and one `Compare every destination` action to `/dashboard/#destinations`.

- [ ] **Step 6: Add exclusion and comparison tests**

Assert:

```python
for forbidden in (
    "Country Thesis",
    "Buyer Fit",
    "Recommended Premium Brief",
    "Review my shortlist",
    "Estimate your retirement capital",
    "Representative property",
    "Asking price",
):
    self.assertNotIn(forbidden, self.japan)

self.assertEqual(1, self.japan.count('id="destinations"'))
self.assertEqual(1, self.japan.count('class="foreign-buyer-destination-table"'))
for destination_id in ("fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"):
    self.assertIn(f'/destinations/{destination_id}/', self.japan)
```

- [ ] **Step 7: Run renderer and legacy-regression tests**

Run:

```bash
python3 -m unittest \
  tests.test_foreign_buyer_country_guide \
  tests.test_japan_retirement_article \
  tests.test_remaining_country_retirement_articles
```

Expected: all selected tests pass and Spain remains on the legacy hub renderer.

- [ ] **Step 8: Commit the renderer**

```bash
git add src/build_unified_app.py tests/test_foreign_buyer_country_guide.py
git commit -m "feat: render acquisition-first Japan country guide"
```

---

### Task 4: Add Matching Editorial Design and Responsive Behaviour

**Files:**
- Modify: `src/site_design_system.py`
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_foreign_buyer_country_guide.py`

**Interfaces:**
- Produces: `foreign_buyer_country_guide_css() -> str`
- The renderer embeds this CSS after the shared head markup.

- [ ] **Step 1: Write failing design-contract tests**

```python
class ForeignBuyerCountryGuideDesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = render_country("japan-property")

    def test_page_uses_premium_editorial_typography_without_heavy_weights(self) -> None:
        self.assertIn('--foreign-buyer-serif:', self.html)
        self.assertIn('.foreign-buyer-hero h1', self.html)
        for weight in ("font-weight: 800", "font-weight: 850", "font-weight: 900"):
            self.assertNotIn(weight, self.html)

    def test_rail_and_mobile_targets_are_explicit(self) -> None:
        self.assertIn('.foreign-buyer-rail { position: sticky;', self.html)
        self.assertIn('.foreign-buyer-rail a { min-height: 44px;', self.html)
        self.assertIn('@media (max-width: 720px)', self.html)

    def test_comparison_has_desktop_table_and_mobile_cards(self) -> None:
        self.assertIn('class="foreign-buyer-destination-table"', self.html)
        self.assertIn('class="foreign-buyer-destination-cards"', self.html)
        self.assertIn('.foreign-buyer-destination-table { display: none;', self.html)
```

- [ ] **Step 2: Run the design tests and verify they fail**

Run:

```bash
python3 -m unittest tests.test_foreign_buyer_country_guide.ForeignBuyerCountryGuideDesignTests
```

Expected: missing CSS and mobile comparison contracts.

- [ ] **Step 3: Implement `foreign_buyer_country_guide_css()`**

Use the established palette and type system:

```css
:root {
  --foreign-buyer-ink: #202825;
  --foreign-buyer-paper: #f3efe5;
  --foreign-buyer-surface: #fbf8f0;
  --foreign-buyer-muted: #646e69;
  --foreign-buyer-accent: #a44e2f;
  --foreign-buyer-serif: "Iowan Old Style", Baskerville, "Palatino Linotype", Palatino, Georgia, serif;
  --foreign-buyer-sans: "Avenir Next", Avenir, "Helvetica Neue", Helvetica, Arial, sans-serif;
}
```

Implement:

- A shared maximum-width shell aligned with the landing and retirement-guide grid
- A two-column hero with copy and the existing `/assets/fukuoka-itoshima-coast.webp`
- Four direct answers as a plain ruled grid, not decorative cards
- Article plus sticky rail at desktop widths
- Comfortable paragraph measure and open section spacing
- Numbered purchase steps
- A simple cost table
- Desktop destination table plus equivalent mobile cards
- Visible keyboard focus
- 44px rail and action targets
- One-column layout below 960px and mobile cards below 720px
- No horizontal overflow

- [ ] **Step 4: Import and embed the CSS**

Update both import branches in `src/build_unified_app.py`:

```python
from src.site_design_system import (
    foreign_buyer_country_guide_css,
    landing_design_css,
    site_footer_html,
    site_header_html,
)
```

Place `<style>{foreign_buyer_country_guide_css()}</style>` in the new renderer head. Use `site_header_html()` and `site_footer_html()` so the pilot matches the approved landing-page chrome.

- [ ] **Step 5: Run design and landing-regression tests**

Run:

```bash
python3 -m unittest \
  tests.test_foreign_buyer_country_guide \
  tests.test_site_design_system
```

Expected: all tests pass.

- [ ] **Step 6: Commit the design**

```bash
git add src/site_design_system.py src/build_unified_app.py tests/test_foreign_buyer_country_guide.py
git commit -m "feat: style the Japan foreign-buyer guide"
```

---

### Task 5: Add SEO Schema and Reciprocal Guide Links

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_foreign_buyer_country_guide.py`
- Modify: `tests/test_japan_retirement_article.py`

**Interfaces:**
- Produces: `schema_for_foreign_buyer_country_guide(guide: dict, selected: list[dict], canonical: str) -> list[dict]`
- Visible FAQ and destination data are the only source for `FAQPage` and `ItemList` entities.

- [ ] **Step 1: Write failing metadata, schema, and reciprocal-link tests**

```python
def test_metadata_targets_acquisition_intent(self) -> None:
    self.assertIn(
        "<title>Buying Property in Japan as a Foreigner | Global Home Atlas</title>",
        self.japan,
    )
    self.assertIn('<link rel="canonical" href="https://globalhomeatlas.com/countries/japan-property/">', self.japan)
    description = re.search(r'<meta name="description" content="([^"]+)">', self.japan).group(1)
    self.assertLessEqual(len(description), 160)
    self.assertIn("foreigners", description.lower())
    self.assertNotIn("retirement property", description.lower())

def test_visible_faq_and_destination_rows_match_schema(self) -> None:
    schema_text = re.search(
        r'<script type="application/ld\+json">(.*?)</script>',
        self.japan,
        flags=re.DOTALL,
    ).group(1)
    schemas = json.loads(schema_text)
    faq = next(item for item in schemas if item.get("@type") == "FAQPage")
    item_list = next(item for item in schemas if item.get("@type") == "ItemList")
    self.assertEqual(self.japan.count('class="foreign-buyer-faq-item"'), len(faq["mainEntity"]))
    self.assertEqual(4, len(item_list["itemListElement"]))

def test_country_and_retirement_guides_link_to_each_other(self) -> None:
    self.assertIn('/japan-retirement-property-foreign-buyers/', self.japan)
    retirement = render_japan_retirement_article()
    self.assertIn('/countries/japan-property/', retirement)
    self.assertIn("buying property in Japan as a foreigner", retirement.lower())
```

Use the standard-library regular-expression and JSON modules shown above; do not add a runtime dependency for this assertion.

- [ ] **Step 2: Run the SEO tests and verify they fail**

Run:

```bash
python3 -m unittest \
  tests.test_foreign_buyer_country_guide \
  tests.test_japan_retirement_article
```

Expected: missing acquisition schema and missing retirement-to-country reciprocal link.

- [ ] **Step 3: Implement acquisition schema**

Return the existing global entities plus:

- `Article` with headline, description, canonical URL, `datePublished`, `dateModified`, author, and publisher
- `BreadcrumbList` for Home → Countries → Japan
- `FAQPage` generated from `guide["faqs"]`
- `ItemList` generated from the four visible destination entries

Do not retain the legacy `CollectionPage` entity on the migrated Japan page.

- [ ] **Step 4: Add contextual reciprocal links**

In the Japan acquisition guide, place one link after the direct residency answer:

```html
Planning to live in Japan long term? Read the
<a href="/japan-retirement-property-foreign-buyers/">Japan retirement property guide</a>
for residence, healthcare and retirement-life planning.
```

In the Japan retirement guide’s first residency section, add:

```html
For the acquisition process, costs and owner obligations, see
<a href="/countries/japan-property/">buying property in Japan as a foreigner</a>.
```

Do not add either link to a second article location.

- [ ] **Step 5: Run SEO, schema, and internal-link tests**

Run:

```bash
python3 -m unittest \
  tests.test_foreign_buyer_country_guide \
  tests.test_japan_retirement_article \
  tests.test_seo_infrastructure_integrity
```

Expected: all selected tests pass.

- [ ] **Step 6: Commit SEO and linking**

```bash
git add src/build_unified_app.py tests/test_foreign_buyer_country_guide.py tests/test_japan_retirement_article.py
git commit -m "feat: separate Japan acquisition and retirement intent"
```

---

### Task 6: Build, Review, and Hand Off the Local Japan Pilot

**Files:**
- Modify: `docs/UX_UI_PREMIUM_REVAMP_HANDOFF.md`
- Generated but do not commit: `artifacts/countries/japan-property/index.html`

**Interfaces:**
- Produces: a locally rendered Japan pilot at `http://127.0.0.1:8765/countries/japan-property/?v=foreign-buyer-pilot`.
- Does not merge, push, deploy, or migrate another country.

- [ ] **Step 1: Run the focused suite**

Run:

```bash
python3 -m unittest \
  tests.test_foreign_buyer_country_guide \
  tests.test_japan_retirement_article \
  tests.test_remaining_country_retirement_articles \
  tests.test_site_design_system \
  tests.test_seo_infrastructure_integrity
```

Expected: all focused tests pass with zero failures and zero errors.

- [ ] **Step 2: Run the full repository suite**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

Expected: all tests pass.

- [ ] **Step 3: Build the static site**

Run:

```bash
python3 src/build_unified_app.py
git diff --check -- src tests docs
```

Expected: build exits 0 and `git diff --check` reports no errors.

- [ ] **Step 4: Verify generated-page contracts**

Run:

```bash
rg -n "Buying Property in Japan as a Foreigner|Can foreigners buy property in Japan|How the purchase works|Costs and financing|Rules after purchase|Where to buy|Before making an offer|References and update policy" artifacts/countries/japan-property/index.html
rg -n "Country Thesis|Buyer Fit|Recommended Premium Brief|Review my shortlist|Estimate your retirement capital|Representative property" artifacts/countries/japan-property/index.html
```

Expected: every required phrase appears; the second command returns no matches.

- [ ] **Step 5: Start or reuse the local preview server**

Serve `artifacts/` on port 8765 and open:

```text
http://127.0.0.1:8765/countries/japan-property/?v=foreign-buyer-pilot
```

- [ ] **Step 6: Perform desktop browser QA**

At a viewport near 1440×1100, verify:

- One H1 and the approved section order
- Four direct answers above the main article
- Sticky section rail
- One destination comparison
- Four dossier links
- References as the final article section
- No horizontal overflow
- No duplicate Atlas or retirement links
- Hero image is scenic, sharp, and correctly cropped

- [ ] **Step 7: Perform mobile browser QA**

At a viewport near 390×844, verify:

- Single-column reading order
- Destination cards replace the desktop table
- Rail becomes a non-sticky compact navigation block
- Minimum 44px targets
- No clipped headings, links, or table content
- No horizontal overflow

- [ ] **Step 8: Update the handoff document**

Add a `Foreign-buyer country guide pilot` section stating:

- Japan is the only migrated country hub.
- The local pilot URL.
- The acquisition, retirement, dossier, and Atlas page roles.
- Sample listings remain exclusive to destination dossiers.
- Other countries remain on the legacy renderer pending Japan approval and country-specific evidence review.
- Generated artifacts are not source files and are not committed with the feature.

- [ ] **Step 9: Commit the handoff update**

```bash
git add docs/UX_UI_PREMIUM_REVAMP_HANDOFF.md
git commit -m "docs: record Japan foreign-buyer guide pilot"
```

- [ ] **Step 10: Request independent code review**

Use `superpowers:requesting-code-review` over the complete Japan-pilot commit range. Require the reviewer to check spec alignment, source handling, legacy-country isolation, SEO/schema consistency, accessibility, responsive behaviour, analytics preservation, and test coverage. Fix all Critical and Important findings, then rerun Steps 1–7.

- [ ] **Step 11: Present the local pilot for user approval**

State the exact test count and browser checks from fresh verification. Confirm that nothing was merged, pushed, deployed, or applied to another country. Wait for explicit user approval before creating the rollout plan for country two.
