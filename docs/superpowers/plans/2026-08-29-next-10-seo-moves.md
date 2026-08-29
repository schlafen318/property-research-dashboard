# Next 10 SEO Moves Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the approved ten-move SEO roadmap as tested static-site metadata, content, internal linking, and a citeable data asset.

**Architecture:** Keep editorial changes in the existing dossier and SEO-page data structures, route authority through the deterministic internal-link system, and generate the data asset from the canonical destination dataset. Verify behavior through rendered HTML, sitemap output, static verification, analytics coverage, and the complete unit suite.

**Tech Stack:** Python 3 standard library, static HTML generation, `unittest`, JSON and CSV artifacts, GitHub Actions deployment.

**Spec:** `docs/superpowers/specs/2026-08-29-next-10-seo-moves-design.md`

## Global Constraints

- Do not change `/best-places-to-buy-vacation-home-abroad/` before 26 September 2026.
- Do not change Andermatt, Spain, or Portugal content.
- Preserve existing URLs and canonicals.
- Reuse repository evidence; add no unsupported legal or financial claims.
- New internal links must be contextual and analytics-trackable.
- New indexable routes must appear in the sitemap and generated artifacts.

---

### Task 1: Near-ranking snippet experiments

**Files:**
- Modify: `src/premium_destination_dossiers.py`
- Modify: `src/build_unified_app.py`
- Test: `tests/test_seo_next_10.py`

**Interfaces:**
- Consumes: `PremiumDossierSpec` and the homepage static builder.
- Produces: rendered `<title>` and meta-description values for Crete, Dolomites/South Tyrol, Croatia, Annecy, and `/`.

- [ ] **Step 1: Write failing rendered-page tests** for search-focused, distinct snippets and unchanged canonicals/H1 intent.
- [ ] **Step 2: Run `python3 -m unittest tests.test_seo_next_10.NearRankingSnippetTests -v`** and confirm failures are caused by the old snippets.
- [ ] **Step 3: Update the five metadata definitions** without changing destination facts or the vacation-home route.
- [ ] **Step 4: Rerun the focused tests** and confirm they pass.
- [ ] **Step 5: Commit the snippet experiment task.**

### Task 2: Ranking-intent content for Queenstown, Thailand, and overseas investment

**Files:**
- Modify: `src/premium_destination_dossiers.py`
- Modify: `src/build_unified_app.py`
- Test: `tests/test_seo_next_10.py`

**Interfaces:**
- Consumes: existing Queenstown dossier evidence, Thailand SEO-page data, and `SEO_PAGES` rendering.
- Produces: query-aligned metadata and visible decision content for the three ranking targets.

- [ ] **Step 1: Write failing rendered-page tests** for Queenstown property-market language, Thailand foreign-buyer-guide language, and a visible overseas-investment comparison framework.
- [ ] **Step 2: Run the three focused tests** and verify expected failures.
- [ ] **Step 3: Implement the minimum metadata and visible content changes** using existing facts and caveats.
- [ ] **Step 4: Rerun the focused tests** and confirm they pass.
- [ ] **Step 5: Commit the ranking-intent task.**

### Task 3: Deterministic internal authority

**Files:**
- Modify: `data/seo_auto_internal_links.json`
- Modify: `tests/test_seo_next_10.py`

**Interfaces:**
- Consumes: existing static pages and `apply_auto_internal_links()`.
- Produces: contextual source-to-target links for Queenstown, Thailand villa ownership, and overseas property investment.

- [ ] **Step 1: Write failing rendered-page tests** that require relevant tracked links from existing country/guide pages to all three targets.
- [ ] **Step 2: Run the internal-authority tests** and verify the links are absent.
- [ ] **Step 3: Add minimal deterministic link entries** with descriptive anchors and no source overlap with protected pages.
- [ ] **Step 4: Build and rerun focused tests** to confirm links appear once and retain analytics attributes.
- [ ] **Step 5: Commit the internal-authority task.**

### Task 4: Linkable global property market data asset

**Files:**
- Modify: `src/build_unified_app.py`
- Create: `docs/seo-outreach/2026-08-29-global-property-data-campaign.md`
- Modify: `tests/test_seo_next_10.py`
- Generate: `artifacts/global-property-market-data/index.html`
- Generate: `artifacts/data/global-property-market-data.csv`
- Modify: `artifacts/sitemap.xml`

**Interfaces:**
- Consumes: `data/destinations.json` enriched by the existing scoring pipeline.
- Produces: `build_property_market_data_page(destinations) -> str`, `property_market_csv(destinations) -> str`, an indexable route, a downloadable CSV, and an outreach brief.

- [ ] **Step 1: Write failing behavior tests** for canonical metadata, methodology, destination rows, CSV headers, escaping, download link, sitemap inclusion, and artifact generation.
- [ ] **Step 2: Run the data-asset test class** and verify failures are caused by missing behavior.
- [ ] **Step 3: Implement focused HTML and CSV helpers and register generation** using only existing destination fields.
- [ ] **Step 4: Add an outreach brief** with target categories, pitch copy, qualification rules, and tracking fields; do not send messages.
- [ ] **Step 5: Generate artifacts and rerun the focused tests.**
- [ ] **Step 6: Commit the data-asset task.**

### Task 5: Release verification and integration

**Files:**
- Regenerate: `artifacts/`

**Interfaces:**
- Consumes: all prior task outputs.
- Produces: verified deployable static artifacts.

- [ ] **Step 1: Run `python3 src/build_unified_app.py`.**
- [ ] **Step 2: Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`.**
- [ ] **Step 3: Run `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`.**
- [ ] **Step 4: Run `python3 -m unittest discover -s tests`.**
- [ ] **Step 5: Review the diff against every spec item and protected-route guardrail.**
- [ ] **Step 6: Commit generated artifacts and verification-ready release state.**

