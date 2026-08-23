# Destination dossier concision and image-variety design

Date: 2026-08-23
Status: Proposed for user review

## Purpose

Upgrade the shared premium destination-dossier system so every page presents property evidence once, speaks in reader-useful conclusions rather than production language, and uses a visually varied image set. Fukuoka / Itoshima is the first acceptance page; the approved contract then applies to every completed dossier and all future editions.

## Problems to correct

1. Property examples are discussed repeatedly. The value lens announces the listings, the listing introduction explains the data process, and official market anchors appear as a second listing-like block. Even when the facts differ, the reading experience feels duplicated.
2. Reader-facing copy sometimes describes how the page was produced rather than what the buyer should conclude. Examples include “Local asking price is primary; USD uses the recorded dataset exchange basis” and “the complete ten-dimension assessment appears once.”
3. The image set relies too often on similar lifestyle scenes, especially older people walking. Repetition makes distinct destinations feel templated and visually interchangeable.

## Reader-facing information architecture

The fixed dossier sequence remains:

1. The verdict
2. Five destination lenses
3. The Atlas assessment
4. What homes cost
5. Where to look
6. Buyer checklist
7. References and update policy

“Representative property evidence,” “Representative listings,” and “Official market anchors” will no longer appear as separate navigable concepts.

### One property section

The single property section is titled **What homes cost**. It contains:

- a two- or three-sentence conclusion stating the observed price range and what materially changes value;
- exactly three current property examples, presented once;
- the most relevant public-market comparison integrated into each example as a compact “Local comparison” field when a claim-fit official anchor exists;
- one short caveat after the examples covering asking-price status, availability, legal use, condition and valuation limits;
- direct listing and official-source links at the point of use.

Official anchors remain required evidence, but they cease to be a second visual block. If an anchor cannot be matched honestly to one example, it appears in a single compact “Market context” paragraph after the examples. The paragraph must explain a price conclusion; it must not describe the research workflow.

Other sections may state conclusions supported by the examples, but must not announce the table, repeat the three cases, or say “the listings below.”

### Property-example fields

Each example keeps only information that changes a decision:

- property and micro-location;
- local asking price;
- size and exact area basis;
- translated USD comparison and USD/m² where denominators are comparable;
- buyer relevance: daily-life pattern, legal-use issue, condition/completion issue or likely resale pool;
- local comparison, if claim-fit;
- source, capture date and confidence.

On desktop, examples render as three readable editorial records rather than a wide nine-column spreadsheet. On mobile, the same records stack without horizontal scrolling.

## Editorial-output rule

Reader-facing prose must answer at least one of these questions:

- What does this mean for the buyer?
- What differs by location or property type?
- What can go wrong?
- What should be verified before commitment?
- What is the practical price, cost, access or resale implication?

Production commentary is prohibited in titles, introductions, captions and narrative paragraphs. Prohibited patterns include:

- “we use,” “the dataset uses,” “recorded dataset exchange basis”;
- “this section/table shows,” “the prose below explains”;
- “the complete assessment appears once”;
- “these inputs connect the dossier to the model”;
- “local price is primary” when the same fact is already evident from the field order;
- announcements of a later table such as “the listings below.”

Necessary methodology remains available without interrupting the article:

- currency and area basis live in their fields;
- capture date and confidence live with each example;
- conversion date/rate and detailed limitations live in the caveat or references;
- scoring methodology remains linked from the assessment footer;
- evidence ledgers remain internal publishing records, not article copy.

Introductions must lead with the conclusion. For Fukuoka, the property introduction should resemble: “The current examples run from about ¥31.8 million for a rail-accessible western-Fukuoka apartment to ¥180 million for a large coastal holiday house. Access to rail and ordinary services matters more to resale depth than proximity to the sea alone.”

## Image-direction contract

Each dossier keeps exactly three distinct editorial images, but the three images must perform different jobs.

1. **Defining place:** the hero establishes the destination’s strongest spatial identity. Prefer landscape, skyline, coastline, mountain form or a recognisable urban-natural relationship. People are optional and never the subject by default.
2. **Built environment or access:** architecture, streetscape, transit, harbour, market street, neighbourhood texture, interior-exterior relationship or infrastructure that explains daily life.
3. **Decision texture:** a materially different view tied to seasonality, climate, food economy, landscape management, hazard, building condition, beach access, agriculture or another destination-specific diligence theme.

### Visual-variety rules

- Do not use “older couple walking,” “retired couple,” or equivalent as the default human motif.
- Across a page, no two images may share the same basic composition, subject category or camera distance.
- At least two of the three images should work without a prominent person.
- If people appear, they should be incidental and contextually natural: commuters, market activity, swimmers, cyclists, café life, workers or mixed-age public life.
- Avoid staged lifestyle advertising, posed couples, generic resort pools, montages, text overlays, visible brands and invented signage.
- Vary scale and viewpoint: wide establishing view, medium built-environment view and close/detail or functional scene.
- Captions state the buyer-relevant point, not merely the place name.
- Alt text describes what is visible without marketing language.

Before an image is approved, the provenance record must state its role, exact source/output, dimensions, rights basis and a visual-review note. The visual review explicitly records whether any repeated “people walking” motif remains.

## Rollout

### Phase 1 — Fukuoka acceptance page

- update the shared renderer to the single-section property design;
- rewrite Fukuoka’s value-lens and property introduction to conclusions;
- integrate its three official market anchors with the three examples;
- audit its three current images against the new roles and replace only those that fail;
- verify desktop and 390×844 mobile presentation, source links and zero page overflow.

### Phase 2 — Global template and rulebook

- update the premium dossier rulebook, validation rules and regression tests;
- add automated checks for prohibited production-language patterns;
- require one property section, three property records and no separate official-anchor heading;
- require three unique image roles and provenance fields.

### Phase 3 — Completed dossiers

- regenerate every completed premium destination dossier through the shared renderer;
- rewrite page-specific process copy where automated rules flag it;
- visually audit all image trios and regenerate only failed assets;
- run the existing canonical content, evidence, data-math, responsive and independent-review gates;
- deploy in reviewed batches so an image or listing issue on one destination does not block unrelated pages.

Perth / Margaret River remains outside the completed batch until its current independent listing review is resolved; it adopts the new contract before approval.

## Data and renderer behavior

The existing listing observations and official market anchors remain separate evidence objects internally. Rendering performs an explicit ordered association from each property example to zero or one official anchor. The association is editorial configuration, not automatic geography inference.

If a destination has unmatched anchors, the renderer produces one concise market-context paragraph after the examples. It must never render a second three-row anchor list. Missing or weak anchor matching is a publishing-review issue, not a reason to fabricate a comparison.

USD/m² renders only when the recorded area basis is sufficiently comparable for that example. A destination-level median USD/m² must not be derived from mixed internal, gross, plot or unspecified areas.

## Tests and acceptance criteria

Automated checks must establish that:

- the page has exactly one property-evidence section and no “Official market anchors” heading;
- exactly three property examples render once each;
- all required official sources remain linked at the point of use or in the compact market-context paragraph;
- prohibited process-language patterns are absent from reader-facing dossier copy;
- desktop property records fit the content column without horizontal scrolling;
- mobile property records remain labelled and readable at exactly 390×844;
- exactly three distinct image assets render once each;
- each image has one of the three required roles and a complete provenance record;
- no page-level overflow or page-origin console warning/error is introduced;
- data, listing arithmetic, score and country-handoff tests remain green.

Fukuoka is accepted only after direct desktop/mobile visual inspection. The global rollout is complete only when every previously approved dossier passes the revised contract and its quality record notes the new editorial and image audit.

## Non-goals

- Removing source transparency or market anchors.
- Hiding currency, area, capture-date or confidence limitations.
- Increasing the number of images.
- Adding carousels, montages, decorative cards or other unnecessary interface elements.
- Regenerating an image that already satisfies a distinct editorial role.
