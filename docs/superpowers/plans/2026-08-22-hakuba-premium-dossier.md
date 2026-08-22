# Hakuba Premium Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Hakuba's generic destination page with a publish-ready premium dossier that meets every hard gate and scores at least 95/100 under the canonical rule book.

**Architecture:** Add one destination-specific `PremiumDossierSpec` to the existing premium registry, while preserving the canonical scores in `data/destinations.json` and reusing the shared renderer. Refresh only Hakuba's listing observations, add an evidence ledger and exactly three original editorial images, then validate generated HTML and production rendering without destination-specific CSS.

**Tech Stack:** Python 3 dataclasses and unittest, JSON datasets, static HTML/CSS generation, ImageGen/WebP assets, browser visual QA, GitHub Actions deployment.

**Spec:** `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md`

## Global Constraints

- Preserve Hakuba's canonical Atlas scores; prose and Atlas reads explain them but do not override them.
- Use exactly five paired lenses covering all ten decision dimensions once, three market anchors, four micro-locations, three listing observations, three editorial images, eight checklist actions, and references last.
- Lead with the Japan residence and healthcare constraint; property ownership does not create residence status.
- Distinguish Happo/Wadano, Echoland/Misorano, Iwatake, and Kamishiro/Goryu rather than presenting Hakuba as one resort market.
- Treat lodging permissions, the 180-night minpaku route, the June 2026 accommodation tax, heavy snow, road access, drainage, slope hazards, building condition, staffing and operator dependence as address-level diligence.
- Prefer current official sources for legal, tax, planning, hazard, transport, healthcare and market claims; listings are dated asking observations only.
- Use the shared premium renderer without decorative additions or Hakuba-only CSS.

---

### Task 1: Lock the Hakuba acceptance contract

**Files:**
- Create: `tests/test_hakuba_premium_dossier.py`
- Modify: the seven existing premium-dossier tests whose registry assertions enumerate reviewed destinations

**Interfaces:**
- Consumes: `get_premium_dossier`, `validate_premium_dossier`, `PREMIUM_DESTINATION_DOSSIERS`, `build_destination_page`.
- Produces: executable gates for the Hakuba spec, listings, evidence ledger, images, rendering order, Atlas reads and mobile layout.

- [ ] **Step 1: Write failing contract tests**

Add tests equivalent to the Valencia contract but requiring `hakuba`, exactly five lenses/all ten dimensions, three anchors, four micro-locations, three images, eight checklist actions, two orientation groups and `sources` last. Require 1,800–2,500 narrative words and locally specific mentions of Happo, Wadano, Echoland, Misorano, Iwatake, Kamishiro, Goryu and Hakuba Station.

- [ ] **Step 2: Add evidence and rendering tests**

Require official Japan and Hakuba source domains, a dated evidence ledger with limitations and recheck triggers, three direct JPY listing URLs with the recorded FX basis, a premium rendered sequence, ten score rows labelled `Atlas read`, three market anchors, three images, internal country/calculator links, and no mobile-overflow regression.

- [ ] **Step 3: Verify red**

Run: `python3 -m unittest tests.test_hakuba_premium_dossier -v`

Expected: FAIL because Hakuba is absent from the premium registry and the evidence ledger/assets do not exist.

### Task 2: Implement evidence-backed Hakuba content

**Files:**
- Modify: `src/premium_destination_dossiers.py`
- Create: `docs/research/hakuba-evidence-ledger.md`

**Interfaces:**
- Produces: `HAKUBA_DOSSIER: PremiumDossierSpec`, registered as `hakuba`.

- [ ] **Step 1: Add the complete Hakuba specification**

Write the verdict, five paired lenses, ten concise local Atlas reads, three public market anchors, four micro-locations, eight ordered checklist actions, source/update policy, three image declarations, two orientation groups and the standard country/Atlas handoff. Use reader-facing language and decision rules, not academic methodology prose.

- [ ] **Step 2: Add the evidence ledger**

Record claim/topic, source owner, source date/status, review date `2026-08-22`, scope, limitation and recheck trigger for residence, ownership/reporting, tax, healthcare, transport, planning, hazards, accommodation tax, market anchors, listings and FX.

- [ ] **Step 3: Verify content gates turn green except missing assets/listings**

Run: `python3 -m unittest tests.test_hakuba_premium_dossier.HakubaDossierContractTests -v`

Expected: content and source assertions pass; asset-dependent assertions may remain red until Task 4.

### Task 3: Refresh representative listing evidence

**Files:**
- Modify: `data/listings.json`

**Interfaces:**
- Produces: exactly three current `hakuba` rows consumed by the premium listing table.

- [ ] **Step 1: Replace stale aggregate observations**

Use three direct, live cases captured 2026-08-22: Misorano Forest Chalet at JPY 77,000,000 / 189 m²; Kamishiro Cozy House at JPY 78,000,000 / 101.4 m²; and Miru Residences Hakuba 207 at JPY 152,460,000 / 77 m². Record source names, direct URLs, buyer-use notes and the repository JPY/USD basis.

- [ ] **Step 2: Derive USD values independently**

Use literal FX basis `1 JPY = 0.0061994395724 USD; repository reference rate, 2026-07-22` and calculate `usd_price` and `usd_per_m2` from the recorded JPY price and usable interior area.

- [ ] **Step 3: Verify listings**

Run: `python3 -m unittest tests.test_hakuba_premium_dossier.HakubaListingTests -v`

Expected: PASS with three direct rows and exact arithmetic.

### Task 4: Create and install editorial imagery

**Files:**
- Create: `src/site_assets/hakuba-alpine-village-hero.webp`
- Create: `src/site_assets/hakuba-winter-daily-life.webp`
- Create: `src/site_assets/hakuba-green-season-access.webp`

**Interfaces:**
- Produces: exactly three original non-montage WebP images matching the spec's hero and two lens placements.

- [ ] **Step 1: Generate one image per approved composition**

Generate: a restrained year-round Hakuba village hero with the Northern Alps; a cleared winter residential street showing snow-management reality; and a green-season village/transit scene showing ordinary access. Avoid text, logos, luxury-montage styling and impossible geography.

- [ ] **Step 2: Inspect and convert each image**

Visually reject artefacts or false signage, then convert accepted outputs to WebP under the exact asset names.

- [ ] **Step 3: Verify the complete targeted suite**

Run: `python3 -m unittest tests.test_hakuba_premium_dossier -v`

Expected: PASS.

### Task 5: Build and visually validate

**Files:**
- Generated: `artifacts/destinations/hakuba/index.html`
- QA only: desktop and 390-pixel mobile screenshots

**Interfaces:**
- Consumes: the registered spec, canonical scores, listing rows and image assets.
- Produces: verified static output ready for review.

- [ ] **Step 1: Build and run the static verifier**

Run: `python3 src/build_unified_app.py`

Run: the repository's existing static-output verifier command identified from `package.json`.

- [ ] **Step 2: Inspect desktop and mobile**

At wide and 390-pixel viewports, check hierarchy, body measure, image crops, sticky rail, table scrollers, captions, Atlas reads, references, no clipped text and `scrollWidth === innerWidth`.

- [ ] **Step 3: Run the complete regression suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass with no failures.

### Task 6: Score, publish and production-verify

**Files:**
- Create: `docs/research/hakuba-quality-review.md`

**Interfaces:**
- Produces: a documented 100-point review, merged revision and live verified URL.

- [ ] **Step 1: Score every rule-book category**

Record the weighted 100-point result, each hard gate, evidence counts, test/build results and visual-QA findings. Do not call the dossier 10/10 unless it scores 95–100, every hard gate passes and no category is below 80%.

- [ ] **Step 2: Commit, push and merge**

Stage only Hakuba source, listing, test, evidence, quality-review and image files plus registry-enumeration test updates. Create a PR describing evidence boundaries and verification output, then merge after checks.

- [ ] **Step 3: Verify production**

Open the cache-busted live Hakuba URL and confirm HTTP 200, premium renderer, five lenses, ten score rows, three anchors, three listing rows, all three images, count-free Atlas copy, references last, no console errors and no 390-pixel overflow.

- [ ] **Step 4: Move to the next ranked unfinished destination**

Only after production verification, inspect Costa Brava / Girona before making any changes.
