from __future__ import annotations

import json
import subprocess
import unittest
from datetime import date
from pathlib import Path

from src.fire_abroad import load_fire_abroad, validate_fire_abroad_payload


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_tax_scenarios.js"
FIXTURE = ROOT / "tests" / "fixtures" / "fire_tax_scenarios.json"


def run_scenario(payload: object) -> object:
    script = (
        "const scenarios = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify("
        "scenarios.estimateTaxScenario(input.input, input.country)"
        "));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(ENGINE), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def fixture_country() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["country"]


class FireTaxScenarioTests(unittest.TestCase):
    def test_total_audit_uses_only_active_categories_and_sources(self) -> None:
        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "full_relocation",
                    "dependableIncome": 40_000,
                    "portfolioWithdrawals": 60_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "none",
                    "wealthBand": "under_threshold",
                    "asOf": "2026-09-01",
                },
                "country": fixture_country(),
            }
        )
        central = result["amountExplanations"]["central"]
        total = central["total"]

        self.assertEqual("included", central["incomeTaxReserve"]["status"])
        self.assertEqual("not_applicable", central["propertyTaxReserve"]["status"])
        self.assertEqual("not_applicable", central["wealthTaxReserve"]["status"])
        self.assertEqual("included", central["complianceReserve"]["status"])
        self.assertEqual(
            ["income tax reserve", "Annual filing and advice allowance"],
            total["inclusions"],
        )
        self.assertIn("Annual property ownership tax allowance (not applicable)", total["exclusions"])
        self.assertIn("Annual wealth-tax planning allowance (not applicable)", total["exclusions"])
        self.assertEqual(["tax-residence", "income-scope"], total["sourceIds"])
        self.assertEqual([], central["wealthTaxReserve"]["sourceIds"])
        wealth = next(item for item in result["explanations"] if item["category"] == "wealth_tax")
        self.assertEqual("not_applicable", wealth["status"])
        self.assertEqual([], wealth["sourceIds"])

    def test_user_after_tax_has_one_zero_case_with_complete_excluded_audits(self) -> None:
        result = run_scenario(
            {
                "input": {"taxMode": "user_after_tax"},
                "country": {},
            }
        )

        self.assertEqual("user_after_tax", result["status"])
        self.assertEqual(["user_after_tax"], list(result["cases"]))
        self.assertEqual(["user_after_tax"], list(result["amountExplanations"]))
        fields = result["amountExplanations"]["user_after_tax"]
        self.assertEqual(
            {
                "total",
                "incomeTaxReserve",
                "propertyTaxReserve",
                "wealthTaxReserve",
                "complianceReserve",
            },
            set(fields),
        )
        for field_name, explanation in fields.items():
            with self.subTest(field=field_name):
                self.assertEqual(0, result["cases"]["user_after_tax"][field_name])
                self.assertEqual("excluded", explanation["status"])
                self.assertTrue(explanation["formula"])
                self.assertTrue(explanation["assumptions"])
                self.assertTrue(explanation["inclusions"])
                self.assertTrue(explanation["exclusions"])
                self.assertEqual("not_applicable", explanation["taxYear"])
                self.assertEqual("user_supplied", explanation["confidence"])
                self.assertEqual([], explanation["sourceIds"])

    def test_freshness_crosses_after_day_366_while_tax_year_remains_evidence_year(self) -> None:
        country = fixture_country()
        common = {
            "taxMode": "destination_estimate",
            "stayMode": "full_relocation",
            "dependableIncome": 40_000,
            "portfolioWithdrawals": 60_000,
            "realizedGainIntensity": "moderate",
            "propertyUse": "none",
            "wealthBand": "under_threshold",
        }

        boundary = run_scenario({"input": {**common, "asOf": "2027-09-02"}, "country": country})
        crossed = run_scenario({"input": {**common, "asOf": "2027-09-03"}, "country": country})

        self.assertEqual("available", boundary["status"])
        self.assertEqual("2026", boundary["amountExplanations"]["central"]["total"]["taxYear"])
        self.assertEqual("unavailable", crossed["status"])
        self.assertIn("stale", crossed["explanations"][0]["reason"])

    def test_destination_estimate_returns_ordered_data_backed_cases(self) -> None:
        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "full_relocation",
                    "dependableIncome": 40_000,
                    "portfolioWithdrawals": 60_000,
                    "realizedGainIntensity": "moderate",
                    "propertyPrice": 500_000,
                    "propertyUse": "personal",
                    "wealthBand": "under_threshold",
                    "asOf": "2026-09-01",
                },
                "country": fixture_country(),
            }
        )

        self.assertEqual(["favorable", "central", "adverse"], list(result["cases"]))
        self.assertLessEqual(result["cases"]["favorable"]["total"], result["cases"]["central"]["total"])
        self.assertLessEqual(result["cases"]["central"]["total"], result["cases"]["adverse"]["total"])
        self.assertEqual(10_500, result["cases"]["favorable"]["total"])
        self.assertEqual(20_500, result["cases"]["central"]["total"])
        self.assertEqual(32_000, result["cases"]["adverse"]["total"])
        self.assertEqual(100_000, result["planningBase"])
        self.assertEqual(["tax-residence", "income-scope", "property-tax"], result["sourceIds"])

    def test_amount_explanations_cover_each_case_amount(self) -> None:
        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "full_relocation",
                    "dependableIncome": 40_000,
                    "portfolioWithdrawals": 60_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "personal",
                    "wealthBand": "under_threshold",
                    "asOf": "2026-09-01",
                },
                "country": fixture_country(),
            }
        )

        self.assertEqual(["favorable", "central", "adverse"], list(result["amountExplanations"]))
        for case_name, fields in result["amountExplanations"].items():
            with self.subTest(case=case_name):
                self.assertEqual(
                    {
                        "total",
                        "incomeTaxReserve",
                        "propertyTaxReserve",
                        "wealthTaxReserve",
                        "complianceReserve",
                    },
                    set(fields),
                )
            for field_name, explanation in fields.items():
                with self.subTest(case=case_name, field=field_name):
                    self.assertIsInstance(explanation["formula"], str)
                    self.assertTrue(explanation["formula"])
                    self.assertIsInstance(explanation["assumptions"], list)
                    self.assertTrue(explanation["assumptions"])
                    self.assertIsInstance(explanation["inclusions"], list)
                    self.assertTrue(explanation["inclusions"])
                    self.assertIsInstance(explanation["exclusions"], list)
                    self.assertTrue(explanation["exclusions"])
                    self.assertEqual("2026", explanation["taxYear"])
                    self.assertEqual("medium_high", explanation["confidence"])
                    self.assertIsInstance(explanation["sourceIds"], list)
                    if result["cases"][case_name][field_name] > 0:
                        self.assertTrue(explanation["sourceIds"])

    def test_gain_intensity_modifier_changes_only_the_income_tax_reserve(self) -> None:
        payload = {
            "input": {
                "taxMode": "destination_estimate",
                "stayMode": "part_year",
                "dependableIncome": 40_000,
                "portfolioWithdrawals": 60_000,
                "realizedGainIntensity": "high",
                "propertyUse": "none",
                "wealthBand": "under_threshold",
                "asOf": "2026-09-01",
            },
            "country": fixture_country(),
        }

        result = run_scenario(payload)

        self.assertEqual(5_000, result["cases"]["favorable"]["incomeTaxReserve"])
        self.assertEqual(10_000, result["cases"]["central"]["incomeTaxReserve"])
        self.assertEqual(17_500, result["cases"]["adverse"]["incomeTaxReserve"])
        self.assertEqual(1_000, result["cases"]["favorable"]["complianceReserve"])

    def test_property_tax_already_in_owner_costs_is_excluded_explicitly(self) -> None:
        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "seasonal",
                    "dependableIncome": 20_000,
                    "portfolioWithdrawals": 20_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "personal",
                    "wealthBand": "above_threshold",
                    "propertyTaxIncludedInRetirementCosts": True,
                    "asOf": "2026-09-01",
                },
                "country": fixture_country(),
            }
        )

        self.assertEqual(0, result["cases"]["central"]["propertyTaxReserve"])
        self.assertEqual(3_000, result["cases"]["central"]["wealthTaxReserve"])
        property_explanations = [
            item for item in result["explanations"] if item["category"] == "property_tax"
        ]
        self.assertEqual(1, len(property_explanations))
        self.assertEqual("excluded", property_explanations[0]["status"])
        self.assertIn("already included", property_explanations[0]["reason"])

    def test_missing_or_pending_scenario_evidence_is_unavailable_not_zero(self) -> None:
        country = fixture_country()
        del country["tax_screen"]["annual_allowances"]

        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "seasonal",
                    "dependableIncome": 20_000,
                    "portfolioWithdrawals": 20_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "personal",
                    "wealthBand": "under_threshold",
                    "asOf": "2026-09-01",
                },
                "country": country,
            }
        )

        self.assertEqual("unavailable", result["status"])
        self.assertIsNone(result["cases"]["central"]["total"])
        self.assertTrue(result["conditional"])

    def test_partial_missing_allowance_category_is_unavailable_not_zero(self) -> None:
        country = fixture_country()
        del country["tax_screen"]["annual_allowances"]["property_tax"]

        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "seasonal",
                    "dependableIncome": 20_000,
                    "portfolioWithdrawals": 20_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "personal",
                    "wealthBand": "under_threshold",
                    "asOf": "2026-09-01",
                },
                "country": country,
            }
        )

        self.assertEqual("unavailable", result["status"])
        self.assertIsNone(result["cases"]["central"]["propertyTaxReserve"])
        self.assertIsNone(result["cases"]["central"]["total"])
        self.assertIn("allowance", result["explanations"][0]["reason"])

    def test_destination_estimate_requires_a_freshness_anchor(self) -> None:
        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "seasonal",
                    "dependableIncome": 20_000,
                    "portfolioWithdrawals": 20_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "personal",
                    "wealthBand": "under_threshold",
                },
                "country": fixture_country(),
            }
        )

        self.assertEqual("unavailable", result["status"])
        self.assertIsNone(result["cases"]["central"]["total"])
        self.assertIn("freshness", result["explanations"][0]["reason"])

    def test_stale_scenario_evidence_is_unavailable_not_zero(self) -> None:
        country = fixture_country()
        country["tax_screen"]["last_reviewed"] = "2024-01-01"

        result = run_scenario(
            {
                "input": {
                    "taxMode": "destination_estimate",
                    "stayMode": "seasonal",
                    "dependableIncome": 20_000,
                    "portfolioWithdrawals": 20_000,
                    "realizedGainIntensity": "moderate",
                    "propertyUse": "personal",
                    "wealthBand": "under_threshold",
                    "asOf": "2026-09-01",
                },
                "country": country,
            }
        )

        self.assertEqual("unavailable", result["status"])
        self.assertIsNone(result["cases"]["central"]["total"])
        self.assertIn("stale", result["explanations"][0]["reason"])

    def test_fire_abroad_validation_requires_tax_scenario_assumptions(self) -> None:
        payload = load_fire_abroad()
        destination_ids = set(payload["launch_destination_ids"])
        retirement_ids = set(payload["launch_destination_ids"])
        for country in payload["countries"].values():
            screen = country["tax_screen"]
            source_id = screen["source_ids"][0]
            screen["gain_intensity_modifiers"] = {
                "low": 0.75,
                "moderate": 1,
                "high": 1.25,
            }
            screen["gain_intensity_source_ids"] = [source_id]
            screen["annual_allowances"] = {
                "property_tax": {
                    "label": "Annual property ownership tax allowance",
                    "favorable_usd": 0,
                    "central_usd": 0,
                    "adverse_usd": 0,
                    "applies_to_property_uses": ["personal", "rental", "mixed"],
                    "source_ids": [source_id],
                },
                "wealth_tax": {
                    "label": "Annual wealth-tax planning allowance",
                    "favorable_usd": 0,
                    "central_usd": 0,
                    "adverse_usd": 0,
                    "applies_to_wealth_bands": ["above_threshold"],
                    "source_ids": [source_id],
                },
                "compliance": {
                    "label": "Annual filing and advice allowance",
                    "favorable_usd": 0,
                    "central_usd": 0,
                    "adverse_usd": 0,
                    "source_ids": [source_id],
                },
            }

        self.assertEqual(
            [],
            validate_fire_abroad_payload(
                payload,
                destination_ids=destination_ids,
                retirement_ids=retirement_ids,
                as_of=date(2026, 9, 1),
            ),
        )

        del payload["countries"]["Spain"]["tax_screen"]["gain_intensity_modifiers"]
        errors = validate_fire_abroad_payload(
            payload,
            destination_ids=destination_ids,
            retirement_ids=retirement_ids,
            as_of=date(2026, 9, 1),
        )
        self.assertTrue(any("gain_intensity_modifiers" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
