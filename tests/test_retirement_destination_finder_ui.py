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
    def test_tax_result_fields_are_written_as_text_not_generated_html(self) -> None:
        script = (
            "const ui = require(process.argv[1]);"
            "const values = {};"
            "const nodes = {};"
            "['target','range','centralGap','favorableGap','adverseGap'].forEach((key) => {"
            "  const node = {};"
            "  Object.defineProperty(node, 'innerHTML', {set() { throw new Error('unsafe HTML sink'); }});"
            "  Object.defineProperty(node, 'textContent', {set(value) { values[key] = value; }});"
            "  nodes[key] = node;"
            "});"
            "ui.writeTaxResultFields(nodes, {"
            "  retirementTarget: 120000, retirementTargetRange: [110000, 130000],"
            "  favorableGap: -10000, surplusGap: -20000, adverseGap: -30000, taxStatus: 'available'"
            "});"
            "process.stdout.write(JSON.stringify(values));"
        )
        result = subprocess.run(
            ["node", "-e", script, str(UI)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(
            {
                "target": "$120,000",
                "range": "$110,000–$130,000",
                "centralGap": "−$20,000",
                "favorableGap": "−$10,000",
                "adverseGap": "−$30,000",
            },
            json.loads(result.stdout),
        )

    def test_conditional_tax_result_fields_never_render_null_as_zero(self) -> None:
        script = (
            "const ui = require(process.argv[1]);"
            "const values = {};"
            "const nodes = {};"
            "['target','range','centralGap','favorableGap','adverseGap'].forEach((key) => {"
            "  Object.defineProperty(nodes, key, {value: {set textContent(value) { values[key] = value; }}});"
            "});"
            "ui.writeTaxResultFields(nodes, {"
            "  retirementTarget: null, retirementTargetRange: [null, null],"
            "  favorableGap: null, surplusGap: null, adverseGap: null, taxStatus: 'unavailable'"
            "});"
            "process.stdout.write(JSON.stringify(values));"
        )
        result = subprocess.run(
            ["node", "-e", script, str(UI)],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual({key: "Unavailable" for key in (
            "target", "range", "centralGap", "favorableGap", "adverseGap"
        )}, json.loads(result.stdout))

    def test_analytics_payload_excludes_tax_inputs_and_results(self) -> None:
        payload = run_ui(
            "finderAnalyticsPayload",
            {
                "housingPlan": "buy_now",
                "purchaseMethod": "mortgage",
                "taxMode": "destination_estimate",
                "taxProfile": {"dependableIncome": 90_000, "wealthBand": "above_threshold"},
                "taxResult": {"central": 1_200_000, "adverse": 1_400_000},
            },
        )
        self.assertEqual({"housing_plan": "buy_now", "purchase_method": "mortgage"}, payload)

    def test_evidence_summary_exposes_conditional_tax_results_beyond_the_display_cap(self) -> None:
        self.assertEqual(
            "7 destinations have conditional tax-adjusted results because current evidence is unavailable.",
            run_ui("finderEvidenceSummary", {"excludedCount": 0, "conditionalCount": 7}),
        )
        self.assertEqual(
            "1 destination could not be recommended under these assumptions.",
            run_ui("finderEvidenceSummary", {"excludedCount": 1, "conditionalCount": 0}),
        )

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
        self.assertEqual("Conditional", run_ui("tierLabel", "conditional"))

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
