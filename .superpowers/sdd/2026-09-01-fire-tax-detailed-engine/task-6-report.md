# Task 6 report: detailed FIRE tax refinement UI

Date: 2026-09-01

Base revision: `d446aef`

Round 1 integration base: `3573eb5`

## Outcome

The retirement calculator now publishes one real, executable exact profile: **Hong Kong home jurisdiction → Dubai destination** for a renter with no separately sourced pension, other income, rental income, or owned property. It is a narrow destination-and-home result, not a destination-only estimate. Unsupported profiles and material facts fail closed with a specific plain-language reason.

The normal calculator remains non-technical. Dubai selection reveals the native home-jurisdiction control, and Hong Kong is its only production option. Exact refinement appears only after a required after-fees-and-tax return is entered. A separate detailed form then asks only facts that can change an enabled branch; every answer is retained in memory and re-routes the remaining questions.

## Supported profile boundary

Exact access currently requires all of the following:

- at least 183 UAE days under the supported domestic-residence route;
- no continuing Hong Kong treaty residence;
- no Hong Kong-source services, business, property income, Hong Kong pension-fund amount, or retained Hong Kong property;
- retirement or UAE employment salary only, with no natural-person business or consulting activity;
- ordinary personal investments rather than MPF or another retirement-scheme withdrawal;
- zero generic pension, other-income and rental-income amounts, because their payer/source country, treaty and withholding treatment is not collected by the initial screen;
- no owned property or purchase in the exact profile; and
- UAE employment salary only for any separately added dependable income.

Mixed inflation-linking choices across non-zero dependable-income streams are also rejected because the approved retirement integration currently accepts one dependable-income indexing treatment. These restrictions are stated on-site; the implementation does not assume an adviser handoff.

## Live calculation and UI

- No production rule bundle contains personalized amounts. The detailed profile is normalized from live age, retirement timing, horizon, monthly retirement spending, pension/other/rental income, portfolio withdrawals, property price/use/timing, current monthly income, invested share, return, inflation and reserve inputs, plus detailed material answers.
- Owned-property lifecycle calculation is deliberately unavailable. The official material validates several DLD registration fees and UAE real-estate corporate-tax/VAT boundaries, but does not establish every potentially applicable purchase, annual, gift and inheritance tax branch required for an exact total. A fee line is never used as evidence that a tax does not exist.
- The result is hidden until calculation and uses one table comparing plain-language branch, annual tax, after-tax dependable income, property effects and capital needed today; property effects are explicitly not applicable for the enabled renter profile.
- Expandable audit lines link the controlling official sources and expose formula, assumptions, exclusions, rule IDs, tax year and confidence.
- The dedicated form uses native labels, fieldsets, radio/select/number controls, `required` validation, keyboard behavior and ARIA live status updates.
- Unsupported destinations have no home-jurisdiction choice or refine entry point. Unsupported pair/fact combinations cannot run.

## Official rule sources

All enabled renter-profile legal and tax rules use current primary government sources with claim-level IDs, effective dates and 2026-09-01 check dates. These are the UAE taxation, UAE natural-person, UAE residence, Hong Kong territorial and Hong Kong–UAE treaty sources listed first below. The later property sources remain research evidence only and do not enable an exact owned-property result:

- [UAE Government — taxation](https://u.ae/en/information-and-services/finance-and-investment/taxation): no UAE individual income tax.
- [UAE Federal Tax Authority — natural persons](https://tax.gov.ae/en/taxes/corporate.tax/corporate.tax.topics/basis.of.taxation.natural.person.aspx): business/business-activity corporate-tax scope and explicit wage, personal-investment and real-estate-investment exclusions. Business/consulting is outside the enabled profile.
- [UAE Federal Tax Authority — Cabinet Decision No. 85 of 2022](https://tax.gov.ae/en/content/cabinet.decision.no.85.of.2022.on.determination.of.tax.residency.home.aspx): supported 183-day residence route, effective 2023-03-01.
- [Hong Kong IRD — non-resident individuals](https://www.ird.gov.hk/eng/tax/ind_nr.htm): Hong Kong territorial source exposure.
- [Hong Kong IRD — synthesised Hong Kong–UAE agreement](https://www.ird.gov.hk/eng/pdf/Synthesised_Text_HKSAR_UAE.pdf): residence/treaty framework and double-tax relief context.
- [Dubai Land Department — sale registration](https://dubailand.gov.ae/en/eservices/property-sale-registration/): 2% buyer and 2% seller shares, title/map/knowledge/innovation and trustee fees.
- [Dubai Land Department — gift registration](https://dubailand.gov.ae/en/eservices/property-gift-registration/): 0.125% valuation fee, AED 2,000 minimum, qualifying relationships and service fees.
- [Dubai Land Department — inheritance transfer](https://dubailand.gov.ae/en/eservices/inheritance-title-transfer/): current fixed transfer and service fees.
- [Dubai Land Department — service-charge index](https://dubailand.gov.ae/en/eservices/service-charge-index-overview/service-charge-index): property-specific approved service charges; no rate is invented.
- [Dubai Municipality — services](https://www.dm.gov.ae/dubai-municipality-services/): owned/leased-unit housing fee based on rental value; the billed amount is user supplied.
- [UAE Government — residential property VAT](https://u.ae/participate/-/media/Information-and-services/Finance-and-Investment/VAt-guidelines/vattreatmentofproperties-Eng.ashx?la=en): supported residential rent/sale VAT treatment.
- [Central Bank of the UAE — official exchange rates](https://www.centralbank.ae/umbraco/Surface/Exchange/GetExchangeRateAllCurrency): current AED conversion for AED-denominated fees.

Dubai was added to the ordinary retirement-cost dataset so the enabled tax destination is genuinely selectable. Its initial cost benchmark discloses current Numbeo observations, official Dubai household-expenditure context and DLD property evidence; users may replace every material cash-flow amount. UAE mortgage availability remains `research_incomplete`, and any owned-property plan is excluded from the exact profile.

## Verification

- Focused rules/UI/page/builder/integration suite: 180 tests passed.
- Full repository suite: 1,208 tests passed in 47.817 seconds after the final fail-closed source and property-boundary corrections.
- The non-vacuous static verifier selects the real pair, initializes a DOM, fills live inputs, routes every progressive answer, submits, renders the result, checks official links/plain branch/handoff state, rejects an unsupported pair, and traps history, storage, network and analytics calls. Result: 33 calculator destinations, one enabled profile, zero privacy calls, no detailed-tax errors.
- Real Chrome layout pass at 320, 375, 390, 430, 736 and 1024 CSS pixels found no horizontal overflow; JavaScript-disabled Chrome kept refinement and results hidden. The final legal narrowing did not change markup or layout. The current renter flow is additionally exercised through parsed emitted native controls by the static verifier.
- `git diff --check`: clean.

The repository-wide static verifier still reports unrelated pre-existing generated-site problems: two missing Spain page markers and three missing Chamonix images. It reports no detailed-tax error.

## Privacy

Detailed answers/results remain in memory only. The flow does not write personal values to URLs, generated personal HTML, storage, analytics or network APIs.

## Round 2 review fixes

- The public `runRefinement` path now requires live planning facts and merges every live fact over detailed answers before the same profile-access check used by the UI. Direct calls therefore fail closed for non-zero pension, other income, rental income or property amounts, unsupported housing/use, unsupported retirement accounts, and a missing or invalid after-fees-and-tax return.
- Renter property output is now `N/A`, including audit lines and both property columns in the reconciled table. The result says: “Owned-property calculation not applicable; include renter municipal/housing fees in annual spending.” No zero property-tax conclusion is shown.
- The former legal self-classification was removed. Progressive native controls now collect the Hong Kong–UAE agreement's factual Article 4 sequence: domestic Hong Kong day/ordinary-residence facts, permanent-home availability, closest personal/family and economic relations, habitual abode, and—only when needed—right of abode/nationality. Every judgment-sensitive choice includes `Not sure` and fails closed. Exact access proceeds only for a deterministic non-dual or UAE treaty outcome.
- Exact refinement is no longer suppressed merely because the broad destination estimate is unavailable. It remains independently gated by the complete supported home-to-destination profile and live facts.
- The reconciled table is inside a responsive horizontal scroll container. A real-browser pass initially found body overflow at 320–430px; the final rerun had no body or main overflow at 320, 375, 390, 430, 736 or 1024px.

Final Round 2 verification:

- Focused tax/page/UI suite: 261 tests passed in 24.433 seconds.
- Full repository suite: 1,211 tests passed in 49.727 seconds.
- Detailed static runtime evidence: zero errors. The repository-wide verifier remains non-zero only for the same unrelated Spain markers and three missing Chamonix image files recorded above.
- Real Playwright/Chrome: eligible renter completed using native controls and keyboard blur; initial submit was disabled with three required controls, follow-ups rerouted after each answer, the completed form had zero invalid controls, and the result contained one reconciled table, the plain-language branch, property `N/A`, and 57 official-source audit links. A currency change cleared detailed answers/results. A non-zero live pension hid exact access with the specific payer-country/treaty/withholding reason.
- A separate real browser context at 320px with `javaScriptEnabled: false` exposed the no-JavaScript fallback in the accessibility tree and exposed no refine/exact controls.
