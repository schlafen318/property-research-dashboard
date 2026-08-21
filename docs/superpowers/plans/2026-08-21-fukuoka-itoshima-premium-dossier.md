# Fukuoka / Itoshima Premium Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a premium, evidence-backed Fukuoka / Itoshima destination dossier that validates the reusable dossier standard before the Portugal rollout.

**Architecture:** Add an isolated premium-dossier registry in a focused module and route only `fukuoka-itoshima` through a new premium renderer in the existing static-site builder. The renderer consumes the current 10-dimension destination model and `data/listings.json`, validates the content contract, and leaves all generic destination pages unchanged.

**Tech Stack:** Python 3 static-site generator, `unittest`, HTML/CSS, JSON data, existing analytics scripts, Playwright CLI for rendered QA, GitHub Pages deployment.

**Spec:** `docs/superpowers/specs/2026-08-21-fukuoka-itoshima-premium-dossier-design.md`

## Global Constraints

- Upgrade only `fukuoka-itoshima`; every other destination keeps the existing renderer.
- Keep editorial prose between 1,800 and 2,400 words, excluding tables and references.
- Use no more than seven section-rail anchors.
- Group all 10 Atlas dimensions into five editorial lenses and show exactly one 10-row score table.
- Render three to five representative listings from `data/listings.json`; never duplicate listing values in the editorial registry.
- Use exactly three editorial images, each once, with non-empty destination-specific alt text.
- Keep references as the final article section.
- Preserve count-free Atlas calls to action and restrained semibold contextual links.
- Do not add an FAQ without destination-specific search evidence.
- Do not alter a score unless refreshed evidence justifies changing the underlying destination dataset.
- Require desktop and 390 × 844 mobile visual QA with no page overflow or browser-console errors.

---

## File structure

- Create `src/premium_destination_dossiers.py`: typed premium-dossier content contract, Fukuoka / Itoshima specification, and validation helpers. This module contains editorial content and references but no score or listing values.
- Modify `src/build_unified_app.py`: import the premium registry; route the prototype; render the premium semantic HTML, score table, listing table, navigation, schema, and CSS.
- Modify `data/listings.json`: refresh or explicitly retain three representative Fukuoka / Itoshima asking-price observations with current source checks.
- Modify `data/destinations.json` only if the documented score audit supports a model-input change; do not override score output in HTML.
- Create `tests/test_fukuoka_premium_dossier.py`: contract, rendering, data, isolation, schema, links, images, and order acceptance tests.
- Modify `docs/CONTENT_PUBLISH_READINESS_CHECKLIST.md`: add destination-dossier requirements for five-lens score coverage and dated representative listings.
- Reuse `src/site_assets/fukuoka-itoshima-coast.webp`, `src/site_assets/fukuoka-itoshima-city-access.webp`, and `src/site_assets/fukuoka-itoshima-seaside-life.webp`; create no new image unless visual review proves an existing asset unsuitable.

---

### Task 1: Define the premium dossier contract and isolation boundary

**Files:**
- Create: `src/premium_destination_dossiers.py`
- Create: `tests/test_fukuoka_premium_dossier.py`

**Interfaces:**
- Produces: `PremiumDossierSpec`, `PREMIUM_DESTINATION_DOSSIERS`, `get_premium_dossier(destination_id: str) -> PremiumDossierSpec | None`, and `validate_premium_dossier(spec: PremiumDossierSpec) -> None`.
- Consumes later: `build_destination_page(...)` uses `get_premium_dossier` to choose the renderer.

- [ ] **Step 1: Write the failing registry and validation tests**

```python
class PremiumDossierContractTests(unittest.TestCase):
    def test_only_fukuoka_uses_the_premium_registry(self) -> None:
        self.assertEqual({"fukuoka-itoshima"}, set(PREMIUM_DESTINATION_DOSSIERS))
        self.assertIsNotNone(get_premium_dossier("fukuoka-itoshima"))
        self.assertIsNone(get_premium_dossier("valencia"))

    def test_fukuoka_spec_has_the_complete_bounded_contract(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        validate_premium_dossier(spec)
        self.assertEqual(5, len(spec.lenses))
        self.assertEqual(10, len({key for lens in spec.lenses for key in lens.dimension_keys}))
        self.assertLessEqual(len(spec.nav_items), 7)
        self.assertEqual(3, len(spec.images))
        self.assertEqual("sources", spec.nav_items[-1][0])
```

- [ ] **Step 2: Run the tests and verify the contract is missing**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierContractTests -v`

Expected: import failure because `src.premium_destination_dossiers` does not exist.

- [ ] **Step 3: Implement the minimal typed contract and validation**

Use frozen dataclasses with these exact public fields:

```python
@dataclass(frozen=True)
class DossierLens:
    heading: str
    dimension_keys: tuple[str, str]
    paragraphs: tuple[str, ...]
    image_key: str | None = None

@dataclass(frozen=True)
class DossierImage:
    key: str
    src: str
    alt: str
    caption: str
    placement_class: str

@dataclass(frozen=True)
class PremiumDossierSpec:
    destination_id: str
    title: str
    description: str
    h1: str
    lede: str
    author: str
    date_published: str
    date_reviewed: str
    verdict_paragraphs: tuple[str, ...]
    lenses_intro: str
    lenses: tuple[DossierLens, ...]
    micro_locations_intro: str
    micro_locations: tuple[dict[str, str], ...]
    checklist: tuple[str, ...]
    references_intro: str
    references: tuple[dict[str, str], ...]
    images: tuple[DossierImage, ...]
    nav_items: tuple[tuple[str, str], ...]
```

`validate_premium_dossier` must raise `ValueError` for the wrong destination ID, any missing required text, a lens count other than five, repeated or incomplete dimension keys, more than seven navigation items, a final navigation item other than `sources`, an image count other than three, duplicate image keys or paths, empty alt text, fewer than three micro-locations, a checklist outside six to eight items, or absent references.

- [ ] **Step 4: Add the structural Fukuoka specification**

Add the seven nav items in this exact order:

```python
(
    ("verdict", "Verdict"),
    ("lenses", "Five destination lenses"),
    ("scores", "Atlas assessment"),
    ("listings", "Representative listings"),
    ("locations", "Where to look"),
    ("checklist", "Buyer checklist"),
    ("sources", "References"),
)
```

Add five lens dimension pairs covering `lifestyle_magnetism`, `retirement_fit`, `global_access`, `foreigner_fit`, `ownership_clarity`, `regulatory_safety`, `rental_profit`, `capital_upside`, `value_entry`, and `exit_liquidity` exactly once.

- [ ] **Step 5: Run the contract tests**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierContractTests -v`

Expected: PASS.

- [ ] **Step 6: Commit the contract**

```bash
git add src/premium_destination_dossiers.py tests/test_fukuoka_premium_dossier.py
git commit -m "Add premium destination dossier contract"
```

---

### Task 2: Research and write the Fukuoka / Itoshima editorial specification

**Files:**
- Modify: `src/premium_destination_dossiers.py`
- Modify: `tests/test_fukuoka_premium_dossier.py`
- Modify if evidence requires: `data/destinations.json`

**Interfaces:**
- Consumes: the `PremiumDossierSpec` contract from Task 1.
- Produces: publication-ready Fukuoka / Itoshima content with five lenses, four verified micro-locations, eight ordered checklist items, and authoritative references.

- [ ] **Step 1: Refresh the primary-source packet**

Open and verify the current authoritative pages that support the dossier:

- Ministry of Foreign Affairs long-stay route: `https://www.mofa.go.jp/ca/fna/page22e_000738.html`
- Ministry of Finance non-resident real-property reporting: `https://www.mof.go.jp/english/policy/international_policy/real_property/index.html`
- Ministry of Justice registration obligations: `https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html`
- MLIT property-tax overview: `https://www.mlit.go.jp/totikensangyo/totikensangyo_tk5_000071.html`
- National Tax Agency non-resident transaction tax: `https://www.nta.go.jp/about/organization/sapporo/hikyoju_gaikoku/pdf/02.pdf`
- MLIT transaction and planning systems: `https://www.mlit.go.jp/report/press/totikensangyo13_hh_000269.html`
- MLIT flood-hazard explanation: `https://www.mlit.go.jp/totikensangyo/const/sosei_const_fr3_000074.html`
- national hazard portal: `https://disaportal.gsi.go.jp/`
- Ministry of Health foreign-resident insurance guidance: `https://www.mhlw.go.jp/content/12400000/001406614.pdf`
- MLIT foreign condominium-owner guidance: `https://www.mlit.go.jp/jutakukentiku/house/content/001978284.pdf`
- Japan Tourism Agency minpaku overview: `https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html`
- JNTO Fukuoka Airport access: `https://faq.japan-travel.jnto.go.jp/en/plan/airport-access/fukuoka-airport/`
- Statistics Bureau regional consumer-price comparisons: `https://www.stat.go.jp/english/data/nenkan/74nenkan/1431-20.html`

Also verify current Fukuoka City and Itoshima City hazard, transport, healthcare-access, and planning material before making local claims. Prefer official municipal sources; do not substitute a property portal for legal or hazard guidance.

- [ ] **Step 2: Write failing behavioral tests for source coverage and content boundaries**

Test that the specification contains direct authoritative links for residence, ownership/reporting, tax, healthcare, hazards, rental rules, and airport access; that every lens contains destination-specific Fukuoka or Itoshima analysis; that the four micro-location rows have non-empty `best_for`, `daily_life`, and `diligence`; and that the checklist contains eight ordered actions.

- [ ] **Step 3: Run the source and content tests to verify they fail**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierContentTests -v`

Expected: FAIL because the structural specification does not yet contain the researched prose and complete source categories.

- [ ] **Step 4: Write the final editorial content**

Use these five headings and pairings:

1. `Live well between city and coast` — lifestyle magnetism + retirement fit.
2. `Reach Fukuoka easily—and integrate beyond the airport` — global access + foreigner fit.
3. `Own clearly, then operate locally` — ownership clarity + regulatory safety.
4. `Separate ordinary demand from a rental story` — rental profit + capital upside.
5. `Enter with discipline and preserve the exit` — value entry + exit liquidity.

Use four verified micro-location rows expected to distinguish central/waterfront Fukuoka, western Fukuoka/Meinohama, Maebaru, and the Itoshima coast. Rename or regroup them when official geography or the evidence makes the expected labels misleading.

Keep country-wide rules concise and link to the Japan retirement guide. Write buyer consequences, not score narration. Keep the full editorial word count between 1,800 and 2,400 words.

- [ ] **Step 5: Audit the 10 dimension inputs**

Compare each current dimension score and rationale with the refreshed evidence. Recalculate the weighted score using the existing model. If a model input changes, edit `data/destinations.json`, run `consolidate_destination`, and update the test fixture to the new model-derived literal. If no score changes, add a test asserting the displayed total is derived from the unchanged dataset and record the current review date in the specification.

- [ ] **Step 6: Run the content tests**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierContentTests -v`

Expected: PASS.

- [ ] **Step 7: Commit researched content and any justified model changes**

```bash
git add src/premium_destination_dossiers.py tests/test_fukuoka_premium_dossier.py data/destinations.json
git commit -m "Write Fukuoka premium dossier research"
```

Omit `data/destinations.json` from the commit when the audit supports no score change.

---

### Task 3: Refresh representative listing evidence

**Files:**
- Modify: `data/listings.json`
- Modify: `tests/test_fukuoka_premium_dossier.py`

**Interfaces:**
- Produces: `fukuoka-itoshima` listing rows consumed directly by the premium renderer.
- Required row fields: `destination_id`, `destination_name`, `property_type`, `listing_name`, `usd_price`, `local_currency`, `local_price`, `size_m2`, `usd_per_m2`, `source_name`, `source_url`, `note`, `confidence`, and `captured_date`.

- [ ] **Step 1: Write the failing listing-evidence test**

```python
def test_fukuoka_has_three_to_five_complete_listing_observations(self) -> None:
    rows = [row for row in load_json("listings.json") if row["destination_id"] == "fukuoka-itoshima"]
    self.assertGreaterEqual(len(rows), 3)
    self.assertLessEqual(len(rows), 5)
    required = {"property_type", "listing_name", "local_currency", "local_price", "usd_price", "size_m2", "usd_per_m2", "source_name", "source_url", "captured_date", "confidence", "note"}
    for row in rows:
        self.assertFalse(required - row.keys())
        self.assertTrue(all(row[field] not in (None, "") for field in required))
        self.assertEqual("JPY", row["local_currency"])
```

Add an assertion that the observations represent at least two property types and at least one practical daily-life case plus one higher-end coastal or lifestyle case.

- [ ] **Step 2: Run the listing test and verify stale evidence is caught**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierListingTests -v`

Expected: FAIL on the freshness or diversity requirement until the 2026-06-21 observations are rechecked.

- [ ] **Step 3: Recheck the three current source collections and replace weak observations**

Recheck Akiya Japan and RealEstate.co.jp source pages. Prefer direct listing URLs when stable and public; otherwise use the destination collection URL and describe the observation as a dated collection-page capture. Capture local JPY price and area from the source, record the current date, convert USD with one documented same-day basis, and recompute `usd_per_m2`.

Keep three observations when they cover a practical apartment, an ordinary house, and a higher-end coastal/lifestyle case. Add a fourth or fifth only when it materially broadens the evidence.

- [ ] **Step 4: Reconcile the visible benchmark**

Compare the refreshed sample with `price_basis`, `price_confidence`, `usd_per_m2`, and the value-entry dimension. Update the underlying destination data only when the sample and broader market evidence show a material contradiction; never calculate the destination benchmark as an unqualified mean of three listings.

- [ ] **Step 5: Run listing and destination-data tests**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierListingTests tests.test_seo_ctr_content -v`

Expected: PASS.

- [ ] **Step 6: Commit the refreshed evidence**

```bash
git add data/listings.json tests/test_fukuoka_premium_dossier.py data/destinations.json
git commit -m "Refresh Fukuoka listing evidence"
```

Omit `data/destinations.json` when the benchmark remains supported.

---

### Task 4: Route and render the premium destination page

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_fukuoka_premium_dossier.py`

**Interfaces:**
- Consumes: `get_premium_dossier`, destination dictionaries from `consolidate_destination`, destination-filtered listing rows, and the existing guide and destination collections.
- Produces: `build_premium_destination_page(dest: dict, listings: list[dict], destinations: list[dict], pages: list[dict], spec: PremiumDossierSpec) -> str`.
- Changes: `build_destination_page(...)` returns the premium renderer output when `get_premium_dossier(dest["id"])` returns a specification.

- [ ] **Step 1: Write failing rendering and isolation tests**

Assert that rendered Fukuoka HTML:

- uses `<body class="premium-dossier">`;
- contains the seven section IDs in specification order;
- contains five lens headings once;
- renders exactly 10 score rows from `decision_dimensions` with score and weight;
- derives the displayed weighted total from `dest["decision_score"]`;
- renders three to five listing rows from `data/listings.json`;
- renders one micro-location table and no micro-location cards;
- renders references last;
- contains authorship, publication and reviewed dates;
- contains Article and Breadcrumb schema;
- links to the Japan retirement guide and methodology;
- uses count-free Atlas copy.

Render Valencia through `build_destination_page` and assert it does not contain `premium-dossier` or Fukuoka sections.

- [ ] **Step 2: Run rendering tests and verify Fukuoka still uses the generic page**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierRenderingTests -v`

Expected: FAIL because the premium renderer and routing branch do not exist.

- [ ] **Step 3: Add the isolated routing branch**

At the beginning of `build_destination_page`, resolve `spec = get_premium_dossier(dest["id"])`. When present, call `validate_premium_dossier(spec)` and return `build_premium_destination_page(...)`. Otherwise continue unchanged through the existing generic renderer.

- [ ] **Step 4: Implement semantic section renderers**

Add focused helpers in `src/build_unified_app.py`:

```python
def premium_dossier_score_table(dest: dict) -> str:
    dimensions = dest.get("decision_dimensions", [])
    if len(dimensions) != 10 or len({item["key"] for item in dimensions}) != 10:
        raise ValueError(f"{dest['id']} premium dossier requires exactly 10 score dimensions")
    rows = "".join(
        f"<tr><th>{escape(item['label'])}</th><td>{float(item['score']):.1f}/5</td>"
        f"<td>{float(item['weight']) * 100:.0f}%</td><td>{escape(item['evidence'])}</td></tr>"
        for item in dimensions
    )
    return (
        '<div class="premium-table-wrap"><table class="premium-score-table">'
        '<thead><tr><th>Dimension</th><th>Score</th><th>Weight</th><th>Research read</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>'
    )

def premium_dossier_listing_table(rows: list[dict]) -> str:
    required = {"property_type", "listing_name", "local_currency", "local_price", "usd_price", "size_m2", "usd_per_m2", "source_name", "source_url", "captured_date", "confidence", "note"}
    if not 3 <= len(rows) <= 5:
        raise ValueError("premium dossier requires three to five representative listings")
    for row in rows:
        missing = required - row.keys()
        if missing or any(row[field] in (None, "") for field in required):
            raise ValueError(f"incomplete representative listing: {sorted(missing)}")
    body = "".join(
        f'<tr><th>{escape(row["listing_name"])}</th><td>{escape(row["property_type"])}</td>'
        f'<td>{float(row["local_price"]):,.0f} {escape(row["local_currency"])}</td>'
        f'<td>{money(row["usd_price"])}</td><td>{float(row["size_m2"]):,.1f} m²</td>'
        f'<td>{money(row["usd_per_m2"])}/m²</td><td><a href="{escape(row["source_url"])}" rel="noopener noreferrer">{escape(row["source_name"])}</a><br>{escape(row["captured_date"])}</td>'
        f'<td>{escape(row["confidence"])}</td><td>{escape(row["note"])}</td></tr>'
        for row in rows
    )
    return f'<div class="premium-table-wrap"><table class="premium-listing-table"><tbody>{body}</tbody></table></div>'

def premium_dossier_lenses_html(spec: PremiumDossierSpec) -> str:
    images = {item.key: item for item in spec.images}
    sections = []
    for lens in spec.lenses:
        paragraphs = "".join(f"<p>{paragraph}</p>" for paragraph in lens.paragraphs)
        figure = destination_editorial_figure_html(asdict(images[lens.image_key]), images[lens.image_key].caption, images[lens.image_key].placement_class) if lens.image_key else ""
        sections.append(f"<section class=\"premium-lens\"><h3>{escape(lens.heading)}</h3>{paragraphs}{figure}</section>")
    return f'<section class="premium-section" id="lenses"><h2>Fukuoka / Itoshima through five destination lenses</h2><p>{spec.lenses_intro}</p>{"".join(sections)}</section>'

def premium_dossier_micro_locations_html(spec: PremiumDossierSpec) -> str:
    rows = "".join(
        f'<tr><th>{escape(item["name"])}</th><td>{escape(item["best_for"])}</td><td>{escape(item["daily_life"])}</td><td>{escape(item["diligence"])}</td></tr>'
        for item in spec.micro_locations
    )
    return f'<section class="premium-section" id="locations"><h2>Where to look</h2><p>{spec.micro_locations_intro}</p><div class="premium-table-wrap"><table><tbody>{rows}</tbody></table></div></section>'

def premium_dossier_references_html(spec: PremiumDossierSpec) -> str:
    links = "".join(
        f'<li><a href="{escape(item["url"])}" rel="noopener noreferrer">{escape(item["label"])}</a></li>'
        for item in spec.references
    )
    return f'<section class="premium-section" id="sources"><h2>References and update policy</h2><p>{spec.references_intro}</p><ul>{links}</ul></section>'
```

`build_premium_destination_page` must assemble the page in this exact article order: `verdict`, `lenses`, `scores`, `listings`, `locations`, `checklist`, one compact related-research handoff, and `sources`. Its hero uses `spec.images[0]`; its article body uses the five helpers above plus an ordered checklist. It must call `head_html(...)`, premium Article schema, `primary_nav_html()`, `analytics_event_script()`, and the existing footer primitives rather than duplicating global navigation or analytics behavior.

The listing renderer must filter rows by destination ID, validate three to five complete rows, display local currency before USD, and include the asking-price disclaimer. The reference helper must generate the final article section with `id="sources"`.

- [ ] **Step 5: Extend destination schema for the premium page**

Use Article schema only for the premium renderer, adding `headline`, `description`, `datePublished`, `dateModified`, `author`, `publisher`, canonical `mainEntityOfPage`, and the existing BreadcrumbList. Leave generic destination schema behavior unchanged.

- [ ] **Step 6: Run focused rendering tests**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierRenderingTests -v`

Expected: PASS.

- [ ] **Step 7: Run generic destination regressions**

Run: `python3 -m unittest tests.test_human_readable_market_pages tests.test_seo_ctr_content -v`

Expected: PASS.

- [ ] **Step 8: Commit the renderer**

```bash
git add src/build_unified_app.py tests/test_fukuoka_premium_dossier.py
git commit -m "Render premium Fukuoka dossier"
```

---

### Task 5: Apply the premium country-guide visual system

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `tests/test_fukuoka_premium_dossier.py`
- Reuse: `src/site_assets/fukuoka-itoshima-coast.webp`
- Reuse: `src/site_assets/fukuoka-itoshima-city-access.webp`
- Reuse: `src/site_assets/fukuoka-itoshima-seaside-life.webp`

**Interfaces:**
- Consumes: premium semantic HTML and three `DossierImage` entries.
- Produces: responsive `.premium-dossier` CSS and exactly three distributed `<figure>` elements.

- [ ] **Step 1: Write failing design-system tests**

Assert that Fukuoka HTML contains:

- `.premium-dossier` scoped CSS;
- the established editorial serif and sans variables;
- a two-column hero and sticky rail desktop layout;
- a single-column mobile breakpoint;
- contained horizontal wrappers around score, listing, and micro-location tables;
- exactly one occurrence of each approved image path;
- non-empty alt text and a figcaption for each image;
- no montage, generic page cards, score bars, sticky mobile action strip, or rounded listing cards;
- a restrained `font-weight: 600` contextual-link rule rather than heavy sans-serif emphasis.

- [ ] **Step 2: Run the design tests and verify the premium styles are absent**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierDesignTests -v`

Expected: FAIL because the renderer has semantic structure but not the final premium CSS and figure placement.

- [ ] **Step 3: Implement the scoped premium CSS**

Match the country retirement guides' warm ivory, dark green, rust accent, serif headings, restrained sans body, fine rules, and square buttons. Use a destination-specific class so generic pages do not inherit the design. Keep body text at 17 pixels desktop and 16 pixels mobile, cap prose at 72 characters, and avoid horizontal page overflow.

- [ ] **Step 4: Distribute the three images**

Use one image in the hero, one after the first paired lens, and one after the second or third paired lens. Do not render an image grid or repeat an image in related content.

- [ ] **Step 5: Run design tests**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierDesignTests -v`

Expected: PASS.

- [ ] **Step 6: Commit the visual system**

```bash
git add src/build_unified_app.py tests/test_fukuoka_premium_dossier.py
git commit -m "Style premium Fukuoka dossier"
```

---

### Task 6: Complete internal links and publishing rules

**Files:**
- Modify: `src/build_unified_app.py`
- Modify: `docs/CONTENT_PUBLISH_READINESS_CHECKLIST.md`
- Modify: `tests/test_fukuoka_premium_dossier.py`
- Modify as needed: `tests/test_japan_retirement_article.py`

**Interfaces:**
- Produces: reciprocal Japan-guide/dossier links and durable dossier publishing requirements.

- [ ] **Step 1: Write failing link tests**

Assert that the premium dossier links once to the Japan retirement guide and methodology, and that the Japan retirement guide links contextually to `/destinations/fukuoka-itoshima/`. Assert there are no duplicate destination-dossier links within one section and no hard-coded Atlas destination total.

- [ ] **Step 2: Run the link tests and verify the reciprocal handoff is incomplete**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier.PremiumDossierLinkTests tests.test_japan_retirement_article -v`

Expected: FAIL on the missing or non-contextual reciprocal link.

- [ ] **Step 3: Add restrained contextual links**

Link the first substantive Fukuoka / Itoshima destination mention in the Japan guide to the dossier. Use one compact `Continue your research` handoff near the end of the dossier for the Japan guide, methodology, and relevant comparisons; do not add four repeated card groups.

- [ ] **Step 4: Extend the publishing checklist**

Add two checklist items:

- destination dossiers map narrative analysis to all 10 score dimensions without creating 10 repetitive prose sections;
- representative listings show source, capture date, local currency, USD comparison, size, unit price, confidence, and an asking-price disclaimer.

- [ ] **Step 5: Run link and checklist-adjacent acceptance tests**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier tests.test_japan_retirement_article -v`

Expected: PASS.

- [ ] **Step 6: Commit links and rules**

```bash
git add src/build_unified_app.py docs/CONTENT_PUBLISH_READINESS_CHECKLIST.md tests/test_fukuoka_premium_dossier.py tests/test_japan_retirement_article.py
git commit -m "Connect premium dossier research paths"
```

---

### Task 7: Run complete build and rendered QA

**Files:**
- Generated only: `artifacts/destinations/fukuoka-itoshima/index.html`
- QA output only: `output/playwright/fukuoka-premium-dossier-desktop.png`
- QA output only: `output/playwright/fukuoka-premium-dossier-mobile.png`

**Interfaces:**
- Consumes: the completed implementation.
- Produces: verification evidence; generated artifacts and screenshots remain uncommitted unless repository policy says otherwise.

- [ ] **Step 1: Run the focused dossier suite**

Run: `python3 -m unittest tests.test_fukuoka_premium_dossier -v`

Expected: PASS with zero failures.

- [ ] **Step 2: Run the complete automated suite**

Run: `python3 -m unittest discover -s tests`

Expected: PASS with zero failures.

- [ ] **Step 3: Build the static site**

Run: `python3 src/build_unified_app.py`

Expected: exit 0 and generated `artifacts/destinations/fukuoka-itoshima/index.html`.

- [ ] **Step 4: Check generated structure and links**

Verify the generated page contains the premium body class, seven anchors, five lenses, 10 score rows, three-to-five listing rows, three images, Article schema, the Japan-guide link, and references last. Verify every internal page target exists in `artifacts/` and every source URL is syntactically valid.

- [ ] **Step 5: Run desktop visual QA**

Serve `artifacts/` locally. At the normal 1453 × 1237 review viewport, inspect the hero, line length, sticky rail, score table, listing table, micro-location table, image crops, captions, checklist, references, and footer. Save `output/playwright/fukuoka-premium-dossier-desktop.png`.

- [ ] **Step 6: Run mobile visual QA**

At 390 × 844, verify no horizontal page overflow, body copy is at least 16 pixels, navigation is compact, tables scroll only inside their wrappers, image crops remain useful, and no text clips. Save `output/playwright/fukuoka-premium-dossier-mobile.png`.

- [ ] **Step 7: Check browser console and destination links**

Expected: zero console errors or warnings caused by the page; all internal dossier, Japan-guide, methodology, and Atlas links return HTTP 200 locally.

- [ ] **Step 8: Check the final diff**

Run: `git diff --check`

Expected: no output and exit 0. Confirm generated `artifacts/**` and `output/playwright/**` remain outside the commit.

---

### Task 8: Publish and verify the prototype

**Files:**
- No additional source files unless deployment verification reveals a defect.

**Interfaces:**
- Produces: merged production revision and live Fukuoka / Itoshima dossier URL.

- [ ] **Step 1: Push the implementation branch and open a pull request**

Include the premium dossier scope, research sources, score/listing audit outcome, isolated-renderer guarantee, and verification evidence in the PR description.

- [ ] **Step 2: Confirm security and repository checks**

Do not merge with a failing required check. When no automated site checks exist, cite the fresh full-suite, build, and visual evidence.

- [ ] **Step 3: Squash-merge and monitor GitHub Pages deployment**

Expected: build, deploy, and sitemap-notification jobs complete successfully.

- [ ] **Step 4: Verify the live page**

Fetch the cache-busted production URL and confirm HTTP 200, premium body class, five lenses, 10 score rows, listing evidence, three images, count-free Atlas copy, and references last.

- [ ] **Step 5: Open the live dossier for user review**

The user review is the rollout gate. Do not start Portugal until the user approves the Fukuoka / Itoshima information density, scoring, listings, design consistency, and mobile behavior.
