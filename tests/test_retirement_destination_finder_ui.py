from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "src" / "retirement_destination_finder_ui.js"
SCENARIO = ROOT / "src" / "retirement_finder_scenario.js"
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
const scenarioApi = require(process.argv[3]);

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
  dispatch(name, target) {
    const event = { preventDefault() {}, target: target || this };
    (this.listeners[name] || []).forEach((callback) => callback(event));
  }
  setCustomValidity(message) { this.validationMessage = message; }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  removeAttribute(name) { delete this.attributes[name]; }
  querySelectorAll() { return []; }
  closest() { return null; }
  focus() {}
  select() { this.selected = true; }
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
const settingControls = ["City", "CoastOrIsland", "Mountain", "Lake"].map((value) => {
  const control = el("finder-setting-" + value.toLowerCase());
  control.value = value;
  control.checked = (input.settings || []).includes(value);
  return control;
});
const projectionGroups = Array.from({ length: input.projectionGroupCount || 0 }, (_, index) => {
  const group = new FakeElement("projection-" + index);
  group.dataset.yearIndex = String(index);
  return group;
});
el("finder-projection-bars").querySelectorAll = (selector) =>
  selector === ".finder-chart-year" ? projectionGroups : [];
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
  querySelectorAll(selector) {
    if (selector === "[data-finder-group]") return groups;
    if (selector === '[name="finder-setting"]') return settingControls;
    return [];
  },
};
let engineInput = null;
const engineInputs = [];
let engineCalls = 0;
const trackedEvents = [];
const fakeWindow = {
  location: {
    origin: "https://globalhomeatlas.com",
    pathname: "/retirement-destination-finder/",
    search: input.search || "",
  },
  navigator: input.clipboard ? { clipboard: { writeText(value) { input.copied = value; return Promise.resolve(); } } } : {},
  GHA: { track(name, fields) { trackedEvents.push({ name, fields: fields || {} }); } },
  GHARetirementFinderScenario: scenarioApi,
  GHARetirementDestinationFinder: {
    recommendDestinations(request) {
      engineInput = request;
      engineInputs.push(request);
      engineCalls += 1;
      return input.engineResult || {
        summary: { withinReachCount: 0, closeCount: 0, stretchCount: 0 },
        sharedProjection: null,
        recommendations: [],
        excluded: [],
      };
    },
  },
};
const context = { window: fakeWindow, document, Intl, Number, String, Array, Set, Map, Math, JSON };
vm.runInNewContext(fs.readFileSync(process.argv[1], "utf8"), context);
fakeWindow.GHARetirementDestinationFinderUI.initRetirementDestinationFinder("retirement-destination-finder", {
  asOf: "2026-08-27",
  planning_currencies: { rates_to_usd: input.rates },
  destinations: input.destinations || [],
  retirementCosts: input.retirementCosts || [],
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
if (input.region) el("finder-region").value = input.region;
if (input.submit) el("retirement-destination-finder-form").dispatch("submit");
if (input.clickShare) el("finder-share").dispatch("click");
if (input.preferenceChange) {
  const control = el(input.preferenceChange.id);
  if (Object.prototype.hasOwnProperty.call(input.preferenceChange, "checked")) {
    control.checked = input.preferenceChange.checked;
  } else {
    control.value = input.preferenceChange.value;
  }
  control.dispatch("change");
}
if (input.clickDestination) {
  const target = {
    closest(selector) {
      return selector === "[data-finder-destination]"
        ? { dataset: input.clickDestination }
        : null;
    },
  };
  el(input.clickDestination.container).dispatch("click", target);
}
if (input.clickProjectionIndex !== undefined) {
  projectionGroups[input.clickProjectionIndex].dispatch("click");
}

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
  eligibleCount: el("finder-eligible-count").textContent,
  projectedCapital: el("finder-projected-capital").textContent,
  landscapeProjectedCapital: el("finder-landscape-projected").textContent,
  strongestMatch: el("finder-strongest-match").textContent,
  landscapeRowsHtml: el("finder-landscape-rows").innerHTML,
  recommendationsHtml: el("finder-recommendations").innerHTML,
  comparisonHtml: el("finder-comparison-body").innerHTML,
  comparisonHidden: el("finder-comparison").hidden,
  shareStatus: el("finder-share-status").textContent,
  shareUrl: el("finder-share-url").value,
  shareUrlHidden: el("finder-share-url").hidden,
  sharedErrorHidden: el("finder-shared-error").hidden,
  landscapeHidden: el("finder-capital-landscape").hidden,
  matchesHidden: el("finder-matches-section").hidden,
  projectionHidden: el("finder-projection-section").hidden,
  emptyStateHidden: el("finder-empty-state").hidden,
  emptyStateText: el("finder-empty-state").textContent,
  activeFilters: el("finder-active-filters").textContent,
  trackedEvents,
}));
'''
    result = subprocess.run(
        ["node", "-e", script, str(UI), json.dumps(payload), str(SCENARIO)],
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

    def test_submission_keeps_all_selected_setting_filters(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "settings": ["CoastOrIsland", "Mountain"],
                "submit": True,
            }
        )

        self.assertEqual(
            ["CoastOrIsland", "Mountain"],
            scenario["user"]["preferences"]["settings"],
        )
        self.assertNotIn("climate", scenario["user"]["preferences"])

    def test_results_name_the_active_region_and_settings(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "region": "asia",
                "settings": ["CoastOrIsland", "Mountain"],
                "submit": True,
                "engineResult": {
                    "summary": {
                        "evaluatedCount": 0,
                        "withinReachCount": 0,
                        "closeCount": 0,
                        "stretchCount": 0,
                    },
                    "sharedProjection": None,
                    "recommendations": [],
                    "excluded": [],
                },
            }
        )

        self.assertEqual(
            "Showing: Asia · Coast or island · Mountain",
            scenario["activeFilters"],
        )

    def test_no_match_state_suggests_relaxing_destination_filters(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "region": "asia",
                "settings": ["Lake"],
                "submit": True,
                "engineResult": {
                    "summary": {
                        "evaluatedCount": 0,
                        "withinReachCount": 0,
                        "closeCount": 0,
                        "stretchCount": 0,
                    },
                    "sharedProjection": None,
                    "recommendations": [],
                    "excluded": [],
                },
            }
        )

        self.assertEqual(
            "No destinations match Asia and Lake. Try removing a setting or choosing another region.",
            scenario["emptyStateText"],
        )

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

    def test_capital_landscape_cost_ranks_every_eligible_destination_without_mutating_match_order(self) -> None:
        recommendations = [
            {
                "destinationId": "strongest",
                "name": "Strongest",
                "country": "A",
                "tier": "close",
                "retirementTarget": 1_900_000,
                "portfolioAtRetirement": 1_500_000,
            },
            {
                "destinationId": "lowest-cost",
                "name": "Lowest cost",
                "country": "B",
                "tier": "within_reach",
                "retirementTarget": 900_000,
                "portfolioAtRetirement": 1_500_000,
            },
            {
                "destinationId": "third-match",
                "name": "Third match",
                "country": "C",
                "tier": "stretch",
                "retirementTarget": 2_200_000,
                "portfolioAtRetirement": 1_500_000,
            },
            {
                "destinationId": "unhighlighted",
                "name": "Unhighlighted",
                "country": "D",
                "tier": "within_reach",
                "retirementTarget": 1_100_000,
                "portfolioAtRetirement": 1_500_000,
            },
        ]

        model = run_ui(
            "finderCapitalLandscape",
            {"recommendations": recommendations, "projectedCapital": 1_500_000},
        )

        self.assertEqual(
            ["lowest-cost", "unhighlighted", "strongest", "third-match"],
            [row["destinationId"] for row in model["rows"]],
        )
        self.assertEqual(
            {"strongest": 1, "lowest-cost": 2, "third-match": 3, "unhighlighted": None},
            {row["destinationId"]: row["matchRank"] for row in model["rows"]},
        )
        self.assertEqual(
            ["strongest", "lowest-cost", "third-match", "unhighlighted"],
            [item["destinationId"] for item in recommendations],
        )

    def test_capital_landscape_uses_one_safe_axis_for_targets_and_projected_capital(self) -> None:
        model = run_ui(
            "finderCapitalLandscape",
            {
                "recommendations": [
                    {
                        "destinationId": "zero",
                        "name": "Zero",
                        "country": "A",
                        "tier": "within_reach",
                        "retirementTarget": 0,
                    },
                    {
                        "destinationId": "target",
                        "name": "Target",
                        "country": "B",
                        "tier": "stretch",
                        "retirementTarget": 250_000,
                    },
                ],
                "projectedCapital": 400_000,
            },
        )

        self.assertEqual(400_000, model["maximum"])
        self.assertEqual(100, model["projectedPosition"])
        self.assertEqual([0, 62.5], [row["position"] for row in model["rows"]])
        self.assertEqual([0, 100_000, 200_000, 300_000, 400_000], model["ticks"])

        large = run_ui(
            "finderCapitalLandscape",
            {
                "recommendations": [
                    {
                        "destinationId": "large",
                        "name": "Large",
                        "country": "A",
                        "tier": "stretch",
                        "retirementTarget": 6_107_245,
                    }
                ],
                "projectedCapital": 1_662_594,
            },
        )
        self.assertEqual(8_000_000, large["maximum"])
        self.assertEqual([0, 2_000_000, 4_000_000, 6_000_000, 8_000_000], large["ticks"])

    def test_capital_landscape_accessible_label_identifies_match_rank_and_selected_currency(self) -> None:
        label = run_ui(
            "finderCapitalLandscapeLabel",
            {
                "row": {
                    "name": "Fukuoka / Itoshima",
                    "country": "Japan",
                    "tier": "close",
                    "target": 800_000,
                    "matchRank": 1,
                },
                "projectedCapital": 700_000,
                "currency": "SGD",
                "ratesToUsd": {"USD": 1, "SGD": 0.8},
            },
        )

        self.assertEqual(
            "Fukuoka / Itoshima, Japan. Required capital SGD\u00a01,000,000. SGD\u00a0125,000 over projected capital. Close. Recommended match number 1.",
            label,
        )

    def test_capital_landscape_markup_renders_every_row_as_an_accessible_dossier_link(self) -> None:
        markup = run_ui(
            "finderCapitalLandscapeMarkup",
            {
                "model": {
                    "projectedCapital": 600_000,
                    "projectedPosition": 60,
                    "ticks": [0, 500_000, 1_000_000],
                    "rows": [
                        {
                            "destinationId": "fukuoka-itoshima",
                            "name": "Fukuoka / Itoshima",
                            "country": "Japan",
                            "tier": "within_reach",
                            "target": 600_000,
                            "position": 60,
                            "matchRank": 1,
                        },
                        {
                            "destinationId": "valencia",
                            "name": "Valencia",
                            "country": "Spain",
                            "tier": "close",
                            "target": 750_000,
                            "position": 75,
                            "matchRank": None,
                        },
                    ],
                },
                "currency": "USD",
                "ratesToUsd": {"USD": 1},
            },
        )

        self.assertEqual(2, markup["rowCount"])
        self.assertIn('href="/destinations/fukuoka-itoshima/"', markup["rowsHtml"])
        self.assertIn('class="finder-landscape-row is-match is-on-target"', markup["rowsHtml"])
        self.assertIn('class="finder-landscape-row is-over"', markup["rowsHtml"])
        self.assertIn(
            '--capital-position:60.00%;--target-position:75.00%;--distance-start:60.00%;--distance-width:15.00%',
            markup["rowsHtml"],
        )
        self.assertIn('class="finder-landscape-capital-dot"', markup["rowsHtml"])
        self.assertIn('class="finder-landscape-distance"', markup["rowsHtml"])
        self.assertIn('class="finder-landscape-dot"', markup["rowsHtml"])
        self.assertIn(
            '<span class="finder-landscape-value"><span>$600,000</span></span>',
            markup["rowsHtml"],
        )
        self.assertIn(
            '<span class="finder-landscape-value"><span>$750,000</span></span>',
            markup["rowsHtml"],
        )
        self.assertNotIn("finder-landscape-gap", markup["rowsHtml"])
        self.assertIn('aria-label="Fukuoka / Itoshima, Japan.', markup["rowsHtml"])
        self.assertIn('class="finder-landscape-capital-label"', markup["axisHtml"])
        self.assertIn("Projected capital", markup["axisHtml"])

    def test_render_places_projected_capital_next_to_the_cost_distance_chart(self) -> None:
        result = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "submit": True,
                "engineResult": {
                    "summary": {"withinReachCount": 1, "closeCount": 0, "stretchCount": 0},
                    "sharedProjection": {"portfolioAtRetirement": 700_000, "series": []},
                    "recommendations": [
                        {
                            "destinationId": "fukuoka-itoshima",
                            "name": "Fukuoka / Itoshima",
                            "country": "Japan",
                            "tier": "within_reach",
                            "retirementTarget": 600_000,
                            "portfolioAtRetirement": 700_000,
                        }
                    ],
                    "excluded": [],
                },
            }
        )

        self.assertEqual("$700,000", result["landscapeProjectedCapital"])

    def test_projected_capital_uses_shared_projection_or_strongest_purchase_scenario(self) -> None:
        self.assertEqual(
            1_750_000,
            run_ui(
                "finderProjectedCapital",
                {
                    "sharedProjection": {"portfolioAtRetirement": 1_750_000},
                    "recommendations": [{"portfolioAtRetirement": 900_000}],
                },
            ),
        )
        self.assertEqual(
            900_000,
            run_ui(
                "finderProjectedCapital",
                {
                    "sharedProjection": None,
                    "recommendations": [{"portfolioAtRetirement": 900_000}],
                },
            ),
        )

    def test_result_summary_explains_the_strongest_match_when_none_are_affordable(self) -> None:
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
        self.assertIn("Fukuoka / Itoshima is the strongest match", read)
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
        for result_id in ("finder-projected-capital",):
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

    def test_submit_renders_all_eligible_destinations_but_only_three_strongest_matches(self) -> None:
        recommendations = [
            {
                "destinationId": f"place-{index}",
                "name": f"Place {index}",
                "country": "Country",
                "tier": "within_reach" if index < 4 else "stretch",
                "fundingRatio": 1,
                "portfolioAtRetirement": 2_000_000,
                "annualProjection": [{"year": 0, "portfolio": 500_000}],
                "retirementTarget": 500_000 + index * 10_000,
                "surplusGap": 1_500_000 - index * 10_000,
                "propertyEquity": 0,
                "mortgageBalance": 0,
                "netRentalCashFlow": 0,
                "financingStatus": "Not applicable",
                "financingReason": "",
                "preferenceMatches": [],
            }
            for index in range(13)
        ]
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "engineResult": {
                    "summary": {"withinReachCount": 4, "closeCount": 0, "stretchCount": 9},
                    "sharedProjection": {
                        "portfolioAtRetirement": 2_000_000,
                        "annualProjection": [{"year": 0, "portfolio": 500_000}],
                    },
                    "recommendations": recommendations,
                    "excluded": [],
                },
                "submit": True,
            }
        )

        self.assertEqual("13", scenario["eligibleCount"])
        self.assertEqual("$2,000,000", scenario["projectedCapital"])
        self.assertEqual("Place 0", scenario["strongestMatch"])
        self.assertEqual(13, scenario["landscapeRowsHtml"].count('role="listitem"'))
        self.assertEqual(3, scenario["recommendationsHtml"].count('class="finder-result"'))
        self.assertFalse(scenario["landscapeHidden"])
        self.assertTrue(scenario["emptyStateHidden"])

    def test_zero_eligible_result_shows_an_empty_state_instead_of_empty_charts(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "engineResult": {
                    "summary": {"withinReachCount": 0, "closeCount": 0, "stretchCount": 0},
                    "sharedProjection": None,
                    "recommendations": [],
                    "excluded": [
                        {"destinationId": "place", "name": "Place", "reasonCode": "property_finance_unavailable"}
                    ],
                },
                "submit": True,
            }
        )

        self.assertEqual("0", scenario["eligibleCount"])
        self.assertEqual("—", scenario["projectedCapital"])
        self.assertTrue(scenario["landscapeHidden"])
        self.assertTrue(scenario["matchesHidden"])
        self.assertTrue(scenario["projectionHidden"])
        self.assertFalse(scenario["emptyStateHidden"])
        self.assertEqual("", scenario["landscapeRowsHtml"])
        self.assertEqual("", scenario["recommendationsHtml"])

    def test_completion_analytics_describe_outcome_without_financial_inputs(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "engineResult": {
                    "summary": {"withinReachCount": 1, "closeCount": 0, "stretchCount": 0},
                    "sharedProjection": {"portfolioAtRetirement": 900000, "annualProjection": []},
                    "recommendations": [
                        {
                            "destinationId": "fukuoka-itoshima",
                            "name": "Fukuoka / Itoshima",
                            "country": "Japan",
                            "tier": "within_reach",
                            "fundingRatio": 1.2,
                            "portfolioAtRetirement": 900000,
                            "retirementTarget": 750000,
                            "surplusGap": 150000,
                            "preferenceMatches": ["Long-stay suitability"],
                            "financingStatus": "Cash purchase",
                        }
                    ],
                    "excluded": [
                        {"destinationId": "place", "name": "Place", "reasonCode": "missing_cost_data"}
                    ],
                },
                "submit": True,
            }
        )

        event = next(item for item in scenario["trackedEvents"] if item["name"] == "retirement_destination_finder_complete")
        self.assertEqual(
            {
                "housing_plan": "rent",
                "purchase_method": "not_applicable",
                "currency": "USD",
                "eligible_count": 1,
                "within_reach_count": 1,
                "excluded_count": 1,
                "strongest_destination_id": "fukuoka-itoshima",
                "strongest_tier": "within_reach",
                "region": "any",
                "setting": "any",
                "healthcare": "normal",
            },
            event["fields"],
        )
        self.assertFalse(
            {"current_age", "retirement_age", "liquid_capital", "monthly_contribution"}
            & set(event["fields"])
        )

    def test_no_result_analytics_identify_primary_exclusion_without_financial_inputs(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "engineResult": {
                    "summary": {"withinReachCount": 0, "closeCount": 0, "stretchCount": 0},
                    "sharedProjection": None,
                    "recommendations": [],
                    "excluded": [
                        {"destinationId": "a", "name": "A", "reasonCode": "financing_unverified"},
                        {"destinationId": "b", "name": "B", "reasonCode": "financing_unverified"},
                        {"destinationId": "c", "name": "C", "reasonCode": "missing_cost_data"},
                    ],
                },
                "submit": True,
            }
        )

        event = next(item for item in scenario["trackedEvents"] if item["name"] == "retirement_destination_finder_no_results")
        self.assertEqual(3, event["fields"]["excluded_count"])
        self.assertEqual("financing_unverified", event["fields"]["primary_exclusion_reason"])
        self.assertNotIn("liquid_capital", event["fields"])

    def test_destination_click_analytics_include_surface_and_rank(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "clickDestination": {
                    "container": "finder-landscape-rows",
                    "destinationId": "fukuoka-itoshima",
                    "surface": "cost_landscape",
                    "costRank": "4",
                    "matchRank": "1",
                    "tier": "within_reach",
                    "action": "dossier",
                },
            }
        )

        event = next(item for item in scenario["trackedEvents"] if item["name"] == "retirement_destination_finder_destination_click")
        self.assertEqual(
            {
                "destination_id": "fukuoka-itoshima",
                "surface": "cost_landscape",
                "cost_rank": 4,
                "match_rank": 1,
                "tier": "within_reach",
                "action": "dossier",
            },
            event["fields"],
        )

    def test_detailed_plan_click_preserves_match_attribution_and_legacy_event(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "clickDestination": {
                    "container": "finder-recommendations",
                    "destinationId": "fukuoka-itoshima",
                    "surface": "recommended_match",
                    "costRank": "0",
                    "matchRank": "2",
                    "tier": "close",
                    "action": "detailed_plan",
                },
            }
        )

        destination_event = next(
            item for item in scenario["trackedEvents"]
            if item["name"] == "retirement_destination_finder_destination_click"
        )
        detail_event = next(
            item for item in scenario["trackedEvents"]
            if item["name"] == "retirement_destination_finder_detail_open"
        )
        self.assertEqual(2, destination_event["fields"]["match_rank"])
        self.assertEqual("detailed_plan", destination_event["fields"]["action"])
        self.assertEqual(destination_event["fields"], detail_event["fields"])

    def test_preference_change_analytics_identify_control_and_selected_value(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "preferenceChange": {"id": "finder-setting-coastorisland", "checked": True},
            }
        )

        event = next(item for item in scenario["trackedEvents"] if item["name"] == "retirement_destination_finder_preference_change")
        self.assertEqual(
            {"preference": "setting", "value": "CoastOrIsland", "selected": True},
            event["fields"],
        )

    def test_comparison_defaults_to_three_and_prevents_duplicate_replacements(self) -> None:
        recommendations = [
            {"destinationId": "fukuoka", "name": "Fukuoka"},
            {"destinationId": "valencia", "name": "Valencia"},
            {"destinationId": "madeira", "name": "Madeira"},
            {"destinationId": "algarve", "name": "Algarve"},
        ]
        selected = run_ui("comparisonSelection", {"recommendations": recommendations, "selectedIds": []})
        self.assertEqual(
            ["fukuoka", "valencia", "madeira"],
            [item["destinationId"] for item in selected],
        )
        self.assertEqual(
            ["fukuoka", "valencia", "madeira"],
            run_ui(
                "replaceComparisonDestination",
                {
                    "selectedIds": ["fukuoka", "valencia", "madeira"],
                    "position": 1,
                    "destinationId": "fukuoka",
                    "recommendations": recommendations,
                },
            ),
        )
        self.assertEqual(
            ["fukuoka", "algarve", "madeira"],
            run_ui(
                "replaceComparisonDestination",
                {
                    "selectedIds": ["fukuoka", "valencia", "madeira"],
                    "position": 1,
                    "destinationId": "algarve",
                    "recommendations": recommendations,
                },
            ),
        )

    def test_comparison_markup_uses_decision_fields_and_native_replacement_controls(self) -> None:
        recommendations = [
            {
                "destinationId": "fukuoka", "name": "Fukuoka / Itoshima", "country": "Japan",
                "retirementTarget": 900_000, "surplusGap": 100_000, "tier": "within_reach",
                "preferenceMatches": ["Preferred region"], "monthlyRetirementCost": 4_200,
                "countryGuideHref": "/countries/japan-property/",
            },
            {
                "destinationId": "valencia", "name": "Valencia", "country": "Spain",
                "retirementTarget": 1_100_000, "surplusGap": -100_000, "tier": "close",
                "preferenceMatches": [], "monthlyRetirementCost": 4_900,
                "countryGuideHref": "/countries/spain-property/",
            },
        ]
        markup = run_ui(
            "comparisonMarkup",
            {
                "recommendations": recommendations,
                "selectedIds": ["fukuoka", "valencia"],
                "housingPlan": "rent",
                "currency": "USD",
                "ratesToUsd": {"USD": 1},
            },
        )
        self.assertIn("Required capital", markup)
        self.assertIn("Gap versus projected capital", markup)
        self.assertIn("Monthly retirement cost", markup)
        self.assertIn('<select data-comparison-position="0"', markup)
        self.assertIn("Destination guide", markup)
        self.assertIn("Country guide", markup)
        self.assertIn('class="finder-comparison-mobile"', markup)
        self.assertIn('<h4>Fukuoka / Itoshima</h4>', markup)
        self.assertNotIn("score", markup.lower())

    def test_share_fallback_exposes_a_privacy_safe_results_link(self) -> None:
        recommendations = [
            {
                "destinationId": slug,
                "name": slug.title(),
                "country": "Example",
                "tier": tier,
                "fundingRatio": ratio,
                "portfolioAtRetirement": 1_000_000,
                "retirementTarget": target,
                "surplusGap": 1_000_000 - target,
                "preferenceMatches": [],
                "annualProjection": [],
            }
            for slug, tier, ratio, target in (
                ("fukuoka", "within_reach", 1.1, 900_000),
                ("valencia", "close", 0.95, 1_050_000),
                ("madeira", "stretch", 0.8, 1_250_000),
            )
        ]
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "engineResult": {
                    "summary": {"withinReachCount": 1, "closeCount": 1, "stretchCount": 1},
                    "sharedProjection": {"portfolioAtRetirement": 1_000_000, "annualProjection": []},
                    "recommendations": recommendations,
                    "excluded": [],
                },
                "submit": True,
                "clickShare": True,
            }
        )
        self.assertFalse(scenario["shareUrlHidden"])
        self.assertIn("?scenario=", scenario["shareUrl"])
        self.assertEqual("Copy this results link.", scenario["shareStatus"])
        event = next(item for item in scenario["trackedEvents"] if item["name"] == "retirement_destination_finder_share")
        self.assertEqual({"housing_plan": "rent"}, event["fields"])
        encoded = scenario["shareUrl"].split("?scenario=", 1)[1]
        from tests.test_retirement_finder_scenario import run_scenario

        snapshot = run_scenario(
            "decodeScenario",
            {"value": encoded, "destinationIds": ["fukuoka", "valencia", "madeira"]},
        )
        serialized = json.dumps(snapshot)
        for forbidden in ("currentAge", "totalLiquidCapital", "monthlyPortfolioContribution", "incomeStreams"):
            self.assertNotIn(forbidden, serialized)

    def test_invalid_shared_link_keeps_the_calculator_available(self) -> None:
        state = run_ui_dom_scenario({"rates": {"USD": 1}, "search": "?scenario=not-valid-json"})
        self.assertFalse(state["sharedErrorHidden"])
        self.assertEqual(0, state["engineCalls"])

    def test_legacy_water_shared_link_keeps_an_honest_filter_label(self) -> None:
        from tests.test_retirement_finder_scenario import encode_unchecked

        encoded = encode_unchecked(
            {
                "v": 1,
                "currency": "USD",
                "projectedCapitalUsd": 1_000_000,
                "household": "couple",
                "horizonYears": 30,
                "housingPlan": "rent",
                "preferences": {
                    "region": "any",
                    "settings": ["Water"],
                    "healthcare": "normal",
                },
                "results": [
                    {
                        "destinationId": "lake-como",
                        "retirementTargetUsd": 1_100_000,
                        "surplusGapUsd": -100_000,
                        "fundingRatio": 0.91,
                        "tier": "close",
                        "preferenceMatches": ["Preferred setting"],
                    }
                ],
                "comparisonIds": ["lake-como"],
                "dataReviewed": "2026-08-27",
            }
        )
        state = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "search": "?scenario=" + encoded,
                "destinations": [
                    {"id": "lake-como", "name": "Lake Como", "country": "Italy"}
                ],
            }
        )

        self.assertEqual("Showing: Water setting (legacy)", state["activeFilters"])
        self.assertIn("Lake Como", state["recommendationsHtml"])

    def test_shared_buy_now_snapshot_does_not_invent_zero_property_values(self) -> None:
        source = UI.read_text()
        self.assertIn("user.sharedSnapshot", source)
        self.assertIn("finder-data-reviewed", source)

    def test_recommendation_card_includes_country_guide_when_available(self) -> None:
        source = UI.read_text()
        self.assertIn("item.countryGuideHref", source)
        self.assertIn('data-action="country_guide"', source)

    def test_match_explanation_names_affordability_rank_and_planning_signals(self) -> None:
        explanation = run_ui(
            "finderMatchExplanation",
            {
                "item": {
                    "tier": "within_reach",
                    "surplusGap": 150000,
                    "fundingRatio": 1.2,
                    "preferenceMatches": ["Preferred region", "Long-stay suitability"],
                },
                "matchRank": 1,
                "currency": "USD",
                "ratesToUsd": {"USD": 1},
            },
        )

        self.assertEqual(
            "Within reach with $150,000 remaining. Matches your preferred region and long-stay priorities. Renting keeps more capital available.",
            explanation,
        )

    def test_match_explanation_states_gap_and_tie_break_when_no_signals_match(self) -> None:
        explanation = run_ui(
            "finderMatchExplanation",
            {
                "item": {
                    "tier": "close",
                    "surplusGap": -75000,
                    "fundingRatio": 0.9,
                    "preferenceMatches": [],
                },
                "matchRank": 2,
                "currency": "USD",
                "ratesToUsd": {"USD": 1},
            },
        )

        self.assertEqual("Close, with a $75,000 gap. Renting keeps more capital available.", explanation)

    def test_match_explanation_avoids_one_hundred_percent_when_a_gap_remains(self) -> None:
        explanation = run_ui(
            "finderMatchExplanation",
            {
                "item": {
                    "tier": "close",
                    "surplusGap": -3000,
                    "fundingRatio": 0.996,
                    "preferenceMatches": [],
                },
                "matchRank": 1,
                "currency": "USD",
                "ratesToUsd": {"USD": 1},
            },
        )

        self.assertIn("Close, with a $3,000 gap.", explanation)
        self.assertNotIn("100%", explanation)

    def test_match_explanation_calls_a_zero_gap_an_exact_match(self) -> None:
        explanation = run_ui(
            "finderMatchExplanation",
            {
                "item": {
                    "tier": "within_reach",
                    "surplusGap": 0,
                    "fundingRatio": 1,
                    "preferenceMatches": [],
                },
                "matchRank": 1,
                "currency": "USD",
                "ratesToUsd": {"USD": 1},
            },
        )

        self.assertTrue(explanation.startswith("Within reach at the required capital."))
        self.assertNotIn("$0", explanation)

    def test_recommendation_cards_render_one_concise_explanation_instead_of_a_duplicate_match_label(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "engineResult": {
                    "summary": {"withinReachCount": 1, "closeCount": 0, "stretchCount": 0},
                    "sharedProjection": {"portfolioAtRetirement": 900000, "annualProjection": []},
                    "recommendations": [
                        {
                            "destinationId": "fukuoka-itoshima",
                            "name": "Fukuoka / Itoshima",
                            "country": "Japan",
                            "tier": "within_reach",
                            "fundingRatio": 1.2,
                            "portfolioAtRetirement": 900000,
                            "retirementTarget": 750000,
                            "surplusGap": 150000,
                            "preferenceMatches": ["Long-stay suitability"],
                            "financingStatus": "Cash purchase",
                        }
                    ],
                    "excluded": [],
                },
                "submit": True,
            }
        )

        self.assertIn('class="finder-rationale"', scenario["recommendationsHtml"])
        self.assertIn("Within reach with $150,000 remaining", scenario["recommendationsHtml"])
        self.assertNotIn("Preference match:", scenario["recommendationsHtml"])
        self.assertIn('data-surface="recommended_match"', scenario["recommendationsHtml"])

    def test_projection_chart_click_tracks_only_position_and_match_categories(self) -> None:
        scenario = run_ui_dom_scenario(
            {
                "rates": {"USD": 1},
                "projectionGroupCount": 2,
                "clickProjectionIndex": 1,
                "engineResult": {
                    "summary": {"withinReachCount": 1, "closeCount": 0, "stretchCount": 0},
                    "sharedProjection": {
                        "portfolioAtRetirement": 900000,
                        "annualProjection": [
                            {"year": 0, "portfolio": 500000},
                            {"year": 10, "portfolio": 900000},
                        ],
                    },
                    "recommendations": [
                        {
                            "destinationId": "fukuoka-itoshima",
                            "name": "Fukuoka / Itoshima",
                            "country": "Japan",
                            "tier": "within_reach",
                            "fundingRatio": 1.2,
                            "portfolioAtRetirement": 900000,
                            "retirementTarget": 750000,
                            "surplusGap": 150000,
                            "preferenceMatches": ["Long-stay suitability"],
                            "financingStatus": "Cash purchase",
                        }
                    ],
                    "excluded": [],
                },
                "submit": True,
            }
        )

        event = next(
            item for item in scenario["trackedEvents"]
            if item["name"] == "retirement_destination_finder_projection_click"
        )
        self.assertEqual(
            {
                "chart": "capital_projection",
                "point_index": 1,
                "point_count": 2,
                "strongest_destination_id": "fukuoka-itoshima",
                "strongest_tier": "within_reach",
            },
            event["fields"],
        )
        self.assertFalse({"age", "year", "portfolio", "value"} & set(event["fields"]))

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
