# SEO Implementation Candidate: Push near-ranking page higher: /best-places-to-buy-a-second-home-abroad/

## Source Issue
https://github.com/schlafen318/property-research-dashboard/issues/43

## Signal
Page is ranking around position 11.9 with 20 impressions. Add internal links, sharpen title/meta, or improve page intent match.

## Target
- Query or page: `https://globalhomeatlas.com/best-places-to-buy-a-second-home-abroad/`
- Recommended page: `https://globalhomeatlas.com/best-places-to-buy-a-second-home-abroad/`
- Kind: `near-ranking-opportunity`
- Severity: `medium`

## Proposed Implementation
- Rewrite the title tag to make `https://globalhomeatlas.com/best-places-to-buy-a-second-home-abroad/` or its buyer intent visible near the front.
- Rewrite the meta description with a concrete buyer promise, eligibility/risk cue, and destination-specific wording.
- Add one query-matched internal anchor pointing to `/best-places-to-buy-a-second-home-abroad/` from the guide hub or a closely related guide.
- Add or sharpen one FAQ that answers the exact query language without keyword stuffing.

## Acceptance Criteria
- Implement the approved title, meta, intro, FAQ, or internal-link updates in `src/build_unified_app.py`.
- Regenerate static artifacts.
- Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`.
- Run `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`.
- Leave this PR as draft unless a human approves the content changes.
- After merge, keep the source issue open as `implemented-awaiting-google` until Search Console validates CTR, impressions, or position improvement.

## Fingerprint
`gha-near-ranking-opportunity-28da3b13e19f`

## Raw Signal
```json
{
  "clicks": 0,
  "ctr": 0,
  "impressions": 20,
  "page": "https://globalhomeatlas.com/best-places-to-buy-a-second-home-abroad/",
  "position": 11.95
}
```
