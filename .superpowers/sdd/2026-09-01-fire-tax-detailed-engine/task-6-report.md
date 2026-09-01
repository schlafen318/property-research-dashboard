# Task 6 report: detailed FIRE tax refinement UI

Date: 2026-09-01

Base revision: `d446aef`

Round 1 integration base: `3573eb5`

## Outcome

The retirement calculator now publishes one real, executable exact profile: **Hong Kong home jurisdiction → Dubai destination**. It is a narrow destination-and-home result, not a destination-only estimate. Unsupported profiles and material facts fail closed with a specific plain-language reason.

The normal calculator remains non-technical. Dubai selection reveals the native home-jurisdiction control, and Hong Kong is its only production option. Exact refinement appears only after a required after-fees-and-tax return is entered. A separate detailed form then asks only facts that can change an enabled branch; every answer is retained in memory and re-routes the remaining questions.

## Supported profile boundary

Exact access currently requires all of the following:

- at least 183 UAE days under the supported domestic-residence route;
- no continuing Hong Kong treaty residence;
- no Hong Kong-source services, business, property income, Hong Kong pension-fund amount, or retained Hong Kong property;
- retirement or UAE employment salary only, with no natural-person business or consulting activity;
- ordinary personal investments rather than MPF or another retirement-scheme withdrawal;
- a cash purchase, if buying, of a Dubai villa or apartment;
- property-specific service charge and municipality housing-fee amounts supplied by the user, with zero allowed when already included in living expenses;
- a supported keep, sale, qualifying first-degree-family gift, or inheritance path; and
- for a gift, a value high enough that the DLD AED 2,000 minimum is not the controlling branch.

Mixed inflation-linking choices across non-zero dependable-income streams are also rejected because the approved retirement integration currently accepts one dependable-income indexing treatment. These restrictions are stated on-site; the implementation does not assume an adviser handoff.

## Live calculation and UI

- No production rule bundle contains personalized amounts. The detailed profile is normalized from live age, retirement timing, horizon, monthly retirement spending, pension/other/rental income, portfolio withdrawals, property price/use/timing, current monthly income, invested share, return, inflation and reserve inputs, plus detailed material answers.
- User-supplied annual property service/housing fees enter retirement spending, and supported DLD purchase fees enter acquisition capital. Sale/gift/inheritance registration fees remain separately reconciled lifecycle effects.
- The result is hidden until calculation and uses one table comparing plain-language branch, annual tax, after-tax dependable income, annual property fees, lifecycle registration fees and capital needed today.
- Expandable audit lines link the controlling official sources and expose formula, assumptions, exclusions, rule IDs, tax year and confidence.
- The dedicated form uses native labels, fieldsets, radio/select/number controls, `required` validation, keyboard behavior and ARIA live status updates.
- Unsupported destinations have no home-jurisdiction choice or refine entry point. Unsupported pair/fact combinations cannot run.

## Official rule sources

All production legal and tax rules use current primary government sources with claim-level IDs, effective dates and 2026-09-01 check dates:

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

Dubai was added to the ordinary retirement-cost dataset so the enabled tax destination is genuinely selectable. Its initial cost benchmark discloses current Numbeo observations, official Dubai household-expenditure context and DLD property evidence; users may replace every material cash-flow amount. UAE mortgage availability remains `research_incomplete`, and the exact tax profile separately permits cash purchases only.

## Verification

- Focused rules/UI/page/builder/cost suite: 154 tests passed.
- Full repository suite: 1,206 tests passed in 47.121 seconds after the final DLD gift-valuation correction.
- The non-vacuous static verifier selects the real pair, initializes a DOM, fills live inputs, routes every progressive answer, submits, renders the result, checks official links/plain branch/handoff state, rejects an unsupported pair, and traps history, storage, network and analytics calls. Result: 33 calculator destinations, one enabled profile, zero privacy calls, no detailed-tax errors.
- Real Chrome exact flow: calculated and rendered one reconciliation table with official audit links.
- Responsive widths 320, 375, 390, 430, 736 and 1024 CSS pixels: document width equalled viewport width and the result remained present.
- JavaScript-disabled Chrome: refine button remains hidden/disabled; detailed section and result remain hidden.
- `git diff --check`: clean.

The repository-wide static verifier still reports unrelated pre-existing generated-site problems: two missing Spain page markers and three missing Chamonix images. It reports no detailed-tax error.

## Privacy

Detailed answers/results remain in memory only. The flow does not write personal values to URLs, generated personal HTML, storage, analytics or network APIs.
