# FIRE Abroad Design

**Date:** 2026-08-29
**Status:** Approved in conversation; awaiting written-spec review

## Purpose

Create a canonical FIRE Abroad destination-discovery page for financially independent people who want an active life outside their current country. The page should help readers screen destinations for a seasonal stay, part-year base, or full relocation without assuming that every user is conventionally retired, over 50, buying property, or seeking permanent residence.

The product combines Global Home Atlas's existing destination, retirement-cost, property, and calculator infrastructure with a compact FIRE-specific evidence layer. It is a screening and planning tool, not individualized financial, tax, immigration, healthcare, or investment advice.

## Audience and Positioning

The primary audience is adults roughly 40–59 who have reached, or are approaching, financial independence and want an active international lifestyle. The methodology has no hard age cutoff. Age 50 is the default planning profile because many users will be near that point, while age-dependent eligibility is evaluated from the user's actual age.

The public category and page name are **FIRE Abroad**. Supporting language may use `financial independence abroad`, `retire abroad early`, `active retirement abroad`, and `best countries to retire early` where it accurately matches the content. The page must define FIRE on first use and should not imply that the experience is limited to people who have stopped all paid work.

## Goals

- Rank destinations for a financially sustainable, active life abroad.
- Distinguish seasonal stays, part-year bases, and full relocation.
- Make legal-stay, tax-residence, healthcare-access, and work-permission constraints visible before users treat a destination as viable.
- Treat daily activity and year-round active living as a first-class decision factor.
- Connect discovery results to the existing retirement calculator and destination research without exposing sensitive data in URLs or analytics.
- Publish transparent evidence, review dates, confidence, and limitations.
- Reuse the current static builder, shared datasets, ranking conventions, and calculator.

## Non-goals

- Calculate an individual's tax liability or recommend a tax structure.
- Guarantee visa, residence, insurance, banking, or work eligibility.
- Provide portfolio allocation, withdrawal-rate, or investment advice beyond the existing calculator's documented planning assumptions.
- Collect or persist citizenship, financial balances, income amounts, account types, or health information.
- Create thin country pages or a new application framework in the first release.
- Treat property purchase or permanent residence as necessary for FIRE Abroad.

## User Modes and Eligibility

The page supports three mutually exclusive intended-stay modes:

1. **Seasonal:** repeated shorter stays without intending to become locally resident.
2. **Part-year base:** a recurring base for a material portion of each year while maintaining another home or tax base.
3. **Full relocation:** the destination becomes the user's principal home and requires a credible long-term legal route.

The fundamental requirement is a credible legal pathway for the intended duration, not residence in every case. A missing long-term residence route blocks only full relocation. A destination may remain viable for seasonal or part-year use if the evidence supports the intended stay pattern.

Eligibility rules are evaluated before weighted ranking:

- If no credible legal-stay route is documented for the selected mode, classify the destination as **Not currently eligible** and explain why.
- Apply actual age thresholds from the evidence rather than using 50 as an eligibility cutoff.
- Classify age context for explanation as under 50, 50–59, or 60+, without excluding a band by default.
- Where nationality or family status determines eligibility and the user has not supplied the relevant broad category, show **Eligibility depends on profile** rather than guessing.
- When evidence is missing, contradictory, or stale, show **Needs verification** and do not rank the destination for full relocation.

## Ranking Methodology

After mode eligibility, calculate a FIRE Abroad score on a 0–5 scale using these weights:

| Dimension | Weight | What it measures |
| --- | ---: | --- |
| Active Life | 25% | Whether meaningful daily activity is convenient and sustainable through a normal year |
| Sustainable annual cost | 20% | Comfortable recurring cost plus realistic resilience allowances |
| Healthcare Bridge | 15% | Practical access from arrival through later life, not healthcare reputation alone |
| Stay Flexibility | 10% | Credible options for the selected duration and ability to change modes later |
| Tax Compatibility | 10% | Clarity, administrative complexity, and scenario-specific exposure flags, not a personal tax rate |
| Global Access | 8% | Practical access to airports, family, and international connections |
| Community Fit | 7% | Ease of building a social life and functioning as a foreign resident or repeat visitor |
| Property and Exit Flexibility | 5% | Ability to rent or buy appropriately, avoid lock-in, sell, and move capital |

The weights total 100%. Scores must be generated by a FIRE-specific wrapper around the existing ranking conventions rather than adding a second general destination engine. The wrapper may reuse existing normalized destination dimensions where their meaning matches; it must not relabel an unrelated score as FIRE evidence.

### Active Life Score

Active Life is composed of:

| Subcomponent | Active Life weight |
| --- | ---: |
| Everyday movement | 30% |
| Access to active pursuits | 30% |
| Year-round continuity | 25% |
| Activity ecosystem | 15% |

`Everyday movement` covers walkability, cycling practicality, routine outdoor access, and the ability to be active without planning an excursion. `Access to active pursuits` covers trails, water, mountains, sports, or other locally relevant pursuits, with no credit for nominal access that normally requires a long drive. `Year-round continuity` measures a normal week across seasons, including heat, rain, snow, daylight, air quality, and shoulder-season closures. `Activity ecosystem` covers clubs, instruction, facilities, groups, and realistic opportunities to participate with others.

The score rewards sustainable daily activity, not only strenuous or elite sport. Cities may outrank resorts when ordinary movement, continuity, and community are stronger. Healthcare capacity remains separate and must not be double-counted here.

### Sustainable Annual Cost and Resilience Budget

Reuse `data/retirement_costs.json` for destination costs. The FIRE Abroad presentation must not stop at a lowest plausible local budget. It should show a resilience budget composed of:

- recurring comfortable living costs for the selected household and housing scenario;
- private healthcare or insurance allowance already represented in the shared data;
- recurring immigration and administration costs;
- realistic travel home;
- an explicit contingency allowance;
- a clearly labeled currency and inflation buffer; and
- one-time relocation costs shown separately rather than disguised as recurring spending.

The first release may use documented scenario allowances rather than forecast exchange rates or local inflation. It must explain that currency and inflation can materially change affordability. It must not add the same healthcare, travel, visa, or contingency cost twice when the shared dataset already includes it.

### Healthcare Bridge

The score measures whether the user can actually bridge healthcare from arrival through longer-term life:

- eligibility for private insurance or public coverage;
- residence dependencies and waiting periods;
- documented age limits;
- treatment of pre-existing conditions at a broad, non-personalized level;
- local primary, specialist, and emergency access; and
- evacuation or travel-insurance dependence where relevant.

High national healthcare quality cannot compensate for an access path that is unavailable to the intended user profile. Personal medical information is neither requested nor stored.

### Stay Flexibility and Work Permissions

Stay Flexibility evaluates routes for the selected mode, duration limits, renewal burden, age or income thresholds, dependants where documented, and the ability to transition between modes. It also displays work permissions as one of:

- passive income only;
- remote work permitted;
- local work permitted; or
- unclear / professional review required.

Work permission modifies Stay Flexibility and does not receive a separate weight. The page must not imply that passive-income residence automatically authorizes consulting, remote work, or local employment.

### Tax Compatibility

Tax Compatibility measures the clarity and administrative burden of the likely scenario. It must not claim that a destination is universally low-tax or estimate personal liability.

For each country and mode, record and display:

- the standard tax-residence trigger and important non-day-count tests;
- whether residents are generally taxed on worldwide or local-source income;
- broad flags for pensions, dividends, capital gains, property, wealth, and inheritance;
- relevant treaty and reporting complexity;
- source-country or property-income exposure that can exist while nonresident; and
- a warning when the intended stay is likely to create local tax residence.

The user may optionally select a broad home-tax context, including a US-person warning state, intended stay mode, approximate days, and broad income categories. Precise income, balances, gains, accounts, or health data are not collected. These selections remain in the browser and are excluded from URLs and analytics.

Tax residence and immigration residence must be presented as separate concepts. For example, a seasonal visitor may still owe tax on local-source income, while a full resident may enter local worldwide-income scope. US citizens and resident aliens receive a persistent reminder that US worldwide-income filing commonly continues abroad, without attempting a treaty or foreign-tax-credit calculation.

### Financial Infrastructure

The Tax Compatibility detail also displays non-scored supporting flags for:

- bank-account opening requirements;
- tax-identification or residence dependencies;
- international transfer friction and capital controls;
- common international-payment access; and
- known brokerage or account-access issues that require user verification.

These are screening warnings, not guarantees about a particular financial institution.

### Property and Long-Term Exit Resilience

Property is optional. A destination can score well when renting provides a flexible and credible route. This dimension evaluates rental availability, foreign-buyer access where relevant, transaction costs, market liquidity, and the ability to sell and move proceeds.

The result also explains longer-term resilience: whether a user can transition from seasonal use to residence, maintain healthcare access as needs change, avoid being forced to buy, reach family, and exit if regulation, climate, disaster exposure, or personal circumstances change. Broad political, regulatory, climate, and disaster risks appear as evidence-backed warnings rather than an over-precise predictive score.

## Initial Coverage

Launch one canonical page at `/fire-abroad/` with ten destinations already covered by the shared destination and retirement datasets:

- Algarve / Cascais
- Bali
- Croatia / Istria / Dalmatia
- Crete
- Da Nang / Hoi An
- Fukuoka / Itoshima
- Madeira
- Málaga / Costa del Sol
- Phuket / Koh Samui
- Valencia

This set provides multiple regions, legal-stay patterns, cost levels, and activity contexts while keeping evidence work bounded. A destination is published in the ranked experience only when every launch-critical FIRE field passes validation. The rendered destination count is dynamic. Additional destinations require the same evidence completeness; do not create thin pages merely to expand coverage.

## Page and User Experience

### SEO identity

- **URL:** `/fire-abroad/`
- **Title:** `FIRE Abroad: Best Places for an Active Life Overseas | Global Home Atlas`
- **H1:** `FIRE Abroad`
- **Primary intent:** `FIRE abroad`
- **Supporting intents:** `financial independence abroad`, `retire abroad early`, `active retirement abroad`, and `best countries to retire early`

The server-rendered page should define FIRE Abroad immediately, explain that residence is mode-dependent, and provide useful ranked content before JavaScript runs.

### Controls

Keep the first interaction compact:

- intended stay: seasonal, part-year base, or full relocation;
- current age, default 50;
- household: single or couple;
- housing: rent, already own, buy now, or buy at retirement;
- broad mobility-rights context, optional: local/free-movement rights, general nonlocal passport, or prefer not to say;
- broad home-tax context, optional;
- approximate annual days, used only for warnings;
- broad income type, optional: portfolio, pension, property, business/consulting, or mixed; and
- activity priorities as optional filters after the general Active Life ranking.

Do not request net worth, account values, detailed nationality, passport number, health history, or exact income on this page.

### Results

Use a concise ranked table or list rather than dense repeated cards. Each result should show only distinct decision information:

- destination and FIRE Abroad score;
- eligibility for the selected stay mode;
- resilience-budget estimate;
- Active Life score and strongest activity reason;
- healthcare-bridge status;
- stay route and work-permission flag;
- tax-residence warning or compatibility status;
- strongest risk or verification requirement;
- evidence confidence and last review date;
- links to the relevant destination/country guide; and
- **Build your plan** link to the retirement calculator.

The detailed methodology section explains weights, evidence, limitations, and why immigration and tax residence differ. Country-specific evidence opens progressively rather than duplicating every source in each summary row.

The calculator handoff includes only values already accepted by `retirementPrefill()`: validated destination, household, and housing. Age, tax context, days, income categories, scores, and financial values must not enter the URL. Expanding the calculator's allowlist is outside this release.

### Internal linking

Link to `/fire-abroad/` contextually from:

- `/guides/`;
- `/retirement-abroad-calculator/`;
- `/retirement-destination-finder/`;
- `/best-places-to-buy-property-abroad-for-retirement/`;
- `/buying-property-abroad-for-retirement/`; and
- launch destination and country guides where a FIRE Abroad recommendation is substantiated.

Do not add another primary-navigation item. The FIRE Abroad page links back to those planning tools and relevant evidence pages. Add the canonical page to the sitemap and applicable guide-hub collections.

## Architecture and Data Flow

### Shared inputs

- `data/destinations.json` remains the source for destination identity, existing decision dimensions, links, and property context.
- `data/retirement_costs.json` remains the source for household costs, housing scenarios, travel, visa/admin, healthcare allowances, contingency, inflation assumptions, and representative property figures.
- The existing pure retirement calculator remains unchanged and continues to model user-entered after-tax income. FIRE Abroad does not inject a guessed tax rate into that engine.

### FIRE overlay

Add `data/fire_abroad.json` as a compact evidence overlay keyed by country with destination overrides. It contains only FIRE-specific facts and scoring inputs that are not safely available from shared data. Required structures include:

- supported destination IDs and optional destination override;
- legal-stay routes by mode, duration, age/income/dependant conditions, and renewal burden;
- work-permission classification;
- tax-residence trigger, taxation scope, category flags, treaty/reporting note, and tax complexity;
- healthcare eligibility, waiting period, age/pre-existing-condition flags, access and evacuation dependency;
- Active Life subcomponent scores with supporting evidence;
- banking/capital-mobility flags;
- long-term transition and risk warnings;
- source records with metric supported, URL, publisher, source date, accessed date, jurisdiction level, and notes; and
- confidence and last-reviewed date for each volatile section.

Country-level records may be inherited, but destination-specific Active Life evidence and any local override must be explicit. Immigration, tax, healthcare, and financial-infrastructure facts should use official or primary sources wherever available. Editorial summaries must not replace the underlying evidence records.

### Ranking boundary

Add a focused pure function, conceptually `rank_fire_abroad_destinations(destinations, retirement_costs, fire_overlay, profile)`. It:

1. validates and normalizes the profile;
2. joins the three datasets by stable IDs;
3. applies mode and age eligibility;
4. composes non-duplicative resilience costs;
5. calculates Active Life and the weighted FIRE score;
6. attaches tax, work, healthcare, banking, and risk warnings;
7. excludes results that fail the explicit launch-critical validation rules; and
8. returns deterministic ranked view models for rendering.

Keep calculation, validation, and HTML rendering separate. The browser may rerun equivalent pure ranking logic for interactive controls, but the static builder must render a useful default ranking for age 50, single household, renting, and part-year base. All page copy and counts derive from data rather than hardcoded claims.

Sort eligible results by FIRE Abroad score descending, then complete-evidence confidence descending, then destination display name ascending. Conditional destinations follow eligible destinations and unranked verification states follow conditional destinations. Evidence confidence never changes a calculated score; it determines whether a result can be ranked and resolves ties only.

## Evidence Freshness and Error Handling

- Every immigration, tax, healthcare, cost, banking, and risk claim requires a source and checked date.
- A launch-critical legal, tax-residence, or healthcare field without a supported source fails build-time validation for that destination and mode.
- Conflicting evidence produces **Needs verification**, preserves the conflict in source notes, and prevents an unsupported definitive claim.
- Volatile facts have a review interval and become visibly stale when overdue; staleness cannot silently retain a high-confidence label.
- Missing Active Life subcomponents make the destination unranked rather than treating missing values as zero.
- Unknown profile-dependent eligibility is displayed as conditional, not eligible or ineligible.
- Invalid query values and browser inputs fall back to documented defaults.
- If JavaScript fails, the default server-rendered ranking, methodology, caveats, and internal links remain available.
- Analytics may record control categories and result clicks, but never age, tax home, days, income categories, or financial inputs.

## Structured Data and Accessibility

Use the site's existing metadata helpers for canonical, Open Graph, breadcrumbs, and a primary `WebPage` or `CollectionPage` entity. Add FAQ structured data only for questions visibly answered on the page and only when consistent with current search-engine guidance. Do not describe the ranking as professional financial advice or use review/rating schema for the internal score.

Controls require native labels, keyboard operation, visible focus, and announced result changes. Tables must remain readable or transform into an accessible linear list on small screens without losing headers or context. Score color is supplementary; eligibility and warnings must always have text.

## Testing and Verification

### Data and scoring tests

- weights total 100% and Active Life subweights total 100%;
- FIRE and Active Life scores are bounded and deterministic;
- seasonal, part-year, and full-relocation eligibility differ correctly;
- no residence route blocks full relocation only;
- age thresholds use actual age and boundary values;
- profile-dependent eligibility remains conditional when inputs are absent;
- missing or stale critical evidence follows validation rules;
- country inheritance and destination overrides resolve correctly;
- resilience costs do not double-count shared healthcare, travel, visa/admin, or contingency categories;
- work permissions modify Stay Flexibility only;
- tax warnings vary by mode, days, and broad home-tax context without calculating liability;
- missing score inputs never become an implicit zero; and
- tie-breaking is stable and documented.

### Static, SEO, and integration tests

- the build emits `artifacts/fire-abroad/index.html`;
- title, meta description, canonical, H1, breadcrumb, and structured data are valid;
- useful default rankings and methodology are present without JavaScript;
- the page is included in the sitemap and required internal-link surfaces;
- every rendered destination and calculator link resolves;
- calculator links contain only destination, household, and housing allowlisted values;
- no sensitive fields enter analytics payloads, URLs, or generated HTML; and
- source, confidence, and review dates render for critical claims.

### Interaction and visual verification

Exercise all three stay modes, age boundaries, households, housing states, incomplete-profile states, and at least one US-person warning scenario. Check 320, 375, 390, 430, 736, and 1024 pixel widths for legibility, focus treatment, table/list reflow, and no horizontal overflow. Confirm that the page remains understandable when scripts are disabled.

## Rollout and Success Measures

Deploy the single canonical page after data validation, unit tests, static build checks, and responsive verification pass. Do not launch destination-specific FIRE pages in this release.

Track non-sensitive events for page view, stay-mode change, activity-filter use, destination-guide click, and calculator handoff. Evaluate the first release using:

- organic impressions and click-through rate for FIRE Abroad and related early-retirement queries;
- calculator handoff rate;
- destination and country-guide click-through rate;
- engagement with stay modes and activity filters; and
- evidence freshness and percentage of launch destinations remaining fully rankable.

Search performance is an observation target, not a guaranteed outcome. Expansion should follow evidence quality and demonstrated user interest rather than page-count goals.
