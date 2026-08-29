from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "src" / "retirement_destination_finder_ui.js"
CALCULATOR_UI = ROOT / "src" / "retirement_calculator_ui.js"


def run_module(ui_path: Path, function_name: str, payload: object) -> object:
    script = (
        "const ui = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(ui.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ui_path), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_ui(function_name: str, payload: object) -> object:
    return run_module(UI, function_name, payload)


def run_calculator_ui(function_name: str, payload: object) -> object:
    return run_module(CALCULATOR_UI, function_name, payload)


def run_ui_dom_scenario(payload: object) -> dict:
    script = r'''
const fs = require("fs");
const vm = require("vm");
const input = JSON.parse(process.argv[2]);

class FakeElement {
  constructor(id) {
    this.id = id;
    this.value = "";
    this.checked = false;
    this.hidden = false;
    this.disabled = false;
    this.dataset = {};
    this.min = "";
    this.step = "";
    this.textContent = "";
    this.innerHTML = "";
    this.listeners = {};
    this.attributes = {};
    this.classList = { toggle() {}, remove() {} };
  }
  addEventListener(name, callback) { (this.listeners[name] ||= []).push(callback); }
  dispatch(name) {
    const event = { preventDefault() {}, target: this };
    (this.listeners[name] || []).forEach((callback) => callback(event));
  }
  setCustomValidity(message) { this.validationMessage = message; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  querySelectorAll() { return []; }
  closest() { return null; }
  focus() {}
  scrollIntoView() {}
}

const elements = new Map();
function el(id) {
  if (!elements.has(id)) elements.set(id, new FakeElement(id));
  return elements.get(id);
}
const values = {
  "finder-currency": "USD",
  "finder-current-age": "50",
  "finder-retirement-age": "60",
  "finder-horizon": "30",
  "finder-household": "single",
  "finder-housing-plan": "rent",
  "finder-liquid-capital": "500,000",
  "finder-monthly-contribution": "2,000",
  "finder-return": "4",
  "finder-region": "any",
  "finder-climate": "any",
  "finder-healthcare": "normal",
  "finder-property-allocation": "300,000",
  "finder-purchase-method": "cash",
  "finder-buyer-residency": "non_resident",
  "finder-income-source": "overseas",
  "finder-requested-ltv": "60",
  "finder-mortgage-rate": "5",
  "finder-mortgage-term": "20",
  "finder-mortgage-treatment": "payoff",
  "finder-use-before-retirement": "personal",
  "finder-rental-yield": "5",
  "finder-vacancy-rate": "10",
  "finder-operating-cost-rate": "20",
  "finder-pension": "0",
  "finder-other-income": "0",
};
Object.entries(values).forEach(([id, value]) => { el(id).value = value; });
[
  ["finder-liquid-capital", "0", "1000"],
  ["finder-monthly-contribution", "0", "100"],
  ["finder-property-allocation", "0", "1000"],
  ["finder-pension", "0", "100"],
  ["finder-other-income", "0", "100"],
].forEach(([id, min, step]) => { el(id).min = min; el(id).step = step; });
el("finder-contribution-indexed").checked = true;
el("finder-pension-indexed").checked = true;
el("finder-other-income-indexed").checked = true;

const groups = ["buyNow", "mortgage", "rental", "buyAtRetirement"].map((name) => {
  const group = new FakeElement("group-" + name);
  group.dataset.finderGroup = name;
  const controlsByGroup = {
    buyNow: ["finder-property-allocation", "finder-purchase-method", "finder-use-before-retirement", "finder-mortgage-treatment"],
    mortgage: ["finder-buyer-residency", "finder-income-source", "finder-requested-ltv", "finder-mortgage-rate", "finder-mortgage-term"],
    rental: ["finder-rental-yield", "finder-vacancy-rate", "finder-operating-cost-rate"],
    buyAtRetirement: [],
  };
  group.controls = controlsByGroup[name].map(el);
  group.querySelectorAll = () => group.controls;
  return group;
});
const document = {
  activeElement: null,
  getElementById: el,
  querySelectorAll(selector) { return selector === "[data-finder-group]" ? groups : []; },
};
let engineInput = null;
const engineInputs = [];
let engineCalls = 0;
const window = {
  GHA: { track() {} },
  GHARetirementDestinationFinder: {
    recommendDestinations(request) {
      engineInput = request;
      engineInputs.push(request);
      engineCalls += 1;
      return {
        summary: { withinReachCount: 0, closeCount: 0, stretchCount: 0 },
        sharedProjection: null,
        recommendations: [],
        excluded: [],
      };
    },
  },
};
const context = { window, document, Intl, Number, String, Array, Set, Map, Math, JSON };
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), context);
window.GHARetirementDestinationFinderUI.initRetirementDestinationFinder("retirement-destination-finder", {
  planning_currencies: { rates_to_usd: input.rates },
  destinations: [],
  retirementCosts: [],
  mortgageProfiles: {},
});

if (input.invalidHiddenProperty) {
  el("finder-property-allocation").value = "not money";
  el("finder-property-allocation").dispatch("input");
}
if (input.submitBeforeCurrency) el("retirement-destination-finder-form").dispatch("submit");
if (input.currency) {
  el("finder-currency").value = input.currency;
  el("finder-currency").dispatch("change");
}
if (input.editLiquid) {
  el("finder-liquid-capital").value = input.editLiquid;
  el("finder-liquid-capital").dispatch("input");
}
if (input.submit) el("retirement-destination-finder-form").dispatch("submit");

process.stdout.write(JSON.stringify({
  currency: el("finder-currency").value,
  liquidDisplay: el("finder-liquid-capital").value,
  monthlyDisplay: el("finder-monthly-contribution").value,
  propertyDisplay: el("finder-property-allocation").value,
  propertyDisabled: el("finder-property-allocation").disabled,
  propertyError: el("finder-property-allocation").validationMessage || "",
  engineCalls,
  user: engineInput && engineInput.user,
  users: engineInputs.map((request) => request.user),
}));
'''
    result = subprocess.run(
        ["node", "-e", script, str(UI), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class RetirementDestinationFinderUITests(unittest.TestCase):
    def test_money_helpers_match_the_retirement_calculator(self) -> None:
        conversion = {
            "amount": 24000,
            "fromCurrency": "USD",
            "toCurrency": "SGD",
            "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
        }
        cases = (
            ("convertPlanningAmount", conversion),
            ("convertPlanningControlAmount", {**conversion, "step": 100}),
            ("parseMoneyInput", "2,000,000"),
            ("formatMoneyInputValue", 2000000),
            (
                "formatPlanningMoney",
                {
                    "amountUsd": 1000,
                    "currency": "SGD",
                    "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
                },
            ),
        )
        for function_name, payload in cases:
            with self.subTest(function_name=function_name):
                self.assertEqual(
                    run_calculator_ui(function_name, payload),
                    run_ui(function_name, payload),
                )

    def test_money_helpers_reject_invalid_input_and_missing_rates(self) -> None:
        for value in ("36,3x9", None):
            with self.subTest(value=value):
                self.assertIsNone(run_ui("parseMoneyInput", value))
        self.assertIsNone(
            run_ui(
                "convertPlanningAmount",
                {"amount": 100, "fromCurrency": "USD", "toCurrency": "XYZ", "ratesToUsd": {"USD": 1}},
            )
        )

    def test_currency_switch_uses_canonical_usd_for_untouched_money_inputs(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1, "EUR": 0.91},
                "submitBeforeCurrency": True,
                "currency": "EUR",
                "submit": True,
            }
        )

        self.assertEqual("EUR", scenario["currency"])
        self.assertEqual("549,000", scenario["liquidDisplay"])
        self.assertEqual("2,200", scenario["monthlyDisplay"])
        self.assertEqual(500000, scenario["user"]["totalLiquidCapital"])
        self.assertEqual(2000, scenario["user"]["monthlyPortfolioContribution"])

        from tests.test_retirement_destination_finder import (
            cost_record,
            destination,
            mortgage_profile,
            run_finder,
        )

        destinations = [destination("first"), destination("second")]
        common = {
            "destinations": destinations,
            "retirementCosts": [cost_record("first", 150000), cost_record("second", 180000)],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        usd = run_finder("recommendDestinations", {**common, "user": scenario["users"][0]})
        eur = run_finder("recommendDestinations", {**common, "user": scenario["users"][1]})
        self.assertEqual(
            [(item["destinationId"], item["tier"]) for item in usd["recommendations"]],
            [(item["destinationId"], item["tier"]) for item in eur["recommendations"]],
        )

        edited = run_ui_dom_scenario(
            {
                "rates": {"USD": 1, "EUR": 0.91},
                "currency": "EUR",
                "editLiquid": "550,000",
                "submit": True,
            }
        )
        self.assertEqual(500500, edited["user"]["totalLiquidCapital"])

    def test_hidden_invalid_property_money_does_not_block_rent_submission(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1, "EUR": 0.91},
                "invalidHiddenProperty": True,
                "submit": True,
            }
        )

        self.assertEqual("not money", scenario["propertyDisplay"])
        self.assertTrue(scenario["propertyDisabled"])
        self.assertEqual(1, scenario["engineCalls"])
        self.assertEqual("rent", scenario["user"]["housingPlan"])

    def test_invalid_next_currency_rates_leave_selection_and_values_unchanged(self) -> None:
        for invalid_rate in (0, -1, "Infinity", "not-a-rate"):
            with self.subTest(invalid_rate=invalid_rate):
                scenario = run_ui_dom_scenario(
                    {"rates": {"USD": 1, "EUR": invalid_rate}, "currency": "EUR", "submit": False}
                )
                self.assertEqual("USD", scenario["currency"])
                self.assertEqual("500,000", scenario["liquidDisplay"])
                self.assertEqual("2,000", scenario["monthlyDisplay"])

    def test_currency_change_and_money_control_wiring_are_safe(self) -> None:
        source = UI.read_text()
        self.assertIn('const moneyControlIds = MONEY_CONTROL_IDS.slice();', source)
        self.assertIn('element("finder-currency").addEventListener("change"', source)
        self.assertIn('if (!control || control.value === "") return;', source)
        self.assertIn('if (amount === null) return;', source)
        self.assertIn('convertPlanningControlAmount({', source)
        self.assertIn('step: control.step,', source)
        self.assertIn('formatMoneyControl(control);', source)
        self.assertIn('control.addEventListener("blur"', source)
        self.assertIn('control.setAttribute("aria-invalid", "true")', source)
        self.assertIn('control.removeAttribute("aria-invalid")', source)

    def test_money_values_do_not_leave_the_browser(self) -> None:
        source = UI.read_text()
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "URLSearchParams"):
            self.assertNotIn(forbidden, source)
        for sensitive_id in (
            "finder-liquid-capital",
            "finder-monthly-contribution",
            "finder-property-allocation",
            "finder-pension",
            "finder-other-income",
        ):
            self.assertNotIn('track("' + sensitive_id, source)
    def test_buy_now_visibility_tracks_financing_and_use(self) -> None:
        visible = run_ui(
            "housingVisibility",
            {"housingPlan": "buy_now", "purchaseMethod": "mortgage", "useBeforeRetirement": "rental"},
        )
        self.assertEqual(
            {"buyNow": True, "mortgage": True, "rental": True, "buyAtRetirement": False},
            visible,
        )
        rent = run_ui(
            "housingVisibility",
            {"housingPlan": "rent", "purchaseMethod": "cash", "useBeforeRetirement": "personal"},
        )
        self.assertFalse(any(rent.values()))

    def test_detail_href_contains_only_allowlisted_categories(self) -> None:
        href = run_ui(
            "safeDetailHref",
            {
                "destinationId": "valencia",
                "household": "couple",
                "housingPlan": "buy_now",
                "totalLiquidCapital": 900000,
                "passport": "GB",
            },
        )
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=valencia&household=couple&housing=buy_now",
            href,
        )
        self.assertNotIn("900000", href)
        self.assertNotIn("passport", href)

    def test_dossier_href_accepts_only_destination_slugs(self) -> None:
        self.assertEqual(
            "/destinations/valencia/",
            run_ui("safeDossierHref", "valencia"),
        )
        self.assertEqual(
            "/destinations/fukuoka-itoshima/",
            run_ui("safeDossierHref", "fukuoka-itoshima"),
        )
        self.assertEqual("/destinations/", run_ui("safeDossierHref", "../contact"))

    def test_recommendation_list_shows_five_before_expansion(self) -> None:
        items = list(range(12))
        self.assertEqual(items[:5], run_ui("recommendationsForDisplay", {"items": items, "expanded": False}))
        self.assertEqual(items, run_ui("recommendationsForDisplay", {"items": items, "expanded": True}))

    def test_result_summary_explains_the_closest_match_when_none_are_affordable(self) -> None:
        read = run_ui(
            "resultSummaryRead",
            {
                "withinReachCount": 0,
                "recommendations": [
                    {"name": "Fukuoka / Itoshima", "surplusGap": -322418},
                ],
                "currency": "SGD",
                "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
            },
        )
        self.assertIn("No destinations are within reach yet", read)
        self.assertIn("Fukuoka / Itoshima is the closest modeled match", read)
        self.assertIn("SGD\u00a0409,882", read)

    def test_result_money_formats_negative_gaps_equity_and_jpy(self) -> None:
        rates = {"USD": 1, "SGD": 0.7866117265603891, "JPY": 0.0067}
        self.assertEqual(
            "-SGD\u00a0409,882",
            run_ui("resultMoney", {"amountUsd": -322418, "currency": "SGD", "ratesToUsd": rates}),
        )
        self.assertEqual(
            "SGD\u00a0762,765",
            run_ui("resultMoney", {"amountUsd": 600000, "currency": "SGD", "ratesToUsd": rates}),
        )
        self.assertEqual(
            "\u00a5" + "89,552,239",
            run_ui("resultMoney", {"amountUsd": 600000, "currency": "JPY", "ratesToUsd": rates}),
        )

    def test_result_money_wiring_covers_all_result_amounts_and_rerenders(self) -> None:
        source = UI.read_text()
        self.assertIn("function resultMoney(input)", source)
        for result_id in ("finder-capital-today", "finder-monthly-summary"):
            self.assertIn(f'element("{result_id}").textContent = displayResultMoney(', source)
        for recommendation_value in (
            "item.portfolioAtRetirement",
            "item.retirementTarget",
            "item.surplusGap",
            "item.propertyEquity",
            "item.mortgageBalance",
            "item.netRentalCashFlow",
        ):
            self.assertIn("displayResultMoney(" + recommendation_value + ")", source)
        self.assertIn("renderCurrentResults();", source)

    def test_currency_changes_do_not_change_recommendation_identity_or_tier(self) -> None:
        recommendations = [
            {"destinationId": "fukuoka-itoshima", "tier": "close", "surplusGap": -322418},
            {"destinationId": "valencia", "tier": "within_reach", "surplusGap": 41250},
        ]
        usd = [
            (item["destinationId"], item["tier"], run_ui("resultMoney", {"amountUsd": item["surplusGap"]}))
            for item in recommendations
        ]
        sgd = [
            (
                item["destinationId"],
                item["tier"],
                run_ui(
                    "resultMoney",
                    {
                        "amountUsd": item["surplusGap"],
                        "currency": "SGD",
                        "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
                    },
                ),
            )
            for item in recommendations
        ]
        self.assertEqual([(item[0], item[1]) for item in usd], [(item[0], item[1]) for item in sgd])
        self.assertNotEqual([item[2] for item in usd], [item[2] for item in sgd])

    def test_tier_labels_are_plain_language(self) -> None:
        self.assertEqual("Within reach", run_ui("tierLabel", "within_reach"))
        self.assertEqual("Close", run_ui("tierLabel", "close"))
        self.assertEqual("Stretch", run_ui("tierLabel", "stretch"))

    def test_projection_model_scales_portfolio_and_target_to_the_same_axis(self) -> None:
        self.assertEqual(
            {
                "maximum": 200,
                "targetY": 18,
                "years": [
                    {"year": 0, "portfolio": 100, "height": 120},
                    {"year": 1, "portfolio": 150, "height": 180},
                ],
            },
            run_ui(
                "finderProjectionModel",
                {
                    "series": [
                        {"year": 0, "portfolio": 100},
                        {"year": 1, "portfolio": 150},
                    ],
                    "targetValue": 200,
                },
            ),
        )

    def test_projection_tooltip_exposes_age_and_selected_currency_amount(self) -> None:
        tooltip = run_ui(
            "finderProjectionTooltip",
            {
                "currentAge": 50,
                "point": {"year": 7, "portfolio": 432100},
                "currency": "SGD",
                "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
            },
        )
        self.assertEqual("Year 7 · age 57", tooltip["heading"])
        self.assertEqual("SGD\u00a0549,318", tooltip["value"])
        self.assertEqual(
            "Year 7, age 57. Projected portfolio SGD\u00a0549,318.",
            tooltip["accessibleLabel"],
        )

    def test_projection_axis_label_shows_elapsed_years_and_age(self) -> None:
        self.assertEqual(
            "Now · age 50",
            run_ui("finderProjectionAxisLabel", {"year": 0, "currentAge": 50}),
        )
        self.assertEqual(
            "+7y · age 57",
            run_ui("finderProjectionAxisLabel", {"year": 7, "currentAge": 50}),
        )

    def test_non_buy_now_projection_view_uses_shared_series_and_closest_target(self) -> None:
        self.assertEqual(
            {
                "heading": "Projected portfolio by year",
                "series": [{"year": 0, "portfolio": 500000}],
                "targetValue": 700000,
                "destinationName": "Valencia",
            },
            run_ui(
                "finderProjectionView",
                {
                    "housingPlan": "rent",
                    "sharedProjection": {"annualProjection": [{"year": 0, "portfolio": 500000}]},
                    "recommendations": [
                        {
                            "name": "Valencia",
                            "retirementTarget": 700000,
                            "annualProjection": [{"year": 0, "portfolio": 1}],
                        }
                    ],
                },
            ),
        )

    def test_buy_now_projection_view_uses_closest_destination_series(self) -> None:
        self.assertEqual(
            {
                "heading": "Projection for Fukuoka / Itoshima",
                "series": [{"year": 0, "portfolio": 420000}],
                "targetValue": 650000,
                "destinationName": "Fukuoka / Itoshima",
            },
            run_ui(
                "finderProjectionView",
                {
                    "housingPlan": "buy_now",
                    "sharedProjection": {"annualProjection": [{"year": 0, "portfolio": 999999}]},
                    "recommendations": [
                        {
                            "name": "Fukuoka / Itoshima",
                            "retirementTarget": 650000,
                            "annualProjection": [{"year": 0, "portfolio": 420000}],
                        },
                        {
                            "name": "Valencia",
                            "retirementTarget": 600000,
                            "annualProjection": [{"year": 0, "portfolio": 510000}],
                        },
                    ],
                },
            ),
        )

    def test_focusable_projection_points_use_non_button_semantics(self) -> None:
        source = UI.read_text()
        self.assertIn('class="finder-chart-year" tabindex="0" role="img"', source)
        self.assertNotIn('class="finder-chart-year" tabindex="0" role="button"', source)

    def test_ui_does_not_store_or_transmit_financial_values(self) -> None:
        source = UI.read_text()
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage"):
            self.assertNotIn(forbidden, source)
        for sensitive_key in (
            "total_liquid_capital:",
            "monthly_contribution:",
            "property_allocation:",
            "mortgage_rate:",
            "passport:",
            "portfolio_at_retirement:",
        ):
            self.assertNotIn(sensitive_key, source)


if __name__ == "__main__":
    unittest.main()
