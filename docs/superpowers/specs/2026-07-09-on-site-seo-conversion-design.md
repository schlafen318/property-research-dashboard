# On-Site SEO Conversion Design

## Context

Global Home Atlas has started getting indexed by Google. The current static build already publishes sitemap and robots files, canonical tags, structured data, country hubs, destination pages, SEO guide pages, a guide hub, a shortlist-review page, and optional GA4 tracking. The repo also includes Search Console and IndexNow monitoring scripts, so the next highest-leverage work is to strengthen the indexed pages and their conversion paths without changing URLs.

## Goal

Improve the first indexed pages so they are easier for Google to understand, easier for buyers to navigate, and more likely to send qualified users into the dashboard or shortlist-review flow.

## Non-Goals

- Do not remove or rename existing indexed URLs.
- Do not add a large batch of new pages before Search Console query data indicates which clusters are working.
- Do not introduce a new framework or deployment surface.
- Do not make legal, tax, visa, or guaranteed-return claims beyond the existing research caveats.

## Approach

Make targeted template changes in `src/build_unified_app.py`, then regenerate `artifacts/`. Keep the generated URL set stable unless a verification step proves that an unchanged URL list is impossible. Reuse existing data structures, tracking attributes, schema helpers, and internal-link helpers wherever possible.

## Page Changes

### Guide Hub

Strengthen `/guides/` as both a crawl hub and a buyer route map. Add clearer intent groupings, priority guide links, and a compact section that routes users to the dashboard, country hubs, and shortlist review.

### SEO Guide Pages

Add a concise decision-path block near the top of each SEO guide page. The block should tell the user what to compare next and should link to relevant country hubs, related guides, the dashboard, and shortlist review. Existing titles, canonicals, FAQ schema, and page slugs should remain stable.

### Country Hubs

Add a buyer-next-step module to each country hub. It should connect the country page to the most relevant guide cluster, destination comparisons, and shortlist review. The module should be compact and should not duplicate large guide content.

## Tracking

Use the existing `data-track` and `data-track-label` patterns for new dashboard, guide, country, and shortlist-review links. This keeps future GA4 and first-party event analysis consistent with the current event model.

## Data Flow

The static builder loads destination and listing data, builds page HTML from in-file templates and helper functions, and writes generated files under `artifacts/`. The new modules should derive their links from existing `SEO_PAGES`, `COUNTRY_HUBS`, destination data, and helper functions instead of introducing separate hard-coded navigation lists when a helper can do the job.

## Error Handling

If a referenced guide or country hub is missing, the helper should omit that link instead of rendering a broken anchor. Generated page content should remain valid even when a country has fewer related destinations or guides than expected.

## Verification

Run the static build and verify:

- `python3 src/build_unified_app.py` succeeds.
- Sitemap URL count does not decrease.
- Key generated pages exist: `/guides/`, at least one SEO guide, and at least one country hub.
- Local links in generated HTML do not point to missing generated pages or assets.
- A quick text scan confirms new modules are present on the guide hub, SEO guide pages, and country hubs.

## Rollout

Ship this as a focused on-site SEO improvement. After deployment, use Search Console data to decide whether to tune existing pages or create new cluster pages.
