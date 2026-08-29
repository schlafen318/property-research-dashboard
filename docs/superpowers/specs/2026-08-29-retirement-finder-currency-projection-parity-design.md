# Retirement Finder Currency and Projection Parity Design

## Goal

Bring the retirement destination finder into behavioral and visual alignment with the retirement abroad calculator wherever the two tools perform the same planning task. The finder must support the same planning currencies, money-entry conventions, retirement-income period, and projection presentation while preserving its distinct purpose: ranking many destinations from one financial scenario.

## Scope

This change covers:

- a planning-currency selector in the finder;
- comma-formatted monetary inputs;
- conversion between the selected currency and the USD-normalized calculation engines;
- monthly retirement-income inputs, matching the detailed calculator;
- selected-currency formatting for summaries, recommendation rows, exclusions, and projection tooltips;
- a projection chart that uses the detailed calculator's visual language;
- parity and regression tests across the two calculator experiences.

The retirement-cost, retirement-target, mortgage, and property-finance engines continue to calculate in USD. The detailed calculator's existing behavior is not redesigned.

## Non-goals

- Do not add live exchange-rate fetching.
- Do not persist financial inputs or selected currency.
- Do not transmit financial values through analytics.
- Do not merge the two calculators into one interface or one calculation engine.
- Do not pass financial values through links between the tools.
- Do not add an annual/monthly period toggle.

## Planning currency

The finder adds a `Planning currency` selector at the beginning of Step 1. It uses the same ordered choices and reference-rate dataset as the detailed calculator:

1. USD — US dollar
2. EUR — Euro
3. GBP — Pound sterling
4. CAD — Canadian dollar
5. AUD — Australian dollar
6. CHF — Swiss franc
7. JPY — Japanese yen
8. HKD — Hong Kong dollar
9. SGD — Singapore dollar

USD is always the default. A concise note states the reference-rate date and explains that selection changes presentation, not future currency-risk assumptions.

The finder page payload receives the same `planning_currencies` object as the detailed calculator. The UI converts selected-currency amounts to USD before calling the engines and converts USD engine results back to the selected currency for display. Conversion must never alter percentage, age, duration, household, preference, or categorical inputs.

Changing currency converts every populated monetary field once from the prior selected currency to the new selected currency. Each converted control observes its existing rounding step. Empty and invalid controls remain unchanged and must not silently become zero.

## Money inputs

The following finder controls become text inputs with numeric input mode and comma formatting:

- total liquid capital today;
- monthly amount invested;
- maximum capital allocated to a property purchase;
- monthly pension;
- monthly other dependable income.

Formatting occurs initially, after a valid currency conversion, and on blur. Parsing accepts digits, commas, and an optional decimal portion. Invalid characters remain visible and produce an accessible validation error; they are not coerced to zero.

Labels do not repeat currency codes. Currency is stated once through the selector. Default monetary values display as `500,000`, `2,000`, `300,000`, and `0` in USD.

## Retirement income

Step 3 is renamed `Income continuing after retirement (monthly)`. Pension and other dependable income default to `0`, and both `Inflation-linked` controls default to checked.

The UI converts each selected-currency monthly amount to USD, then multiplies by 12 before creating the engine's annual income streams. The engine contract remains annual USD, avoiding changes to retirement-target calculations.

## Result formatting

All finder monetary output uses the selected planning currency and no decimal places:

- capital today;
- monthly investing;
- closest-match gap in the plain-language result;
- projected portfolio;
- retirement target;
- surplus or gap;
- property equity;
- mortgage remaining;
- annual property cash flow;
- projection tooltip values and target label.

Destination affordability tiers and rankings remain based on USD-normalized values. Changing presentation currency cannot change ordering or tier assignment.

## Projection display

The existing basic green-bar chart is replaced with an SVG presentation consistent with the detailed calculator:

- a restrained editorial chart frame;
- readable year/age axis labels;
- accessible focus targets for each annual point;
- a dark tooltip panel with year, age, and projected portfolio;
- a horizontal reference line for the closest recommended destination's retirement target;
- selected-currency formatting throughout;
- the same motion and reduced-motion behavior as the detailed calculator.

For rent and buy-at-retirement scenarios, the chart uses the shared portfolio projection. The existing already-own route continues to direct users to the destination-specific calculator. For buy-now scenarios, each destination has a different property-finance projection; the chart uses the closest recommended destination's annual projection and explicitly labels it `Projection for [destination]`.

The finder engine adds the relevant annual projection to each recommendation. This is presentation data only and does not change ranking calculations. The chart presents total liquid portfolio rather than claiming a component breakdown that the property-finance model cannot support consistently across all housing plans.

If no recommendation or valid projection is available, the chart is hidden and the existing explanatory fallback remains visible.

## Visual parity

The finder retains its four-step form and destination-ranking results. Shared elements align with the detailed calculator:

- currency selector width and explanatory note;
- input typography, borders, focus treatment, and money formatting;
- result summary typography;
- chart colors, axes, tooltip, and target reference;
- regular-weight disclosure headings.

No decorative pills, badges, duplicated summaries, or repeated currency labels are added.

## Accessibility and privacy

- Every input retains an explicit label.
- Invalid money controls receive `aria-invalid` and a useful validation message.
- The projection remains a labelled image with a title and description.
- Every annual chart point is keyboard-focusable and has a complete accessible label.
- Currency selection and chart updates do not move focus unexpectedly.
- No financial input or calculated output is added to analytics events, storage, URLs, or network requests.

## Error handling

- Unsupported currencies cannot become the selected value.
- Missing or non-positive reference rates prevent conversion and leave the previous valid value intact.
- Empty money inputs remain empty during currency changes.
- Invalid money text is reported in the existing error summary.
- A missing projection hides the chart rather than rendering misleading zero bars.

## Testing

Implementation follows test-driven development.

Automated coverage must verify:

- the finder payload contains the same planning-currency dataset as the detailed calculator;
- USD is the default and SGD is available;
- currency conversion and currency formatting match the detailed calculator for representative values;
- money parsing, comma formatting, invalid text, and step-aware conversion;
- selected-currency inputs become USD engine inputs without changing rankings;
- monthly retirement income becomes annual USD exactly once;
- all monetary result surfaces use the selected currency;
- projection selection uses the shared series for non-buy-now plans and the closest recommendation's series for buy-now;
- chart tooltips and accessible labels include year, age, currency, and value;
- currency selection does not add financial values to analytics or storage;
- existing finder engine, calculator engine, page, UI, SEO, and full-site tests remain green.

## Acceptance criteria

The upgrade is complete when:

1. A user can enter and view the entire finder scenario in any supported planning currency.
2. Monetary inputs display thousands separators and retain valid values across currency changes.
3. The engines continue to receive normalized USD values.
4. Pension and other retirement income are clearly monthly and inflation-linked by default.
5. Every monetary result and projection label uses the selected currency.
6. The finder projection visually belongs to the same calculator family and works for every calculable finder housing plan without misrepresenting the model.
7. Finder rankings are invariant under presentation-currency changes.
8. Automated parity, accessibility, privacy, focused, and full-site tests pass.
