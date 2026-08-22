# Costa Brava / Girona Premium Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Costa Brava / Girona's generic destination page with a publish-ready premium dossier that meets every hard gate and scores at least 95/100 under the canonical rule book.

**Architecture:** Add one destination-specific `PremiumDossierSpec` to the existing premium registry, preserve the canonical scores in `data/destinations.json`, and reuse the shared renderer without destination-only CSS. Refresh only Costa Brava / Girona's listing observations, add an evidence ledger and exactly three original editorial images, then validate generated HTML and production rendering.

**Tech Stack:** Python 3 dataclasses and unittest, JSON datasets, static HTML/CSS generation, ImageGen/WebP assets, browser visual QA, GitHub Actions deployment.

**Spec:** `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md`

## Global Constraints

- Preserve Costa Brava / Girona's canonical Atlas scores; prose and Atlas reads explain them but do not override them.
- Use exactly five paired lenses covering all ten decision dimensions once, three official market anchors, four micro-locations, three listing observations, three editorial images, eight checklist actions, and references last.
- Lead with the location choice: Girona city, a serviced coast town, a Baix Empordà village and a remote cove do not support the same retirement life or exit.
- Keep property ownership separate from Spanish residence, tax residence and public-healthcare eligibility.
- Treat tourist-housing permission as municipality-, building- and address-specific under the Catalan HUT framework; never make rental income necessary to the purchase case.
- Distinguish Girona city; Begur / Palafrugell / Pals; Palamós / Sant Feliu / S'Agaró / Platja d'Aro; and L'Escala / Roses / Llançà / Cadaqués.
- Prefer current Spanish, Catalan and municipal primary sources for residence, tax, tourist use, planning, hazards, transport, healthcare and market claims; listings are dated asking observations only.
- Use the shared premium renderer without decorative additions, hard-coded Atlas totals or Costa Brava-only CSS.

---

### Task 1: Lock the Costa Brava / Girona acceptance contract

**Files:**
- Create: `tests/test_costa_brava_girona_premium_dossier.py`
- Modify: the eight existing premium-dossier tests whose registry assertions enumerate reviewed destinations

**Interfaces:**
- Consumes: `get_premium_dossier`, `validate_premium_dossier`, `PREMIUM_DESTINATION_DOSSIERS`, `build_destination_page`.
- Produces: executable gates for the spec, listings, evidence ledger, images, rendering order, Atlas reads and mobile layout.

- [ ] **Step 1: Write failing contract tests**

Add tests requiring `costa-brava-girona`, exactly five lenses/all ten dimensions, three anchors, four micro-locations, three images, eight checklist actions, two orientation groups and `sources` last. Require 1,800–2,500 narrative words and locally specific mentions of Girona, Begur, Palafrugell, Pals, Palamós, Sant Feliu de Guíxols, Platja d'Aro, L'Escala, Roses and Cadaqués.

- [ ] **Step 2: Add evidence and rendering tests**

Require official Spanish and Catalan source domains, a dated evidence ledger with limitations and recheck triggers, three direct EUR listing URLs with the recorded ECB FX basis, a premium rendered sequence, ten score rows labelled `Atlas read`, three official market anchors, three images, internal Spain-guide/calculator links, references last, and no mobile-overflow regression.

- [ ] **Step 3: Verify red**

Run: `python3 -m unittest tests.test_costa_brava_girona_premium_dossier -v`

Expected: FAIL because Costa Brava / Girona is absent from the premium registry and the evidence ledger/assets do not exist.

### Task 2: Implement evidence-backed Costa Brava / Girona content

**Files:**
- Modify: `src/premium_destination_dossiers.py`
- Create: `docs/research/costa-brava-girona-evidence-ledger.md`

**Interfaces:**
- Produces: `COSTA_BRAVA_GIRONA_DOSSIER: PremiumDossierSpec`, registered as `costa-brava-girona`.

- [ ] **Step 1: Add the complete specification**

Write the verdict, five paired lenses, ten concise local Atlas reads, three official market anchors, four micro-locations, eight ordered checklist actions, source/update policy, three image declarations, two orientation groups and the standard country/Atlas handoff. Use reader-facing language and decision rules, not academic methodology prose.

- [ ] **Step 2: Bound the local market structure**

Separate Girona's rail, hospital and year-round service case from Baix Empordà village/cove car dependence, the more serviced central and southern coast, and the longer-access northern coast. Explain that coastal views, historic fabric, summer crowds, tramuntana, wildfire/flood exposure, community rules and tourist permission all require address-level checks.

- [ ] **Step 3: Add the evidence ledger**

Record claim/topic, source owner, source date/status, review date `2026-08-22`, scope, limitation and recheck trigger for residence, ownership/tax, healthcare, transport, HUT permission, planning, hazards, official market anchors, listings and FX.

- [ ] **Step 4: Verify content gates turn green except missing assets/listings**

Run: `python3 -m unittest tests.test_costa_brava_girona_premium_dossier.CostaBravaGironaDossierContractTests -v`

Expected: content and source assertions pass; asset-dependent assertions may remain red until Task 4.

### Task 3: Refresh representative listing evidence

**Files:**
- Modify: `data/listings.json`

**Interfaces:**
- Produces: exactly three current `costa-brava-girona` rows consumed by the premium listing table.

- [ ] **Step 1: Replace stale aggregate observations**

Use three direct, live cases captured 2026-08-22: the Engel & Völkers Girona Cathedral apartment at EUR 359,000 / 72 m² total surface; the Costa Brava House Sa Roda house no. 1 at EUR 850,000 / 207.47 m² useful area; and the Lucas Fox Sant Feliu / S'Agaró penthouse at EUR 420,000 / 102 m² constructed area. Record direct URLs, area bases, source names, buyer-use notes and the repository EUR/USD basis.

- [ ] **Step 2: Derive USD values independently**

Use the current literal ECB basis from `data/fx_rates.json` and calculate `usd_price` and `usd_per_m2` from the recorded EUR price and stated area. Do not mix useful and constructed area without labelling the distinction in the observation note.

- [ ] **Step 3: Verify listings**

Run: `python3 -m unittest tests.test_costa_brava_girona_premium_dossier.CostaBravaGironaListingTests -v`

Expected: PASS with three direct rows and exact arithmetic.

### Task 4: Create and install editorial imagery

**Files:**
- Create: `src/site_assets/costa-brava-girona-city-hero.webp`
- Create: `src/site_assets/costa-brava-girona-coastal-daily-life.webp`
- Create: `src/site_assets/costa-brava-girona-village-access.webp`

**Interfaces:**
- Produces: exactly three original non-montage WebP images matching the spec's hero and two lens placements.

- [ ] **Step 1: Generate one image per composition**

Generate: a restrained Girona city scene that conveys year-round walkability rather than tourism; a lived-in serviced coastal-town scene with older residents and ordinary errands; and a Baix Empordà stone-village/coast-access scene that makes car and distance trade-offs believable. Avoid text, logos, luxury-montage styling, empty postcard staging and impossible geography.

- [ ] **Step 2: Inspect each image**

Visually reject artefacts, illegible signage, implausible landmarks or over-stylised resort imagery, then install accepted WebP files under the exact asset names.

- [ ] **Step 3: Verify the complete targeted suite**

Run: `python3 -m unittest tests.test_costa_brava_girona_premium_dossier -v`

Expected: PASS.

### Task 5: Build and visually validate

**Files:**
- Generated: `artifacts/destinations/costa-brava-girona/index.html`
- QA only: desktop and 390-pixel mobile screenshots

**Interfaces:**
- Consumes: the registered spec, canonical scores, listing rows and image assets.
- Produces: verified static output ready for review.

- [ ] **Step 1: Build and run the static verifier**

Run: `python3 src/build_unified_app.py`

Run: `python3 scripts/verify_static_site.py --min-sitemap-urls 65`

- [ ] **Step 2: Inspect desktop and mobile**

At wide and exact 390 × 844 viewports, check hierarchy, body measure, image crops, sticky rail, table wrappers, captions, Atlas reads, references, no clipped text and `scrollWidth === innerWidth`.

- [ ] **Step 3: Run the complete regression suite**

Run: `python3 -m unittest discover -s tests -v`

Expected: all tests pass with no failures.

### Task 6: Score, publish and production-verify

**Files:**
- Create: `docs/research/costa-brava-girona-quality-review.md`

**Interfaces:**
- Produces: a documented 100-point review, merged revision and live verified URL.

- [ ] **Step 1: Score every rule-book category**

Record the weighted 100-point result, each hard gate, evidence counts, test/build results and visual-QA findings. Do not call the dossier 10/10 unless it scores 95–100, every hard gate passes and no category is below 80%.

- [ ] **Step 2: Commit, push and merge**

Stage only Costa Brava / Girona source, listing, test, evidence, quality-review and image files plus registry-enumeration test updates. Create a PR describing evidence boundaries and verification output, then merge after checks.

- [ ] **Step 3: Verify production**

Open the cache-busted live URL and confirm HTTP 200, premium renderer, five lenses, ten score rows, three anchors, three listing rows, all three images, count-free Atlas copy, references last, no console errors and no 390-pixel overflow.

- [ ] **Step 4: Move to the next ranked unfinished destination**

Only after production verification, inspect the next destination before making any changes.
