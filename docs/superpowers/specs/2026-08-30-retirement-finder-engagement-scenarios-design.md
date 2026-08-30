# Retirement Finder Engagement and Scenario Pages Design

## Goal

Turn retirement-finder results into a clearer decision path and a stronger organic-search entry point by adding concise match explanations, a three-destination comparison, five indexable capital-scenario pages, and privacy-conscious shared results.

## Principles

- Keep the existing recommendation order and financial methodology unchanged.
- Use the existing Global Home Atlas editorial design system.
- Write for readers seeking outcomes. Do not describe schemas, scoring, generation processes, or internal data handling in user-facing copy.
- Reuse the established terms: **Projected capital**, **Required capital**, **Within reach**, **Close**, **Stretch**, **Planning estimate**, and **Destination guide**.
- Avoid decorative badges, duplicated summaries, generic prose, and unnecessary controls.
- Never send financial values to analytics.

## Shared scenario architecture

One versioned scenario contract will support recommendation explanations, comparison, static capital pages, and shared-result URLs.

The contract is a read-only outcome snapshot. It excludes current age, current savings, contributions, salary, pension sources, and other raw financial inputs.

```ts
type FinderScenarioV1 = {
  v: 1;
  currency: string;
  projectedCapitalUsd: number;
  household: "single" | "couple";
  horizonYears: number;
  housingPlan: "rent" | "own" | "buy_now" | "buy_retirement";
  preferences: {
    region: string;
    climate: string;
    healthcare: "normal" | "high";
  };
  results: Array<{
    destinationId: string;
    retirementTargetUsd: number;
    surplusGapUsd: number;
    fundingRatio: number;
    tier: "within_reach" | "close" | "stretch";
    preferenceMatches: string[];
  }>;
  comparisonIds: string[];
  dataReviewed: string;
};
```

Constraints:

- `results` contains the full eligible ranked destination set so a shared view can reproduce the chart and allow comparison replacement without raw inputs.
- `comparisonIds` contains exactly three unique destination IDs when three eligible results exist; otherwise it contains every eligible result.
- Numeric fields must be finite and non-negative where applicable.
- Destination IDs must exist in the page payload.
- Decoding rejects unknown versions, invalid enums, duplicate IDs, excessive array lengths, and payloads above 16 KB.
- Shared URLs use base64url-encoded JSON in the `scenario` query parameter. They are read-only snapshots and do not repopulate the calculator form.

## Recommendation explanations and guide paths

The existing recommendation algorithm remains unchanged. The UI explains its existing outcome using at most three concise lines:

1. Affordability outcome, using projected capital, required capital, and the exact gap.
2. Preference alignment when a region, setting, healthcare, or long-stay signal applies.
3. Housing outcome, expressed in plain language for the selected housing plan.

Examples:

- “Lowest required capital among your matches.”
- “Matches your preference for Asia and coastal living.”
- “Renting keeps more of your capital available.”

Each of the strongest three recommendations links to:

- its destination guide;
- its country guide when one exists;
- the detailed retirement calculator preselected for that destination.

The result card does not expose scoring formulas or ranking mechanics.

## Three-destination comparison

The comparison appears after the recommendation summary and defaults to the strongest three recommendations.

It compares only distinct decision-useful fields:

- Required capital
- Gap versus projected capital
- Financial tier
- Monthly retirement cost
- Housing assumption
- Preference alignment
- Destination and country guide links

Users can replace any comparison destination from the eligible ranked list. Replacement is a native select control labeled by the destination being replaced. The comparison remains limited to three destinations and prevents duplicates.

Desktop uses a compact table with metrics as rows. Mobile stacks one destination at a time with the same metric order and no horizontal page overflow.

## Capital-scenario pages

Launch five canonical pages:

- `/retire-abroad-with-500k/`
- `/retire-abroad-with-750k/`
- `/retire-abroad-with-1-million/`
- `/retire-abroad-with-1-5-million/`
- `/retire-abroad-with-2-million/`

Each uses a canonical preset scenario:

- Capital at retirement: the page amount
- Household: couple
- Retirement duration: 30 years
- Housing: rent
- Reliable retirement income: none
- Region: no preference
- Setting: no preference
- Healthcare: important
- Retirement begins today, so no pre-retirement portfolio projection is applied

The recommendation engine will expose a projected-capital entry point that reuses the existing destination-target calculation and ordering logic while bypassing the accumulation projection.

Each page contains:

1. A search-intent H1 such as “Where can you retire abroad with $1 million?”
2. A concise answer stating how many destinations are Within reach and naming the strongest fit, or clearly stating that none are Within reach.
3. The assumptions in one compact section.
4. Destinations Within reach, followed by the closest alternatives when needed.
5. Required capital and exact surplus or shortfall for every shown destination.
6. Links to destination guides and relevant country guides.
7. A primary action to test a personal retirement plan.
8. Links to the other four capital scenarios.
9. A planning-estimate disclaimer and methodology link.

Pages must not imply that the capital amount guarantees retirement, visa eligibility, tax outcomes, healthcare access, or property-purchase eligibility.

## Shared results

The live finder shows a “Share results” action after calculation.

When activated:

- build and validate `FinderScenarioV1` from the current outcome;
- generate a same-page URL with the encoded scenario;
- copy the URL to the clipboard when supported;
- show the inline confirmation “Results link copied.”;
- provide a selectable URL fallback when clipboard access is unavailable.

A valid shared link opens a read-only results view containing:

- projected capital;
- strongest matches and concise explanations;
- capital landscape;
- comparison;
- data-review date;
- a primary action to calculate a personal plan.

The page shows one concise note before sharing: “This link includes your projected capital and planning choices. It does not include your age, current savings, income or pension details.”

Invalid, oversized, or outdated links show: “This results link cannot be opened. Start a new calculation.” The calculator remains usable.

## SEO and internal linking

Every scenario page receives a unique title, meta description, H1, canonical URL, Open Graph title and description, breadcrumb markup, and FAQ structured data where the visible FAQ supports it.

All five pages are included in the sitemap and linked from:

- the retirement destination finder;
- the retirement calculator;
- the retirement guide hub;
- one another.

Scenario-page text must be specific to the amount and outcome. Boilerplate is limited to assumptions, disclaimer, and methodology language.

## Analytics

Track only categorical engagement events:

- `retirement_destination_finder_compare_open`
- `retirement_destination_finder_compare_replace`
- `retirement_destination_finder_match_guide_click`
- `retirement_destination_finder_share`
- `retirement_destination_finder_shared_open`
- `retirement_capital_scenario_calculator_start`
- `retirement_capital_scenario_guide_click`

Allowed parameters are destination ID, comparison position, scenario slug, link type, and housing-plan category. Do not send capital, costs, gaps, ages, income, pensions, contributions, or encoded scenario payloads.

## Accessibility and responsive behavior

- Use semantic headings, lists, tables, links, buttons, labels, and native selects.
- Announce share success and comparison changes with `aria-live="polite"`.
- Preserve keyboard operation and visible focus styles.
- Use a table caption for the desktop comparison and equivalent headings in the mobile stacked layout.
- Results and controls must fit at 320 CSS pixels without page-level horizontal overflow.
- Shared-result errors use `role="alert"` without moving focus automatically.

## Error handling

- Schema construction fails closed and never creates a partial share URL.
- Decoder failures do not change calculator inputs or hide the calculator.
- Missing destination payload entries are omitted from shared results and comparison; the view explains when fewer than three remain.
- Scenario pages with no Within reach destinations lead with the closest alternatives and label every shortfall explicitly.
- Missing country guides omit that link rather than showing a disabled action.

## Testing and verification

Automated tests cover:

- scenario construction, validation, encoding, decoding, size limits, and version rejection;
- projected-capital recommendation parity with the existing ranking logic;
- concise explanation text and existing terminology;
- comparison defaults, replacement, duplicate prevention, and mobile markup;
- share success, clipboard fallback, invalid-link recovery, and analytics redaction;
- unique scenario-page metadata, headings, outcomes, cross-links, sitemap entries, and structured data;
- destination and country guide URL validity;
- page build and full repository regression suite.

Visual verification covers the finder, shared-result state, and all scenario-page templates at desktop, tablet, and mobile widths.
