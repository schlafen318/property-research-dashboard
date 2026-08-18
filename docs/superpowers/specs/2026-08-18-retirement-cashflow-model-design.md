# Retirement cash-flow model design

## Objective

Replace the interactive calculator's default withdrawal-rate method with a transparent annual cash-flow model. Required retirement capital will be derived from the user's living expenses, inflation assumptions, reliable outside income, retirement horizon, and expected portfolio return after fees.

The change also adds a **Buy now** housing plan, clarifies that the monthly spending field represents living expenses, and removes the portfolio-style illustration that does not affect required capital.

## Scope

This design applies to the interactive calculator at `/retirement-abroad-calculator/`.

The static destination benchmark tables remain a separate standardized comparison using their documented 3.5% withdrawal assumption. Their copy must distinguish that comparison methodology from the personalized cash-flow calculator.

The model is a deterministic planning estimate. It will not claim a probability of success and will not model market volatility, sequence-of-returns risk, taxes, portfolio rebalancing, mortality, or bequests.

## Inputs

### Core planning inputs

- Current age.
- Planned retirement age.
- Retirement horizon in years.
- Household type.
- Destination.
- Housing plan.
- Monthly retirement living expenses expressed in today's USD.
- Reliable after-tax income streams.
- Expected annual portfolio return after fees.

Expected portfolio return is a required user input with no prefilled value. The accepted range is -5% to 15%. The UI explains that it is a straight-line assumption rather than a guaranteed return.

### Inflation inputs

- General inflation.
- Healthcare inflation.
- Property inflation.

Destination defaults continue to populate these fields. The monthly living-expense benchmark continues to scale the destination's underlying spending categories proportionally.

### Removed inputs

- Withdrawal-rate override.
- Portfolio style.
- Portfolio cash yield.

## Living-expense treatment

The field label becomes **Monthly retirement living expenses (today's USD)**. It represents the intended destination lifestyle after retirement, expressed at today's prices; it is not the user's current pre-retirement household spending.

Its guidance changes with the housing plan:

- **Rent:** includes rent and other monthly living expenses.
- **Already own:** includes owner running costs and other monthly living expenses; no new property purchase.
- **Buy now:** includes owner running costs after purchase and other monthly living expenses; the purchase budget is separate.
- **Buy at retirement:** includes owner running costs after purchase and other monthly living expenses; the purchase budget is separate.

The monthly amount is annualized internally. It scales food, transport, utilities, healthcare, discretionary expenses, and the applicable housing-running-cost benchmark without treating the property purchase as spending.

## Annual cash-flow calculation

Let:

- `Y` be years until retirement.
- `N` be the retirement horizon in years.
- `r` be the user's expected annual portfolio return after fees.
- `t` be a retirement year index from `0` through `N - 1`.

For each expense category `c` with today's annual amount `E_c` and inflation rate `i_c`:

```text
expense(c, t) = E_c × (1 + i_c)^(Y + t)
```

For each reliable income stream `j` with today's annual amount `I_j`:

```text
income(j, t) = I_j × (1 + general inflation)^(Y + t)  when inflation-linked
income(j, t) = I_j                                      when fixed nominal
```

The annual funding gap is calculated independently for every year:

```text
funding_gap(t) = max(0, total_expenses(t) - total_income(t))
```

Required liquid portfolio capital at the retirement date is the present value of those annual gaps:

```text
liquid_portfolio = Σ funding_gap(t) / (1 + r)^t, for t = 0 ... N - 1
```

Year zero is undiscounted because the first retirement-year withdrawal begins at the retirement date. The model assumes the entered return is earned smoothly. It does not infer safety from that return.

The liquid portfolio is allowed to amortize to zero at the end of the selected horizon. The model does not include a bequest or minimum ending-balance target.

The emergency reserve remains separate:

```text
emergency_reserve = first_year_expenses / 12 × reserve_months
retirement_capital = liquid_portfolio + emergency_reserve
```

The first-year implied withdrawal percentage is an output:

```text
implied_first_year_withdrawal = first_year_funding_gap / liquid_portfolio
```

It is displayed only when liquid portfolio capital is greater than zero and is labeled as descriptive, not safe or recommended.

## Housing plans and property timing

### Rent

- Living expenses include rent.
- Property purchase capital is zero.

### Already own

- Living expenses include owner running costs instead of rent.
- Property purchase capital is zero.

### Buy at retirement

- Living expenses include owner running costs instead of rent.
- The editable home purchase budget is prefilled from the selected destination.
- Purchase capital is required at the retirement date:

```text
property_at_retirement = purchase_budget_today × (1 + property_inflation)^Y × (1 + acquisition_cost_rate)
```

- The retirement-date headline may combine retirement capital and property-at-retirement capital because both are expressed at the same date.

### Buy now

- Living expenses include owner running costs instead of rent.
- The editable home purchase budget is prefilled from the selected destination.
- Purchase capital is required today:

```text
property_today = purchase_budget_today × (1 + acquisition_cost_rate)
```

- Property inflation is not applied to the purchase.
- The UI shows **Home purchase needed now** in today's USD and **Retirement capital needed at retirement** separately. It must not add them into a single mixed-date headline.

## Results

The results panel keeps only decision-relevant outputs:

- Retirement capital needed at retirement.
- Liquid portfolio.
- Emergency reserve.
- Home purchase needed now or at retirement, when applicable.
- Retirement capital in today's dollars.
- First-year retirement living expenses.
- First-year reliable outside income.
- First-year funding gap.
- Expected portfolio return after fees.
- Implied first-year withdrawal percentage.

The portfolio cash-income and illustrative asset-sale outputs are removed with the portfolio-style control.

For Buy now, the two differently timed capital requirements are visually separate and explicitly dated. For Buy at retirement, a combined retirement-date total can be shown.

## Validation and error handling

- Expected return is required and must be between -5% and 15%.
- Retirement age must exceed current age.
- Retirement horizon must be positive.
- Spending, income, property budget, reserve months, and acquisition costs must be finite and non-negative.
- Inflation assumptions remain bounded by the existing limits.
- The engine rejects a return of -100% or below; the UI's narrower range prevents this condition in normal use.
- Invalid input focuses the first invalid control and displays a plain-language message.

## Explanatory copy and limitations

The calculator states that the estimate assumes the entered return occurs smoothly every year. Actual portfolios experience volatility and sequence-of-returns risk, so the result is not a safe-withdrawal recommendation or a probability-of-success analysis.

The methodology explains that expected return affects the discounted value of future funding gaps, whereas a label such as “balanced” is insufficient to determine return or risk. Users can change the return assumption to test sensitivity.

## Implementation boundaries

- `src/retirement_calculator.js` owns annual cash-flow projection, discounting, property timing, validation, and derived outputs.
- `src/retirement_calculator_ui.js` owns destination defaults, monthly-to-annual conversion, housing guidance, form visibility, and result labels.
- `src/build_unified_app.py` owns calculator markup and indexable methodology copy.
- No financial inputs are persisted or transmitted.
- Existing analytics retain destination, household, housing plan, and horizon bands but do not transmit spending, income, return, property budget, or result values.

## Verification

Automated tests must cover:

- Zero-return capital equals the undiscounted sum of annual funding gaps.
- A higher positive return lowers required liquid capital for the same cash flows.
- Higher inflation raises required capital when other inputs are unchanged.
- Fixed and inflation-linked income follow different paths.
- Annual funding gaps floor at zero independently each year.
- Implied first-year withdrawal is derived from the calculated portfolio.
- Buy now uses today's purchase budget plus acquisition costs without property inflation.
- Buy at retirement applies property inflation through the retirement date.
- Rent and Already own require no purchase capital.
- Monthly spending is annualized and uses rent or owner costs according to the selected plan.
- Changing destination resets the purchase budget to that destination's benchmark.
- Changing housing plans preserves a user-edited purchase budget where appropriate.
- Removed portfolio-style, cash-yield, and withdrawal-rate controls are absent from the personalized form.
- Static benchmark content and structured data remain indexable.

Browser verification must cover all four housing plans, destination changes, a custom property budget, a custom expected return, result timing labels, narrow-screen layout, and production behavior after deployment.
