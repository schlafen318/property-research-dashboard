# Statutory Tax Range Design

**Date:** 2 September 2026  
**Status:** Approved direction; implementation specification for review

## Objective

Replace the initial FIRE and retirement calculators' product-defined tax-rate stress test with a transparent range anchored to current statutory destination tax rules. Remove questions users should not need to answer during screening, while keeping exact assumptions available in a detailed refinement.

The initial result is a planning estimate, not a tax return. It must never present a numerical destination tax range when the necessary statutory rule, source, or freshness evidence is incomplete.

## Coverage

The first implementation covers the jurisdictions whose FIRE tax screens are currently complete:

- Croatia
- Greece
- Indonesia
- Japan
- Portugal
- Spain
- Thailand
- Vietnam

The calculator may continue to show other destinations. For an unsupported or stale jurisdiction, it must show that the tax estimate is unavailable and exclude that destination from tax-adjusted ranking. It must not substitute generic percentage bands.

The initial statutory calculation models an individual or couple making a full-year relocation and funding retirement through a personal taxable investment portfolio plus the retirement-income categories already entered. It does not silently assume a pension treaty, tax-advantaged account wrapper, loss carry-forward, or home-country credit.

## Initial-screen inputs

Remove these controls from both the destination calculator and destination finder:

- Expected annual portfolio withdrawals
- How much of withdrawals may be realized gains

Continue collecting the existing nontechnical inputs: retirement spending, dependable retirement income, housing plan, portfolio assumptions, and destination.

The initial screen should show one estimated capital requirement and one planning range. It should not use the labels “favorable,” “central,” or “adverse.”

## Derived portfolio withdrawal

For each destination, calculate today's-money annual portfolio withdrawal as:

```text
annual living expenses
minus dependable annual retirement income
= portfolio withdrawal, floored at zero
```

Living expenses include the selected rent or recurring owner costs. They exclude a one-time property purchase and acquisition costs. Destination tax is also excluded from this first pass to avoid a circular input; the resulting annual statutory tax estimate is then added to expenses by the retirement engine.

The destination finder performs this calculation separately for every destination because living costs differ. The single-destination calculator derives it from the selected destination and the user's edited spending.

## Realized-gain uncertainty

The initial screen cannot infer actual cost basis from the existing inputs. It therefore uses a disclosed sensitivity range rather than asking the user for a technical estimate:

| Result | Portion of portfolio withdrawal treated as gain |
|---|---:|
| Lower end | 0% |
| Planning estimate | 50% |
| Upper end | 100% |

These percentages are product assumptions about cost basis, not tax rates or predictions. They bracket a withdrawal consisting entirely of returned capital through one consisting entirely of taxable gain. The detailed refinement replaces them with the user's actual cost basis or expected realized-gain amount.

## Statutory calculation

Each supported jurisdiction receives a versioned rule record for the applicable tax year. At minimum it must encode:

- tax residence scope used by the initial full-relocation assumption;
- treatment of gains on personally held listed securities;
- whether tax applies to gain, sale proceeds, remittance, or another statutory base;
- flat or progressive rates and thresholds;
- holding-period rules and material statutory exemptions;
- currency and rounding rules;
- effective date, checked date, review interval, official source identifiers, and confidence;
- conditions that make the result unavailable rather than calculable.

For each of the three disclosed gain-share assumptions:

1. Derive the annual portfolio withdrawal.
2. Derive the statutory tax base using the jurisdiction's base rule. A gain-based regime uses `withdrawal × gain share`; a proceeds-based regime uses the applicable proceeds amount instead.
3. Apply current statutory rates, thresholds, exemptions, and holding-period rules that can be supported by the screening profile.
4. Calculate dependable-income categories separately under their supported destination rules. Do not apply a capital-gains modifier to pensions or other income.
5. Add separately supported recurring property, wealth, and compliance amounts. Do not double-count property tax already included in owner costs.
6. Add the resulting annual destination tax to retirement expenses and rerun the retirement-capital calculation.

The displayed planning estimate uses the 50% gain-share result. The planning range uses the minimum and maximum capital requirements from the 0% and 100% gain-share results. If a jurisdiction's rule is not monotonic, the engine must calculate all three results and use their actual minimum and maximum.

## Income, home-country tax, and treaties

The initial range is destination-side. It must say so plainly. Pension, rental, interest, dividend, or other income is included only when the jurisdiction has a supported category rule for the information collected. Unsupported categories make the numerical tax result conditional or unavailable; they are not assigned a generic rate.

Home-country liability, treaty residence, foreign-tax credits, account wrappers, and source-country withholding require additional facts. The detailed refinement collects those facts and uses the existing category-level rule graph where a complete home-and-destination profile is enabled. The screening result must link to that refinement without implying that professional handoff is the only next step.

## User experience

The initial result uses this structure:

```text
Estimated amount needed
$1.29m

Planning range
$1.24m–$1.38m

This range uses current destination tax rules and assumes that 0%–100% of
portfolio withdrawals could be taxable gains. The estimate uses 50%.
```

“How this range is calculated” expands to show:

- calculated annual portfolio withdrawal;
- 0%, 50%, and 100% gain-share assumptions and their dollar gain amounts;
- statutory capital-gains rule applied, including tax year;
- separately calculated income and recurring property-related amounts;
- destination-side scope and known exclusions;
- linked official sources and last-checked date.

Technical category tables remain collapsed by default. The destination finder uses the same logic but keeps result cards compact; details appear on expansion or in the single-destination calculator.

## Data and engine boundaries

- `data/fire_tax_rules.json` remains the versioned statutory rule source and is expanded to the supported destination jurisdictions.
- `src/fire_tax_rules.py` validates completeness, dates, operands, rates, thresholds, conditions, and source references.
- The detailed tax primitives calculate residence, category income, gains, property amounts, and credits.
- `src/fire_tax_scenarios.js` becomes an orchestration adapter. It may select gain-share cases and summarize results, but may not contain generic destination tax rates.
- The calculator and finder derive withdrawals from their existing expense and income models before calling the statutory engine.
- Presentation code receives named estimate/range values plus explanations; it does not recalculate tax.

## Evidence and freshness standard

Every numerical statutory rule requires a primary official source where one is publicly available. A secondary professional source may clarify implementation but cannot be the sole basis for a rate or threshold when official material exists.

Each rule records its tax year, effective date, access date, review interval, and recheck trigger. A stale rule produces an unavailable result. Source links shown to users must support the specific rate, base, threshold, or exemption claimed.

## Validation and testing

Implementation follows test-driven development. Required coverage includes:

- withdrawal derivation for renters, owners, property buyers, and income exceeding expenses;
- per-destination withdrawal derivation in the finder;
- 0%, 50%, and 100% gain-share cases;
- gain-based, proceeds-based, progressive, flat, exempt, holding-period, and remittance-dependent rules;
- separation of pension/other income from capital gains;
- no double-counting of recurring property tax;
- unsupported, incomplete, stale, and non-applicable outcomes;
- source and explanation completeness;
- calculator and finder UI removal of both technical inputs;
- plain-language estimate/range labels and disclosures;
- desktop and mobile interaction tests;
- static build verification and live browser checks after deployment.

Each country fixture must include boundary examples derived from its documented statutory rules. Cross-jurisdiction tests must prove that removing or staling a required source disables the numerical result.

## Migration and release

The old product-defined `planning_bands` and `gain_intensity_modifiers` are removed from runtime calculation after all eight covered jurisdictions pass the statutory-rule contract. They may remain temporarily in data only during migration and must then be deleted to prevent accidental fallback.

Release is blocked unless all supported jurisdictions pass rule validation, the full test suite and static verifier pass, and visual checks confirm that both calculators communicate the range without technical questions. Deployment proceeds through the existing GitHub Pages workflow, followed by live verification of the calculator, finder, and FIRE pages.
