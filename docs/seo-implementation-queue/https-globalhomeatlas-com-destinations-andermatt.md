# SEO Implementation Candidate: Push near-ranking page higher: /destinations/andermatt/

## Source Issue
https://github.com/schlafen318/property-research-dashboard/issues/25

## Signal
Page is ranking around position 14.8 with 46 impressions. Add internal links, sharpen title/meta, or improve page intent match.

## Target
- Query or page: `https://globalhomeatlas.com/destinations/andermatt/`
- Recommended page: `https://globalhomeatlas.com/destinations/andermatt/`
- Kind: `near-ranking-opportunity`
- Severity: `medium`

## Proposed Implementation
- Rewrite the title tag to make `https://globalhomeatlas.com/destinations/andermatt/` or its buyer intent visible near the front.
- Rewrite the meta description with a concrete buyer promise, eligibility/risk cue, and destination-specific wording.
- Add one query-matched internal anchor pointing to `/destinations/andermatt/` from the guide hub or a closely related guide.
- Add or sharpen one FAQ that answers the exact query language without keyword stuffing.

## Acceptance Criteria
- Implement the approved title, meta, intro, FAQ, or internal-link updates in `src/build_unified_app.py`.
- Regenerate static artifacts.
- Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`.
- Run `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`.
- Leave this PR as draft unless a human approves the content changes.
- After merge, keep the source issue open as `implemented-awaiting-google` until Search Console validates CTR, impressions, or position improvement.

## Fingerprint
`gha-near-ranking-opportunity-d8e73ad3207d`

## Raw Signal
```json
{
  "clicks": 0,
  "ctr": 0,
  "impressions": 46,
  "page": "https://globalhomeatlas.com/destinations/andermatt/",
  "position": 14.826086956521738
}
```
