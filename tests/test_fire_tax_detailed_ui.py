from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.test_fire_tax_detailed import detailed_payload
from src import build_unified_app


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src" / "fire_tax_detailed_ui.js"


def run_node(expression: str, payload: dict) -> object:
    script = (
        "const api=require(process.argv[1]);const input=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify({expression}));"
    )
    completed = subprocess.run(
        ["node", "-e", script, str(MODULE), json.dumps(payload)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


class DetailedFireTaxUiTests(unittest.TestCase):
    def test_real_hong_kong_to_dubai_pair_executes_from_live_amounts(self) -> None:
        ui_payload = build_unified_app.detailed_fire_tax_page_payload()
        planning = {
            "currency": "USD", "currentAge": 50, "retirementAge": 60, "horizonYears": 30,
            "annualSpending": 72000, "annualPension": 0, "annualOtherIncome": 0,
            "annualRentalIncome": 0, "annualWithdrawals": 18000, "propertyPrice": 0,
            "housingPlan": "rent", "propertyUse": "personal", "selectedAfterTaxReturn": 0.04,
            "planningRange": {"minimum": 900000, "maximum": 1100000}, "aedPerCurrency": 3.6725,
        }
        answers = {
            "daysInDestination": 200, "daysInHome": 30, "isHongKongTreatyResident": False, "hasHongKongSourceIncome": False,
            "hasHongKongProperty": False, "activityType": "retired_or_employee",
            "retirementAccountClassification": "personal_investment", "annualEmploymentIncome": 0,
        }

        response = run_node("api.runRefinement(input)", {
            "destinationId": "dubai", "homeJurisdictionId": "hong-kong",
            "uiPayload": ui_payload, "planningFacts": planning, "answers": answers,
        })

        self.assertEqual("calculated", response["result"]["status"])
        self.assertEqual(0, response["result"]["totals"]["annualTax"])
        self.assertIn("Hong Kong to Dubai", response["markup"])

    def test_live_planning_facts_build_profile_without_bundle_amounts(self) -> None:
        definition = {
            "id": "hong-kong-to-dubai",
            "tax_year": 2026,
            "home_jurisdiction_id": "hong-kong",
            "destination_id": "dubai",
            "runtime_definition": {"factory": "hong-kong-to-dubai-v1"},
        }
        facts = {
            "currency": "USD", "currentAge": 50, "retirementAge": 60,
            "horizonYears": 30, "annualSpending": 72000, "annualPension": 24000,
            "annualOtherIncome": 6000, "annualRentalIncome": 0,
            "annualWithdrawals": 18000, "propertyPrice": 500000,
            "housingPlan": "buy_retirement", "propertyUse": "personal",
            "selectedAfterTaxReturn": 0.04, "planningRange": {"minimum": 900000, "maximum": 1100000},
            "monthlyIncomeBeforeRetirement": 8000, "incomeInvestedRate": 0.25,
            "generalInflation": 0.025, "propertyInflation": 0.03, "emergencyReserveMonths": 12,
            "hasLiveDependableIncome": True, "dependableIncomeIndexed": True,
        }
        answers = {
            "daysInDestination": 200, "daysInHome": 30,
            "hasHongKongSourceIncome": False, "hasHongKongProperty": False,
            "activityType": "retired_or_employee", "annualServiceCharges": 4000,
            "annualHousingFee": 2500, "propertyType": "villa_or_apartment",
            "financingType": "cash",
            "expectedGiftValuation": 575000,
            "annualDividends": 50000, "annualInterest": 1000, "annualRealizedGains": 2000,
            "giftRelationship": "first_degree_family", "retirementAccountClassification": "personal_investment",
        }

        profile = run_node("api.buildDetailedProfile(input.definition,input.facts,input.answers)", {
            "definition": definition, "facts": facts, "answers": answers,
        })

        self.assertEqual(24000, profile["destination"]["income"]["privatePension"])
        self.assertEqual(18000, profile["destination"]["income"]["retirementAccountWithdrawal"])
        self.assertEqual(500000, profile["destination"]["property"]["purchasePrice"])
        self.assertEqual(575000, profile["destination"]["property"]["giftValuation"])
        self.assertIn("dividends", profile["retirement"]["dependableIncomeCategories"])
        self.assertNotIn("dividends", profile["retirement"]["returnCoveredCategories"])
        self.assertEqual(72000, profile["retirement"]["baseInput"]["expenseCategories"][0]["amount"])
        self.assertEqual(0.04, profile["retirement"]["selectedAfterTaxReturn"])
        self.assertEqual(8000, profile["retirement"]["baseInput"]["monthlyIncomeBeforeRetirement"])
        self.assertEqual(0.25, profile["retirement"]["baseInput"]["incomeInvestedRate"])
        self.assertEqual(12, profile["retirement"]["baseInput"]["emergencyReserveMonths"])
        self.assertTrue(profile["retirement"]["dependableIncomeIndexed"])
        self.assertNotIn("profile", definition["runtime_definition"])

    def test_renter_profile_marks_property_calculation_not_applicable(self) -> None:
        definition = {"tax_year": 2026, "destination_id": "dubai"}
        facts = {"currency": "USD", "propertyPrice": 0, "housingPlan": "rent"}

        profile = run_node("api.buildDetailedProfile(input.definition,input.facts,{})", {"definition": definition, "facts": facts})

        self.assertFalse(profile["destination"]["property"]["enabled"])
        self.assertEqual([], profile["destination"]["property"]["activeStages"])

    def test_profile_access_fails_closed_outside_narrow_supported_facts(self) -> None:
        payload = {
            "tax_year": 2026,
            "supported_profiles": {
                "hong-kong-to-dubai": {
                    "id": "hong-kong-to-dubai", "detailed_enabled": True, "synthetic": False,
                    "destination_id": "dubai", "home_jurisdiction_id": "hong-kong",
                    "source_ids": ["uae", "hk", "treaty", "dld"],
                    "tax_year": 2026,
                    "income_categories": ["private_pension", "government_pension", "social_security", "dividends", "interest", "realized_gains", "retirement_account_withdrawal", "rental_income", "employment_consulting"],
                    "property_lifecycle": ["purchase", "annual", "rental", "sale", "inheritance", "gift"],
                    "runtime_definition": {"factory": "hong-kong-to-dubai-v1", "rule_constants": {}},
                }
            },
            "sources": [
                {"id": source_id, "source_kind": "official", "url": "https://example.gov/" + source_id,
                 "checked_on": "2026-09-01", "effective_from": "2026-01-01"}
                for source_id in ("uae", "hk", "treaty", "dld")
            ],
        }
        payload = build_unified_app.detailed_fire_tax_page_payload()
        base = {
            "daysInDestination": 200, "daysInHome": 30,
            "hasHongKongSourceIncome": False, "hasHongKongProperty": False,
            "activityType": "retired_or_employee",
        }

        supported = run_node(
            "api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},input.facts)",
            {"payload": payload, "facts": base},
        )
        hk_income = run_node(
            "api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},Object.assign({},input.facts,{hasHongKongSourceIncome:true}))",
            {"payload": payload, "facts": base},
        )
        business = run_node(
            "api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},Object.assign({},input.facts,{activityType:'business_or_consulting'}))",
            {"payload": payload, "facts": base},
        )

        self.assertTrue(supported["available"])
        self.assertFalse(hk_income["available"])
        self.assertIn("Hong Kong-source", hk_income["reason"])
        self.assertFalse(business["available"])
        self.assertIn("business", business["reason"].lower())

        buyer = run_node(
            "api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},Object.assign({},input.facts,{propertyPrice:500000,housingPlan:'buy_retirement'}))",
            {"payload": payload, "facts": base},
        )
        self.assertFalse(buyer["available"])
        self.assertIn("property-tax branch", buyer["reason"])

        pension = run_node(
            "api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},Object.assign({},input.facts,{annualPension:12000}))",
            {"payload": payload, "facts": base},
        )
        self.assertFalse(pension["available"])
        self.assertIn("payer country", pension["reason"])

        dividends = run_node(
            "api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},Object.assign({},input.facts,{annualDividends:50000}))",
            {"payload": payload, "facts": base},
        )
        self.assertFalse(dividends["available"])
        self.assertIn("source-country", dividends["reason"])

        incomplete = run_node(
            "(()=>{delete input.payload.supported_profiles['hong-kong-to-dubai'].runtime_definition.supported_housing_plans;return api.profileAccess('dubai',input.payload,{homeJurisdictionId:'hong-kong'},input.facts);})()",
            {"payload": payload, "facts": base},
        )
        self.assertFalse(incomplete["available"])
        self.assertIn("coverage", incomplete["reason"])

    def test_fully_enabled_destination_home_bundle_runs_end_to_end(self) -> None:
        calculation = detailed_payload()
        payload = {
            "destinationId": "fixture-destination",
            "homeJurisdictionId": "fixture-home",
            "uiPayload": {
                "sources": [],
                "jurisdictions": {
                    "fixture-destination": {
                        "detailed_enabled": True,
                        "synthetic": False,
                        "supported_home_jurisdiction_ids": ["fixture-home"],
                        "runtime_bundles": {
                            "fixture-home": {
                                "profile": calculation["profile"],
                                "rules": calculation["rules"],
                                "questions": [],
                            }
                        },
                    }
                },
            },
            "answers": {},
        }

        result = run_node("api.runRefinement(input)", payload)

        self.assertEqual("calculated", result["result"]["status"])
        self.assertEqual(21_150, result["result"]["totals"]["annualTax"])
        self.assertEqual(1, result["markup"].count("<table"))
        self.assertIn("Capital needed today", result["markup"])

    def test_access_requires_an_explicit_real_enabled_complete_bundle(self) -> None:
        payload = {
            "jurisdictions": {
                "disabled": {"detailed_enabled": False, "synthetic": False, "runtime_bundle": {}},
                "synthetic": {"detailed_enabled": True, "synthetic": True, "runtime_bundle": {}},
                "missing": {"detailed_enabled": True, "synthetic": False},
                "ready": {"detailed_enabled": True, "synthetic": False, "supported_home_jurisdiction_ids": ["home"], "runtime_bundles": {"home": {"rules": {}}}},
            }
        }

        result = run_node(
            "Object.fromEntries(Object.keys(input.jurisdictions).map(id=>[id,api.jurisdictionAccess(id,input,{homeJurisdictionId:'home'})]))",
            payload,
        )

        self.assertFalse(result["disabled"]["available"])
        self.assertFalse(result["synthetic"]["available"])
        self.assertFalse(result["missing"]["available"])
        self.assertTrue(result["ready"]["available"])

        no_home = run_node("api.jurisdictionAccess('ready',input,{homeJurisdictionId:''})", payload)
        self.assertFalse(no_home["available"])
        self.assertIn("home tax jurisdiction", no_home["reason"])

    def test_question_markup_uses_native_label_help_and_control_contract(self) -> None:
        question = {
            "id": "days-there",
            "fact": "daysThere",
            "control": "number",
            "label": "How many days will you spend there?",
            "reason": "This can change the residence branch.",
            "acceptedValues": {"min": 0, "max": 365, "step": 1, "integer": True},
        }

        markup = run_node("api.questionMarkup(input)", question)

        self.assertIn('<label for="fire-tax-question-days-there">', markup)
        self.assertIn('id="fire-tax-question-days-there"', markup)
        self.assertIn('type="number"', markup)
        self.assertIn('aria-describedby="fire-tax-question-days-there-help"', markup)
        self.assertIn('min="0" max="365" step="1"', markup)

    def test_select_and_radio_questions_keep_native_keyboard_controls_labeled(self) -> None:
        select_question = {
            "id": "ties", "fact": "ties", "control": "select", "label": "Where are your closest ties?",
            "reason": "This controls a branch.", "acceptedValues": ["home", "destination"],
        }
        radio_question = {
            "id": "account", "fact": "account", "control": "radio", "label": "Account type",
            "reason": "This controls a branch.", "acceptedValues": ["pension", "other"],
        }

        select_markup = run_node("api.questionMarkup(input)", select_question)
        radio_markup = run_node("api.questionMarkup(input)", radio_question)

        self.assertIn('for="fire-tax-question-ties"', select_markup)
        self.assertIn('id="fire-tax-question-ties"', select_markup)
        self.assertIn("<fieldset", radio_markup)
        self.assertIn("<legend>Account type</legend>", radio_markup)
        self.assertIn('id="fire-tax-question-account-0"', radio_markup)
        self.assertIn('for="fire-tax-question-account-0"', radio_markup)

    def test_pair_questions_reveal_only_applicable_plain_language_followups(self) -> None:
        planning = {"propertyPrice": 500000, "housingPlan": "buy_retirement", "propertyUse": "personal"}
        eligibility = {
            "daysInDestination": 200, "daysInHome": 30, "isHongKongTreatyResident": False,
            "hasHongKongSourceIncome": False, "hasHongKongProperty": False,
            "activityType": "retired_or_employee",
        }

        first = run_node("api.nextPairQuestions(input.planning,{})", {"planning": planning})
        advanced = run_node("api.nextPairQuestions(input.planning,input.answers)", {"planning": planning, "answers": eligibility})
        gift = run_node("api.nextPairQuestions(input.planning,Object.assign({},input.answers,{exitPlan:'gift'}))", {"planning": planning, "answers": eligibility})

        self.assertIn("daysInDestination", [item["fact"] for item in first])
        self.assertNotIn("annualServiceCharges", [item["fact"] for item in first])
        self.assertIn("annualServiceCharges", [item["fact"] for item in advanced])
        self.assertNotIn("giftRelationship", [item["fact"] for item in advanced])
        self.assertIn("giftRelationship", [item["fact"] for item in gift])
        self.assertIn("expectedGiftValuation", [item["fact"] for item in gift])
        activity = next(item for item in first if item["fact"] == "activityType")
        self.assertEqual("Retired or employee only", activity["options"][0]["label"])

    def test_option_markup_shows_plain_language_labels_not_internal_values(self) -> None:
        question = {
            "id": "activity", "fact": "activityType", "control": "radio", "label": "Work activity",
            "reason": "Material", "acceptedValues": ["retired_or_employee", "business_or_consulting"],
            "options": [
                {"value": "retired_or_employee", "label": "Retired or employee only"},
                {"value": "business_or_consulting", "label": "I run a business or consult"},
            ],
        }

        markup = run_node("api.questionMarkup(input)", question)

        self.assertIn("Retired or employee only", markup)
        self.assertNotIn("> retired_or_employee</label>", markup)

    def test_result_markup_has_one_reconciled_table_branch_comparison_and_sources(self) -> None:
        payload = {
            "result": {
                "status": "conditional",
                "currency": "EUR",
                "taxYear": 2026,
                "totals": {
                    "annualTax": {"minimum": 1000, "maximum": 1800},
                    "oneTimeTaxes": 2500,
                    "grossDependableIncome": 30000,
                    "afterTaxDependableIncome": {"minimum": 28200, "maximum": 29000},
                },
                "retirementProjection": {
                    "status": "conditional",
                    "planningRange": {"minimum": 500000, "maximum": 700000},
                    "capitalRange": {"minimum": 540000, "maximum": 610000},
                },
                "scenarios": [
                    {"id": "resident", "totals": {"annualTax": 1800}},
                    {"id": "nonresident", "totals": {"annualTax": 1000}},
                ],
            },
            "audit": [
                {"id": "annual", "label": "Annual tax", "lines": [{
                    "label": "Pension tax", "value": {"minimum": 1000, "maximum": 1800},
                    "formula": "Validated rate bands applied to taxable pension.",
                    "assumptions": ["Residence remains unresolved."], "exclusions": [],
                    "confidence": "high", "ruleIds": ["pension-2026"],
                    "sourceIds": ["official-2026"], "taxYear": 2026,
                }]},
            ],
            "sources": [{"id": "official-2026", "publisher": "Tax authority", "url": "https://tax.example.gov/rule"}],
        }

        markup = run_node("api.resultMarkup(input.result,input.audit,input.sources)", payload)

        self.assertEqual(1, markup.count("<table"))
        self.assertIn("Current broad planning estimate", markup)
        self.assertIn("Capital needed today", markup)
        self.assertIn("Resident branch", markup)
        self.assertIn("Non-resident branch", markup)
        self.assertIn("Annual property fees", markup)
        self.assertIn("<details", markup)
        self.assertIn('href="https://tax.example.gov/rule"', markup)
        self.assertNotIn('aria-live="polite"', markup)

    def test_controller_keeps_answers_in_memory_and_announces_updates(self) -> None:
        payload = {
            "questions": [{
                "id": "days-there", "fact": "daysThere", "control": "number",
                "label": "Days?", "reason": "Material", "acceptedValues": {"min": 0, "max": 365, "step": 1},
            }]
        }
        expression = "(()=>{const c=api.createController(input);c.answer('daysThere',183);return {state:c.snapshot(),announcement:c.announcement()};})()"

        result = run_node(expression, payload)

        self.assertEqual({"daysThere": 183}, result["state"]["answers"])
        self.assertIn("updated", result["announcement"].lower())
        self.assertNotIn("url", result["state"])
        self.assertNotIn("storage", result["state"])

    def test_controller_rejects_answers_outside_the_active_question_contract(self) -> None:
        payload = {
            "questions": [{
                "id": "days-there", "fact": "daysThere", "control": "number",
                "acceptedValues": {"min": 0, "max": 365, "step": 1, "integer": True},
            }]
        }
        expression = "(()=>{const c=api.createController(input);try{c.answer('daysThere',365.5);return false;}catch(e){return e instanceof TypeError;}})()"

        self.assertTrue(run_node(expression, payload))

    def test_native_control_values_are_typed_before_calculation(self) -> None:
        payload = [
            {"question": {"control": "number"}, "value": "183", "checked": False},
            {"question": {"control": "checkbox"}, "value": "on", "checked": True},
            {"question": {"control": "select"}, "value": "destination", "checked": False},
        ]
        expression = "input.map(x=>api.coerceAnswer(x.question,x.value,x.checked))"

        self.assertEqual([183, True, "destination"], run_node(expression, payload))


if __name__ == "__main__":
    unittest.main()
