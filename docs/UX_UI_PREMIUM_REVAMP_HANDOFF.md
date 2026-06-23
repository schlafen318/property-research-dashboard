# Global Home Atlas UX/UI Premium Revamp Handoff

## Handoff Goal

Revamp Global Home Atlas into a premium, mobile-first global property intelligence platform for affluent international buyers and investors. Improve trust, navigation, visual appeal, and page comprehension before scaling more SEO pages.

## Primary Outcome

The site should feel high-end, bespoke, and credible within the first viewport, while making country, destination, and guide navigation easier on mobile.

## Target User

Affluent global citizens evaluating where to buy a next home, second home, retirement base, or lifestyle-led investment property.

They care about:

- Credibility
- Discretion
- Jurisdictional clarity
- Long-term lifestyle fit
- Tax and ownership risk
- Exit liquidity
- Practical decision confidence

## Design Direction

Avoid generic luxury real-estate stock imagery and content-farm layouts. The site should feel like:

- Private-bank research
- Global mobility intelligence
- Bespoke atlas
- Investment memo meets lifestyle planning tool

Visual elements should include:

- Refined atlas and map motifs
- Destination coordinate details
- Data-led score visualizations
- Understated premium textures
- Editorial comparison graphics
- Elegant country and destination dossier cards

Avoid:

- Generic villa photos
- Oversized marketing fluff
- Cartoon visuals
- One-note dark blue or purple gradients
- Cluttered cards inside cards
- SEO-page feeling above the fold

## Scope

### 1. Homepage Redesign

Create a premium first impression.

Requirements:

- Show clear positioning within the first viewport.
- Add a global atlas-style destination visual.
- Surface credibility early: methodology, independent research, scoring system.
- Add clear pathways:
  - Compare Destinations
  - Explore Countries
  - Read Buying Guides

### 2. Mobile Navigation Redesign

Add polished mobile navigation that is fast to understand and hard to get lost in.

Requirements:

- Add a mobile drawer or compact mobile navigation pattern.
- Make core sections reachable within 2 taps:
  - Compare
  - Countries
  - Destinations
  - Guides
  - Methodology
  - Contact
- Add sticky page navigation for long country and destination pages.

### 3. Destination Page Redesign

Turn destination pages into property market dossiers.

Above the fold should include:

- Destination name
- Verdict
- Decision score
- Best for
- Watch-outs
- Ownership clarity
- Lifestyle and retirement fit

Add:

- Visual score bars or compact radar-style scoring.
- Buyer-fit panels.
- Trust and methodology context.

### 4. Country Hub Redesign

Make each country hub feel like a strategic briefing.

Requirements:

- Country thesis
- Top destination match
- Buyer profile
- Risk posture
- Destination comparison table
- Related guides
- Internal links to destination pages
- Map or cluster visual treatment

### 5. Guide Hub Redesign

Make guides easier to scan and use as a decision pathway.

Group guides by intent:

- Getting Started
- Retirement
- Second Homes
- Risk
- Country Selection
- Investment

Also add:

- Country hub links
- Priority guide calls to action

### 6. Trust Layer

Add a reusable credibility module across homepage, country pages, and destination pages.

It should include:

- Scoring methodology
- Research standards
- Update cadence
- Not brokerage / not paid placement positioning
- Transparent limitations

Make it visible without overwhelming the user.

## Measurable Goals

- Homepage communicates the value proposition within the first viewport.
- Mobile user can reach Countries, Guides, Destinations, and Methodology within 2 taps.
- 100% of destination pages include score visualization and trust context.
- 100% of country hubs include destination comparison and buyer-fit modules.
- No mobile text overflow or incoherent layout overlap.
- Existing sitemap URL count should not decrease.
- Tracking verification must still pass.
- Lighthouse or mobile smoke check should show no major layout or accessibility regressions.
- SEO metadata and schema should remain intact.

## Implementation Guidance

Use the existing static generation system in `src/build_unified_app.py`.

Do not hand-edit generated HTML except as generated output artifacts. Update shared CSS and template components in the builder so all generated pages remain consistent.

Expected files:

- `src/build_unified_app.py`
- generated `artifacts/**/*.html`
- possibly `artifacts/sitemap.xml` only if URLs change, though this workstream should avoid adding URLs

Tracking verification should remain unchanged.

## Verification Plan

Run local checks:

```bash
python3 -m py_compile src/build_unified_app.py scripts/seo_monitor.py scripts/seo_status_dashboard.py scripts/seo_feedback_loop.py
python3 src/build_unified_app.py
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
git diff --check
```

Then verify live deployment after push:

```bash
curl -s https://globalhomeatlas.com/ | rg -n "Global Home Atlas|methodology|Countries|Guides"
curl -s https://globalhomeatlas.com/countries/spain-property/ | rg -n "Spain Property Guide|CollectionPage|Country Thesis"
curl -s https://globalhomeatlas.com/destinations/valencia/ | rg -n "Valencia|Country Context|Decision Score"
```

## Acceptance Criteria

- The site feels visibly more premium and bespoke.
- Homepage no longer feels like a plain dashboard or SEO page.
- Country and destination pages feel like decision briefings.
- Mobile navigation is clearly easier.
- SEO artifacts still pass.
- No existing indexed or submitted URLs are removed.
- Deploy succeeds and production pages reflect the redesign.

## Recommended Agent Brief

Take over the UX/UI premium revamp workstream for Global Home Atlas. Preserve all existing URLs, SEO metadata, schema, tracking, and sitemap behavior. Redesign the static templates in `src/build_unified_app.py` to create a high-end, bespoke, mobile-first global property intelligence experience for affluent international buyers.

Focus on:

- Homepage
- Mobile navigation
- Destination templates
- Country hub templates
- Guide hub
- Reusable trust and credibility modules

Generate artifacts, verify tracking, run checks, commit, push, and confirm production deploy.
