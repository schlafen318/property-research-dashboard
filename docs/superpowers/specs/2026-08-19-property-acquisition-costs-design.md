# Property Acquisition Costs Design

## Purpose

Global Home Atlas currently compares an indicative 100 m² retirement-home property price across 30 destinations. That estimate excludes the taxes, statutory charges, professional fees, and foreign-buyer costs required to complete a purchase. This design adds a comparable acquisition-cost layer without implying that one generic buyer profile captures every legal or tax outcome.

The feature must answer two separate questions:

1. What property price does the standardized retirement-home archetype imply?
2. How much additional capital would the agreed baseline buyer normally need to acquire it?

Property-price evidence and acquisition-cost evidence remain separate. A high-confidence tax source must not improve the evidence label of a proxy property benchmark.

## Agreed Baseline Scenario

The comparable base case is:

- A nonresident foreign individual.
- A cash purchase with no mortgage or financing costs.
- A second home rather than a primary residence.
- A completed resale property rather than an off-plan or newly constructed unit.
- The existing indicative 100 m² retirement-home archetype: two bedrooms, two bathrooms, move-in ready, upper-middle market, and a managed apartment, condominium, or closest local equivalent.
- No first-time-buyer, treaty, residency, citizenship, family, age, or investment-program relief.
- Direct personal ownership where that is legally plausible for the target asset. Required leasehold, company, trust, quota, permit, or approval routes are disclosed separately.

The baseline is deliberately generic. Nationality- or residency-dependent items must be marked conditional unless they apply to all nonresident foreign individuals represented by the base case.

## Chosen Approach

Use a comparable base-cost estimate with conditional overlays.

The base total includes costs that are mandatory or normally unavoidable for the baseline transaction. Conditional items are shown separately and do not enter the comparable total unless their applicability is certain. This is preferable to a worst-case model, which would overstate many destinations, and to a full citizenship/residency calculator, which would require a substantially larger legal-rule engine and user-profile surface.

## Cost Boundaries

### Included in the comparable acquisition estimate

- Transfer, conveyance, stamp, or registration taxes applicable to the baseline resale purchase.
- Mandatory land-registry, title-registration, cadastral, or government filing charges.
- Mandatory notary or conveyancing charges.
- Legal fees when independent representation is legally required or effectively unavoidable for a normal foreign-buyer transaction.
- Universally applicable nonresident or foreign-buyer surcharges.
- Mandatory purchase permits or approvals with a determinable charge.
- Buyer-paid brokerage fees only where the buyer normally bears them.

### Conditional and displayed separately

- Nationality-, treaty-, visa-, residence-, or domicile-dependent surcharges and exemptions.
- New-build VAT, GST, sales tax, or developer charges.
- Mortgage registration, valuation, lender counsel, and financing charges.
- Entity, company, trust, nominee, usufruct, leasehold, or other ownership-structure setup costs.
- Quota, permit, or approval costs that depend on the exact buyer, asset, municipality, or canton.
- Buyer-agent fees that are optional or negotiable.
- Inspection, survey, translation, apostille, power-of-attorney, and due-diligence costs that are prudent but not universally mandatory.
- Renovation, furnishing, moving, and utility-connection costs.

### Excluded from acquisition costs

- Annual property tax.
- HOA, condominium, or service charges.
- Insurance.
- Maintenance and capital expenditure.
- Vacancy, empty-home, wealth, or second-home taxes charged after acquisition.
- Lease renewal, ground rent, or recurring land-use charges.
- Rental licensing and operating costs.
- Exit taxes, agent fees, and capital-gains tax.

Recurring ownership costs should become a separate future comparison layer rather than being blended into upfront capital.

## Data Architecture

Create `data/acquisition_costs.json` as the auditable research dataset. The file contains one global buyer profile and exactly one destination record for every destination in `data/destinations.json`.

Top-level structure:

```json
{
  "as_of": "2026-08-19",
  "reporting_currency": "USD",
  "buyer_profile": {
    "residency": "nonresident",
    "buyer_type": "individual",
    "use": "second_home",
    "financing": "cash",
    "property_market": "resale",
    "reliefs": "none"
  },
  "destinations": []
}
```

Each destination record must contain:

```json
{
  "destination_id": "valencia",
  "local_currency": "EUR",
  "jurisdiction_basis": "Valencian Community; Valencia municipality where a local charge requires it",
  "purchase_route": {
    "status": "available",
    "label": "Direct individual ownership",
    "notes": "Foreign-buyer eligibility still requires local legal verification."
  },
  "components": [],
  "sources": [],
  "confidence": "high",
  "reviewed_on": "2026-08-19",
  "review_notes": ""
}
```

`purchase_route.status` is one of `available`, `conditional`, or `unavailable`. A conditional or unavailable route must never be silently presented as an ordinary purchasable home.

Each component must contain:

```json
{
  "id": "transfer_tax",
  "label": "Property transfer tax",
  "category": "tax",
  "inclusion": "base",
  "calculation": {
    "type": "progressive",
    "tax_base": "purchase_price",
    "brackets": [
      {"up_to": 100000, "rate": 0.05},
      {"up_to": null, "rate": 0.08}
    ]
  },
  "estimate_strategy": "statutory",
  "source_ids": ["tax-authority-transfer-tax"],
  "notes": ""
}
```

Supported calculation types:

- `fixed`: one local-currency amount.
- `rate`: one rate multiplied by the declared tax base.
- `progressive`: ordered, non-overlapping local-currency brackets.
- `fixed_plus_rate`: fixed amount plus a percentage.
- `range_rate`: minimum and maximum rates where the exact rate is property- or municipality-dependent.
- `range_fixed`: minimum and maximum local-currency amounts.
- `manual`: a sourced central estimate and range only when the rule cannot be represented safely by the other types.

Each variable component must declare `estimate_strategy` as `statutory`, `midpoint`, `lower_bound`, `upper_bound`, or `manual`. The comparable central estimate uses statutory values where exact and the midpoint where a sourced normal range is unavoidable. The UI must retain and display the low/high range.

Every source record must contain:

```json
{
  "id": "tax-authority-transfer-tax",
  "name": "Official authority name",
  "url": "https://example.gov/official-page",
  "source_type": "official",
  "metric_supported": "Transfer-tax rates and brackets",
  "source_date": "2026-01-01",
  "accessed_on": "2026-08-19",
  "notes": "English summary used; local-language rule cross-checked."
}
```

## Research Standard

Research all 30 destinations. Use this source hierarchy:

1. National, regional, cantonal, state, provincial, or municipal tax authorities.
2. Official land registries, government buyer guides, legislation, or statutory fee schedules.
3. Major accounting or law firms explaining the primary rule.
4. Established property research providers only when primary or professional sources do not publish the needed normal-cost range.

Agent pages, developer marketing, unsourced blogs, search-result snippets, and AI-generated summaries cannot be the sole support for a base component.

Every base component requires at least one source. Progressive tax rules and foreign-buyer surcharges require a primary or professional source. Every source must use HTTPS, contain an access date, and identify the exact metric it supports.

When a destination spans multiple tax jurisdictions, select and disclose a representative jurisdiction consistent with the property-price archetype. If no single jurisdiction is defensible, model a sourced range and mark the destination cost evidence as proxy. Examples include Lake Tahoe's state boundary, Algarve/Cascais, Phuket/Koh Samui, and Swiss multi-canton resort groupings.

## Calculation Engine

Create a focused module, `src/acquisition_costs.py`, rather than expanding the already large static-site builder.

The public calculation interface is:

```python
def calculate_acquisition_costs(
    destination: dict,
    property_price_usd: float,
    fx_rates_to_usd: dict[str, float],
) -> dict:
    ...
```

The engine converts the USD property estimate to local currency using the same dated FX snapshot used by the dashboard. It applies local-currency thresholds and amounts, then converts every result back to USD without rounding intermediate values.

The result contains:

```python
{
    "property_price_usd": 384000.0,
    "base_cost_low_usd": 42000.0,
    "base_cost_estimate_usd": 44500.0,
    "base_cost_high_usd": 47000.0,
    "base_cost_rate": 0.115885,
    "all_in_low_usd": 426000.0,
    "all_in_estimate_usd": 428500.0,
    "all_in_high_usd": 431000.0,
    "all_in_usd_per_m2": 4285.0,
    "components": [],
    "conditional_components": [],
    "purchase_route": {},
    "confidence": "high",
}
```

Base rates are calculated against the unrounded standardized property-price estimate. `all_in_usd_per_m2` uses the archetype's exact 100 m² area. Display rounding happens only in rendering helpers.

## Validation and Failure Behavior

The build must fail with a destination-specific error when:

- A destination record is missing or duplicated.
- A base component has no source.
- A source URL is not HTTPS.
- A calculation type is unsupported.
- A fixed amount or rate is negative.
- A range has `minimum > maximum`.
- Progressive brackets are unordered, overlapping, empty, or lack an open-ended final bracket.
- The local currency lacks an FX rate.
- A conditional component is accidentally included in the base total.
- A purchase route is conditional or unavailable but has no explanatory note.
- The property price or archetype area is zero or negative.

Unknown or genuinely unquantifiable costs are not converted to zero. They remain conditional with an explicit explanation. An unavailable purchase route may still show statutory transaction-cost research for context, but the UI must not present an ordinary all-in purchasable total.

## Evidence and Confidence

Add a separate `acquisition_cost_confidence` value to each calculated result. Accepted values are `low`, `medium`, `medium-high`, and `high`.

Confidence reflects source authority, rule specificity, jurisdiction fit, and how much of the total is modeled from ranges. It is independent of `comparison_home_evidence`.

Country aggregates are conservative:

- Show `aligned` only when every included destination has an available route and high or medium-high acquisition-cost confidence.
- Otherwise show `mixed/proxy`.
- Do not calculate a country average from an unavailable route.
- Clearly state how many destinations contribute to the country figure.

## User-Facing Surfaces

Use minimal additions to existing surfaces.

### Dashboard destination card

Show:

- Indicative 100 m² property price.
- Acquisition costs as a central USD estimate and effective percentage.
- All-in acquisition capital.
- Low/high range when a component is variable.
- Purchase-route status and acquisition-cost confidence.
- One compact disclosure for conditional costs.

### Dashboard comparison table

Add rows for:

- Property price.
- Acquisition costs.
- All-in acquisition capital.
- Effective acquisition-cost percentage.
- Purchase-route status.
- Acquisition-cost evidence.

### Destination pages

Add an `Acquisition Cost` section showing the component breakdown, range, sources, conditional items, jurisdiction basis, buyer scenario, and data date. The hero may show all-in capital only when the purchase route is available or clearly conditional.

### Country comparison and country hubs

Show a conservative average all-in acquisition figure, contributor count, and aggregate evidence status. Exclude unavailable routes from the numeric average and disclose the exclusion.

### Guides, exports, and memo

- Guide tables and cards show all-in capital with a short acquisition-cost status.
- JSON exports include the complete methodology, source records, and calculated components.
- CSV exports include property price, acquisition-cost low/estimate/high, effective rate, all-in low/estimate/high, route status, confidence, jurisdiction basis, and source date.
- Shortlist memos include the component summary and conditional-cost warning.

### Methodology and research standards

Document the buyer profile, cost boundaries, midpoint treatment, FX treatment, jurisdiction selection, conditional-cost treatment, and source hierarchy.

## Testing Strategy

Use test-driven development.

Unit fixtures must cover:

- A simple percentage tax.
- A fixed statutory fee.
- A fixed-plus-percentage fee.
- Progressive brackets at, below, and above boundaries.
- Rate and fixed ranges with midpoint central estimates.
- A foreign-buyer surcharge included in the base total.
- A conditional surcharge excluded from the base total.
- Local-currency threshold calculation and USD conversion.
- An unavailable purchase route.
- Every validation failure listed above.

Dataset tests must assert:

- Exactly 30 unique destination records.
- Exact ID parity with `data/destinations.json`.
- Every base component is sourced.
- All sources are HTTPS and dated.
- Every destination has a route status, jurisdiction basis, confidence, and review date.
- Every calculated result is finite and internally reconciles: property price plus acquisition cost equals all-in capital.

Generated-artifact integration tests must use a temporary artifact directory and verify the dashboard, one aligned destination, one proxy destination, one conditional route, the country comparison, methodology page, JSON payload, CSV code path, and shortlist memo labels.

Run the complete repository test suite and static-site verifier before completion.

## Delivery Sequence

1. Add schema fixtures, validation, and failing dataset tests.
2. Research and populate all 30 destination records with traceable sources.
3. Implement the pure calculation engine and unit tests.
4. Integrate calculated results into the builder's enriched destination data.
5. Update dashboard and destination surfaces.
6. Update country, guide, export, memo, methodology, and research-standard surfaces.
7. Regenerate artifacts and run calculation reconciliation, full tests, static verification, and code review.

## Non-Goals

- Personalized tax or legal advice.
- A citizenship/residency questionnaire.
- Mortgage comparisons.
- New-build versus resale toggles.
- Annual holding-cost or exit-cost modeling.
- Live tax or FX APIs.
- Automatic scraping or unsupervised legal-data updates.

Those capabilities can be designed later after the baseline acquisition-cost dataset is stable and reviewed.
