from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI_MODULE = ROOT / "src" / "retirement_calculator_ui.js"
ENGINE_MODULE = ROOT / "src" / "retirement_calculator.js"


def run_ui(function_name: str, payload: object) -> object:
    script = (
        "const ui = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"const fn = ui.{function_name} || (() => null);"
        "process.stdout.write(JSON.stringify(fn(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(UI_MODULE), json.dumps(payload)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def run_ui_args(function_name: str, *args: object) -> object:
    script = (
        "const ui = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"const fn = ui.{function_name};"
        "process.stdout.write(JSON.stringify(fn.apply(null, input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(UI_MODULE), json.dumps(args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def run_engine(function_name: str, payload: object) -> object:
    script = (
        "const engine = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(engine.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE_MODULE), json.dumps(payload)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def tax_scenario() -> dict:
    return {
        "status": "available",
        "cases": {
            "favorable": {"total": 1_000, "propertyTaxReserve": 0},
            "central": {"total": 2_000, "propertyTaxReserve": 0},
            "adverse": {"total": 3_000, "propertyTaxReserve": 0},
        },
        "amountExplanations": {
            "favorable": {"total": {"formula": "fixture"}},
            "central": {"total": {"formula": "fixture"}},
            "adverse": {"total": {"formula": "fixture"}},
        },
    }


def calculator_payload() -> dict:
    return {
        "currentAge": 59,
        "retirementAge": 60,
        "horizonYears": 2,
        "expenseCategories": [{"amount": 10_000, "inflationRate": 0}],
        "incomeStreams": [{"amount": 2_000, "indexed": False, "inflationRate": 0}],
        "housingPlan": "rent",
        "propertyPrice": 0,
        "propertyInflation": 0,
        "acquisitionCostRate": 0,
        "generalInflation": 0,
        "emergencyReserveMonths": 0,
        "expectedPortfolioReturn": 0,
        "monthlyIncomeBeforeRetirement": 0,
        "incomeInvestedRate": 0,
    }


class RetirementCalculatorUITests(unittest.TestCase):
    def test_tax_adjusted_central_case_matches_direct_engine_destination_estimate(self) -> None:
        base = calculator_payload()
        result = run_ui_args("calculateTaxAdjustedScenarios", base, tax_scenario())
        direct = run_engine(
            "calculateRetirement",
            {
                **base,
                "annualTaxExpenses": 2_000,
                "taxMode": "destination_estimate",
                "returnBasis": "after_fees_and_tax",
            },
        )

        self.assertEqual(["favorable", "central", "adverse"], list(result))
        self.assertEqual(direct, result["central"]["result"])
        self.assertEqual(2_000, result["central"]["annualTaxReserve"])
        self.assertEqual(2_000, result["central"]["annualTaxExpenses"])
        self.assertEqual(12_000, result["central"]["firstYearExpenses"])
        self.assertEqual(10_000, result["central"]["fundingGap"])
        self.assertEqual(20_000, result["central"]["requiredCapital"])
        self.assertEqual(4_000, result["central"]["requiredCapitalDifference"])
        self.assertEqual("No added destination tax", result["central"]["noTaxComparisonLabel"])

    def test_tax_adjusted_scenario_bands_remain_ordered_by_required_capital(self) -> None:
        result = run_ui_args("calculateTaxAdjustedScenarios", calculator_payload(), tax_scenario())

        self.assertLessEqual(result["favorable"]["requiredCapital"], result["central"]["requiredCapital"])
        self.assertLessEqual(result["central"]["requiredCapital"], result["adverse"]["requiredCapital"])

    def test_tax_adjusted_scenarios_replace_existing_tax_and_preserve_property_tax_exclusion(self) -> None:
        base = calculator_payload()
        base.update(
            {
                "annualTaxExpenses": 9_000,
                "taxMode": "destination_estimate",
                "returnBasis": "after_fees_and_tax",
            }
        )
        scenario = tax_scenario()
        scenario["cases"]["central"] = {
            "total": 1_000,
            "incomeTaxReserve": 0,
            "propertyTaxReserve": 0,
            "wealthTaxReserve": 0,
            "complianceReserve": 1_000,
        }
        direct = run_engine(
            "calculateRetirement",
            {
                **calculator_payload(),
                "annualTaxExpenses": 1_000,
                "taxMode": "destination_estimate",
                "returnBasis": "after_fees_and_tax",
            },
        )

        result = run_ui_args("calculateTaxAdjustedScenarios", base, scenario)

        self.assertEqual(1_000, result["central"]["annualTaxReserve"])
        self.assertEqual(direct["firstYearExpenses"], result["central"]["firstYearExpenses"])
        self.assertEqual(direct["totalNeededToday"], result["central"]["requiredCapital"])

    def test_user_after_tax_scenario_returns_one_zero_added_tax_result_without_amount_explanations(self) -> None:
        base = calculator_payload()
        base["incomeStreams"] = []
        scenario = {"status": "user_after_tax", "cases": {"central": {"total": 0}}}
        direct = run_engine(
            "calculateRetirement",
            {
                **base,
                "annualTaxExpenses": 0,
                "taxMode": "user_after_tax",
                "returnBasis": "after_fees_and_tax",
            },
        )

        result = run_ui_args("calculateTaxAdjustedScenarios", base, scenario)

        self.assertEqual(["user_after_tax"], list(result))
        self.assertEqual(0, result["user_after_tax"]["annualTaxReserve"])
        self.assertEqual(0, result["user_after_tax"]["requiredCapitalDifference"])
        self.assertEqual(direct, result["user_after_tax"]["result"])

    def test_planning_currency_conversion_preserves_the_usd_scenario(self) -> None:
        rates = {"USD": 1, "SGD": 0.7866117265603891, "EUR": 1.1645}

        self.assertAlmostEqual(
            786.6117265603891,
            run_ui(
                "convertPlanningAmount",
                {"amount": 1_000, "fromCurrency": "SGD", "toCurrency": "USD", "ratesToUsd": rates},
            ),
        )
        self.assertAlmostEqual(
            1_000,
            run_ui(
                "convertPlanningAmount",
                {
                    "amount": 786.6117265603891,
                    "fromCurrency": "USD",
                    "toCurrency": "SGD",
                    "ratesToUsd": rates,
                },
            ),
        )

    def test_planning_summary_formats_results_in_singapore_dollars(self) -> None:
        self.assertEqual(
            "Central estimate needed today: SGD\u00a01,271.",
            run_ui(
                "planningSummary",
                {
                    "result": {
                        "totalNeededToday": 1_000,
                    },
                    "currency": "SGD",
                    "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
                },
            ),
        )

    def test_converted_currency_input_respects_the_controls_step(self) -> None:
        self.assertEqual(
            30_500,
            run_ui(
                "convertPlanningControlAmount",
                {
                    "amount": 24_000,
                    "fromCurrency": "USD",
                    "toCurrency": "SGD",
                    "step": 100,
                    "ratesToUsd": {"USD": 1, "SGD": 0.7866117265603891},
                },
            ),
        )

    def test_invalid_money_amount_is_not_converted_to_zero(self) -> None:
        self.assertIsNone(
            run_ui(
                "convertPlanningControlAmount",
                {
                    "amount": None,
                    "fromCurrency": "USD",
                    "toCurrency": "EUR",
                    "step": 100,
                    "ratesToUsd": {"USD": 1, "EUR": 1.1645},
                },
            )
        )

    def test_saved_planning_currency_never_overrides_the_usd_default(self) -> None:
        self.assertEqual(
            "USD",
            run_ui(
                "preferredPlanningCurrency",
                {"storedCurrency": "SGD", "ratesToUsd": {"USD": 1, "SGD": 0.7866}},
            ),
        )
        self.assertEqual(
            "USD",
            run_ui(
                "preferredPlanningCurrency",
                {"storedCurrency": "BTC", "ratesToUsd": {"USD": 1, "SGD": 0.7866}},
            ),
        )

    def test_money_inputs_parse_and_display_thousands_separators(self) -> None:
        self.assertEqual(2_000_000, run_ui("parseMoneyInput", "2,000,000"))
        self.assertEqual(36_319, run_ui("parseMoneyInput", " 36,319 "))
        self.assertIsNone(run_ui("parseMoneyInput", "36,3x9"))
        self.assertEqual("2,000,000", run_ui("formatMoneyInputValue", 2_000_000))
        self.assertEqual("36,319", run_ui("formatMoneyInputValue", "36319"))

    def test_money_input_validation_preserves_minimum_and_step_rules(self) -> None:
        self.assertFalse(
            run_ui("isInvalidMoneyInput", {"value": "24,000", "min": 0, "step": 100})
        )
        self.assertTrue(
            run_ui("isInvalidMoneyInput", {"value": "24,050", "min": 0, "step": 100})
        )
        self.assertTrue(
            run_ui("isInvalidMoneyInput", {"value": "24x000", "min": 0, "step": 100})
        )

    def test_illustrative_return_example_is_disclosed_and_trackable(self) -> None:
        self.assertEqual(4, run_ui("illustrativeReturnExample", {}))
        source = UI_MODULE.read_text(encoding="utf-8")
        self.assertIn('el("ret-example-return").addEventListener("click"', source)
        self.assertIn('track("retirement_calculator_example_return")', source)

    def test_detail_handoff_accepts_only_allowlisted_categories(self) -> None:
        self.assertEqual(
            {"destination": "valencia", "household": "couple", "housing": "buy_now"},
            run_ui(
                "retirementPrefill",
                "?destination=valencia&household=couple&housing=buy_now&capital=900000&passport=GB",
            ),
        )
        self.assertEqual(
            {"destination": "", "household": "", "housing": ""},
            run_ui(
                "retirementPrefill",
                "?destination=%3Cscript%3E&household=family&housing=sell&income=40000",
            ),
        )

    def test_first_valid_result_is_tracked_once_and_reveals_save_intent(self) -> None:
        source = UI_MODULE.read_text(encoding="utf-8")

        self.assertIn("let hasTrackedResult = false;", source)
        self.assertIn('track("retirement_calculator_result_view")', source)
        self.assertIn("hasTrackedResult = true;", source)
        self.assertIn('el("ret-save-action").hidden = false;', source)
        self.assertIn('el("ret-save-intent-button").addEventListener("click"', source)
        self.assertIn('el("ret-save-intent-status").hidden = false;', source)

    def test_current_cost_input_events_reuse_the_latest_retirement_result(self) -> None:
        source = UI_MODULE.read_text(encoding="utf-8")

        self.assertIn(
            'el(id).addEventListener("input", function () { renderCurrentCostComparison(); });',
            source,
        )
        self.assertNotIn(
            'el(id).addEventListener("input", renderCurrentCostComparison);',
            source,
        )

    def test_engine_input_uses_selected_tax_mode_and_explicit_after_tax_return_basis(self) -> None:
        source = UI_MODULE.read_text(encoding="utf-8")

        self.assertIn("taxMode: selectedTaxMode()", source)
        self.assertIn('returnBasis: "after_fees_and_tax"', source)

    def test_converts_monthly_spending_to_annual_for_the_engine(self) -> None:
        self.assertEqual(64_596, run_ui("annualSpendingFromMonthly", 5_383))

    def test_destination_monthly_spending_rounds_to_the_nearest_hundred(self) -> None:
        self.assertEqual(9_200, run_ui("roundToNearestHundred", 9_183))
        self.assertEqual(5_500, run_ui("roundToNearestHundred", 5_517))
        self.assertEqual(0, run_ui("roundToNearestHundred", 0))
        source = UI_MODULE.read_text(encoding="utf-8")
        self.assertIn(
            "formatMoneyInputValue(roundToNearestHundred(fromUsd(benchmarkValue / 12)))",
            source,
        )

    def test_currency_conversion_keeps_only_automatic_destination_costs_rounded(self) -> None:
        self.assertEqual(
            100,
            run_ui(
                "planningControlConversionStep",
                {
                    "controlId": "ret-monthly-spending",
                    "controlStep": 1,
                    "monthlySpendingIsAutomatic": True,
                },
            ),
        )
        self.assertEqual(
            1,
            run_ui(
                "planningControlConversionStep",
                {
                    "controlId": "ret-monthly-spending",
                    "controlStep": 1,
                    "monthlySpendingIsAutomatic": False,
                },
            ),
        )
        source = UI_MODULE.read_text(encoding="utf-8")
        self.assertIn("let monthlySpendingIsAutomatic = true;", source)
        self.assertIn("monthlySpendingIsAutomatic = false;", source)

    def test_current_cost_comparison_reports_a_lower_destination_cost(self) -> None:
        self.assertEqual(
            {
                "direction": "lower",
                "monthlyDifference": 1_500,
                "annualDifference": 18_000,
                "percentDifference": 25,
                "currentBarPercent": 100,
                "destinationBarPercent": 75,
            },
            run_ui(
                "currentCostComparison",
                {"currentMonthly": 6_000, "destinationMonthly": 4_500},
            ),
        )

    def test_current_cost_comparison_reports_a_higher_destination_cost(self) -> None:
        self.assertEqual(
            {
                "direction": "higher",
                "monthlyDifference": 1_500,
                "annualDifference": 18_000,
                "percentDifference": 30,
                "currentBarPercent": 76.92307692307693,
                "destinationBarPercent": 100,
            },
            run_ui(
                "currentCostComparison",
                {"currentMonthly": 5_000, "destinationMonthly": 6_500},
            ),
        )

    def test_current_cost_comparison_handles_equal_and_missing_costs(self) -> None:
        self.assertEqual(
            {
                "direction": "same",
                "monthlyDifference": 0,
                "annualDifference": 0,
                "percentDifference": 0,
                "currentBarPercent": 100,
                "destinationBarPercent": 100,
            },
            run_ui(
                "currentCostComparison",
                {"currentMonthly": 4_000, "destinationMonthly": 4_000},
            ),
        )

    def test_retirement_target_comparison_reports_destination_reduction(self) -> None:
        self.assertEqual(
            {
                "direction": "lower",
                "targetDifference": 500_000,
                "percentDifference": 25,
            },
            run_ui(
                "retirementTargetComparison",
                {"currentTarget": 2_000_000, "destinationTarget": 1_500_000},
            ),
        )

    def test_retirement_target_comparison_reports_increase_and_handles_zero_current_target(self) -> None:
        self.assertEqual(
            {
                "direction": "higher",
                "targetDifference": 300_000,
                "percentDifference": 20,
            },
            run_ui(
                "retirementTargetComparison",
                {"currentTarget": 1_500_000, "destinationTarget": 1_800_000},
            ),
        )
        self.assertEqual(
            {
                "direction": "higher",
                "targetDifference": 1_800_000,
                "percentDifference": None,
            },
            run_ui(
                "retirementTargetComparison",
                {"currentTarget": 0, "destinationTarget": 1_800_000},
            )
        )
        self.assertIsNone(
            run_ui(
                "currentCostComparison",
                {"currentMonthly": 0, "destinationMonthly": 4_000},
            )
        )

    def test_owner_plans_use_owner_costs(self) -> None:
        profile = {
            "categories_usd": {"food": 20_000, "healthcare": 5_000},
            "annual_rent_usd": 24_000,
            "annual_owner_costs_usd": 8_000,
        }
        self.assertEqual(49_000, run_ui("annualBenchmark", {"profile": profile, "plan": "rent"}))
        for plan in ("own", "buy_now", "buy_retirement"):
            self.assertEqual(33_000, run_ui("annualBenchmark", {"profile": profile, "plan": plan}))

    def test_destination_costs_rank_the_full_input_by_monthly_household_cost(self) -> None:
        destinations = [
            {
                "destination_id": "alpha",
                "name": "Alpha",
                "profiles": {
                    "couple": {
                        "categories_usd": {"living": 100},
                        "annual_rent_usd": 1100,
                        "annual_owner_costs_usd": 500,
                    }
                },
            },
            {
                "destination_id": "beta",
                "name": "Beta",
                "profiles": {
                    "couple": {
                        "categories_usd": {"living": 200},
                        "annual_rent_usd": 400,
                        "annual_owner_costs_usd": 100,
                    }
                },
            },
        ]
        self.assertEqual(
            [
                {"destinationId": "beta", "name": "Beta", "monthlyCost": 50},
                {"destinationId": "alpha", "name": "Alpha", "monthlyCost": 100},
            ],
            run_ui(
                "rankDestinationCosts",
                {"destinations": destinations, "household": "couple", "plan": "rent"},
            ),
        )

    def test_destination_costs_use_owner_running_costs_for_purchase_plans(self) -> None:
        destinations = [
            {
                "destination_id": "alpha",
                "name": "Alpha",
                "profiles": {
                    "couple": {
                        "categories_usd": {"living": 100},
                        "annual_rent_usd": 1100,
                        "annual_owner_costs_usd": 500,
                    }
                },
            }
        ]
        for plan in ("own", "buy_now", "buy_retirement"):
            self.assertEqual(
                [{"destinationId": "alpha", "name": "Alpha", "monthlyCost": 50}],
                run_ui(
                    "rankDestinationCosts",
                    {"destinations": destinations, "household": "couple", "plan": plan},
                ),
            )

    def test_only_purchase_plans_use_property_budget(self) -> None:
        self.assertFalse(run_ui("usesPropertyBudget", "rent"))
        self.assertFalse(run_ui("usesPropertyBudget", "own"))
        self.assertTrue(run_ui("usesPropertyBudget", "buy_now"))
        self.assertTrue(run_ui("usesPropertyBudget", "buy_retirement"))

    def test_disabled_hidden_number_does_not_block_calculation(self) -> None:
        self.assertFalse(
            run_ui(
                "isInvalidNumericControl",
                {"disabled": True, "value": "", "valid": False},
            )
        )
        self.assertTrue(
            run_ui(
                "isInvalidNumericControl",
                {"disabled": False, "value": "", "valid": False},
            )
        )

    def test_negative_net_return_is_flagged(self) -> None:
        self.assertTrue(run_ui("isNegativeRate", -0.001))
        self.assertFalse(run_ui("isNegativeRate", 0))
        self.assertFalse(run_ui("isNegativeRate", 0.001))

    def test_benchmark_panel_is_hidden_when_household_does_not_match(self) -> None:
        self.assertFalse(run_ui("isBenchmarkPanelHidden", {"panel": "couple", "selected": "couple"}))
        self.assertTrue(run_ui("isBenchmarkPanelHidden", {"panel": "single", "selected": "couple"}))

    def test_benchmark_rows_are_partitioned_by_continent(self) -> None:
        rows = [
            {"id": f"europe-{index}", "continent": "europe"}
            for index in range(12)
        ] + [{"id": "asia-1", "continent": "asia"}]
        result = run_ui(
            "partitionBenchmarkRows",
            {"rows": rows, "selectedContinent": "europe", "visibleCount": 10},
        )
        self.assertEqual([f"europe-{index}" for index in range(10)], [row["id"] for row in result["visible"]])
        self.assertEqual(["europe-10", "europe-11"], [row["id"] for row in result["expandable"]])
        self.assertEqual(["asia-1"], [row["id"] for row in result["excluded"]])

    def test_all_continents_preserves_the_full_benchmark_order(self) -> None:
        rows = [{"id": str(index), "continent": "europe"} for index in range(11)]
        result = run_ui(
            "partitionBenchmarkRows",
            {"rows": rows, "selectedContinent": "all", "visibleCount": 10},
        )
        self.assertEqual([str(index) for index in range(10)], [row["id"] for row in result["visible"]])
        self.assertEqual(["10"], [row["id"] for row in result["expandable"]])

    def test_housing_guidance_distinguishes_rent_owner_costs_and_purchase_budget(self) -> None:
        self.assertEqual(
            "Monthly retirement living expenses, including rent.",
            run_ui("housingGuidance", "rent"),
        )
        self.assertEqual(
            "Monthly retirement living expenses, including owner running costs; no new home purchase.",
            run_ui("housingGuidance", "own"),
        )
        self.assertEqual(
            "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase.",
            run_ui("housingGuidance", "buy_now"),
        )
        self.assertEqual(
            "Monthly retirement living expenses after purchase, including owner running costs but not the home purchase at retirement.",
            run_ui("housingGuidance", "buy_retirement"),
        )

    def test_housing_expense_labels_name_the_included_cost(self) -> None:
        self.assertEqual(
            {
                "input": "Monthly retirement living expenses including rent",
                "result": "Annual spending incl. rent",
            },
            run_ui("housingExpenseLabels", "rent"),
        )
        for plan in ("own", "buy_now", "buy_retirement"):
            self.assertEqual(
                {
                    "input": "Monthly retirement living expenses including owner costs",
                    "result": "Annual spending incl. owner costs",
                },
                run_ui("housingExpenseLabels", plan),
            )

    def test_accumulation_chart_model_stacks_each_funding_source_by_year(self) -> None:
        result = run_ui(
            "accumulationChartModel",
            {
                "series": [
                    {"year": 0, "lumpSumValue": 100, "contributionValue": 0, "totalValue": 100},
                    {"year": 1, "lumpSumValue": 110, "contributionValue": 40, "totalValue": 150},
                ],
                "targetValue": 200,
            },
        )
        self.assertEqual(200, result["maximum"])
        self.assertEqual(18, result["targetY"])
        self.assertEqual(
            {
                "year": 1,
                "lumpSumValue": 110,
                "contributionValue": 40,
                "totalValue": 150,
                "lumpHeight": 132,
                "contributionHeight": 48,
            },
            result["years"][1],
        )

    def test_return_sensitivity_uses_one_percentage_point_either_side(self) -> None:
        self.assertEqual(
            [
                {"key": "lower", "label": "Lower return", "rate": 0.04},
                {"key": "selected", "label": "Your assumption", "rate": 0.05},
                {"key": "higher", "label": "Higher return", "rate": 0.06},
            ],
            run_ui("sensitivityRates", 0.05),
        )

    def test_planning_summary_is_the_single_central_needed_today_headline(self) -> None:
        self.assertEqual(
            "Central estimate needed today: $986,656.",
            run_ui(
                "planningSummary",
                {
                    "totalNeededToday": 986_656,
                },
            ),
        )
        self.assertEqual(
            "Estimate needed today: $986,656.",
            run_ui(
                "planningSummary",
                {
                    "result": {"totalNeededToday": 986_656},
                    "taxScenario": {"status": "user_after_tax"},
                },
            ),
        )

    def test_chart_tooltip_reports_age_and_each_source_for_the_selected_year(self) -> None:
        self.assertEqual(
            {
                "heading": "Year 3 · age 53",
                "lumpSum": "$110",
                "contributions": "$40",
                "total": "$150",
                "accessibleLabel": "Year 3, age 53. Lump sum and growth $110. Contributions and growth $40. Total $150.",
            },
            run_ui(
                "accumulationTooltipContent",
                {
                    "currentAge": 50,
                    "point": {"year": 3, "lumpSumValue": 110, "contributionValue": 40, "totalValue": 150},
                },
            ),
        )


if __name__ == "__main__":
    unittest.main()
