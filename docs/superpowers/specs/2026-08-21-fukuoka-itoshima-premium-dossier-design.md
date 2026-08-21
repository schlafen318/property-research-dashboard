# Fukuoka / Itoshima Premium Destination Dossier Design

**Date:** 2026-08-21

**Status:** Proposed for user review

## Objective

Redesign the Fukuoka / Itoshima destination dossier as the prototype for a reusable premium destination-dossier system. The finished page must match the editorial quality and visual language of the Japan and Spain retirement-property guides while remaining shorter, more destination-specific, and easier to scan. It will validate the dossier standard before the system is applied country by country, beginning with Portugal.

## Success criteria

The prototype is successful when it:

- gives a foreign retirement-property buyer a clear proceed, pause, or reject view within the opening screen and first section;
- explains the destination through the same 10 decision dimensions used by the Atlas without turning the article into 10 repetitive sections;
- shows a complete, auditable 10-dimension scorecard and three to five refreshed representative listings;
- distinguishes Fukuoka's urban retirement case from Itoshima's coastal lifestyle and operating trade-offs;
- uses current primary sources for legal, administrative, healthcare, hazard, access, and rental claims;
- stays between 1,800 and 2,400 editorial words, excluding tables and references;
- renders without overflow or browser errors at the normal desktop viewport and 390-pixel mobile width;
- leaves every non-prototype destination dossier unchanged;
- is deployed and reviewed before work begins on the first Portuguese dossier.

## Scope

### In scope

- Fukuoka / Itoshima destination content, evidence, metadata, score presentation, representative listings, imagery, layout, navigation, and references.
- A reusable premium-dossier renderer and structured dossier specification that can support future destinations.
- Validation that the current Fukuoka / Itoshima scores and listing benchmarks still agree with refreshed research.
- Reuse of the three existing Fukuoka / Itoshima editorial images where they accurately support the page.
- Contextual links to the Japan retirement guide, the methodology, relevant destination comparisons, and the Atlas.

### Out of scope

- Redesigning all 37 destination dossiers in the prototype release.
- Rewriting the Japan country guide.
- Adding a new destination to the Atlas.
- Changing the global scoring methodology or dimension weights.
- Presenting listings as recommendations, verified availability, valuations, or transaction advice.
- Adding decorative score badges, listing cards, duplicated summaries, a montage, or an FAQ without demonstrated destination-specific query demand.

## Architecture

The prototype will introduce a structured premium-dossier registry keyed by destination ID. The registry will contain editorial content and presentation metadata unique to the destination: title treatment, verdict, five-lens narrative, micro-locations, checklist, references, imagery, and review date.

The existing destination data remains authoritative for:

- destination name and country;
- 10 decision dimensions, weights, scores, weighted decision score, and evidence labels;
- price basis and confidence;
- ownership, rental, yield, strengths, red flags, and related quantitative fields.

`data/listings.json` remains authoritative for representative listing observations. The renderer must filter by destination ID and must not duplicate listing data inside the editorial specification.

The destination-page builder will select the premium renderer only when the requested destination has a premium-dossier specification. All other destinations continue using the existing renderer until they are intentionally upgraded. This makes the Fukuoka prototype isolated, testable, and reversible without a site-wide design change.

Editorial snippets may contain reviewed internal or external links. All dataset-derived values must continue to be escaped by the renderer. The renderer must fail clearly during the build if a premium specification is incomplete, its scorecard does not resolve to exactly 10 decision dimensions, its listing sample falls outside the permitted range, an image is missing, or the references section cannot be placed last.

## Information architecture

The dossier will use no more than seven navigation anchors.

### 1. Editorial hero

- H1 naming Fukuoka / Itoshima and its buyer decision.
- A concise introduction explaining the urban-plus-coast proposition.
- Global Home Atlas Research Team byline, publication date, and substantive review date.
- One accurate hero image with descriptive alt text and a location-specific caption.
- No generic theme eyebrow, score badge, pill, or repeated summary panel.

### 2. Verdict and suitability

- Direct conclusion before methodology or listings.
- Who Fukuoka / Itoshima suits.
- Who should look elsewhere.
- The controlling constraint: property ownership does not establish residence, healthcare entitlement, or financing access.
- One ordered decision rule telling the reader what to verify first.

### 3. Five destination lenses

One article section will contain five editorial subsections. Each subsection explains buyer consequences and supports two score dimensions:

| Editorial lens | Atlas dimensions |
|---|---|
| Can I live well here? | Lifestyle magnetism + Retirement fit |
| Can I reach it and integrate? | Global access + Foreigner fit |
| Can I own and operate safely? | Ownership clarity + Regulatory safety |
| Can the financial case work? | Rental profit + Capital upside |
| Can I enter and eventually exit well? | Value entry + Exit liquidity |

The prose must not restate the score table. It must explain the evidence, trade-offs, and practical consequence of the paired dimensions. Country-wide visa, tax, and healthcare rules receive only the destination-specific summary needed for the decision, followed by a link to the Japan retirement guide or authoritative source.

The five lenses will distinguish at least:

- Fukuoka's compact-city services, hospitals, food, transport, and domestic demand;
- Itoshima's coast, lower-density living, car dependence, local-service variation, building condition, and hazard exposure;
- Fukuoka Airport and Hakata access against the last-mile reality of coastal Itoshima;
- Japanese-language administration and trade coordination against the area's international accessibility;
- ordinary residential demand from any seasonal or short-term-rental thesis.

### 4. Atlas assessment

Show one compact 10-row score table with:

- dimension name;
- score on the existing five-point scale;
- model weight;
- concise destination-specific rationale.

Show the weighted decision score once, with the scoring review date and a link to the methodology. Scores are comparative research inputs, not predictions. The total score must not dominate the hero.

Before publication, every current Fukuoka / Itoshima dimension will be audited. A score may change only when the refreshed evidence justifies the change. Any score change must update the underlying destination dataset rather than being overridden in page markup.

### 5. Representative property evidence

Show one simple table containing three to five listing observations selected to represent distinct buyer cases. Required fields:

- property type and descriptive location;
- local asking price;
- dated USD comparison;
- internal area;
- price per square metre;
- source and direct source link;
- capture date;
- confidence;
- short explanation of what the observation represents.

The existing three Fukuoka / Itoshima observations were captured on 2026-06-21 and must be refreshed or explicitly retained as dated historical observations after rechecking the source. The sample should cover a practical apartment, an ordinary detached-home case, and a higher-end coastal or lifestyle case when reliable evidence supports each category.

Listings are asking-price evidence only. The section must state that availability, legal status, condition, negotiability, fees, and completed transaction price have not been verified. Local currency is primary; USD uses the conversion basis recorded for the observation. No listing photography may be used without confirmed reuse rights.

The visible price basis, confidence statement, value-entry score, and listing observations must reconcile. When they do not, publication stops until the data or narrative is corrected.

### 6. Micro-location comparison

Use one compact table rather than cards. The research phase will verify a useful four-part comparison, expected to distinguish:

- central or waterfront Fukuoka;
- the western Fukuoka / Meinohama corridor;
- Maebaru and practical Itoshima daily life;
- the lower-density Itoshima coast.

Columns will be limited to micro-location, best for, daily-life character, and primary diligence. Names and claims must be verified during research; this expected grouping is not permission to publish unsupported neighborhood conclusions.

### 7. Ordered buyer checklist

Six to eight actions in decision order:

1. establish the residence and healthcare route;
2. confirm financing and total cash requirement;
3. choose the urban or coastal daily-life pattern;
4. verify title, planning, building condition, condominium governance, and access;
5. review flood, slope, typhoon, seismic, and other site-specific hazards;
6. confirm intended rental use and local operating rules;
7. price maintenance, management, tax, insurance, and currency exposure;
8. test resale demand before making a binding offer.

### 8. References and update policy

References are always the final article section. Sources must link directly to the most authoritative supporting page available. The source hierarchy is:

1. Japanese ministries, agencies, municipal bodies, official statistics, airport or transport operators, and statutory material;
2. land-registry, tax, healthcare, hazard, tourism, and administrative guidance;
3. reliable dated market statistics or transaction evidence;
4. listing portals only for asking-price observations, never for high-stakes legal claims.

The section will state the substantive review date, local-rule caveat, listing capture policy, and which claims require current professional verification.

## Editorial length and duplication controls

- Target 1,800–2,400 editorial words, excluding tables and references.
- Verdict: approximately 200–250 words.
- Five lenses combined: approximately 900–1,100 words.
- Market, listing, micro-location, and checklist introductions combined: no more than approximately 500 words outside their tables.
- Do not repeat country-guide explanations of residence, healthcare, tax, or national ownership rules.
- Do not repeat score rationales in surrounding prose.
- Use one score table, one listing table, and one micro-location table.
- Use one conclusion in the verdict; the checklist may not restate it.
- Related links appear once in a compact handoff, not as repeated promotional cards.

## Visual design

The dossier will inherit the premium country-guide visual language while remaining a distinct, shorter page type.

### Desktop

- Warm ivory editorial background, dark green ink, restrained rust accent, and the established serif/sans pairing.
- Two-column hero with large serif H1 and one tall destination image.
- Main article width optimized for 65–72 characters per line.
- Sticky right rail with no more than seven meaningful anchors and one count-free Atlas action.
- Fine rules and generous vertical spacing instead of rounded cards.
- Score, listing, and micro-location tables use simple rules, aligned numbers, readable headers, and no decorative cells.

### Mobile

- Single-column hero and article at 390 pixels without horizontal page overflow.
- Body copy at 16 pixels or larger.
- Compact menu and section navigation without a permanently occupying rail.
- Tables may use an explicit contained horizontal scroller, but labels and first columns must remain understandable.
- Images retain useful crops and captions; text must not overlap or clip.

### Typography and emphasis

- Serif display headings use medium weight, not artificial heavy bold.
- Navigation, bylines, buttons, labels, and captions use restrained sans-serif weights.
- First substantive destination or micro-location mentions may use semibold contextual links; repeated mentions in the same section remain plain.
- No bold uppercase score labels, decorative chips, montage, or repeated metadata bands.

## Imagery

Use exactly three editorial images distributed through the page:

1. hero: the city-and-coast proposition;
2. within the first two lenses: daily urban access or waterfront life;
3. later in the lenses: everyday coastal or Itoshima life.

The implementation may reuse the existing Fukuoka / Itoshima assets when their composition and captions fit the dossier:

- `fukuoka-itoshima-coast.webp`;
- `fukuoka-itoshima-city-access.webp`;
- `fukuoka-itoshima-seaside-life.webp`.

No new image will be generated merely to make the asset set different from the Japan guide. Any replacement must be geographically accurate, show a distinct editorial purpose, use descriptive alt text, and be visually reviewed before publication.

## Metadata, schema, and internal links

- Unique destination-specific title, description, H1, canonical URL, and visible introduction.
- Article schema with organization author, publisher, publication date, modified date, and canonical main entity.
- Breadcrumbs remain valid.
- No FAQ schema unless visible, destination-specific FAQs are justified by search demand.
- First substantive references to the Japan retirement guide, methodology, and related destination pages use descriptive anchors.
- The Japan retirement guide and Japan country hub should link back to the upgraded dossier where contextually useful without adding duplicate navigation blocks.
- All internal links must resolve in the generated artifact and on the deployed site.

## Error handling and publication stops

The build or acceptance suite must stop publication when:

- the premium specification is missing a required section or review date;
- the scorecard does not contain exactly the 10 decision dimensions or its displayed total disagrees with the model output;
- fewer than three or more than five representative listings are selected;
- a listing lacks source, capture date, local price, currency, property type, or confidence;
- price basis and displayed listing evidence materially contradict each other;
- an image path is missing or alt text is empty;
- references are absent or are not the final article section;
- a required internal destination, guide, methodology, or source link is broken;
- the rendered page has horizontal page overflow at the required mobile width.

If refreshed evidence is unavailable, the page must use a transparent insufficiency statement or retain a clearly dated historical observation. It must not create false precision or silently reuse stale availability language.

## Testing and verification

Implementation follows test-driven development.

### Automated acceptance tests

- Only Fukuoka / Itoshima selects the premium renderer in the prototype release.
- Section order matches this specification and references are last.
- Navigation contains no more than seven correct section anchors.
- The five editorial lenses appear once and map to all 10 dimensions.
- The score table contains exactly 10 unique dimensions, correct weights, and a model-derived total.
- Three to five listing rows render from `data/listings.json` with every required field and disclaimer.
- The micro-location table contains only verified rows and does not duplicate cards.
- Exactly three editorial images render once each with non-empty alt text.
- Authorship, dates, canonical URL, Article schema, and breadcrumbs are correct.
- Contextual links and count-free Atlas copy are present.
- Generic destination dossiers remain on their existing renderer.

### Full verification

- Complete automated test suite.
- Static-site build.
- Whitespace and generated-link checks.
- Desktop visual review at the normal application viewport.
- Mobile visual review at 390 × 844.
- Browser-console review.
- Internal and external link checks proportionate to source importance.
- Live HTTP and rendered-structure verification after deployment.

## Rollout gate

Fukuoka / Itoshima is a prototype, not an automatic site-wide launch. After deployment, the user will review:

- information density and page length;
- whether the five-lens narrative makes the 10-dimension model easier to understand;
- whether scores and listings feel evidentiary rather than promotional;
- design consistency with the Japan and Spain retirement guides;
- desktop and mobile usability.

Only after explicit approval will the premium dossier system proceed to Portugal. Portugal will then follow the agreed country-by-country sequence: inspect coverage, create or split destinations as needed, upgrade the destination set, review it, build the country guide, review it, and only then move to the next country.
