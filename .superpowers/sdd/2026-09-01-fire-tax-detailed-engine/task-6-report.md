# Task 6 report: detailed FIRE tax refinement UI

Date: 2026-09-01
Base revision: `d446aef`

## Outcome

The retirement calculator now contains a progressive detailed-tax refinement runtime, but production exposes no exact-refinement entry point until a validated destination-and-home jurisdiction pair is available. Exact means the reconciled destination and continuing-home result; it is not a destination-only estimate.

The runtime is ready to accept a data-provided, profile-level bundle. Access requires all of the following:

- an explicitly enabled, non-synthetic destination;
- a selected home tax jurisdiction;
- the home jurisdiction in the destination's supported-home allow-list; and
- an executable destination-and-home rule/profile bundle.

Unsupported profiles receive the plain-language reason: “Complete current rules do not yet cover this destination together with your home tax jurisdiction.” The general server-rendered status says exact refinement remains unavailable until complete current rules cover both jurisdictions.

## Implementation

- Added `src/fire_tax_detailed_ui.js` with strict profile-level routing, native accessible material-question controls, in-memory answer handling, detailed calculation orchestration, one reconciled table, branch comparison, and expandable calculation/source audit.
- Embedded the approved residence, income, credit, property, detailed, explanation, profile, and detailed-UI engines in the retirement calculator page.
- Added a hidden server-rendered detailed section and fail-closed refine hook. Ordinary planning recalculation cannot reveal the hook unless the detailed runtime marked the current profile available.
- Added a validated page-payload builder that strips synthetic and non-official candidates. The current production payload contains no enabled jurisdiction.
- Added a behavioral static verifier. It executes routing for all calculator destinations, rejects synthetic exposure, exercises in-memory validated answers, and traps URL history, storage, and network access.
- Added a synthetic fully enabled destination-and-home bundle test that runs the approved detailed engine end to end and renders the reconciled result. The synthetic bundle is test-only and never appears in the generated site.

No personal tax answers are written to URLs, analytics, generated personal HTML, browser storage, or network APIs.

## UAE/Dubai research and enablement decision

UAE/Dubai was investigated as the first candidate using current primary government sources. The evidence supports several important domestic rules:

- The UAE government states that the UAE does not levy income tax on individuals. Source: [UAE Government — Taxation](https://u.ae/en/information-and-services/finance-and-investment/taxation), checked 2026-09-01; page current in 2026.
- The Federal Tax Authority states that a natural person enters corporate-tax scope only when conducting UAE business/business activity and business turnover exceeds AED 1 million in a calendar year; wages, personal investment income, and real-estate investment income are excluded from that test. Sources: [FTA — Basis of Taxation: Natural Person](https://tax.gov.ae/en/taxes/corporate.tax/corporate.tax.topics/basis.of.taxation.natural.person.aspx), last updated 2024-05-06, checked 2026-09-01; [FTA — Taxation of natural persons guide](https://tax.gov.ae/Datafolder/Files/Guides/CT/Taxation%20of%20natural%20persons%20-%2025%2011%202023.pdf), effective for relevant corporate-tax periods, checked 2026-09-01; [FTA — Real Estate Investment guide](https://tax.gov.ae/Datafolder/Files/Pdf/2024/Real-Estate-Investment-for-natural-persons-22-10-2024.pdf), published 2024, checked 2026-09-01.
- UAE domestic tax residence includes fact-dependent 183-day, 90-day, and centre-of-interests routes; treaty residence and tie-breakers must be evaluated under the applicable agreement. Sources: [FTA — Cabinet Decision No. 85 of 2022](https://tax.gov.ae/en/content/cabinet.decision.no.85.of.2022.on.determination.of.tax.residency.home.aspx), effective 2023-03-01, checked 2026-09-01; [FTA — Tax Resident and Tax Residency Certificate guide](https://tax.gov.ae/Datafolder/Files/Guides/VAT/VAT%20Guides/Tax-Resident-and-TRC--18-10-2024.pdf), published 2024, checked 2026-09-01.
- Dubai Land Department describes the 4% sale-registration fee as 2% seller and 2% buyer, subject to transaction-specific additional charges; gift registration is 0.125% of valuation with an AED 2,000 minimum for the stated qualifying relationships/conditions; inheritance title transfer has stated fixed registration and document/map fees. These are registration/service fees, not relabelled as income taxes. Sources: [DLD — Property Sale Registration](https://dubailand.gov.ae/en/eservices/property-sale-registration/), checked 2026-09-01; [DLD — Property Gift Registration](https://dubailand.gov.ae/en/eservices/property-gift-registration/), checked 2026-09-01; [DLD — Inheritance Title Transfer](https://dubailand.gov.ae/en/eservices/inheritance-title-transfer/), checked 2026-09-01; [DLD — registration fee legislation](https://dubailand.gov.ae/media/zrrd4qw4/en-legislation.pdf), checked 2026-09-01.
- Building service charges vary by property and are available through DLD's property-specific index, so no universal rate was invented. Source: [DLD — Service Charge Index](https://dubailand.gov.ae/en/eservices/service-charge-index-overview/service-charge-index), checked 2026-09-01.

UAE/Dubai remains disabled. A UAE domestic bundle cannot produce the promised exact FIRE result without a complete current home-jurisdiction residence, income, foreign-tax-credit, treaty, and continuing-property overlay for the user's actual home jurisdiction. Enabling UAE would therefore present a partial destination total as exact. No partial UAE business or property rule graph was added to production data.

## Tests and verification

TDD coverage was added for:

- strict destination-plus-home enablement and synthetic rejection;
- native labels, fieldsets, radio/select/number controls, typed answers, and contract validation;
- one reconciled result table, branch comparison, audit details, and official links;
- memory-only state and privacy traps;
- end-to-end calculation through a synthetic fully enabled pair;
- builder stripping of all production entry points while no complete pair exists;
- retirement UI protection against re-showing the refine control; and
- static-verifier rejection of a forged enabled-but-non-executable destination.

Fresh verification on 2026-09-01:

- `python3 src/build_unified_app.py` — exit 0.
- Focused detailed/page/UI/builder suite — 108 tests, all passed.
- `python3 -m unittest discover -s tests` — 1,197 tests, all passed in 48.754 seconds.
- Detailed-tax static runtime verifier — 32 destinations exercised, zero privacy calls, synthetic probe unavailable, no detailed-tax errors.
- `git diff --check` — clean.
- Browser checks at 320, 375, 390, 430, 736, and 1024 CSS pixels — no horizontal overflow; refine control hidden/disabled; detailed section hidden.
- JavaScript-disabled headless Chrome load — exit 0; the server-rendered refine control and detailed section remain hidden/disabled.

The repository-wide `scripts/verify_static_site.py` still exits 1 for unrelated pre-existing generated-site issues: two missing Spain page markers and three missing Chamonix image assets. It reports no detailed-tax runtime error.

## Remaining launch condition

Launch requires at least one complete, officially sourced destination-and-home pair that passes the existing rule validator and the executable full-bundle tests. Until then, the exact feature remains intentionally unavailable while the existing non-technical planning range continues to work.
