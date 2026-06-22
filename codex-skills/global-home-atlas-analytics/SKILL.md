---
name: global-home-atlas-analytics
description: Track Global Home Atlas SEO, Search Console, sitemap, indexing, conversion, and analytics health. Use when Codex is asked to monitor site analytics, generate weekly SEO reports, check sitemap/indexing status, verify tracking or conversion events, review GA4/Bing setup, or recommend next analytics actions for globalhomeatlas.com.
---

# Global Home Atlas Analytics

## Scope

Use this skill for recurring analytics operations on the Global Home Atlas static site.

Core assets in the repo:

- Site generator: `src/build_unified_app.py`
- Search Console report script: `scripts/seo_monitor.py`
- Generated site: `artifacts/`
- Live sitemap: `https://globalhomeatlas.com/sitemap.xml`
- Search Console property: `sc-domain:globalhomeatlas.com`
- OAuth token path, if available: `tmp/globalhomeatlas-google-token.json`

## Standard Workflow

1. Check repo state first:

```bash
git status --short --branch
```

2. Run the analytics report:

```bash
python3 scripts/seo_monitor.py --write
```

3. Verify generated tracking coverage:

```bash
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
```

4. Review the report written under `output/seo/`.

5. Summarize:

- Sitemap URL count and errors/warnings
- Whether Search Console returned query/page data
- Top query and page movements, if available
- Pages with impressions but low CTR
- Tracking/conversion coverage status
- Recommended next action

## Tracking Expectations

The site should maintain:

- 40 live sitemap URLs unless new content is added
- First-party event queue on every generated page: `gha_event_queue`
- `window.GHA.track` on every generated page
- Contact intake form on `/contact/#custom-shortlist`
- Homepage conversion section: `#conversion`
- Events for `dashboard_open`, `guide_click`, `destination_click`, `compare_selection`, `memo_shortlist_add`, `memo_shortlist_remove`, `memo_export`, `data_export_json`, `data_export_csv`, `outbound_listing_click`, and `custom_shortlist_submit`

GA4 and Bing are optional external configuration values:

- `GA4_MEASUREMENT_ID`
- `BING_SITE_VERIFICATION`
- `CONTACT_EMAIL`

If GA4 is not configured, do not treat that as a site failure. The first-party event queue still proves the tracking layer is present; report GA4 as an external setup gap.

## Live Checks

Use network access when live verification is requested or needed:

```bash
curl -s https://globalhomeatlas.com/ | rg "gha_event_queue|compare_selection|memo_export"
curl -s https://globalhomeatlas.com/contact/ | rg "custom-shortlist-form|custom_shortlist_submit"
```

If the sitemap changes, submit it through Search Console using `scripts/seo_monitor.py` for status and the existing Google API setup where available.

## Reporting Standard

Keep the final analytics summary concise and decision-oriented. Include concrete dates, counts, and file paths. Distinguish:

- Implemented and verified
- Live but waiting for Google data
- External setup still required
- Recommended next build or operating action
