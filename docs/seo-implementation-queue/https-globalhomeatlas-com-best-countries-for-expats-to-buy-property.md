# SEO Implementation Candidate: Improve CTR for /best-countries-for-expats-to-buy-property/

## Source Issue
https://github.com/schlafen318/property-research-dashboard/issues/21

## Signal
Page has 56 impressions, 0.00% CTR, and average position 22.1.

## Target
- Query or page: `https://globalhomeatlas.com/best-countries-for-expats-to-buy-property/`
- Recommended page: `https://globalhomeatlas.com/best-countries-for-expats-to-buy-property/`
- Kind: `low-ctr-opportunity`
- Severity: `medium`

## Proposed Implementation
- Rewrite the title tag to make `https://globalhomeatlas.com/best-countries-for-expats-to-buy-property/` or its buyer intent visible near the front.
- Rewrite the meta description with a concrete buyer promise, eligibility/risk cue, and destination-specific wording.
- Add one query-matched internal anchor pointing to `/best-countries-for-expats-to-buy-property/` from the guide hub or a closely related guide.
- Add or sharpen one FAQ that answers the exact query language without keyword stuffing.

## Acceptance Criteria
- Implement the approved title, meta, intro, FAQ, or internal-link updates in `src/build_unified_app.py`.
- Regenerate static artifacts.
- Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`.
- Run `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`.
- Leave this PR as draft unless a human approves the content changes.
- After merge, keep the source issue open as `implemented-awaiting-google` until Search Console validates CTR, impressions, or position improvement.

## Fingerprint
`gha-low-ctr-opportunity-291df557309a`

## Raw Signal
```json
{
  "clicks": 0,
  "ctr": 0,
  "impressions": 56,
  "page": "https://globalhomeatlas.com/best-countries-for-expats-to-buy-property/",
  "position": 22.142857142857142
}
```
