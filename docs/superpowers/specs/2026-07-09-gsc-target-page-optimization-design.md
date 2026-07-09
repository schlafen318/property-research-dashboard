# GSC Target Page Optimization Design

## Context

Search Console data refreshed on 2026-07-09 shows early impressions but low CTR for a small set of pages. The strongest actionable signals are:

- `/best-places-to-buy-vacation-home-abroad/`: 107 impressions, 0 clicks, average position 32.2.
- `/destinations/andermatt/`: 61 impressions, 0 clicks, average position 14.9.
- `/destinations/annecy/`: 25 impressions, 0 clicks, average position 8.6.

The query set includes vacation-home phrases such as `best country to buy a vacation home` and `best locations for vacation homes`, plus destination-specific real-estate phrases for Andermatt. The site already has these pages indexed or visible in Search Console, so this batch should tune existing pages rather than add new URLs.

## Goal

Improve query match, click-through potential, and internal routing for the three GSC target pages without changing URLs, canonicals, schema structure, or the sitemap URL count.

## Non-Goals

- Do not create new landing pages.
- Do not rename or remove existing URLs.
- Do not make legal, tax, visa, rental-income, or guaranteed-return claims.
- Do not broaden this batch to unrelated pages.

## Approach

Make targeted template and data updates in `src/build_unified_app.py`, then regenerate `artifacts/`. Use existing destination data, existing guide page structures, and existing tracking conventions.

## Page Changes

### Vacation-Home Guide

Tune the vacation-home guide for the language Google is already testing:

- Improve title, description, H1, or intro copy around `best country/place/location to buy a vacation home`.
- Add a compact `Quick Answer` block near the top of the page.
- Surface top vacation-home destinations with concise rationale and links.
- Include Andermatt and Annecy as relevant Alpine/lifestyle comparison options where supported by existing destination data.

### Andermatt Destination Page

Add a destination-specific query-match block that helps users who arrive from `andermatt real estate` or `andermatt switzerland real estate` queries. The block should explain how to evaluate Andermatt through the Atlas model, link to relevant guides, and preserve research caveats.

### Annecy Destination Page

Add a destination-specific query-match block for users evaluating Annecy as a vacation-home or second-home market. The block should use existing destination facts, link to relevant guides, and avoid unsupported transaction claims.

## Tracking

Use existing `data-track` and `data-track-label` attributes for new internal links and shortlist-review links.

## Verification

Run:

- `python3 src/build_unified_app.py`
- `python3 scripts/verify_static_site.py --min-sitemap-urls 65`
- `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`

Also scan generated pages for:

- `Quick Answer` on `/best-places-to-buy-vacation-home-abroad/`
- `Andermatt real estate` on `/destinations/andermatt/`
- `Annecy vacation home` on `/destinations/annecy/`

## Rollout

Ship this as one focused SEO optimization batch. After deployment, refresh Search Console in 7 days and compare impressions, CTR, and average position for the same three pages.
