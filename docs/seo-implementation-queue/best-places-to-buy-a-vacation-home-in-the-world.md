# SEO Implementation Candidate: Improve query CTR for `best places to buy a vacation home in the world`

## Source Issue
https://github.com/schlafen318/property-research-dashboard/issues/101

## Signal
Query `best places to buy a vacation home in the world` has 4 impressions, 0 clicks, 0.00% CTR, and average position 10.8. Recommended page: https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/.

## Target
- Query or page: `best places to buy a vacation home in the world`
- Recommended page: `https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/`
- Kind: `query-ctr-opportunity`
- Severity: `medium`

## Proposed Implementation
- Rewrite the title tag to make `best places to buy a vacation home in the world` or its buyer intent visible near the front.
- Rewrite the meta description with a concrete buyer promise, eligibility/risk cue, and destination-specific wording.
- Add one query-matched internal anchor pointing to `/best-places-to-buy-vacation-home-abroad/` from the guide hub or a closely related guide.
- Add or sharpen one FAQ that answers the exact query language without keyword stuffing.

## Acceptance Criteria
- Implement the approved title, meta, intro, FAQ, or internal-link updates in `src/build_unified_app.py`.
- Regenerate static artifacts.
- Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`.
- Run `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`.
- Leave this PR as draft unless a human approves the content changes.
- After merge, keep the source issue open as `implemented-awaiting-google` until Search Console validates CTR, impressions, or position improvement.

## Fingerprint
`gha-query-ctr-opportunity-6ba11e32bde0`

## Raw Signal
```json
{
  "clicks": 0,
  "ctr": 0,
  "impressions": 4,
  "match_score": 5,
  "position": 10.75,
  "query": "best places to buy a vacation home in the world",
  "recommended_actions": [
    "Rewrite the title tag to make `best places to buy a vacation home in the world` or its buyer intent visible near the front.",
    "Rewrite the meta description with a concrete buyer promise, eligibility/risk cue, and destination-specific wording.",
    "Add one query-matched internal anchor pointing to `/best-places-to-buy-vacation-home-abroad/` from the guide hub or a closely related guide.",
    "Add or sharpen one FAQ that answers the exact query language without keyword stuffing."
  ],
  "recommended_page": "https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/"
}
```
