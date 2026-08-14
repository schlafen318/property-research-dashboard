# Vacation-Home Exact-Query Content Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align the existing vacation-home guide with the exact Search Console query `best places to buy a vacation home in the world` while preserving its factual content.

**Architecture:** Update the canonical `SEO_PAGES` registry entry rather than creating a generated override or a second page. Protect the change with source-level and rendered-page assertions, then regenerate and validate the static site.

**Tech Stack:** Python 3.11, `unittest`, static HTML generation, GitHub Pages

## Global Constraints

- Add no destinations, ownership assertions, regulatory details, statistics, dates, or URLs.
- Preserve the existing first FAQ answer verbatim.
- Keep the keyword, theme, intent, destination list, remaining FAQs, and existing internal link unchanged.
- Use the exact phrase `best places to buy a vacation home in the world` in the title, description, H1, introduction, and first FAQ question.

---

### Task 1: Protect exact-query alignment

**Files:**
- Modify: `tests/test_seo_ctr_content.py`
- Modify: `src/build_unified_app.py:240-254`

**Interfaces:**
- Consumes: `seo_page(slug)` and `build_unified_app.build_seo_page(...)`.
- Produces: canonical guide metadata and rendered HTML aligned to the exact vacation-home query.

- [ ] **Step 1: Write the failing source behavior test**

Replace the broad location-intent assertions with assertions that the exact lowercase query occurs in the title, description, H1, and first FAQ question. Render the guide and assert the phrase also appears in the visible introduction.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python3 -m unittest tests.test_seo_ctr_content.SeoCtrContentTests.test_vacation_home_page_targets_exact_world_query -v`

Expected: FAIL because the current title is `Best Locations for Vacation Homes Abroad | Global Home Atlas` and does not contain the exact query.

- [ ] **Step 3: Update the canonical source entry**

Set the title and H1 to `Best Places to Buy a Vacation Home in the World`. Set the description to `Compare the best places to buy a vacation home in the world by lifestyle use, ownership clarity, rental-rule risk, value discipline, and resale depth.` Change only the first FAQ question to `What are the best places to buy a vacation home in the world?`; retain its answer verbatim.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run: `python3 -m unittest tests.test_seo_ctr_content.SeoCtrContentTests.test_vacation_home_page_targets_exact_world_query -v`

Expected: PASS.

- [ ] **Step 5: Commit the behavior change**

Stage `src/build_unified_app.py`, `tests/test_seo_ctr_content.py`, and the regenerated target artifact, then commit `Align vacation-home guide with exact query`.

### Task 2: Verify, review, and release

**Files:**
- Verify: `src/build_unified_app.py`
- Verify: `tests/test_seo_ctr_content.py`
- Verify: `artifacts/best-places-to-buy-vacation-home-abroad/index.html`

**Interfaces:**
- Consumes: the updated canonical guide entry.
- Produces: a reviewed pull request, a successful production deployment, and a live exact-query-aligned page.

- [ ] **Step 1: Run full verification**

Run:

```bash
python3 -m unittest discover tests -v
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
git diff --check
```

Expected: all tests and verification commands pass; the target artifact contains the exact title, meta description, H1, introduction, and FAQ question.

- [ ] **Step 2: Independently review the branch**

Review `origin/main..HEAD` for unsupported claims, accidental destination or URL changes, title/description length violations, structured-data mismatch, and unrelated artifact churn. Resolve every Critical or Important finding.

- [ ] **Step 3: Publish and merge**

Push `codex/vacation-home-query-content`, open a ready pull request against `main`, and squash-merge after checks and review pass.

- [ ] **Step 4: Verify production and close the loop**

Confirm the deployment succeeds, the Google sitemap receipt reports `ok: true`, and the live page exposes the approved title, description, H1, and FAQ. Update issue #101 to `implemented-awaiting-google` with links to the PR and live page.
