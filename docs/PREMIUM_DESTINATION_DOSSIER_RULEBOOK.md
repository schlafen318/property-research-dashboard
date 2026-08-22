# Premium Destination Dossier Rule Book

**Status:** Canonical production standard

**Reference implementation:** Fukuoka / Itoshima

**Applies to:** Every destination-page revamp and every future premium destination-dossier edition

This rule book turns the Fukuoka / Itoshima dossier into a repeatable production system. It governs research, writing, scoring, property evidence, design, implementation, quality assurance, publication, and later updates.

The Fukuoka page is the structural and visual reference. It is not a copy source. Every destination must be researched independently, and its conclusions, evidence, scores, locations, imagery, and language must be specific to that market.

## 1. Definition of an Atlas 10/10 dossier

A dossier qualifies as Atlas 10/10 only when:

1. every hard publishing gate in this rule book passes;
2. the page scores at least 95 out of 100 on the quality scorecard;
3. no scorecard category earns less than 80% of its available points;
4. the generated desktop and mobile pages—not only the content configuration—have been reviewed;
5. a reviewer can identify the recommendation, controlling constraint, best-fit buyer, unsuitable buyer, and next action in under one minute.

A polished layout cannot compensate for weak evidence. Strong research cannot compensate for an unreadable page. The dossier is a single product: decision quality, evidence, editorial clarity, and presentation must all pass together.

## 2. Non-negotiable principles

### 2.1 Lead with the decision

State the verdict before scores, listings, methodology, or calls to action. The reader should learn whether the destination is credible for the intended buyer and what could invalidate the case before seeing supporting detail.

### 2.2 Separate property ownership from the right to live there

Never imply that buying property creates residency, tax residence, healthcare eligibility, financing access, work rights, or citizenship. Explain these as separate systems and cite the primary rule for each material claim.

### 2.3 Use the ten-dimension model without writing ten repetitive sections

The score table contains all ten dimensions. The main narrative uses five paired editorial lenses to explain buyer consequences. Narrative prose must deepen the analysis rather than paraphrase the score rows.

### 2.4 Distinguish destination facts from country rules

Summarize only the country-wide rules needed to make the destination decision, then link to the country retirement guide and primary sources. The dossier should concentrate on how national rules interact with the local market, daily life, access, hazards, operating environment, and exit.

### 2.5 Treat market evidence as evidence, not inventory or advice

Listings are dated asking-price observations. Official anchors are land, appraisal, or completed-transaction evidence with an explicitly stated asset basis. Neither is a valuation, recommendation, availability guarantee, or substitute for property-specific diligence.

### 2.6 Prefer restraint

Use one clear expression of each idea. Do not add decorative badges, score pills, repeated summaries, duplicate location cards, generic FAQs, promotional interruptions, or hard-coded Atlas destination totals. Every element must either inform a decision or enable an action.

## 3. Production sequence

Revamp one destination at a time. Do not start the next dossier until the current generated page has passed review.

| Stage | Required output | Stop condition |
|---|---|---|
| 1. Inspect | Audit of the current page, data, links, scores, listings, imagery, and known gaps | Stop if the destination dataset is incomplete or internally inconsistent |
| 2. Frame | One-sentence buyer decision and the controlling constraint | Stop if the page cannot name a specific target buyer and decision |
| 3. Research | Evidence ledger with current primary sources and market observations | Stop if a high-stakes claim lacks an authoritative source |
| 4. Audit data | Ten scores, weights, total, confidence, price basis, and listing reconciliation | Stop if narrative evidence contradicts the dataset |
| 5. Draft | Complete structured dossier specification | Stop if any required section or field is missing |
| 6. Edit | Plain-language, duplication, length, and destination-specificity pass | Stop if generic framework copy remains |
| 7. Build | Generated destination page using the shared premium renderer | Stop on validation or build failure |
| 8. QA | Automated tests plus desktop and mobile review | Stop on overflow, console errors, broken links, or unreadable content |
| 9. Review | Completed 100-point scorecard and named reviewer approval | Stop below 95, on any hard-gate failure, or below 80% in a category |
| 10. Publish | Merged, deployed, and live-page verification | Stop if production differs materially from the reviewed build |
| 11. Maintain | Recheck date and trigger recorded | Stop if time-sensitive claims have no owner or recheck rule |

## 4. Required content contract

Each premium dossier must provide the following destination-specific inputs. The shared renderer should control markup and visual treatment; content specifications should not contain one-off styling.

| Field | Requirement |
|---|---|
| Destination identity | Stable destination ID, destination name, country, and canonical URL |
| Editorial identity | H1, concise lede, author, publication date, substantive review date |
| Verdict | Direct conclusion, best-fit buyer, unsuitable buyer, controlling constraint, and ordered decision rule |
| Five lenses | Exactly five lenses covering every Atlas dimension exactly once |
| Score reads | Exactly one concise, destination-specific Atlas read for each of the ten dimensions |
| Market anchors | Exactly three complete official anchors, each with geography, evidence, buyer interpretation, label, URL, date or period, and asset-basis limitation |
| Micro-locations | At least three useful submarkets with best use, daily-life pattern, and primary diligence |
| Orientation | A relationship model based on rail, road, ferry, geography, or another decision-relevant sequence when spatial context changes the recommendation |
| Buyer checklist | Six to eight actions in investigation order |
| References | Direct authoritative links plus a clear update and professional-verification policy |
| Images | Exactly three unique destination-specific editorial images with alt text, captions, and placement roles |
| Navigation | No more than seven meaningful anchors; References is last |

Build validation should fail clearly when a required field is missing, the dimension mapping is incomplete or duplicated, the image count is wrong, the navigation is too long, or References is not last.

## 5. Page anatomy and length budget

The order below is fixed unless a documented user need justifies an exception.

| Order | Section | Required job | Guidance |
|---:|---|---|---|
| 1 | Editorial hero | Name the destination proposition and frame the decision | H1, 60–90-word lede, byline and dates, one hero image; no eyebrow, badge, or score |
| 2 | Verdict | Give the answer before the analysis | Approximately 200–300 words across proceed, pause/look-elsewhere, and investigation-order paragraphs |
| 3 | Five destination lenses | Explain the ten-factor decision through buyer consequences | Approximately 900–1,200 words total; normally two or three paragraphs per lens |
| 4 | Atlas assessment | Show the complete auditable scoring view | Short plain-language introduction, one ten-row table, weighted result once, methodology link |
| 5 | Representative property evidence | Show the range of plausible buyer cases | Three to five observations, disclaimer, then exactly three official market anchors |
| 6 | Where to look | Translate the destination into usable submarket choices | Short introduction, orientation schematic when material, one compact micro-location table |
| 7 | Buyer checklist | Convert the analysis into an investigation sequence | Six to eight numbered actions; do not repeat the verdict |
| 8 | Research handoff | Provide the few next pages that materially deepen the decision | Country guide, methodology, and relevant comparison only; one compact handoff |
| 9 | References and update policy | Make the research auditable and maintainable | Always the final article section |

Target 1,800–2,400 editorial words, excluding tables, captions, and references. The target is a discipline, not permission to pad. A shorter page may pass when the evidence supports a narrower treatment; a longer page requires an editor to identify why the additional material changes the decision.

## 6. Writing standard

### 6.1 Voice

- Write for an informed international reader considering a long-term home, not for a tourist browsing attractions.
- Use calm, direct, specific language. Prefer “A coastal address may require a car for hospital and grocery trips” to “transportation should be considered.”
- Explain the consequence after the fact: what the evidence means for daily life, cost, operating burden, or exit.
- Use professional caution without legalistic filler. A caveat must identify the uncertainty and the verification step.
- Avoid hype, investment promises, lifestyle clichés, and false certainty.

### 6.2 Destination specificity

Every substantive paragraph should contain at least one of the following:

- a named place, system, route, institution, rule, hazard, buyer case, or market segment;
- a verified contrast between two parts of the destination;
- a destination-specific consequence or diligence action.

If a paragraph could be moved unchanged to another destination, rewrite or remove it.

### 6.3 Headings

- Use sentence case.
- Prefer a decision or buyer consequence over a methodology label.
- Keep the fixed major labels where consistency helps: “The verdict,” “The Atlas assessment,” “Representative property evidence,” “Where to look,” “Buyer checklist,” and “References and update policy.”
- Lens headings should express the local story, not merely repeat dimension names.

### 6.4 Emphasis and links

- Use bold sparingly for short decision rules, dates, thresholds, and named locations when emphasis materially improves scanning.
- Do not bold navigation, bylines, buttons, captions, eyebrows, or whole sentences.
- Link the first substantive mention of a relevant country guide or related destination page. Do not repeatedly link the same place within one section.
- Use descriptive link text; never “click here.”

### 6.5 Editorial compression pass

Before build, remove:

- duplicated verdicts or conclusions;
- prose that restates a table row;
- generic introductions to the scoring methodology;
- repeated descriptions of the same city or location;
- adjectives unsupported by evidence;
- precise figures that do not change the decision;
- promotional language that interrupts risk or diligence information.

## 7. The five-lens model

The pairings are fixed so every dossier covers all ten Atlas dimensions once.

| Lens question | Atlas dimensions | Minimum analytical coverage |
|---|---|---|
| Can I live well here over time? | Lifestyle magnetism + Retirement fit | Daily services, healthcare access, climate or seasonality, mobility, social life, and the difference between visiting and living |
| Can I reach it and integrate? | Global access + Foreigner fit | International and domestic access, last mile, language, administration, local support, and integration burden |
| Can I own and operate safely? | Ownership clarity + Regulatory safety | Title access, reporting, local restrictions, building governance, permitted use, hazards, insurance, and professional support |
| Can the financial case work? | Rental profit + Capital upside | Ordinary demand, tourist or seasonal demand, operating cost, legal rental route, evidence limits, and upside conditions |
| Can I enter well and preserve the exit? | Value entry + Exit liquidity | Price segmentation, total ownership cost, buyer pool, property specificity, resale friction, and exit scenario |

Do not force equal paragraph counts when one destination has an unusually material issue. Keep the dimension coverage complete, but give more space to the facts most likely to reverse the decision.

## 8. Score governance

### 8.1 Source of truth

The destination dataset is authoritative for dimension scores, weights, weighted total, evidence labels, confidence, and quantitative benchmarks. Never override a score in article markup.

### 8.2 Score audit

Before drafting:

1. inspect all ten dimension scores and the supporting data;
2. compare them with current research and the proposed narrative;
3. change a score only when evidence justifies the change;
4. update the underlying dataset and affected tests, not only the prose;
5. recalculate the weighted total from the model;
6. confirm the displayed total, individual rows, and narrative do not contradict one another.

### 8.3 Atlas reads

Each row receives one concise destination-specific explanation labelled **Atlas read**.

- Aim for one sentence and approximately 18–35 words.
- State the strongest positive and the controlling trade-off where both matter.
- Name the local place or operating reality when helpful.
- Do not define the dimension, repeat the score, make a forecast, or use academic language such as “comparative inputs.”

### 8.4 Presentation

- Display the ten dimensions once in one table.
- Show score on the five-point scale and the model weight.
- Show the weighted result once below the table with review date and methodology link.
- Do not feature the total in the hero or convert score rows into decorative cards on desktop.
- On narrow screens, transform each row into a labelled record; do not require horizontal scrolling.

## 9. Representative property evidence

### 9.1 Listing sample

Use three to five observations that represent meaningfully different buyer cases—for example, a practical apartment, an ordinary house, and a premium lifestyle property. Do not select only visually attractive or unusually cheap inventory.

Every observation must contain:

- descriptive location and property type;
- local asking price first;
- dated USD comparison and recorded exchange-rate basis;
- internal area and price per square metre using a consistent area definition;
- direct source URL and source name;
- capture date;
- confidence level;
- a short statement of what the observation represents.

The section must say that listings are dated asking-price evidence only and do not verify availability, title, condition, negotiability, fees, legal use, or completed value. Do not use listing photography without confirmed reuse rights.

### 9.2 Official market anchors

Use exactly three official anchors after the listings. Prefer:

1. completed transaction records;
2. official appraisals or assessment comparables;
3. official land or housing benchmarks.

For every anchor, state geography, period, currency and unit, asset basis, source, and what the reader may safely infer. Explicitly distinguish land evidence from finished-home prices. Explain material incompatibilities between an anchor and the listing sample rather than averaging unlike evidence.

### 9.3 Reconciliation gate

Publication stops if the listings, official anchors, price basis, confidence label, value-entry score, or exit-liquidity analysis materially contradict one another. Resolve the data, narrow the claim, or disclose the limitation.

## 10. Micro-location standard

The location section should answer “where does this proposition actually work?” rather than provide a neighborhood directory.

- Select three to five micro-locations that represent distinct daily-life or investment patterns.
- Use one compact table with: micro-location, best for, daily life, and primary diligence.
- Use a simple orientation schematic when rail, road, ferry, altitude, coast, or another spatial relationship materially changes access or operating burden.
- Label the schematic as not to scale and tell readers to verify the exact route or timetable.
- Keep the schematic relational; it is not a substitute for an accurate geographic map.
- Do not duplicate the same micro-location content as cards, prose summaries, and table rows.

## 11. Image standard

Use exactly three destination-specific editorial images:

1. a hero image that expresses the core proposition;
2. an image supporting daily life, access, or the practical base;
3. an image supporting the destination's contrasting lifestyle, geography, or operating reality.

Requirements:

- use a single image in each placement; never create a montage;
- use imagery with clear rights or generated assets approved for publication;
- avoid generic country symbols when the page is about a specific city or region;
- write factual alt text describing what is visible;
- use concise captions that interpret the image's relevance without repeating the alt text;
- distribute inline images through relevant lens sections rather than clustering them;
- verify that mobile crops preserve the subject and that captions remain readable.

## 12. Shared visual system

All premium dossiers use the shared renderer and the Fukuoka visual language. Do not create destination-specific CSS unless the shared system cannot express a necessary content type.

### 12.1 Core tokens

| Role | Standard |
|---|---|
| Paper | Warm ivory `#f4efe4` |
| Ink | Deep green `#24312d` |
| Muted text | `#69736e` |
| Accent | Restrained rust `#a44e2f` |
| Links | Muted green `#516f65` |
| Display serif | Iowan Old Style, Baskerville, Palatino, Georgia fallback stack |
| Body sans | Avenir Next, Avenir, Helvetica Neue, Arial fallback stack |

These values belong in the shared renderer. A destination may not introduce a new palette merely to appear locally themed.

### 12.2 Typography

- H1: serif, regular/medium weight, compact leading, large editorial scale.
- Section and lens headings: serif, regular/medium weight—not bold sans.
- Body: sans, 17px desktop and at least 16px mobile, approximately 1.7 line height.
- Hero lede: serif, regular weight, approximately 19–24px desktop.
- Navigation, captions, table labels, byline, and buttons: sans, restrained weight; never heavy black or faux-bold.
- Keep prose lines at approximately 65–72 characters where possible.

### 12.3 Layout

- Desktop hero: two columns, copy plus one tall destination image.
- Desktop article: main column up to approximately 830px plus a 220px sticky rail.
- Rail: no more than seven anchors and one count-free Atlas action.
- Use fine rules and generous vertical spacing instead of boxes, rounded cards, shadows, or alternating colored panels.
- Tables use plain rules, aligned numbers, and readable labels.
- References remain visually quiet and appear at the end.

### 12.4 Responsive behavior

At 900px and below, the hero and content become single-column and the rail becomes static. At 560px and below:

- use a minimum 14px page gutter;
- keep body copy at 16px or larger;
- hide the desktop navigation in favor of the compact menu;
- turn score and listing tables into stacked labelled records;
- turn the orientation sequence vertical;
- place references in one column;
- preserve a minimum 44px target for interactive controls;
- maintain `documentElement.scrollWidth == documentElement.clientWidth`.

## 13. Research and citation rules

### 13.1 Source hierarchy

Use the highest available source in this order:

1. legislation, ministries, national agencies, courts, tax authorities, land registries, and official statistics;
2. municipalities, regional governments, official hazard maps, health systems, airport and transport operators;
3. official appraisal, transaction, land-price, tourism, and housing-market data;
4. reputable professional or institutional interpretation when the primary rule is inaccessible or requires explanation;
5. listing portals only for dated asking-price observations;
6. reputable editorial sources only for non-critical context that cannot be sourced more directly.

Never use a search-result snippet, generative answer, unsourced aggregator, agent marketing page, or portal article as the sole support for a legal, tax, immigration, healthcare, ownership, hazard, or rental-regulation claim.

### 13.2 Evidence ledger

During research, record for every material claim:

- claim text or topic;
- source owner and direct URL;
- publication or effective date;
- access/review date;
- jurisdiction and geographic scope;
- asset or buyer scope;
- current, future, transitional, or under-review status;
- limitations and required professional verification;
- destination sections that use the source.

### 13.3 Dates and future changes

- Display the real substantive review date in the byline and structured data.
- Label announced future changes with effective date and current status.
- Describe consultations and reviews as reviews, not enacted law.
- Record a recheck trigger for rules, listings, transport, hazard maps, and time-sensitive statistics.

## 14. Links, SEO, and trust

- Use one H1 that names the destination and its decision proposition.
- Write a unique, accurate title and meta description; do not merely swap place names in a template.
- Use the correct canonical URL.
- Include Article and Breadcrumb structured data with author, publisher, publication date, and modified date.
- Link the dossier to the relevant country retirement guide, methodology, and useful comparison page.
- Link the first substantive destination mention in the country guide back to the dossier.
- Do not duplicate internal links throughout the page.
- Link external citations directly to the supporting source page, not a search result or generic homepage when a specific page exists.
- Do not hard-code the number of destinations in Atlas calls to action.
- Keep References as the final article section.

## 15. Accessibility and technical requirements

- Use semantic headings in order, one H1, article landmarks, tables with headers, ordered lists where sequence matters, and figures with captions.
- Give every informative image useful alt text; use empty alt text only for truly decorative images.
- Ensure visible keyboard focus and minimum 44px interactive targets.
- Do not encode meaning through color alone.
- Preserve readable contrast for body text, links, captions, and controls.
- Generated HTML must have no horizontal page overflow at 390 × 844.
- The browser console must report zero errors and zero warnings caused by the page.
- All links must resolve to the intended destination.
- The production build must complete from source without hand-editing generated artifacts.

## 16. Hard publishing gates

Any failure below blocks publication regardless of the numeric score:

- a material legal, tax, immigration, healthcare, ownership, hazard, or rental claim lacks a current authoritative source;
- the article implies that property ownership grants residency or another unrelated right;
- the five lenses do not cover every Atlas dimension exactly once;
- the displayed scores or total are manually overridden or inconsistent with the dataset;
- listings lack source, capture date, local price, area basis, or asking-price disclaimer;
- fewer or more than three official market anchors appear, or an anchor's asset basis is unclear;
- narrative, scores, listings, anchors, price basis, or confidence materially contradict one another;
- References is not the final article section;
- the page contains broken links, browser-console errors, horizontal page overflow, clipped content, or inaccessible controls;
- the generated artifact was not reviewed at desktop and 390 × 844 mobile sizes;
- imagery lacks publication rights, alt text, or useful mobile crops;
- the page contains copied destination conclusions, unverified figures, placeholders, or generic framework prose;
- the visible review date or structured-data date is inaccurate.

## 17. The 100-point quality scorecard

Award points only when the criterion is fully satisfied. Do not award partial points unless the row explicitly permits it.

### A. Decision usefulness — 15 points

| Criterion | Points |
|---|---:|
| Verdict is direct and appears before scores or listings | 4 |
| Best-fit and unsuitable buyers are specific | 3 |
| Controlling constraint could reverse the decision | 3 |
| Costs and risks cover acquisition through exit | 3 |
| Checklist follows the real investigation order | 2 |

### B. Evidence and accuracy — 25 points

| Criterion | Points |
|---|---:|
| High-stakes claims use current primary sources | 8 |
| National and local rules are distinguished | 4 |
| Dates, jurisdiction, buyer scope, and effective status are clear | 4 |
| Hazards, access, healthcare, and operating claims are location-specific | 4 |
| Limitations and professional-verification needs are explicit | 3 |
| Evidence ledger and recheck triggers are complete | 2 |

### C. Atlas model integrity — 15 points

| Criterion | Points |
|---|---:|
| Five lenses cover all ten dimensions exactly once | 4 |
| Dataset remains the sole score source of truth | 4 |
| Ten Atlas reads are concise and destination-specific | 3 |
| Weighted total is derived, dated, and linked to methodology | 2 |
| Narrative adds consequences rather than repeating score rows | 2 |

### D. Property and location evidence — 15 points

| Criterion | Points |
|---|---:|
| Three to five distinct representative observations are complete | 4 |
| Exactly three compatible official market anchors are complete | 4 |
| Listings, anchors, scores, and confidence reconcile | 3 |
| Micro-locations represent distinct daily-life patterns | 2 |
| Orientation device materially improves spatial understanding | 2 |

### E. Editorial quality — 10 points

| Criterion | Points |
|---|---:|
| Opening is concise and destination-specific | 2 |
| Prose is plain, calm, and consequence-led | 2 |
| Headings support fast scanning | 2 |
| Duplication and generic framework language are absent | 2 |
| Length is disciplined and country-guide material is handed off | 2 |

### F. Design, mobile, and accessibility — 10 points

| Criterion | Points |
|---|---:|
| Shared Fukuoka visual system is used without decorative additions | 2 |
| Three images are relevant, licensed, accessible, and well cropped | 2 |
| Desktop hierarchy and line lengths are readable | 2 |
| Mobile records, navigation, and orientation are readable without overflow | 2 |
| Semantic structure, focus, contrast, and controls pass review | 2 |

### G. SEO and trust — 5 points

| Criterion | Points |
|---|---:|
| Metadata, canonical URL, structured data, and visible dates agree | 2 |
| Internal links create a useful country–destination–methodology path | 1 |
| External citations link directly to supporting sources | 1 |
| References and update policy are complete and final | 1 |

### H. Build and maintenance — 5 points

| Criterion | Points |
|---|---:|
| Relevant automated tests and source validation pass | 2 |
| Build, browser console, link, and overflow checks pass | 2 |
| Next review date or recheck triggers are recorded | 1 |

### Score interpretation

| Score | Decision |
|---:|---|
| 95–100, all hard gates pass, no category below 80% | Atlas 10/10; publish-ready |
| 90–94 | Strong draft; revise before publication |
| 80–89 | Material editorial or evidence gaps; do not publish |
| Below 80 | Re-research or restructure the dossier |

## 18. Desktop and mobile review script

Review at the standard desktop viewport and at 390 × 844. At minimum, inspect:

1. hero and first-screen decision clarity;
2. byline weight, heading rhythm, body line length, and image crop;
3. verdict position and right-rail behavior;
4. all ten score records;
5. every representative listing record;
6. all three official market anchors;
7. location orientation and micro-location table;
8. checklist and reference ordering;
9. internal and external links;
10. console output and page-width measurements.

Record the following evidence in the pull request:

- targeted test result;
- complete-suite result, with unrelated failures identified separately;
- build result;
- desktop and mobile screenshots or review notes;
- `documentElement.clientWidth` and `documentElement.scrollWidth` at mobile width;
- browser console error and warning counts;
- reviewer score and hard-gate result.

## 19. Update policy for future editions

### Triggered review

Review a dossier immediately when any of the following occurs:

- residency, ownership, tax, healthcare, rental, or reporting rules change;
- a cited municipal hazard map, transport system, or planning rule changes;
- listing evidence becomes unavailable or materially stale;
- official market data changes the value-entry or exit-liquidity case;
- a score changes in the destination dataset;
- a country guide changes a claim used by the dossier;
- a broken source, production regression, or user-reported factual issue appears.

### Scheduled review

At the scheduled review:

1. re-open every cited source;
2. refresh or explicitly retain dated listing observations;
3. refresh the official market anchors;
4. audit all ten scores and Atlas reads;
5. verify internal links, metadata, dates, and structured data;
6. rebuild and repeat desktop/mobile QA;
7. update the visible review date only after the substantive check is complete.

Do not change the review date for copy edits that do not include a substantive evidence review.

## 20. Rollout rule for existing destinations

For each existing destination:

1. inspect the current dossier before writing;
2. identify the destination's unique proposition and the fact most likely to defeat it;
3. audit the underlying ten-factor data and listings;
4. complete destination-specific research using the source hierarchy;
5. create the premium specification using the shared contract;
6. render only that destination through the premium template;
7. complete the hard gates and 100-point scorecard;
8. publish and inspect the live page;
9. obtain approval before starting the next destination.

Do not bulk-convert pages by replacing names in Fukuoka copy. Shared structure is required; shared conclusions are prohibited.

## 21. Reviewer record

Copy this block into the pull request or review issue:

```text
Destination:
Country guide:
Research review date:
Listing capture date:
Next scheduled review:

Hard publishing gates: PASS / FAIL
Decision usefulness: __ / 15
Evidence and accuracy: __ / 25
Atlas model integrity: __ / 15
Property and location evidence: __ / 15
Editorial quality: __ / 10
Design, mobile, and accessibility: __ / 10
SEO and trust: __ / 5
Build and maintenance: __ / 5
Total: __ / 100

Desktop reviewed: YES / NO
390 × 844 reviewed: YES / NO
Console errors: __
Console warnings: __
Mobile client width: __
Mobile scroll width: __
Reviewer:
Approval date:
Notes:
```

The reviewer approves the destination as a whole. Passing isolated tests or individual sections is not sufficient.
