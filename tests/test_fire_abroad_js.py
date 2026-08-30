from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from src.fire_abroad import eligibility_for_mode, normalize_fire_profile, rank_fire_abroad_destinations


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "src" / "fire_abroad.js"
UI = ROOT / "src" / "fire_abroad_ui.js"
CONTRACT = ROOT / "tests" / "fixtures" / "fire_abroad_contract.json"


def run_js(module: Path, function_name: str, payload: object) -> object:
    script = (
        "const mod=require(process.argv[1]);"
        "const value=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(mod.{function_name}(value)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(module), json.dumps(payload)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_js_call(module: Path, function_name: str, *arguments: object) -> object:
    script = (
        "const mod=require(process.argv[1]);"
        "const args=JSON.parse(process.argv[2]);"
        f"process.stdout.write(JSON.stringify(mod.{function_name}(...args)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(module), json.dumps(arguments)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def run_js_program(source: str) -> object:
    result = subprocess.run(
        ["node", "-e", source, str(UI)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


class FireAbroadJavaScriptParityTests(unittest.TestCase):
    """These fail if browser scoring diverges from the reviewed Python contract."""

    @staticmethod
    def route(status: str = "eligible", score: float | None = 4.0) -> dict:
        return {
            "status": status,
            "base_score": score,
            "summary": "The documented route fits the selected stay.",
            "work_permission": "remote_permitted",
        }

    def country(self) -> dict:
        return {
            "stay_routes": {
                mode: self.route() for mode in ("seasonal", "part_year", "full_relocation")
            },
            "tax": {
                "standard_day_threshold": 183,
                "non_day_tests": "A permanent home can trigger a separate residence test.",
                "by_mode": {
                    mode: {"status": "eligible", "rankable": True, "compatibility_score": 2.0}
                    for mode in ("seasonal", "part_year", "full_relocation")
                },
            },
            "healthcare": {
                "by_mode": {
                    mode: {"eligibility": "eligible", "bridge_score": 3.0}
                    for mode in ("seasonal", "part_year", "full_relocation")
                }
            },
        }

    @staticmethod
    def destination() -> dict:
        return {
            "id": "alpha",
            "name": "Alpha",
            "decision_dimensions": [
                {"key": "global_access", "score": 4.0},
                {"key": "foreigner_fit", "score": 3.0},
            ],
            "scores": {
                "exit_liquidity": {"score": 4.0},
                "ownership_clarity": {"score": 2.0},
            },
        }

    @staticmethod
    def cost() -> dict:
        return {
            "destination_id": "alpha",
            "profiles": {
                "single": {
                    "categories_usd": {"living": 50000, "contingency": 0},
                    "annual_rent_usd": 4545,
                    "annual_owner_costs_usd": 1000,
                }
            },
            "property": {"representative_price_usd": 100000, "acquisition_cost_rate": 0.1},
        }

    @staticmethod
    def override() -> dict:
        return {
            "country": "Example",
            "active_life": {
                "everyday_movement": {"score": 4.0, "summary": "Daily cycling and year-round park access."},
                "active_pursuits": {"score": 4.0, "summary": "Trails support regular outdoor pursuits."},
                "year_round_continuity": {"score": 4.0, "summary": "The climate supports activity through the year."},
                "activity_ecosystem": {"score": 4.0, "summary": "Local clubs create a social activity base."},
            },
            "rent_flexibility_score": 3.0,
            "one_time_relocation_usd": 5000,
            "risk_warnings": ["Heat plans matter in midsummer."],
            "confidence": "high",
            "last_reviewed": "2026-08-29",
        }

    def payload_for(self, case: dict) -> dict:
        country = self.country()
        if case["name"] == "exact_minimum_age":
            country["stay_routes"]["part_year"] = self.route("conditional")
            country["stay_routes"]["part_year"]["minimum_age"] = 50
        elif case["name"] == "full_relocation_unavailable":
            country["stay_routes"]["full_relocation"] = self.route("not_eligible")
        elif case["name"] == "consulting_passive_only":
            country["stay_routes"]["part_year"]["work_permission"] = "passive_only"
        return {
            "destinations": [self.destination()],
            "retirement_costs": {"alpha": self.cost()},
            "countries": {"Example": country},
            "destination_overrides": {"alpha": self.override()},
            "profile": case["raw_profile"],
        }

    def test_contract_cases_match_normalization_and_ranked_result_fields(self) -> None:
        cases = json.loads(CONTRACT.read_text(encoding="utf-8"))["cases"]
        self.assertGreaterEqual(len(cases), 6)
        for case in cases:
            with self.subTest(case=case["name"]):
                self.assertEqual(
                    case["normalized_profile"], run_js(ENGINE, "normalizeProfile", case["raw_profile"])
                )
                results = run_js(ENGINE, "rankDestinations", self.payload_for(case))
                expected = case["expected"]
                self.assertEqual(expected["ordered_ids"], [item["destination_id"] for item in results])
                self.assertEqual(expected["statuses"], [item["status"] for item in results])
                self.assertEqual(expected["scores"], [item["score"] for item in results])
                self.assertEqual(
                    expected["annual_budgets"],
                    [item["resilience_budget"]["annual_total_usd"] for item in results],
                )
                warnings = " ".join(results[0]["warnings"])
                for warning in expected["warning_substrings"]:
                    self.assertIn(warning, warnings)

    def test_budget_uses_the_destination_relocation_override(self) -> None:
        profile = run_js(ENGINE, "normalizeProfile", {})
        budget = run_js_call(
            ENGINE,
            "buildResilienceBudget",
            self.cost(),
            profile,
            {"one_time_relocation_usd": 7500},
        )
        self.assertEqual(7500, budget["one_time_relocation_usd"])
        self.assertEqual(60000, budget["annual_total_usd"])

    def test_missing_consolidated_score_stays_unranked(self) -> None:
        payload = self.payload_for({"name": "default", "raw_profile": {}})
        payload["destinations"][0]["decision_dimensions"] = [{"key": "foreigner_fit", "score": 3.0}]
        result = run_js(ENGINE, "rankDestinations", payload)[0]
        self.assertEqual("needs_verification", result["status"])
        self.assertIsNone(result["score"])
        self.assertIsNone(result["components"]["global_access"])

    def test_malformed_cost_records_stay_unranked_like_the_python_model(self) -> None:
        malformed_costs = {
            "empty_record": {},
            "empty_profiles": {"profiles": {}},
            "missing_selected_household": {"profiles": {"couple": {"categories_usd": {}, "annual_rent_usd": 1}}},
            "missing_required_housing_cost": {"profiles": {"single": {"categories_usd": {"living": 50000}}}},
        }
        for name, cost in malformed_costs.items():
            with self.subTest(cost=name):
                payload = self.payload_for({"name": "default", "raw_profile": {}})
                payload["retirement_costs"] = {"alpha": cost}
                result = run_js(ENGINE, "rankDestinations", payload)[0]
                expected = rank_fire_abroad_destinations(
                    payload["destinations"], payload["retirement_costs"],
                    {"countries": payload["countries"], "destination_overrides": payload["destination_overrides"]},
                    payload["profile"],
                )[0]
                self.assertEqual("needs_verification", result["status"])
                self.assertIsNone(result["score"])
                self.assertIsNone(result["components"]["sustainable_annual_cost"])
                self.assertEqual(expected["status"], result["status"])
                self.assertEqual(expected["score"], result["score"])

    def test_eligibility_clamps_out_of_range_numeric_route_scores(self) -> None:
        for base_score in (0.0, 5.0, 5.5, -1.0):
            with self.subTest(base_score=base_score):
                country = {"stay_routes": {"part_year": self.route("eligible", base_score)}}
                expected = eligibility_for_mode(country, normalize_fire_profile({}))
                actual = run_js_call(ENGINE, "eligibilityForMode", country, {})
                self.assertEqual(expected["stay_score"], actual["stay_score"])

    def test_tied_rankings_use_python_code_point_name_order(self) -> None:
        payload = self.payload_for({"name": "default", "raw_profile": {}})
        payload["destinations"][0]["name"] = "alpha"
        beta = self.destination()
        beta["id"] = "beta"
        beta["name"] = "Zeta"
        payload["destinations"].append(beta)
        payload["retirement_costs"]["beta"] = self.cost()
        payload["destination_overrides"]["beta"] = self.override()
        expected = rank_fire_abroad_destinations(
            payload["destinations"], payload["retirement_costs"],
            {"countries": payload["countries"], "destination_overrides": payload["destination_overrides"]},
            payload["profile"],
        )
        self.assertEqual(
            ["beta", "alpha"],
            [item["destination_id"] for item in run_js(ENGINE, "rankDestinations", payload)],
        )
        self.assertEqual(
            [item["destination_id"] for item in expected],
            [item["destination_id"] for item in run_js(ENGINE, "rankDestinations", payload)],
        )


class FireAbroadJavaScriptPrivacyTests(unittest.TestCase):
    """These fail if private profile data can leave the browser or reach a URL."""

    def test_calculator_href_excludes_fire_profile_and_financial_details(self) -> None:
        href = run_js(UI, "safeCalculatorHref", {
            "destinationId": "valencia",
            "profile": {
                "household": "couple", "housing": "buy_now", "age": 52,
                "homeTaxContext": "us_person", "annualDays": 190,
                "incomeType": "business_consulting", "netWorth": 2500000,
            },
        })
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=valencia&household=couple&housing=buy_now",
            href,
        )

    def test_calculator_href_falls_back_for_invalid_slug_or_categories(self) -> None:
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=&household=single&housing=rent",
            run_js(UI, "safeCalculatorHref", {
                "destinationId": "../contact",
                "profile": {"household": "invalid", "housing": "own_now"},
            }),
        )

    def test_analytics_payload_is_allowlisted_and_drops_sensitive_details(self) -> None:
        safe = run_js_call(UI, "safeAnalyticsPayload", "calculator_handoff", {
            "destinationId": "valencia", "stayMode": "part_year", "activityPriority": "cycling",
            "age": 52, "mobilityRights": "local_free_movement", "homeTaxContext": "us_person",
            "annualDays": 190, "incomeType": "business_consulting", "annual_total_usd": 64000,
            "score": 4.2,
        })
        self.assertEqual(
            {"eventName": "calculator_handoff", "destinationId": "valencia"}, safe
        )
        self.assertIsNone(run_js_call(UI, "safeAnalyticsPayload", "profile_submit", {"destinationId": "valencia"}))

    def test_result_rows_keep_unranked_items_after_ranked_activity_matches(self) -> None:
        rows = run_js_call(UI, "resultRowsForDisplay", [
            {"destination_id": "ranked", "score": 4.0, "status": "eligible", "activity_tags": ["cycling"]},
            {"destination_id": "conditional", "score": None, "status": "needs_verification", "activity_tags": ["cycling"]},
            {"destination_id": "other", "score": 3.0, "status": "eligible", "activity_tags": ["walking"]},
        ], "cycling")
        self.assertEqual(["ranked", "conditional"], [row["destination_id"] for row in rows])

    def test_result_details_expose_complete_human_readable_decision_information(self) -> None:
        details = run_js_call(
            UI,
            "resultDetails",
            {
                "destination_id": "valencia",
                "name": "Valencia",
                "status": "conditional",
                "status_reason": "A residence route depends on the applicant profile.",
                "score": 3.23,
                "components": {
                    "active_life": 4.1,
                    "healthcare_bridge": 3.8,
                    "stay_flexibility": 3.4,
                    "tax_compatibility": 2.9,
                },
                "resilience_budget": {
                    "annual_total_usd": 60000,
                    "currency_inflation_buffer": 4800,
                    "one_time_relocation_usd": 7000,
                },
                "work_permission": "passive_only",
                "warnings": ["Tax residence requires a separate review."],
                "strongest_activity_reason": "Daily walking and cycling are practical.",
                "confidence": "medium_high",
                "last_reviewed": "2026-08-29",
            },
            {"household": "couple", "housing": "buy_now"},
        )
        self.assertEqual("Conditional", details["eligibilityLabel"])
        self.assertEqual(
            "Eligibility: Conditional. A residence route depends on the applicant profile.",
            details["eligibility"],
        )
        self.assertEqual("FIRE Abroad score: 3.23 out of 5.", details["score"])
        self.assertEqual(
            "Resilience budget: $60,000 per year. Currency and inflation buffer: $4,800. One-time relocation estimate: $7,000.",
            details["resilienceBudget"],
        )
        self.assertEqual(
            "Active Life: 4.10 out of 5. Daily walking and cycling are practical.",
            details["activeLife"],
        )
        self.assertEqual("Healthcare Bridge: 3.80 out of 5.", details["healthcare"])
        self.assertEqual(
            "Stay Flexibility: 3.40 out of 5. Work permission: Passive income only.",
            details["stayAndWork"],
        )
        self.assertEqual("Tax Compatibility: 2.90 out of 5.", details["tax"])
        self.assertEqual(
            ["Planning warning: Tax residence requires a separate review."],
            details["warnings"],
        )
        self.assertEqual(
            "Evidence: Medium high confidence; reviewed 2026-08-29.",
            details["evidence"],
        )
        self.assertEqual("Build your plan", details["calculatorLabel"])
        self.assertEqual(
            "/retirement-abroad-calculator/?destination=valencia&household=couple&housing=buy_now",
            details["calculatorHref"],
        )
        self.assertEqual("Read destination guide", details["guideLabel"])
        self.assertEqual("/destinations/valencia/", details["guideHref"])

    def test_result_details_keep_unranked_states_visible_without_raw_enum_values(self) -> None:
        details = run_js_call(
            UI,
            "resultDetails",
            {
                "destination_id": "fukuoka-itoshima",
                "name": "Fukuoka / Itoshima",
                "status": "needs_verification",
                "status_reason": "Nationality-dependent rights must be confirmed.",
                "score": None,
                "components": {},
                "resilience_budget": {"annual_total_usd": 47600},
                "work_permission": "unclear",
                "warnings": [],
                "confidence": "low",
                "last_reviewed": "2026-08-29",
            },
            {"household": "single", "housing": "rent"},
        )
        self.assertEqual("Needs verification", details["eligibilityLabel"])
        self.assertNotIn("needs_verification", json.dumps(details))
        self.assertEqual(
            "Ranking: Unranked until evidence is verified.", details["score"]
        )
        self.assertIn("Needs verification", details["healthcare"])
        self.assertIn("Work permission needs professional review", details["stayAndWork"])

    def test_initialization_binds_controls_without_replacing_server_results(self) -> None:
        state = run_js_program(
            r"""
const ui = require(process.argv[1]);
const listeners = {};
let rankCalls = 0;
let replaceCalls = 0;
let allowCreate = false;
const tracked = [];
function node(tagName) {
  return {
    tagName,
    textContent: "",
    children: [],
    attributes: {},
    appendChild(child) { this.children.push(child); },
    setAttribute(name, value) { this.attributes[name] = value; },
    addEventListener() {},
  };
}
function allText(current) {
  return [current.textContent].concat(current.children.flatMap(allText)).filter(Boolean).join(" ");
}
function allHrefs(current) {
  return [current.href].concat(current.children.flatMap(allHrefs)).filter(Boolean);
}
const form = {
  dataset: {},
  addEventListener(type, listener) { listeners[type] = listener; },
};
const results = node("div");
results.replaceChildren = function () { replaceCalls += 1; this.children = []; };
const summary = { textContent: "SERVER DEFAULT" };
const controls = {
  "fire-stay-mode": { value: "part_year" },
  "fire-age": { value: "50" },
  "fire-household": { value: "single" },
  "fire-housing": { value: "rent" },
  "fire-mobility-rights": { value: "prefer_not_to_say" },
  "fire-home-tax-context": { value: "prefer_not_to_say" },
  "fire-annual-days": { value: "" },
  "fire-income-type": { value: "prefer_not_to_say" },
  "fire-activity-priority": { value: "balanced" },
};
const nodes = Object.assign({}, controls, {
  "fire-abroad-data": { textContent: JSON.stringify({ destinations: [] }) },
  "fire-abroad-form": form,
  "fire-results": results,
  "fire-results-summary": summary,
});
const host = {
  document: {
    getElementById(id) { return nodes[id] || null; },
    createElement(tagName) {
      if (!allowCreate) throw new Error("initialization must not create result nodes");
      return node(tagName);
    },
    createTextNode(value) {
      if (!allowCreate) throw new Error("initialization must not create text nodes");
      const text = node("#text");
      text.textContent = value;
      return text;
    },
  },
  GHAFireAbroad: {
    normalizeProfile() {
      return { stay_mode: "part_year", household: "single", housing: "rent", activity_priority: "balanced" };
    },
    rankDestinations() {
      rankCalls += 1;
      return [{
        destination_id: "valencia",
        name: "Valencia",
        status: "conditional",
        status_reason: "Profile review is required.",
        score: 3.23,
        components: { active_life: 4.1, healthcare_bridge: 3.8, stay_flexibility: 3.4, tax_compatibility: 2.9 },
        resilience_budget: { annual_total_usd: 60000, currency_inflation_buffer: 4800, one_time_relocation_usd: 7000 },
        work_permission: "passive_only",
        warnings: ["Tax residence requires a separate review."],
        strongest_activity_reason: "Daily walking is practical.",
        confidence: "medium_high",
        last_reviewed: "2026-08-29",
      }];
    },
  },
  GHA: { track(name) { tracked.push(name); } },
};
ui.initFireAbroad(host);
const afterInit = {
  rankCalls,
  replaceCalls,
  summary: summary.textContent,
  bound: form.dataset.fireAbroadBound,
  listeners: Object.keys(listeners).sort(),
  tracked: tracked.slice(),
};
allowCreate = true;
listeners.change({ type: "change", target: controls["fire-stay-mode"], preventDefault() {} });
process.stdout.write(JSON.stringify({
  afterInit,
  afterChange: {
    rankCalls,
    replaceCalls,
    summary: summary.textContent,
    tracked,
    text: allText(results),
    hrefs: allHrefs(results),
  },
}));
"""
        )
        self.assertEqual(
            {
                "rankCalls": 0,
                "replaceCalls": 0,
                "summary": "SERVER DEFAULT",
                "bound": "true",
                "listeners": ["change", "submit"],
                "tracked": ["page_view"],
            },
            state["afterInit"],
        )
        self.assertEqual(1, state["afterChange"]["rankCalls"])
        self.assertEqual(1, state["afterChange"]["replaceCalls"])
        self.assertEqual("1 ranked destinations.", state["afterChange"]["summary"])
        self.assertEqual(
            ["page_view", "stay_mode_change"], state["afterChange"]["tracked"]
        )
        rendered_text = state["afterChange"]["text"]
        for expected in (
            "Eligibility: Conditional",
            "FIRE Abroad score: 3.23 out of 5",
            "Resilience budget: $60,000 per year",
            "Active Life: 4.10 out of 5",
            "Healthcare Bridge: 3.80 out of 5",
            "Stay Flexibility: 3.40 out of 5",
            "Work permission: Passive income only",
            "Tax Compatibility: 2.90 out of 5",
            "Planning warning: Tax residence requires a separate review",
            "Evidence: Medium high confidence; reviewed 2026-08-29",
            "Build your plan",
            "Read destination guide",
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, rendered_text)
        self.assertEqual(
            [
                "/retirement-abroad-calculator/?destination=valencia&household=single&housing=rent",
                "/destinations/valencia/",
            ],
            state["afterChange"]["hrefs"],
        )

    def test_ui_source_has_no_network_storage_or_sensitive_analytics_fields(self) -> None:
        source = UI.read_text(encoding="utf-8")
        for forbidden in ("fetch(", "XMLHttpRequest", "localStorage", "sessionStorage", "innerHTML"):
            self.assertNotIn(forbidden, source)
        analytics_source = source.split("function safeAnalyticsPayload", 1)[1].split(
            "function resultRowsForDisplay", 1
        )[0]
        for sensitive_key in (
            "age", "mobilityRights", "homeTaxContext", "annualDays", "incomeType",
            "annual_total_usd", "property_capital_usd", "score",
        ):
            self.assertNotIn(sensitive_key, analytics_source)


if __name__ == "__main__":
    unittest.main()
