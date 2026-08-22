# Mallorca Premium Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Mallorca's generic accordion page with a publish-ready premium dossier that earns every destination-rulebook gate before deployment.

**Architecture:** Reuse `PremiumDossierSpec` and the shared premium renderer. Preserve canonical scores; add Mallorca-specific editorial inputs, authoritative evidence, direct listing observations and three original images through existing build paths.

**Tech Stack:** Python dataclasses and `unittest`, JSON listings, static HTML generation, WebP assets and browser-client QA.

**Spec:** `docs/PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md`

## Global Constraints

- Preserve canonical Mallorca scores in `data/destinations.json`.
- Use five paired lenses and 1,800–2,500 words of locally specific decision prose.
- Distinguish Palma, southwest Calvià / Andratx, Sóller / Tramuntana, north Mallorca and the southeast.
- Treat residence, healthcare, ownership, rural-building legality, tourist places, water, hazards, access, value and exit as separate decisions.
- Use three bounded 2025 Registradores signals, three current direct asking observations, four micro-location patterns, two orientation sequences, eight ordered checklist items and references last.
- Use three separate original editorial images; no montage, text, logos or resort-ad aesthetic.
- Do not award 10/10 until automated, build, desktop, exact 390×844, image, console and production gates pass.

---

### Task 1: Encode the Mallorca quality contract

**Files:**
- Create: `tests/test_mallorca_premium_dossier.py`
- Modify: all existing premium registry expectations

- [x] Write failing tests for structure, local terms, sources, ledger, anchors, Atlas reads, listings, rendering, images and mobile containment.
- [x] Confirm RED is caused by missing Mallorca premium inputs rather than a baseline defect.

### Task 2: Add decision-grade evidence

**Files:**
- Create: `docs/research/mallorca-evidence-ledger.md`
- Modify: `data/listings.json`

- [x] Record source scope, limits and recheck triggers.
- [x] Replace stale benchmarks with direct Palma, Sóller and Santanyí asking observations using `1 EUR = 1.1699 USD`.
- [x] Pass listing and ledger tests without weakening assertions.

### Task 3: Implement the premium specification

**Files:**
- Modify: `src/premium_destination_dossiers.py`

- [x] Write verdict, five paired lenses, ten Atlas reads, three anchors, four micro-locations, two orientation groups, checklist and dated references.
- [x] Register and validate `MALLORCA_DOSSIER`.
- [x] Pass every non-image contract gate.

### Task 4: Produce three original editorial images

**Files:**
- Create: `src/site_assets/mallorca-palma-year-round-life.webp`
- Create: `src/site_assets/mallorca-tramuntana-access.webp`
- Create: `src/site_assets/mallorca-inland-water-daily-life.webp`

- [x] Generate, convert and visually inspect the three single-scene assets.
- [x] Pass the 11-test Mallorca contract.

### Task 5: Build, review, deploy and verify

- [x] Update the registry from 13 to 14 dossiers.
- [x] Run build, premium contracts, full suite, compile and diff checks.
- [x] Inspect desktop and exact 390×844 rendering, image loading, tables, overflow and console.
- [x] Record 100/100 only if every hard gate passes.
- [ ] Commit, merge by pull request, confirm Pages deployment and repeat public cache-busted QA.
