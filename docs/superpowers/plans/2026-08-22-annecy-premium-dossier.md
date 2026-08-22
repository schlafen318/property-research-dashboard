# Annecy Premium Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Annecy's generic accordion page with a publish-ready premium dossier that earns every hard gate in the destination rulebook before deployment.

**Architecture:** Reuse the shared `PremiumDossierSpec` data contract and premium renderer. Preserve canonical scores; supply Annecy-specific editorial inputs, official evidence, direct listing observations, and three original images through the established data and build paths.

**Tech Stack:** Python dataclasses and `unittest`, JSON listing data, static HTML generator, WebP editorial assets, browser-client QA.

**Spec:** `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md`

## Global Constraints

- Preserve `data/destinations.json` and its canonical Annecy scores.
- Use five paired lenses and 1,800–2,500 words of locally specific decision prose.
- Distinguish Annecy centre, Annecy-le-Vieux, the west shore, and the premium east shore.
- Keep residence, healthcare, ownership, copropriété, DPE, tourist letting, tax, access, hazards, value and exit as separate decisions.
- Use three bounded official Notaires market anchors, three current direct asking observations, four micro-location patterns, two orientation sequences, eight ordered checklist items, and references last.
- Use three separate original editorial images; no montage, text, logos, or tourism-advertising aesthetic.
- Do not call the page 10/10 unless automated, build, desktop, exact 390×844, image, console and production gates pass.

---

### Task 1: Encode the Annecy quality contract

**Files:**
- Create: `tests/test_annecy_premium_dossier.py`
- Modify: existing `tests/test_*premium_dossier.py` registry expectations

**Interfaces:**
- Consumes: `get_premium_dossier("annecy")`, `validate_premium_dossier(spec)` and `build_destination_page(...)`.
- Produces: 11 automated hard-gate tests and a 13-dossier registry expectation.

- [x] Write failing tests for structure, local terms, sources, ledger, anchors, Atlas reads, listings, rendering, images and mobile containment.
- [x] Run `python3 -m unittest tests.test_annecy_premium_dossier` and confirm RED from missing Annecy premium inputs.

### Task 2: Add decision-grade evidence

**Files:**
- Create: `docs/research/annecy-evidence-ledger.md`
- Modify: `data/listings.json`

**Interfaces:**
- Produces: a dated claim ledger and exactly three current EUR listing observations using `1 EUR = 1.1699 USD`.

- [x] Record scope, limits and recheck triggers for the high-stakes claims.
- [x] Replace stale rows with direct Annecy, Saint-Jorioz and Veyrier-du-Lac observations.
- [x] Run listing and ledger tests without weakening assertions.

### Task 3: Implement the Annecy premium specification

**Files:**
- Modify: `src/premium_destination_dossiers.py`

**Interfaces:**
- Produces: `ANNECY_DOSSIER`, registered under `"annecy"` and validated at module load.

- [x] Write the verdict, five paired lenses, ten Atlas reads, three anchors, four micro-locations, two orientation groups, checklist and dated references.
- [x] Register and validate the dossier.
- [x] Run the Annecy contract until all non-image gates pass.

### Task 4: Produce three original editorial images

**Files:**
- Create: `src/site_assets/annecy-city-lake-daily-life.webp`
- Create: `src/site_assets/annecy-winter-access-healthcare.webp`
- Create: `src/site_assets/annecy-west-shore-daily-life.webp`

- [x] Generate, convert and inspect three separate scenes.
- [x] Reject montage-like, postcard-only or defective output.
- [x] Run the Annecy contract; expected result is 11 passing tests.

### Task 5: Build, review, deploy and verify

**Files:**
- Generate: `artifacts/destinations/annecy/index.html`
- Create: `docs/research/annecy-quality-review.md`

- [x] Update all premium-registry expectations from 12 to 13 dossiers.
- [x] Run the full build, premium contracts, full unit suite, compile check and `git diff --check`.
- [x] Inspect desktop and exact 390×844 rendering, all images, tables, overflow and console.
- [x] Record the 100-point review only if every hard gate passes.
- [ ] Commit, merge by pull request, confirm Pages deployment and repeat production QA at a cache-busted URL.
