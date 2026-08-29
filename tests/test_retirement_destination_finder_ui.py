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

    def test_currency_change_and_money_control_wiring_are_safe(self) -> None:
        source = UI.read_text()
        self.assertIn('const moneyControlIds = [', source)
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
            },
        )
        self.assertIn("No destinations are within reach yet", read)
        self.assertIn("Fukuoka / Itoshima is the closest modeled match", read)
        self.assertIn("$322,418", read)

    def test_tier_labels_are_plain_language(self) -> None:
        self.assertEqual("Within reach", run_ui("tierLabel", "within_reach"))
        self.assertEqual("Close", run_ui("tierLabel", "close"))
        self.assertEqual("Stretch", run_ui("tierLabel", "stretch"))

    def test_chart_tooltip_exposes_year_and_amount(self) -> None:
        tooltip = run_ui("chartTooltip", {"year": 7, "portfolio": 432100})
        self.assertEqual("Year 7", tooltip["heading"])
        self.assertIn("$432,100", tooltip["value"])
        self.assertIn("Year 7", tooltip["accessibleLabel"])

    def test_mobile_chart_width_preserves_one_touch_target_per_year(self) -> None:
        self.assertEqual(779, run_ui("mobileChartWidth", 16))
        self.assertEqual(44, run_ui("mobileChartWidth", 1))

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
