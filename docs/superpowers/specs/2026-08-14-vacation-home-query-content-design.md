# Vacation-Home Exact-Query Content Design

## Goal

Improve the existing vacation-home guide's relevance for the Search Console query `best places to buy a vacation home in the world` without adding unsupported factual claims or creating a new page.

## Signal

Search Console recorded four impressions, zero clicks, a zero-percent click-through rate, and an average position of 10.75 for the exact query. The existing guide is the correct destination, but its current title and H1 target the broader phrase `Best Locations for Vacation Homes Abroad`.

## Approaches Considered

1. **Update the canonical guide source (selected).** This is deterministic, keeps the copy in the same registry as the rest of the guide, and avoids generated-override lifecycle and stale-hash complexity.
2. **Create a manual generated-content override.** This would reuse the automated application mechanism, but would manufacture model-run metadata for a human-approved edit and introduce unnecessary cooldown semantics.
3. **Wait for the analytics queue to rediscover the query.** This preserves full automation, but the latest run did not select the low-volume query and therefore produced no draft.

## Content Changes

Only the `best-places-to-buy-vacation-home-abroad` entry in `SEO_PAGES` changes:

- Title: `Best Places to Buy a Vacation Home in the World`
- Description: `Compare the best places to buy a vacation home in the world by lifestyle use, ownership clarity, rental-rule risk, value discipline, and resale depth.`
- H1: `Best Places to Buy a Vacation Home in the World`
- Opening sentence: use the same exact-query phrase while preserving the existing comparison criteria and buyer-intent sentence.
- First FAQ question: `What are the best places to buy a vacation home in the world?`
- First FAQ answer: retain the existing answer verbatim.

The keyword, theme, intent, destination list, remaining FAQs, comparison methodology, and existing internal link remain unchanged.

## Safety and Scope

- Add no destinations, ownership assertions, regulatory details, statistics, dates, or URLs.
- Preserve all existing substantive claims and the current first FAQ answer.
- Do not create a second page for the query.
- Do not add an internal link because the guides hub already links to this guide with a vacation-home anchor.
- Keep the title and description inside the existing deterministic length limits.

## Testing

Add a focused behavior test that requires the exact query in the guide title, description, H1, rendered introduction, and first FAQ question. Verify the built HTML contains the title, meta description, H1, visible introduction, and FAQ structured data. Then run the full unit suite, static-site verification, tracking verification, and a clean diff check.

## Release

Publish the focused change through a reviewed pull request. After merge, wait for GitHub Pages deployment and its post-deploy Google sitemap submission, then confirm the live page exposes the new title, description, H1, and FAQ question. Mark source issue #101 as implemented and awaiting Google measurement.
