# Calculator Demand Validation Design

## Goal

Measure whether retirement-calculator users want saved plans before Global Home Atlas builds accounts and server-side storage.

## User experience

After the calculator produces a valid result, the compact result card shows one secondary action: **Save this plan**. Selecting it records a privacy-safe intent event and replaces the action with a plain-language message explaining that saved plans are being evaluated and that the user's figures were not stored. Calculation remains fully available without an account, email address, or gate.

The page must not add pills, badges, signup walls, repeated summaries, or an email form. The existing detailed projection remains below the input/result layout.

## Measurement

The calculator emits these demand-funnel events:

- `retirement_calculator_open` when the calculator initializes.
- `retirement_calculator_result_view` once per page load, after the first valid result is rendered.
- `retirement_calculator_save_intent` when the user selects **Save this plan**.
- Existing calculator cost-comparison, destination-change, and guide-click events remain unchanged.

Events must never contain spending, income, portfolio, property-price, total-capital, or other financial values. The result-view event has no custom financial parameters. The save-intent event uses the existing declarative click tracker and includes only its fixed label and destination URL context.

Production deployment must pass the optional `GA4_MEASUREMENT_ID` GitHub secret into the static build. Without that secret, events remain only in the visitor's local first-party queue and cannot validate aggregate demand.

## Acquisition

Keep one canonical calculator page. Retain the existing homepage, retirement-ranking, guide, country, and retirement-relevant destination links. Move the existing calculator callout earlier on the guide hub so it appears directly after the buying-goal routes; do not add a duplicate callout or new navigation item.

Each calculator callout click should include a fixed source label so acquisition routes can be compared without recording user-entered data.

## Decision rule

Evaluate after either four weeks or 300 qualified calculator visits, whichever is later. Proceed to account-backed saving when the observed funnel includes at least:

- 300 qualified calculator visits;
- 100 first valid results; and
- 15 save-intent clicks, or repeated direct requests for saved-plan functionality.

These are internal product thresholds, not industry benchmarks. Search Console clicks and impressions measure acquisition; GA4 events measure calculator engagement.

## Boundaries

- No Supabase project, authentication, account UI, database, or saved financial data.
- No silent browser persistence of calculator fields or results.
- No new programmatic destination pages.
- No paid-acquisition campaign in this release.
- No claim that a plan has been saved.

## Verification

- Generated markup exposes the save action only as part of the result experience and includes the honest non-storage message.
- The first-result event is emitted once per page load even when automatic recalculation runs repeatedly.
- The save action records exactly one declarative save-intent event per click.
- Calculator UI source contains no persistence or network APIs and no financial analytics keys.
- The deploy workflow passes the GA4 secret to the build.
- Existing internal calculator links remain present, and the guide-hub callout appears before the full guide catalog.
- Desktop and mobile layouts remain readable with no overlap or horizontal overflow.

