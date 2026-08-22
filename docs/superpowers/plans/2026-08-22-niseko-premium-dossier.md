# Niseko Premium Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Niseko's generic accordion page with a publish-ready premium dossier that earns every hard gate in the destination rulebook before deployment.

**Architecture:** Reuse the shared `PremiumDossierSpec` data contract and premium renderer. Keep canonical destination scores unchanged; provide Niseko-specific editorial inputs, evidence, direct listing observations, and original image assets through existing data and build paths.

**Tech Stack:** Python dataclasses and `unittest`, JSON listing data, static HTML generator, WebP editorial assets, browser-client QA.

**Spec:** `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md`

## Global Constraints

- Preserve `data/destinations.json` and its canonical Niseko scores.
- Use five paired lenses and 1,800–2,500 words of locally specific decision prose.
- Distinguish Kutchan, Hirafu / Kabayama, Hanazono, and Niseko Village / Annupuri / Moiwa.
- Treat ownership, residence, non-resident reporting, planning, lodging permission and tax, operator contracts, healthcare, winter access, snow operations, hazards, seasonality and exit as separate decisions.
- Use three bounded 2026 MLIT bare-land anchors, three current direct residential asking observations, four micro-location patterns, two orientation sequences, eight ordered checklist items, and references last.
- Use three separate original editorial images; no montage, text, logo or resort-advertising aesthetic.
- Do not call the page 10/10 unless all automated, build, desktop, exact 390×844, image, console and production gates pass.

---

### Task 1: Encode the Niseko quality contract

**Files:**
- Create: `tests/test_niseko_premium_dossier.py`
- Modify: existing `tests/test_*premium_dossier.py` registry expectations

**Interfaces:**
- Consumes: `get_premium_dossier("niseko")`, `validate_premium_dossier(spec)` and `build_destination_page(...)`.
- Produces: 11 automated hard-gate tests and a 12-dossier registry expectation.

- [ ] **Step 1:** Add the failing contract for structure, local terms, authoritative sources, ledger, anchors, Atlas reads, listings, renderer sequence, images and mobile containment.
- [ ] **Step 2:** Run `python3 -m unittest tests.test_niseko_premium_dossier` and confirm failure is caused by missing Niseko premium inputs, ledger, refreshed listings and images.

### Task 2: Add decision-grade research and listing evidence

**Files:**
- Create: `docs/research/niseko-evidence-ledger.md`
- Modify: `data/listings.json`

**Interfaces:**
- Consumes: dated official and direct public sources.
- Produces: a claim ledger with recheck triggers and exactly three direct JPY listing rows using `1 JPY = 0.0061994395724 USD`.

- [ ] **Step 1:** Record the scope and limitations of ownership, reporting, planning, lodging, accommodation tax, access, health, hazard and 2026 MLIT price claims.
- [ ] **Step 2:** Replace stale June rows with the current Kutchan renovated house, Kizuna 202 and MUWA Niseko 501 observations.
- [ ] **Step 3:** Run the listing and ledger tests until they pass without weakening assertions.

### Task 3: Implement the Niseko premium specification

**Files:**
- Modify: `src/premium_destination_dossiers.py`

**Interfaces:**
- Consumes: `PremiumDossierSpec`, `DossierLens`, `DossierImage`, `DossierOrientationGroup`.
- Produces: `NISEKO_DOSSIER`, registered under `"niseko"`, validated at module load.

- [ ] **Step 1:** Write the verdict, five paired lenses, ten Atlas reads, three 2026 MLIT anchors, four micro-locations, two orientation groups, checklist and dated references.
- [ ] **Step 2:** Register and validate `NISEKO_DOSSIER`.
- [ ] **Step 3:** Run `python3 -m unittest tests.test_niseko_premium_dossier` and correct only production inputs until all content and rendering gates except image existence pass.

### Task 4: Produce and install three original editorial images

**Files:**
- Create: `src/site_assets/niseko-kutchan-working-town.webp`
- Create: `src/site_assets/niseko-winter-snow-operations.webp`
- Create: `src/site_assets/niseko-green-season-mobility.webp`
- Generate: matching `artifacts/assets/` copies through the site builder

**Interfaces:**
- Consumes: the three `DossierImage` paths in `NISEKO_DOSSIER`.
- Produces: separate visually inspected WebP assets with non-zero intrinsic dimensions.

- [ ] **Step 1:** Generate Kutchan working-town, residential snow-operation and green-season mobility scenes.
- [ ] **Step 2:** Convert to WebP, inspect each final file, and reject visual defects or montage-like composition.
- [ ] **Step 3:** Run `python3 -m unittest tests.test_niseko_premium_dossier`; expected result is 11 passing tests.

### Task 5: Build, review, deploy and verify

**Files:**
- Generate: `artifacts/destinations/niseko/index.html`
- Create: `docs/research/niseko-quality-review.md`

**Interfaces:**
- Consumes: all prior tasks.
- Produces: a deployed, production-verified Niseko premium dossier and a dated 100-point review only if every gate passes.

- [x] **Step 1:** Update every exact premium-registry expectation from 11 to 12 dossiers.
- [x] **Step 2:** Run `python3 src/build_unified_app.py`, premium contracts, full `unittest` discovery, `py_compile`, and `git diff --check`.
- [x] **Step 3:** Inspect desktop and exact 390×844 rendering, scroll-load all images, confirm table containment and an empty browser console.
- [x] **Step 4:** Record the weighted review; do not award 10/10 if any hard gate fails.
- [ ] **Step 5:** Commit scoped files, merge through a pull request, confirm build and Pages deploy jobs, then repeat production desktop/mobile/console QA at a cache-busted URL.
