# Fukuoka Property Evidence and Image Variety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Fukuoka / Itoshima the acceptance page for a single, conclusion-led property section and a three-role image system, while changing the shared renderer in a backward-compatible way for the later global rollout.

**Architecture:** Preserve listing observations and official market anchors as separate evidence objects, but add an explicit ordered association in the dossier specification and render each matched anchor inside its property record. Add optional editorial roles to image specifications, enforce the new contract for Fukuoka first, and leave other dossiers renderable until the global migration plan updates them. Replace only the failing Fukuoka image; retain the two already-distinct landscape and city/access assets.

**Tech Stack:** Python 3 dataclasses and static-site generator, JSON listing data, unittest, HTML/CSS, WebP assets, ImageGen, browser visual QA.

**Spec:** `docs/superpowers/specs/2026-08-23-destination-dossier-concision-and-image-variety-design.md`

## Global Constraints

- Fukuoka must contain one property section titled “What homes cost.”
- Exactly three current property examples render once each.
- No separate “Official market anchors” heading or second three-row anchor block may render.
- Reader-facing copy must state buyer conclusions and must not describe dataset, renderer, model or section-production mechanics.
- The three images must have distinct roles: defining place, built environment or access, and decision texture.
- At least two images must work without a prominent person; “older couple walking” is not an accepted default motif.
- Direct listing and official-market sources remain accessible at the point of use.
- Desktop property records fit the content column without horizontal scrolling.
- Mobile property records remain fully labelled and readable at exactly 390×844.
- No page-level overflow or page-origin warning/error is accepted.
- Do not change Fukuoka evidence values, listing arithmetic or canonical score unless a live-source recheck proves they are stale.

---

### Task 1: Establish the Fukuoka acceptance contract

**Files:**
- Modify: `tests/test_fukuoka_premium_dossier.py`
- Modify: `src/premium_destination_dossiers.py`

**Interfaces:**
- Consumes: existing `PremiumDossierSpec`, `DossierImage`, `validate_premium_dossier()`.
- Produces: `DossierImage.role: str`, `PremiumDossierSpec.property_anchor_indexes: tuple[int | None, ...]`, and Fukuoka-specific validation coverage.

- [ ] **Step 1: Write failing specification tests**

Add assertions equivalent to:

```python
def test_fukuoka_declares_property_anchor_associations_and_image_roles(self) -> None:
    spec = get_premium_dossier("fukuoka-itoshima")
    self.assertEqual((0, 1, 2), spec.property_anchor_indexes)
    self.assertEqual(
        ["defining-place", "built-environment-access", "decision-texture"],
        [image.role for image in spec.images],
    )

def test_reader_copy_contains_conclusions_not_production_commentary(self) -> None:
    spec = get_premium_dossier("fukuoka-itoshima")
    reader_copy = " ".join((
        spec.lenses_intro,
        spec.assessment_intro,
        spec.listings_intro,
        *(paragraph for lens in spec.lenses for paragraph in lens.paragraphs),
    )).lower()
    for phrase in (
        "recorded dataset exchange basis",
        "the prose below explains",
        "complete ten-dimension assessment appears once",
        "the listings below",
    ):
        self.assertNotIn(phrase, reader_copy)
```

- [ ] **Step 2: Run the new tests and verify red**

Run:

```bash
python3 -m unittest \
  tests.test_fukuoka_premium_dossier.FukuokaPremiumDossierContractTests.test_fukuoka_declares_property_anchor_associations_and_image_roles \
  tests.test_fukuoka_premium_dossier.FukuokaPremiumDossierContractTests.test_reader_copy_contains_conclusions_not_production_commentary
```

Expected: failures because the two dataclass fields do not exist and current copy contains the prohibited phrases.

- [ ] **Step 3: Add backward-compatible specification fields**

Append these fields at the end of their dataclasses so existing positional constructors remain valid:

```python
@dataclass(frozen=True)
class DossierImage:
    key: str
    src: str
    alt: str
    caption: str
    placement_class: str
    role: str = ""

@dataclass(frozen=True)
class PremiumDossierSpec:
    # existing fields unchanged
    property_anchor_indexes: tuple[int | None, ...] = ()
```

Extend `validate_premium_dossier()`:

```python
if spec.property_anchor_indexes:
    if len(spec.property_anchor_indexes) != 3:
        raise ValueError(f"{spec.destination_id} requires three property-anchor associations")
    indexes = [index for index in spec.property_anchor_indexes if index is not None]
    if len(indexes) != len(set(indexes)) or any(index < 0 or index >= len(spec.market_anchors) for index in indexes):
        raise ValueError(f"{spec.destination_id} has invalid property-anchor associations")
```

Configure Fukuoka with `property_anchor_indexes=(0, 1, 2)` and these image roles in order: `defining-place`, `built-environment-access`, `decision-texture`.

- [ ] **Step 4: Run the specification tests**

Run the two tests from Step 2. Expected: the role/association test passes; the reader-copy test remains red until Task 3.

- [ ] **Step 5: Commit the contract**

```bash
git add src/premium_destination_dossiers.py tests/test_fukuoka_premium_dossier.py
git commit -m "Define concise property and image role contract"
```

---

### Task 2: Render one conclusion-led property section

**Files:**
- Modify: `src/build_unified_app.py:7324-7431`
- Modify: `src/build_unified_app.py:7445-7593`
- Modify: `src/build_unified_app.py:7638-7648`
- Modify: `tests/test_fukuoka_premium_dossier.py:175-210`

**Interfaces:**
- Consumes: `PremiumDossierSpec.property_anchor_indexes`, `PremiumDossierSpec.market_anchors`, three destination listing rows.
- Produces: `premium_dossier_property_records(rows: list[dict], spec: PremiumDossierSpec) -> str`.

- [ ] **Step 1: Replace the old rendering expectations with failing acceptance assertions**

Add or replace tests with:

```python
def test_property_evidence_renders_once_with_integrated_local_comparisons(self) -> None:
    self.assertEqual(1, self.fukuoka_html.count('<section class="premium-section" id="listings">'))
    self.assertIn("<h2>What homes cost</h2>", self.fukuoka_html)
    self.assertEqual(3, self.fukuoka_html.count('class="premium-property-record"'))
    self.assertEqual(3, self.fukuoka_html.count('class="premium-local-comparison"'))
    self.assertNotIn("Official market anchors", self.fukuoka_html)
    self.assertNotIn('id="official-market-anchors"', self.fukuoka_html)
    for value in (
        "121,700–132,400 JPY/m²",
        "82,900–108,500 JPY/m²",
        "7,720–41,400 JPY/m²",
    ):
        self.assertEqual(1, self.fukuoka_html.count(value))

def test_property_records_use_readable_fields_not_a_wide_desktop_table(self) -> None:
    self.assertNotIn("premium-listing-table", self.fukuoka_html)
    self.assertNotIn("<th>USD comparison</th>", self.fukuoka_html)
    for label in ("Asking price", "Area", "USD comparison", "Buyer relevance", "Local comparison", "Source"):
        self.assertIn(label, self.fukuoka_html)
```

- [ ] **Step 2: Run the rendering tests and verify red**

Run:

```bash
python3 -m unittest \
  tests.test_fukuoka_premium_dossier.FukuokaPremiumDossierPageTests.test_property_evidence_renders_once_with_integrated_local_comparisons \
  tests.test_fukuoka_premium_dossier.FukuokaPremiumDossierPageTests.test_property_records_use_readable_fields_not_a_wide_desktop_table
```

Expected: failures against the old table and separate official-anchor block.

- [ ] **Step 3: Implement editorial property records**

Replace `premium_dossier_listing_table()` and `premium_dossier_market_anchors_html()` with one helper that validates the same required listing fields, pairs `rows[i]` with `spec.market_anchors[spec.property_anchor_indexes[i]]`, and emits:

```html
<div class="premium-property-records">
  <article class="premium-property-record">
    <h3>…listing name…</h3>
    <dl>
      <div><dt>Asking price</dt><dd>…local price…</dd></div>
      <div><dt>Area</dt><dd>…size and basis…</dd></div>
      <div><dt>USD comparison</dt><dd>…USD and USD/m²…</dd></div>
      <div><dt>Buyer relevance</dt><dd>…note…</dd></div>
    </dl>
    <p class="premium-local-comparison"><strong>Local comparison:</strong> …anchor evidence and buyer read… <a>…official source…</a></p>
    <p class="premium-property-source"><a>…listing source…</a> · Captured … · …confidence… confidence</p>
  </article>
</div>
```

The helper signature is:

```python
def premium_dossier_property_records(rows: list[dict], spec: PremiumDossierSpec) -> str:
```

If an association is `None`, omit the local-comparison paragraph for that record. After the three records, render unmatched anchors once inside a single `premium-market-context` paragraph; do not render a heading or repeated anchor cards.

- [ ] **Step 4: Replace the page section and CSS**

In `build_premium_destination_page()` render:

```python
<section class="premium-section" id="listings">
  <h2>What homes cost</h2>
  <p>{escape(spec.listings_intro)}</p>
  {premium_dossier_property_records(rows, spec)}
  <p class="premium-disclaimer">Current asking evidence, not completed-sale valuations. Confirm availability, title, legal use, area, condition, fees and negotiability for the exact property.</p>
</section>
```

Remove the separate market-anchor call. Add restrained CSS using a single-column record list, two-column `dl` at desktop and one column below 700px. Do not add pills, badges or decorative summaries. Ensure `.premium-property-records` and each record have `min-width: 0` and no horizontal overflow.

- [ ] **Step 5: Run rendering and full Fukuoka tests**

```bash
python3 -m unittest tests.test_fukuoka_premium_dossier
```

Expected: property-rendering assertions pass; only the reader-copy or image/provenance tests planned later may remain red.

- [ ] **Step 6: Commit the renderer**

```bash
git add src/build_unified_app.py tests/test_fukuoka_premium_dossier.py
git commit -m "Consolidate dossier property evidence"
```

---

### Task 3: Rewrite Fukuoka process copy as conclusions

**Files:**
- Modify: `src/premium_destination_dossiers.py:76-241`
- Modify: `tests/test_fukuoka_premium_dossier.py`

**Interfaces:**
- Consumes: existing Fukuoka facts, evidence ledger and property observations.
- Produces: reader-facing `lenses_intro`, value-lens paragraph, `listings_intro`, `market_anchors_intro`, and nav label that comply with the output rule.

- [ ] **Step 1: Strengthen the failing language test**

Assert the rendered page and source copy do not contain:

```python
for phrase in (
    "recorded dataset",
    "the prose below",
    "appears once",
    "the listings below",
    "public-market check on the asking listings",
    "representative property evidence",
):
    self.assertNotIn(phrase, reader_copy)
```

Assert the property introduction contains `¥31.8 million`, `¥180 million`, `rail` and `resale`.

- [ ] **Step 2: Run the language test and verify red**

Run the language-test method. Expected: it identifies the existing workflow language.

- [ ] **Step 3: Replace the copy with decision conclusions**

Use these exact replacements:

```python
lenses_intro=(
    "Five questions determine whether the city-and-coast proposition will remain useful in ordinary life: where daily services sit, how the last mile works, what the exact property permits, whether demand survives outside peak periods, and who is likely to buy on exit."
),
```

Replace the first paragraph of the value/exit lens so it opens with the observed buyer cases but does not announce a later table:

```text
Fukuoka / Itoshima offers several entry points, but they serve different buyer pools. A rail-accessible apartment can provide lower-cost access to services but may carry weak reserves or a dated building. A newer house around Maebaru can offer practical space yet needs location and resale testing. A renovated or newly built coastal home can command a substantial lifestyle premium while reaching fewer year-round buyers. Compare the exact candidate with completed transactions in the Ministry of Land’s Real Estate Information Library and commission a property-specific assessment.
```

Set:

```python
listings_intro=(
    "The current examples run from about ¥31.8 million for a rail-accessible western-Fukuoka apartment to ¥180 million for a large coastal holiday house. Access to rail and ordinary services matters more to resale depth than proximity to the sea alone."
),
market_anchors_intro=(
    "Public land evidence confirms a steep city-to-coast gradient, but land and finished homes are not interchangeable. Building age, condition, legal area and access can outweigh the headline location."
),
```

Change the nav label from `Representative listings` to `What homes cost`.

- [ ] **Step 4: Run the complete Fukuoka test file**

```bash
python3 -m unittest tests.test_fukuoka_premium_dossier
```

Expected: all content and rendering tests pass except any intentionally pending image/provenance or visual-approval assertion.

- [ ] **Step 5: Commit the editorial rewrite**

```bash
git add src/premium_destination_dossiers.py tests/test_fukuoka_premium_dossier.py
git commit -m "Replace dossier process copy with buyer conclusions"
```

---

### Task 4: Replace the repetitive Fukuoka lifestyle image

**Files:**
- Modify: `src/site_assets/fukuoka-itoshima-seaside-life.webp`
- Modify: `artifacts/assets/fukuoka-itoshima-seaside-life.webp`
- Create: `docs/research/fukuoka-itoshima-image-provenance.md`
- Modify: `src/premium_destination_dossiers.py`
- Modify: `tests/test_fukuoka_premium_dossier.py`

**Interfaces:**
- Consumes: existing hero `fukuoka-itoshima-coast.webp` and city/access `fukuoka-itoshima-city-access.webp`.
- Produces: a distinct decision-texture image using the existing seaside-life filename to preserve country-guide references.

- [ ] **Step 1: Add a failing provenance and visual-role test**

```python
def test_fukuoka_images_are_distinct_and_auditable(self) -> None:
    spec = get_premium_dossier("fukuoka-itoshima")
    self.assertEqual(3, len({image.src for image in spec.images}))
    provenance = (ROOT / "docs/research/fukuoka-itoshima-image-provenance.md").read_text()
    for image in spec.images:
        self.assertIn(Path(image.src).name, provenance)
        with Image.open(ROOT / "src/site_assets" / Path(image.src).name) as rendered:
            self.assertEqual((1672, 941), rendered.size)
    self.assertIn("No repeated older-people-walking motif", provenance)
```

Run the test. Expected: red because the provenance record does not exist.

- [ ] **Step 2: Generate the replacement decision-texture image**

Use ImageGen with this prompt:

```text
Photorealistic editorial travel and property photograph, 16:9. A quiet coastal residential lane in Itoshima, Fukuoka Prefecture, Japan, viewed at human eye level after light rain. Show modest contemporary and older Japanese houses, a narrow road, visible roadside drainage channel, utility poles, sea-salt vegetation and a glimpse of the coast beyond. No people as the subject, no posed retirees, no montage, no text, no logos, no invented signs. Natural overcast-to-clearing light, restrained colors, architectural and infrastructure detail, premium Monocle-style documentary photography. The image should communicate that road width, drainage, salt exposure and last-mile access are part of coastal ownership.
```

Inspect the generated output. Reject it if it contains prominent people, text, logos, malformed architecture, a montage or a generic tropical-resort look. Convert/crop to 1672×941 WebP and install it under the existing seaside-life filename in both asset directories.

- [ ] **Step 3: Update alt text, caption and provenance**

Set the image metadata to:

```python
DossierImage(
    "seaside-life",
    "/assets/fukuoka-itoshima-seaside-life.webp",
    "Narrow coastal residential lane in Itoshima with roadside drainage and the sea beyond",
    "On the Itoshima coast, road width, drainage and salt exposure belong in the ownership decision.",
    "wide",
    "decision-texture",
)
```

The provenance document records all three filenames, role, original generation/source path, dimensions, rights basis and visual approval. Explicitly state that the final trio has no repeated older-people-walking motif.

- [ ] **Step 4: Run the image and Japan cross-page tests**

```bash
python3 -m unittest \
  tests.test_fukuoka_premium_dossier \
  tests.test_japan_retirement_article
```

Expected: green.

- [ ] **Step 5: Commit the image change**

```bash
git add \
  src/site_assets/fukuoka-itoshima-seaside-life.webp \
  artifacts/assets/fukuoka-itoshima-seaside-life.webp \
  docs/research/fukuoka-itoshima-image-provenance.md \
  src/premium_destination_dossiers.py \
  tests/test_fukuoka_premium_dossier.py
git commit -m "Diversify Fukuoka dossier imagery"
```

---

### Task 5: Update the reusable publishing rulebook

**Files:**
- Modify: `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md:90-220`
- Modify: `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md:430-510`
- Create: `tests/test_premium_dossier_editorial_contract.py`

**Interfaces:**
- Consumes: new single-section renderer and image-role fields.
- Produces: reusable publishing rules and a registry-level migration test that can report remaining legacy dossiers without breaking Fukuoka acceptance.

- [ ] **Step 1: Add contract tests for the rulebook and Fukuoka**

Create tests that assert the rulebook contains `What homes cost`, `defining place`, `built environment or access`, `decision texture`, `production commentary`, and `390×844`; and that the rendered Fukuoka page contains no separate official-anchor heading or prohibited process phrases.

- [ ] **Step 2: Run the new test and verify red**

```bash
python3 -m unittest tests.test_premium_dossier_editorial_contract
```

Expected: red because the old rulebook still prescribes representative property evidence plus official anchors.

- [ ] **Step 3: Rewrite the fixed anatomy and quality gates**

Update the rulebook to require:

- section 4 named `What homes cost`;
- three property records once;
- matched official evidence inside each record or one compact unmatched context paragraph;
- no separate official-anchor card/list block;
- conclusion-led copy and the prohibited-pattern list from the design spec;
- the three image roles and visual-variety rules;
- explicit provenance review of repeated human motifs;
- desktop record width and exact 390×844 mobile QA.

Keep the source-quality, legal-claim, listing currency/area, references-last and independent-review gates unchanged.

- [ ] **Step 4: Run contract and Fukuoka tests**

```bash
python3 -m unittest \
  tests.test_premium_dossier_editorial_contract \
  tests.test_fukuoka_premium_dossier \
  tests.test_japan_retirement_article
```

Expected: green.

- [ ] **Step 5: Commit the rulebook**

```bash
git add docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md tests/test_premium_dossier_editorial_contract.py
git commit -m "Codify concise dossier evidence and image variety"
```

---

### Task 6: Rebuild and verify Fukuoka as the acceptance page

**Files:**
- Modify: `artifacts/destinations/fukuoka-itoshima/index.html`
- Modify only if generated from changed inputs: direct consumer artifacts identified by `git diff --name-only`
- Create: `docs/research/fukuoka-itoshima-editorial-refresh-review.md`

**Interfaces:**
- Consumes: completed Fukuoka source, renderer, rulebook and assets.
- Produces: deployable generated page and acceptance evidence for the later all-destination rollout.

- [ ] **Step 1: Rebuild generated artifacts**

```bash
python3 src/build_unified_app.py
```

Inspect `git diff --name-only`. Stage only the intended Fukuoka page, shared consumers whose content actually changed, and already-reviewed shared source files. Preserve unrelated build side effects.

- [ ] **Step 2: Run focused tests**

```bash
python3 -m unittest \
  tests.test_premium_dossier_editorial_contract \
  tests.test_fukuoka_premium_dossier \
  tests.test_japan_retirement_article
```

Expected: all green.

- [ ] **Step 3: Perform exact browser QA**

Serve `artifacts/` locally. At exactly 390×844 and 1440×1000 verify:

- document scroll width equals viewport width;
- three property records are fully readable with every field visible;
- no wide listing table or separate official-anchor section remains;
- all three distinct images load once and serve different roles;
- the replacement Itoshima image contains no prominent walking-retiree motif;
- page-origin console warning/error count is zero;
- links to three listing sources and three official comparisons are present.

Record the measured widths, screenshots reviewed, asset dimensions and console count in the refresh-review document.

- [ ] **Step 4: Run full verification**

```bash
python3 -m unittest discover -s tests
git diff --check
git status --short
```

Expected: full suite green, diff check clean, no unstaged overlap in intended files.

- [ ] **Step 5: Request independent review and remediate findings**

Provide the reviewer the design spec, changed-source diff, generated page, exact viewport evidence, image provenance and test results. Do not mark the refresh 10/10 until Critical/Important/Minor findings are zero.

- [ ] **Step 6: Commit the acceptance build**

```bash
git add artifacts/destinations/fukuoka-itoshima/index.html docs/research/fukuoka-itoshima-editorial-refresh-review.md
git commit -m "Publish concise Fukuoka dossier acceptance page"
```

---

### Task 7: Prepare the completed-dossier rollout plan

**Files:**
- Create: `docs/superpowers/plans/2026-08-23-completed-dossier-editorial-and-image-rollout.md`

**Interfaces:**
- Consumes: accepted Fukuoka renderer contract, rulebook, tests and QA evidence.
- Produces: destination-by-destination migration batches for all previously approved dossiers and Perth before its approval.

- [ ] **Step 1: Inventory every registered dossier**

Generate a table containing destination id, current process-language hits, property-anchor matching status, three current image subjects, repeated-human-motif result, quality-review status and country handoff.

- [ ] **Step 2: Divide the rollout into reviewable batches**

Create batches of no more than four destinations, grouped only when they share no listing/source dependencies. Each destination remains independently rejectable and deployable.

- [ ] **Step 3: Write exact migration tasks**

For each destination, list the three property-to-anchor associations, exact conclusion-led introduction, exact process-language paragraphs to replace, images to retain, images to regenerate, required provenance updates, test files and generated consumers.

- [ ] **Step 4: Self-review the rollout plan**

Verify every registered dossier appears once, no placeholder language remains, every failing image has a concrete replacement brief, and every batch includes focused tests, exact mobile/desktop QA, independent review and deploy verification.

- [ ] **Step 5: Commit the rollout plan**

```bash
git add docs/superpowers/plans/2026-08-23-completed-dossier-editorial-and-image-rollout.md
git commit -m "Plan concise dossier rollout"
```
