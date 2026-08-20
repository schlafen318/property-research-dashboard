from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "src" / "retirement_destination_finder_ui.js"


def run_ui(function_name: str, payload: object) -> object:
    script = (
        "const ui = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(ui.{function_name}(input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(UI), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class RetirementDestinationFinderUITests(unittest.TestCase):
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

    def test_tier_labels_are_plain_language(self) -> None:
        self.assertEqual("Within reach", run_ui("tierLabel", "within_reach"))
        self.assertEqual("Close", run_ui("tierLabel", "close"))
        self.assertEqual("Stretch", run_ui("tierLabel", "stretch"))

    def test_chart_tooltip_exposes_year_and_amount(self) -> None:
        tooltip = run_ui("chartTooltip", {"year": 7, "portfolio": 432100})
        self.assertEqual("Year 7", tooltip["heading"])
        self.assertIn("$432,100", tooltip["value"])
        self.assertIn("Year 7", tooltip["accessibleLabel"])

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
