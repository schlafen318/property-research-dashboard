# Next 10 SEO Moves Design

## Context

Search Console data reviewed on 29 August 2026 shows 1,285 impressions, 7 clicks, 0.5% CTR, and average position 49.6 for the latest 28 days. The strongest current near-ranking pages are Crete, the Dolomites and South Tyrol, Croatia, Annecy, and the homepage. Queenstown, Thailand villa ownership, and overseas property investment need stronger intent match and authority rather than snippet-only changes.

## Goal

Increase qualified organic clicks by improving snippets on pages already near page one, strengthening content and internal authority for larger ranking opportunities, and publishing an original data asset that can earn relevant citations.

## Scope

1. Test search-focused titles and descriptions for Crete.
2. Test search-focused titles and descriptions for the Dolomites and South Tyrol.
3. Test search-focused titles and descriptions for Croatia's Istria and Dalmatia dossier.
4. Test search-focused titles and descriptions for Annecy.
5. Clarify the homepage branded and property-abroad snippet.
6. Align Queenstown with current property-market intent while preserving foreign-buyer eligibility as the controlling message.
7. Strengthen the Thailand villa page for foreign-buyer-guide intent and connect it to the Thailand country and destination cluster.
8. Strengthen the overseas-property-investment page with a concise comparison framework and relevant internal links.
9. Add deterministic contextual internal links from existing authoritative pages to the three ranking targets.
10. Publish an indexable global property market data page, a downloadable CSV derived from the repository data, and an outreach-ready campaign brief.

## Guardrails

- Do not change `/best-places-to-buy-vacation-home-abroad/` before its 28-day review on 26 September 2026.
- Do not change Andermatt, Spain, or Portugal content while their existing changes await Google.
- Do not add new legal, tax, visa, ownership, price, yield, return, or guarantee claims without existing repository evidence.
- Keep existing URLs and canonicals stable.
- Use one current year, 2026, only where the page already has current 2026 evidence.
- Preserve visible source attribution and research caveats.
- Add new routes to the sitemap, guide navigation where relevant, and static verification.

## Architecture

Metadata and editorial changes remain in the existing Python data structures and static builder. Internal links use the existing deterministic link queue. The new data page is generated from `data/destinations.json`, exposes the same comparison fields already used by the site, and publishes a CSV alongside the HTML route. Tests render real pages and assert consumer-visible metadata, content, links, canonical URLs, and sitemap/artifact behavior.

## Measurement

- Snippet tests: review after 28 days and at least 30 impressions where possible; extend low-volume tests rather than rewriting early.
- Positions 5–10: target at least 2% CTR.
- Positions 10–20: target at least 1% CTR and movement toward page one.
- Ranking pages: first milestones are Thailand below position 40, Queenstown below 15, and overseas property investment below 20.
- Data asset: track impressions, external referring domains, and assisted visits to the three ranking targets.

