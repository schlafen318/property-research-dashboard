# Foreign-Buyer Country Guide Redesign

**Date:** 2026-08-27  
**Status:** Approved design; implementation not started  
**Pilot:** Japan  
**Rollout:** One country at a time after pilot approval

## Objective

Redesign the 17 general country property hubs as acquisition-first guides for people asking how to buy property in a country as a foreigner. The guides must be authoritative, concise, evidence-led, and visually consistent with the premium country-retirement guides and destination dossiers.

The Japan page at `/countries/japan-property/` is the pilot. No other country hub is migrated until the rendered Japan page is reviewed and approved.

## Page Roles

Each page family has one job:

- **Foreign-buyer country guide:** national acquisition eligibility, process, costs, obligations, use restrictions, and a compact destination comparison.
- **Country retirement guide:** residence, healthcare, long-term daily life, retirement capital, and retirement-location fit.
- **Destination dossier:** local lifestyle, ten-dimension assessment, neighbourhood or submarket guidance, property examples, and address-level diligence.
- **Atlas rankings and calculator:** cross-destination comparison and user-specific modelling.

Country guides must not reproduce retirement planning, sample listings, or full destination analysis. They link to those products where the reader needs deeper coverage.

## Japan Pilot Structure

The Japan pilot uses the following order:

1. **Hero**
   - H1: `Buying Property in Japan as a Foreigner`
   - One factual summary
   - Publication and update dates
   - One scenic destination image with a useful caption and descriptive alt text
2. **At a glance**
   - Can foreigners buy?
   - Does ownership create residency?
   - Is financing practical?
   - What limits short-term rentals?
3. **Can foreigners buy property in Japan?**
   - Eligibility
   - Land and building ownership
   - Material restrictions and reporting duties
4. **How the purchase works**
   - Numbered sequence from buyer checks through registration
5. **Costs and financing**
   - Acquisition costs
   - Recurring costs
   - Financing constraints
   - Sale and exit costs
6. **Rules after purchase**
   - Non-resident reporting
   - Registered owner-detail updates
   - Tax administration
   - Condominium governance
   - Short-term-rental rules
   - Management and property-level hazards
7. **Where to buy**
   - One compact comparison covering Fukuoka / Itoshima, Hakone / Izu, Hakuba, and Niseko
   - Each entry contains best use, principal diligence issue, and destination-dossier link
8. **Before making an offer**
   - Buyer checklist
9. **FAQ**
   - Questions specific to foreign purchasers
10. **References and update policy**
   - Official sources at the end

The side rail contains section navigation and one restrained Atlas link. A contextual link near the ownership/residence boundary sends retirement readers to the dedicated Japan retirement guide.

## Explicit Exclusions

Country guides do not contain:

- Sample listings or listing images
- Retirement-capital calculator blocks
- Retirement-location analysis beyond a contextual link
- Multiple destination-comparison sections
- `Country Thesis`, `Buyer Fit`, or `Recommended Premium Brief` sections
- Shortlist-review or report-sales panels
- Repeated dashboard calls to action
- Generic instructions such as “use this guide to,” “this page helps,” or descriptions of the research process
- Decorative badges, chips, duplicated metrics, or repeated summaries

Useful factual analysis remains. The exclusion applies to generic, self-referential, and process-description prose—not to substantive guidance.

## Structured Country Data

The shared renderer consumes explicit country data. Required fields are:

```python
{
    "slug": str,
    "country": str,
    "title": str,
    "description": str,
    "h1": str,
    "summary": str,
    "date_published": str,
    "date_reviewed": str,
    "hero_image": {"src": str, "alt": str, "caption": str},
    "direct_answers": [
        {"question": str, "answer": str, "source_urls": [str]},
    ],
    "eligibility_sections": [
        {"heading": str, "body": str, "source_urls": [str]},
    ],
    "purchase_steps": [
        {"heading": str, "body": str, "source_urls": [str]},
    ],
    "cost_rows": [
        {"cost": str, "when": str, "buyer_read": str, "source_urls": [str]},
    ],
    "ownership_rules": [
        {"heading": str, "body": str, "source_urls": [str]},
    ],
    "destination_ids": [str],
    "destination_reads": {
        str: {"best_for": str, "verify_first": str},
    },
    "buyer_checklist": [str],
    "faqs": [{"question": str, "answer": str, "source_urls": [str]}],
    "primary_sources": [{"label": str, "url": str}],
    "retirement_guide_slug": str | None,
}
```

The exact in-code representation may use typed structures or validated dictionaries. The semantic requirements above remain fixed.

## Validation and Failure Behaviour

The new renderer does not invent generic fallback sections. A migrated country must fail validation if it lacks:

- Four direct answers
- At least one eligibility section
- A complete purchase sequence
- Acquisition and recurring cost coverage
- Ongoing owner obligations
- One destination comparison entry per configured destination
- A practical checklist
- At least three foreign-buyer FAQs
- Authoritative sources for legal and administrative claims
- Publication and review dates
- A reciprocal retirement-guide link when a dedicated guide exists

Non-migrated countries continue using the existing renderer until their research record passes the new contract. This permits a safe country-by-country rollout without publishing partially populated pages.

## Rendering Architecture

Add a dedicated acquisition-guide renderer rather than expanding the legacy country-hub template with more conditional branches.

Responsibilities are separated as follows:

- **Country data:** reader-facing facts, sources, dates, destination reads, and links.
- **Validation:** checks required fields, source coverage, destination consistency, and prohibited duplication.
- **Renderer:** produces semantic HTML from already validated data.
- **Shared editorial design:** supplies typography, hero, rail, tables, mobile cards, focus states, and responsive behaviour.
- **Build routing:** chooses the acquisition renderer only for migrated country records; other country hubs remain unchanged.

The renderer uses open `<section>` elements. It does not use `<details>` accordions for core article content.

## SEO Contract

### Search intent

The acquisition guide targets queries such as:

- buying property in Japan as a foreigner
- can foreigners buy property in Japan
- Japan property ownership for foreigners
- Japan property buying process and costs

The retirement guide targets retirement property, residence, healthcare, and retirement-life queries. Destination dossiers target local place and property-market queries.

### URL and metadata

- Preserve the existing canonical route: `/countries/japan-property/`
- Use the approved acquisition-focused H1
- Keep the title and meta description within practical search-display lengths
- Use one canonical tag and self-referential Open Graph URL
- Avoid retirement-led language in the country-guide title and description

### Structured data

Emit:

- `BreadcrumbList`
- `Article` or the existing site-wide editorial article type
- `FAQPage` when visible FAQs are present
- `ItemList` for the destination comparison when supported cleanly by the existing schema helpers

Structured data must match visible page content. Do not add FAQ or destination entries that are absent from the rendered page.

### Internal linking

- Country browsing and country-comparison pages link to the acquisition guide.
- Retirement pathways link to the retirement guide.
- The acquisition guide links once to the retirement guide at the residence boundary and may include it once in related research.
- The retirement guide links contextually back to the acquisition guide.
- Destination rows link to their dossiers.
- Destination dossiers link back to the country guide where useful.
- Anchor text describes the destination or intent; avoid generic repeated `read more` links.

## Editorial Rules

- Lead sections with a direct answer.
- Prefer short paragraphs, numbered steps, checklists, and simple tables.
- State country rules before market commentary.
- Distinguish ownership, immigration, tax residence, financing, and permitted use.
- Separate national rules from municipality, building, and property-level checks.
- Use exact dates for temporary rules and policy changes.
- Label estimates and ranges as such.
- Do not present asking prices as transaction evidence.
- Avoid investment-performance promises.
- References appear only at the end, while contextual source links may appear with the claims they support.
- Use primary government and regulatory sources for legal, tax, immigration, registration, and administrative claims.
- Use secondary sources only for non-authoritative market context, with clear attribution.

## Visual Design

The acquisition guides inherit the premium editorial language of the retirement guides and destination dossiers:

- Serif display headings with regular or medium weight
- Readable sans-serif body text
- Warm paper background, dark ink, restrained accent colour
- One editorial hero image
- Sticky `In this guide` rail on wide screens
- Single-column article flow on mobile
- Simple rules instead of card-heavy boxes
- Responsive tables that become accessible mobile cards when necessary
- Minimum 44px interactive targets on mobile
- WCAG AA contrast for normal text
- No horizontal overflow at supported breakpoints

## Japan Evidence Basis

The Japan pilot must use current authoritative sources for at least:

- Foreign ownership and non-resident acquisition reporting
- Registration and owner-detail obligations
- Purchase and recurring property taxes
- Real-estate transaction and registration process
- Condominium governance and disclosure
- National private-lodging rules and applicable local overlays
- Hazard information used in property diligence
- Immigration separation where the retirement guide is linked

Existing Japan retirement-guide research may be reused only when the underlying source directly supports an acquisition-guide claim. The prose must be rewritten for acquisition intent rather than copied.

## Testing and Review Gates

### Automated tests

- Country data validation fails on each missing required field.
- Japan uses the new renderer while an unmigrated country still uses the legacy renderer.
- H1, title, description, canonical, dates, section order, and source section are correct.
- Prohibited sections and sample listings are absent.
- Exactly one destination comparison is present.
- All configured Japan destinations link to their dossiers.
- Japan and its retirement guide link to one another.
- Visible FAQs match `FAQPage` schema.
- Destination comparison matches `ItemList` schema when emitted.
- Mobile design contracts include 44px targets and responsive comparison treatment.
- Full repository suite passes.

### Browser review

Review the locally rendered Japan pilot at desktop and mobile widths for:

- Clear acquisition-first hierarchy
- Concise text and absence of generic prose
- Readable tables, steps, and checklist
- Correct sticky-rail behaviour
- Image quality and cropping
- Link and keyboard usability
- No overflow or clipped text

### Editorial review

Confirm every legal and administrative claim against its cited source and record the review date. The page cannot be called publish-ready until this review and browser QA pass.

## Rollout

1. Implement and locally render Japan.
2. Run automated, browser, SEO, and editorial checks.
3. Obtain explicit user approval of the Japan page.
4. Update the country-guide rulebook with any lessons from the pilot.
5. Migrate one country at a time.
6. Research and validate countries without complete rule/source records before rendering them with the new template.
7. Re-run the full suite and inspect each country before proceeding to the next.

The other 16 country pages are not batch-converted from generic text. Each migration requires country-specific evidence and a reader-facing review.

## Success Criteria

The Japan pilot succeeds when:

- A foreign buyer can understand eligibility, process, costs, obligations, and market choices without reading another page.
- Retirement planning and sample listings remain clearly delegated to their dedicated pages.
- The page contains no generic filler or repeated conversion sections.
- Search engines receive a distinct acquisition-intent page with valid, visible structured data.
- The page visually belongs to the same premium editorial system as the completed retirement guides and destination dossiers.
- All automated, browser, accessibility, and editorial checks pass.
