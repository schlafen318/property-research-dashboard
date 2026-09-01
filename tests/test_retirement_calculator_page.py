from __future__ import annotations

import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "artifacts" / "retirement-abroad-calculator" / "index.html"
UI_MODULE = ROOT / "src" / "retirement_calculator_ui.js"


def run_ui(function_name: str, payload: object) -> object:
    script = (
        "const ui = require(process.argv[1]);"
        "const input = JSON.parse(process.argv[2]);"
        "process.stdout.write(JSON.stringify(ui[process.argv[3]](input)));"
    )
    result = subprocess.run(
        ["node", "-e", script, str(UI_MODULE), json.dumps(payload), function_name],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class CalculatorMarkupParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.label_targets: set[str] = set()
        self.control_ids: set[str] = set()
        self.live_regions = 0
        self.noscript_sections = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "label" and values.get("for"):
            self.label_targets.add(str(values["for"]))
        if tag in {"input", "select", "button"} and values.get("id"):
            self.control_ids.add(str(values["id"]))
        if values.get("aria-live") == "polite":
            self.live_regions += 1
        if tag == "noscript":
            self.noscript_sections += 1


class RetirementCalculatorPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", "src/build_unified_app.py"], cwd=ROOT, check=True, capture_output=True, text=True)
        cls.html = PAGE.read_text(encoding="utf-8")
        cls.compact_html = re.sub(r"\s+", "", cls.html)

    def test_page_has_indexable_metadata_schema_and_content(self) -> None:
        self.assertIn(
            "<title>Retirement Abroad Calculator: How Much Do You Need? | Global Home Atlas</title>",
            self.html,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/retirement-abroad-calculator/">',
            self.html,
        )
        self.assertIn("<h1>How Much Do You Need to Retire Abroad?</h1>", self.html)
        self.assertIn('"@type":"WebApplication"', self.compact_html)
        self.assertIn('"@type":"FAQPage"', self.compact_html)
        self.assertIn("Fukuoka / Itoshima", self.html)
        self.assertIn("Málaga / Costa del Sol", self.html)
        self.assertIn("Portfolio dividends and interest", self.html)

    def test_page_uses_the_shared_global_home_atlas_utility_shell(self) -> None:
        self.assertIn('<body class="gha-mode-utility gha-top-level calculator-page" data-design-system="gha-v1">', self.html)
        self.assertIn('<header class="gha-header">', self.html)
        self.assertIn('class="gha-mobile-menu"', self.html)
        self.assertIn('/assets/global-home-atlas-logo-compact-light.svg', self.html)
        self.assertIn('<footer class="gha-footer">', self.html)
        self.assertNotIn('<nav class="calc-nav"', self.html)

    def test_page_uses_shared_editorial_typography_and_restrained_surfaces(self) -> None:
        head = self.html.split("</head>", 1)[0]
        utility_marker = '<style id="gha-top-level-design">'
        self.assertEqual(head.rfind("<style"), head.index(utility_marker))
        utility_css = head.split(utility_marker, 1)[1].split("</style>", 1)[0]

        self.assertIn('--gha-display-serif: "Iowan Old Style"', utility_css)
        self.assertIn('--gha-reading-sans: "Avenir Next"', utility_css)
        self.assertRegex(
            utility_css,
            r"\.gha-mode-utility \.calc-panel\s*\{[^}]*border-radius:\s*4px;[^}]*\}",
        )
        self.assertRegex(
            utility_css,
            r"\.gha-mode-utility input,[^{]*\{[^}]*border-radius:\s*0;[^}]*"
            r"font-family:\s*var\(--gha-reading-sans\);[^}]*font-weight:\s*400;[^}]*\}",
        )
        self.assertRegex(
            utility_css,
            r"\.gha-mode-utility \.primary\s*\{[^}]*font-weight:\s*500;[^}]*\}",
        )
        self.assertRegex(
            utility_css,
            r"@media \(max-width:\s*860px\)\s*\{[\s\S]*?"
            r"\.gha-mode-utility \.gha-primary-links\s*\{\s*display:\s*none;\s*\}[\s\S]*?"
            r"\.gha-mode-utility \.gha-mobile-menu\s*\{\s*display:\s*block;\s*\}",
        )

    def test_page_leads_with_search_answer_and_compact_destination_benchmark(self) -> None:
        self.assertIn("<h1>How Much Do You Need to Retire Abroad?</h1>", self.html)
        self.assertIn('id="ret-quick-answer"', self.html)
        quick_answer = self.html.split('id="ret-quick-answer"', 1)[1].split("</section>", 1)[0]
        self.assertIn("couple renting", quick_answer)
        self.assertIn("single retiree", quick_answer)
        self.assertEqual(4, quick_answer.count('class="quick-benchmark-row"'))
        benchmark_destinations = re.findall(
            r'class="quick-benchmark-row".*?<a[^>]*>(.*?)</a>',
            quick_answer,
            re.DOTALL,
        )
        self.assertEqual(4, len(set(benchmark_destinations)))
        self.assertIn("3.5% withdrawal rate", quick_answer)
        self.assertIn('/retirement-destinations-ranked-by-cost/', quick_answer)

    def test_page_exposes_authorship_review_methodology_sources_and_exclusions(self) -> None:
        self.assertIn('id="ret-trust"', self.html)
        trust = self.html.split('id="ret-trust"', 1)[1].split("</section>", 1)[0]
        self.assertIn("Global Home Atlas Research Team", trust)
        self.assertIn("Data reviewed", trust)
        self.assertIn("Individual tax or treaty advice, visa eligibility, currency shocks", trust)
        self.assertIn('href="/methodology/"', trust)
        self.assertIn("Destination cost sources", trust)
        self.assertIn('rel="nofollow noopener"', trust)

    def test_free_web_application_schema_includes_required_offer(self) -> None:
        self.assertIn(
            '"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}',
            self.compact_html,
        )

    def test_return_assumption_offers_a_disclosed_illustrative_example(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn('id="ret-example-return" type="button"', form)
        self.assertIn("Use an illustrative 4% example", form)
        self.assertIn("not a forecast or recommendation", form)

    def test_tax_controls_use_two_plain_language_progressive_modes(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn('<fieldset id="ret-tax-planning">', form)
        self.assertIn('value="destination_estimate" checked', form)
        self.assertIn('value="user_after_tax"', form)
        self.assertIn("Use destination planning estimate", form)
        self.assertIn("I know my after-tax figures", form)
        self.assertIn("Dependable annual income", form)
        self.assertIn("Expected annual portfolio withdrawals", form)
        self.assertIn("How much of those withdrawals may be realized gains?", form)
        self.assertIn('id="ret-tax-property-use-field" hidden', form)
        self.assertIn('id="ret-tax-wealth-band-field" hidden', form)
        self.assertIn("Expected annual portfolio return after fees and tax (%)", form)

    def test_tax_control_visibility_is_mode_housing_and_jurisdiction_dependent(self) -> None:
        renting = run_ui(
            "taxControlVisibility",
            {"taxMode": "destination_estimate", "housingPlan": "rent", "wealthTaxRelevant": False},
        )
        self.assertEqual(
            {"estimate": True, "propertyUse": False, "wealthBand": False, "afterTax": False},
            renting,
        )
        buying_in_wealth_tax_jurisdiction = run_ui(
            "taxControlVisibility",
            {"taxMode": "destination_estimate", "housingPlan": "buy_now", "wealthTaxRelevant": True},
        )
        self.assertEqual(
            {"estimate": True, "propertyUse": True, "wealthBand": True, "afterTax": False},
            buying_in_wealth_tax_jurisdiction,
        )
        bypass = run_ui(
            "taxControlVisibility",
            {"taxMode": "user_after_tax", "housingPlan": "buy_now", "wealthTaxRelevant": True},
        )
        self.assertEqual(
            {"estimate": False, "propertyUse": False, "wealthBand": False, "afterTax": True},
            bypass,
        )

    def test_tax_result_targets_put_central_first_and_details_in_one_disclosure(self) -> None:
        results = self.html.split('id="ret-results"', 1)[1].split('</section>\n    </section>', 1)[0]
        self.assertIn('id="ret-plan-summary"', results)
        self.assertNotIn('id="ret-tax-central"', results)
        self.assertNotIn('id="ret-tax-central-capital"', results)
        self.assertIn('id="ret-tax-range"', results)
        self.assertLess(results.index('id="ret-plan-summary"'), results.index('id="ret-tax-range"'))
        self.assertIn('id="ret-tax-no-tax-comparison"', results)
        self.assertIn("No added destination tax comparison", results)
        self.assertIn('id="ret-tax-details"', results)
        self.assertIn("Assumptions and sources", results)
        disclosure = results.split('id="ret-tax-details"', 1)[1].split("</details>", 1)[0]
        for label in ("Tax reserve", "Total annual requirement", "Capital requirement"):
            self.assertIn(label, disclosure)
        for scenario in ("favorable", "central", "adverse"):
            self.assertIn(f'id="ret-tax-{scenario}-row"', disclosure)
        self.assertIn('id="ret-tax-explanations"', disclosure)
        self.assertIn('id="ret-tax-refine" type="button" hidden disabled', results)

    def test_result_panel_has_one_needed_today_headline_and_distinct_key_figures(self) -> None:
        panel = self.html.split('id="ret-results"', 1)[1].split('</section>\n    </section>', 1)[0]

        self.assertEqual(1, panel.count('id="ret-plan-summary"'))
        self.assertNotIn('id="ret-total-today"', panel)
        self.assertNotIn('id="ret-tax-central-capital"', panel)
        self.assertIn('<span>Monthly contribution</span><strong id="ret-monthly-contribution">', panel)
        self.assertIn('<span>Retirement capital</span><strong id="ret-total-retirement-summary">', panel)
        self.assertIn('<span>Property capital</span><strong id="ret-property-summary">', panel)

    def test_tax_result_presentation_preserves_order_and_unavailable_state(self) -> None:
        available = run_ui(
            "taxResultPresentation",
            {
                "taxScenario": {"status": "available"},
                "scenarioResults": {
                    "favorable": {"requiredCapital": 700000, "firstYearExpenses": 50000, "annualTaxReserve": 5000},
                    "central": {
                        "requiredCapital": 800000,
                        "firstYearExpenses": 60000,
                        "annualTaxReserve": 10000,
                        "noTaxComparison": {"label": "No added destination tax", "requiredCapital": 650000},
                    },
                    "adverse": {"requiredCapital": 900000, "firstYearExpenses": 70000, "annualTaxReserve": 15000},
                },
            },
        )
        self.assertEqual("central", available["headlineKey"])
        self.assertEqual(["favorable", "central", "adverse"], [row["key"] for row in available["rows"]])
        self.assertEqual([700000, 900000], available["capitalRange"])
        self.assertEqual("No added destination tax", available["noTaxComparison"]["label"])
        self.assertTrue(available.get("refineAvailable", False))
        unavailable = run_ui(
            "taxResultPresentation",
            {"taxScenario": {"status": "unavailable", "conditional": True}, "scenarioResults": {}},
        )
        self.assertEqual("unavailable", unavailable["status"])
        self.assertTrue(unavailable["conditional"])
        self.assertEqual([], unavailable["rows"])
        self.assertFalse(unavailable.get("refineAvailable", False))
        bypass = run_ui(
            "taxResultPresentation",
            {"taxScenario": {"status": "user_after_tax"}, "scenarioResults": {}},
        )
        self.assertFalse(bypass.get("refineAvailable", False))

    def test_tax_values_are_not_added_to_calculator_handoff_query(self) -> None:
        prefill = run_ui(
            "retirementPrefill",
            "?destination=valencia&household=couple&housing=rent&taxMode=user_after_tax&dependableIncome=90000&wealthBand=above_threshold",
        )
        self.assertEqual(
            {"destination": "valencia", "household": "couple", "housing": "rent"},
            prefill,
        )

    def test_calculator_panels_allow_320_px_intrinsic_shrink(self) -> None:
        head = self.html.split("</head>", 1)[0]
        self.assertIn(".calc-panel { min-width:0;", head)
        self.assertIn("fieldset { min-width:0;", head)

    def test_form_controls_are_labeled_and_results_are_accessible(self) -> None:
        parser = CalculatorMarkupParser()
        parser.feed(self.html)
        expected_controls = {
            "ret-currency",
            "ret-current-age",
            "ret-retirement-age",
            "ret-horizon",
            "ret-household",
            "ret-destination",
            "ret-monthly-spending",
            "ret-housing-plan",
            "ret-property-budget",
            "ret-pension",
            "ret-other-income",
            "ret-rental-income",
            "ret-expected-return",
            "ret-monthly-income",
            "ret-income-invested-rate",
            "ret-current-location",
            "ret-current-monthly-spending",
            "ret-calculate",
        }
        self.assertTrue(expected_controls.issubset(parser.control_ids))
        self.assertTrue(expected_controls - {"ret-calculate"} <= parser.label_targets)
        self.assertEqual(2, parser.live_regions)
        self.assertGreaterEqual(parser.noscript_sections, 1)

    def test_form_supports_dated_planning_currency_conversion_including_sgd(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        currency_select = form.split('id="ret-currency"', 1)[1].split("</select>", 1)[0]

        self.assertIn('for="ret-currency">Planning currency</label>', form)
        for currency in ("USD", "EUR", "GBP", "CAD", "AUD", "CHF", "JPY", "HKD", "SGD"):
            self.assertIn(f'<option value="{currency}"', currency_select)
        self.assertIn('id="ret-currency-note"', form)
        self.assertIn("27 August 2026", form)
        self.assertIn("presentation currency", form)

        payload = json.loads(
            self.html.split('<script id="retirement-destination-data" type="application/json">', 1)[1]
            .split("</script>", 1)[0]
        )
        self.assertEqual("2026-08-27", payload["planning_currencies"]["as_of"])
        self.assertAlmostEqual(0.7866117265603891, payload["planning_currencies"]["rates_to_usd"]["SGD"])

    def test_housing_inputs_match_how_retirees_plan(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn('id="ret-monthly-spending-label" for="ret-monthly-spending">Monthly retirement living expenses including rent</label>', form)
        self.assertIn(
            'id="ret-monthly-spending" type="text" inputmode="numeric" data-money min="0" step="1"',
            form,
        )
        self.assertIn('for="ret-property-budget">Home purchase budget today</label>', form)
        self.assertIn(
            'id="ret-property-budget" type="text" inputmode="numeric" data-money min="0" step="1"',
            form,
        )
        self.assertIn('id="ret-acquisition-cost-guidance"', form)
        self.assertIn("explicit exclusion", form)
        self.assertIn('id="ret-housing-guidance"', form)
        self.assertIn('<option value="rent" selected>Rent</option>', form)
        self.assertIn('id="ret-cost-compare-open" type="button">Compare destination retirement costs</button>', form)
        self.assertIn("Leave at zero when your destination home is for your own use", form)
        self.assertNotIn("Annual spending today (USD)", form)
        self.assertNotIn("Destination net rental income", form)

    def test_destination_selector_is_grouped_and_sorted_by_country(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        destination_select = form.split('id="ret-destination"', 1)[1].split("</select>", 1)[0]
        country_labels = re.findall(r'<optgroup label="([^"]+)">', destination_select)

        self.assertGreaterEqual(len(country_labels), 10)
        self.assertEqual(sorted(country_labels), country_labels)
        self.assertIn("Japan", country_labels)
        japan_group = destination_select.split('<optgroup label="Japan">', 1)[1].split(
            "</optgroup>", 1
        )[0]
        japan_destinations = re.findall(r'<option[^>]*>([^<]+)</option>', japan_group)
        self.assertEqual(sorted(japan_destinations), japan_destinations)
        self.assertIn(
            '<option value="fukuoka-itoshima" selected>Fukuoka / Itoshima</option>',
            japan_group,
        )

        payload = json.loads(
            self.html.split('<script id="retirement-destination-data" type="application/json">', 1)[1]
            .split("</script>", 1)[0]
        )
        self.assertTrue(all(record.get("country") for record in payload["destinations"]))

    def test_empty_destination_data_raises_a_clear_build_error(self) -> None:
        from src.build_unified_app import build_retirement_calculator_page

        with self.assertRaisesRegex(ValueError, "requires at least four destinations"):
            build_retirement_calculator_page(
                [],
                {"as_of": "2026-08-28", "currency": "USD", "destinations": []},
            )

    def test_destination_cost_sidecar_is_an_accessible_dynamic_selector(self) -> None:
        self.assertIn('<dialog class="cost-sidecar" id="ret-cost-sidecar" aria-labelledby="ret-cost-sidecar-title">', self.html)
        self.assertIn('<h2 id="ret-cost-sidecar-title">Compare monthly living expenses</h2>', self.html)
        self.assertIn('id="ret-cost-sidecar-close" type="button" aria-label="Close destination comparison"', self.html)
        self.assertIn('id="ret-cost-sidecar-chart"', self.html)
        self.assertNotIn('href="/retirement-destinations-ranked-by-cost/">Compare destination retirement costs</a>', self.html)

    def test_income_section_states_period_and_currency_once(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn("<legend>Income continuing after retirement (annual)</legend>", form)
        self.assertIn('for="ret-pension">Pension</label>', form)
        self.assertIn('for="ret-other-income">Other non-portfolio income</label>', form)
        self.assertIn('for="ret-rental-income">Net rental income</label>', form)
        self.assertNotIn("Annual pension (USD)", form)
        self.assertNotIn("Other non-portfolio income (USD)", form)
        self.assertNotIn("Other net rental income (annual USD)", form)

    def test_retirement_income_defaults_to_zero(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn('id="ret-pension" type="text" inputmode="numeric" data-money min="0" step="100" value="0"', form)
        self.assertIn('id="ret-other-income" type="text" inputmode="numeric" data-money min="0" step="100" value="0"', form)

    def test_retirement_income_defaults_to_inflation_linked(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        for field_id in ("ret-pension-indexed", "ret-other-indexed", "ret-rental-indexed"):
            self.assertIn(f'id="{field_id}" type="checkbox" checked', form)

    def test_disclosure_summaries_use_regular_weight(self) -> None:
        self.assertIn("summary { cursor:pointer; font-weight:400; }", self.html)
        self.assertNotIn("details.assumptions summary { font-weight:400; }", self.html)

    def test_personalized_form_uses_cash_flow_inputs(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn("Monthly retirement living expenses including rent", form)
        self.assertIn('<option value="buy_now">Buy now</option>', form)
        self.assertIn('<option value="buy_retirement">Buy at retirement</option>', form)
        self.assertNotIn('<option value="buy_retirement" selected>', form)
        self.assertIn("Expected annual portfolio return after fees and tax (%)", form)
        self.assertIn('id="ret-expected-return" type="number" min="-5" max="15" step="0.1" required', form)
        for removed in ("ret-withdrawal-rate", "ret-income-preset", "ret-cash-yield"):
            self.assertNotIn(f'id="{removed}"', form)

    def test_pre_retirement_income_is_monthly_and_inflation_adjusted(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn("<legend>Income you receive now (monthly)</legend>", form)
        self.assertIn('for="ret-monthly-income">After-tax monthly income</label>', form)
        self.assertIn(
            'id="ret-monthly-income" type="text" inputmode="numeric" data-money min="0" step="100" value="0"',
            form,
        )
        for field_id in ("ret-pension", "ret-other-income", "ret-rental-income"):
            self.assertIn(
                f'id="{field_id}" type="text" inputmode="numeric" data-money min="0" step="100"',
                form,
            )
        self.assertIn('for="ret-income-invested-rate">Share invested from income (%)</label>', form)
        self.assertIn('id="ret-monthly-investment-preview">Monthly contribution: $0</p>', form)
        self.assertIn('id="ret-income-invested-rate" type="number" min="0" max="100" step="1" value="20"', form)
        self.assertIn("Income rises annually with general inflation and the selected share is invested monthly.", form)

    def test_page_states_currency_once_and_leads_with_a_decisive_result(self) -> None:
        self.assertIn("Choose your planning currency below", self.html)
        self.assertIn("Destination data is normalized in today's USD before conversion", self.html)
        results = self.html.split('id="ret-results"', 1)[1].split("<noscript>", 1)[0]
        self.assertIn('id="ret-plan-summary"', results)
        self.assertIn('id="ret-sensitivity"', results)
        self.assertIn('id="ret-sensitivity-rows"', results)
        self.assertIn('id="ret-housing-comparison"', results)
        self.assertIn('id="ret-housing-comparison-rows"', results)

    def test_sticky_result_panel_stays_compact_and_details_span_below_it(self) -> None:
        detailed_marker = '<section class="calc-panel detailed-projection" id="ret-detailed-projection" hidden'
        self.assertIn('</section>\n    ' + detailed_marker, self.html)
        top_layout = self.html.split('<section class="calculator-layout"', 1)[1].split(
            '</section>\n    ' + detailed_marker,
            1,
        )[0]
        result_panel = top_layout.split('id="ret-results"', 1)[1]
        self.assertIn('id="ret-plan-summary"', result_panel)
        self.assertIn('id="ret-today-section"', result_panel)
        self.assertIn('id="ret-total-retirement-summary"', result_panel)
        self.assertIn('id="ret-monthly-contribution"', result_panel)
        self.assertIn('id="ret-property-summary"', result_panel)
        for detail_id in (
            "ret-accumulation-figure",
            "ret-sensitivity",
            "ret-retirement-section",
            "ret-housing-comparison",
            "ret-first-year-section",
        ):
            self.assertNotIn(f'id="{detail_id}"', result_panel)
        detailed = self.html.split('id="ret-detailed-projection"', 1)[1].split('</section>\n    <dialog', 1)[0]
        self.assertIn('<h2 id="ret-detailed-projection-heading">Your detailed projection</h2>', detailed)
        for detail_id in (
            "ret-accumulation-figure",
            "ret-sensitivity",
            "ret-retirement-section",
            "ret-housing-comparison",
            "ret-first-year-section",
        ):
            self.assertIn(f'id="{detail_id}"', detailed)

    def test_current_cost_comparison_follows_the_detailed_projection(self) -> None:
        detailed = self.html.index('id="ret-detailed-projection"')
        comparison = self.html.index('id="ret-current-cost-comparison"')
        sidecar = self.html.index('id="ret-cost-sidecar"')
        self.assertLess(detailed, comparison)
        self.assertLess(comparison, sidecar)
        section = self.html[comparison:sidecar]
        self.assertIn('<h2 id="ret-current-cost-heading">Compare with where you live now</h2>', section)
        self.assertIn(
            'for="ret-current-location">Current location '
            '<span class="optional-label">(optional)</span></label>',
            section,
        )
        self.assertIn('id="ret-current-location" type="text" autocomplete="address-level2"', section)
        self.assertIn('for="ret-current-monthly-spending">Current monthly spending</label>', section)
        self.assertIn(
            'id="ret-current-monthly-spending" type="text" inputmode="numeric" '
            'data-money min="1" step="1"',
            section,
        )
        self.assertIn('id="ret-current-cost-result" hidden aria-live="polite"', section)
        self.assertIn('id="ret-current-cost-summary"', section)
        self.assertIn('id="ret-current-cost-annual"', section)
        self.assertIn('id="ret-current-cost-bars"', section)
        self.assertIn('<h3>Retirement funding target</h3>', section)
        self.assertIn('id="ret-current-target"', section)
        self.assertIn('id="ret-destination-target"', section)
        self.assertIn('id="ret-target-difference"', section)
        self.assertIn('Excludes any separate home purchase', section)

    def test_current_cost_comparison_does_not_persist_or_transmit_personal_values(self) -> None:
        source = UI_MODULE.read_text(encoding="utf-8")
        self.assertIn('track("retirement_calculator_current_cost_compare")', source)
        self.assertNotIn('localStorage.getItem("gha_planning_currency")', source)
        self.assertNotIn('localStorage.setItem("gha_planning_currency", selectedCurrency)', source)
        self.assertNotIn("sessionStorage", source)
        self.assertNotIn("fetch(", source)
        self.assertNotIn("XMLHttpRequest", source)

    def test_result_card_contains_honest_save_intent_test(self) -> None:
        results = self.html.split('id="ret-results"', 1)[1].split('</section>\n    </section>', 1)[0]
        self.assertIn('id="ret-save-action" hidden', results)
        self.assertIn(
            'id="ret-save-intent-button" type="button" '
            'data-track="retirement_calculator_save_intent" '
            'data-track-label="retirement calculator result">Save this plan</button>',
            results,
        )
        self.assertIn('id="ret-save-intent-status" role="status" hidden', results)
        self.assertIn("Saved plans are being evaluated. Your figures have not been stored.", results)
        self.assertNotIn('type="password"', results)
        self.assertNotIn('id="ret-account', results)
        self.assertNotIn('id="ret-signup', results)

    def test_chart_includes_a_retirement_target_line(self) -> None:
        results = self.html.split('id="ret-results"', 1)[1].split("<noscript>", 1)[0]
        self.assertIn('id="ret-accumulation-target"', results)
        self.assertIn('id="ret-accumulation-target-label"', results)

    def test_calculator_recalculates_after_valid_input_changes(self) -> None:
        source = UI_MODULE.read_text(encoding="utf-8")
        self.assertIn('form.addEventListener("input", scheduleCalculation)', source)
        self.assertIn('form.addEventListener("change", scheduleCalculation)', source)

    def test_long_reference_material_is_replaced_with_dedicated_links(self) -> None:
        self.assertNotIn('<section id="benchmarks"', self.html)
        self.assertNotIn('<section id="methodology"', self.html)
        self.assertIn('href="/retirement-destinations-ranked-by-cost/"', self.html)
        self.assertIn('href="/methodology/"', self.html)

    def test_results_remove_cash_yield_breakdown(self) -> None:
        results = self.html.split('id="ret-results"', 1)[1].split("<noscript>", 1)[0]
        for element_id in (
            "ret-today-section",
            "ret-property-summary",
            "ret-invest-today",
            "ret-retirement-section",
            "ret-total-retirement",
            "ret-property-retirement",
            "ret-first-year-section",
            "ret-result-return",
            "ret-result-implied-withdrawal",
            "ret-withdrawal-explanation",
            "ret-result-net-return",
            "ret-net-return-explanation",
            "ret-monthly-contribution",
            "ret-contribution-retirement",
        ):
            self.assertIn(f'id="{element_id}"', results)
        self.assertIn("Central estimate needed today", results)
        self.assertIn("What you need at retirement", results)
        self.assertIn("First retirement year", results)
        self.assertIn('id="ret-first-expenses-label">Annual spending incl. rent</span>', results)
        self.assertIn("First-year funding gap ÷ liquid portfolio", results)
        self.assertIn("not a recommended safe withdrawal rate", results)
        self.assertIn("Expected return minus first-year portfolio withdrawal", results)
        self.assertLess(results.index('id="ret-today-section"'), results.index('id="ret-retirement-section"'))
        self.assertLess(results.index('id="ret-retirement-section"'), results.index('id="ret-first-year-section"'))
        self.assertNotIn('id="ret-cash-income"', results)
        self.assertNotIn('id="ret-asset-sales"', results)
        self.assertNotIn('id="ret-today-total"', results)

    def test_results_include_an_accessible_animated_accumulation_chart(self) -> None:
        results = self.html.split('id="ret-results"', 1)[1].split("<noscript>", 1)[0]
        self.assertIn('id="ret-accumulation-figure"', results)
        self.assertIn('id="ret-accumulation-chart" role="img"', results)
        self.assertIn('aria-labelledby="ret-accumulation-title ret-accumulation-desc"', results)
        self.assertIn("Lump sum invested today", results)
        self.assertIn("Monthly contributions", results)
        self.assertIn('id="ret-accumulation-tooltip" role="status"', results)
        self.assertIn("@keyframes ret-year-in", self.html)
        self.assertIn("prefers-reduced-motion:reduce", self.compact_html)

    def test_concise_reference_section_does_not_depend_on_javascript(self) -> None:
        self.assertIn("How to read this estimate", self.html)
        self.assertIn("portfolio, reserve, and property capital", self.html)
        self.assertIn("Portfolio dividends and interest", self.html)
        self.assertIn("Compare destination retirement costs", self.html)

    def test_calculator_contains_every_retirement_cost_destination_option(self) -> None:
        select = self.html.split('id="ret-destination"', 1)[1].split("</select>", 1)[0]
        retirement_costs = json.loads((ROOT / "data" / "retirement_costs.json").read_text(encoding="utf-8"))
        self.assertEqual(len(retirement_costs["destinations"]), select.count("<option"))

    def test_interactive_contract_and_result_targets_are_embedded(self) -> None:
        required_ids = {
            "ret-pension-indexed",
            "ret-other-indexed",
            "ret-rental-indexed",
            "ret-general-inflation",
            "ret-healthcare-inflation",
            "ret-property-inflation",
            "ret-expected-return",
            "ret-reserve-months",
            "ret-errors",
            "ret-property-summary",
            "ret-invest-today",
            "ret-total-retirement",
            "ret-liquid-portfolio",
            "ret-property-retirement",
            "ret-emergency-reserve",
            "ret-result-return",
            "ret-result-implied-withdrawal",
            "ret-result-net-return",
            "ret-result-assumptions",
        }
        for element_id in required_ids:
            self.assertIn(f'id="{element_id}"', self.html)
        self.assertIn("GHARetirementCalculatorUI.initRetirementCalculator", self.html)
        self.assertNotIn("initRetirementBenchmarkTable(\"ret-benchmark-household\"", self.html)
        self.assertLess(self.html.index("window.GHA ="), self.html.index("GHARetirementCalculatorUI.initRetirementCalculator"))

    def test_ui_module_does_not_persist_or_transmit_financial_inputs(self) -> None:
        source = UI_MODULE.read_text(encoding="utf-8")
        for forbidden in ("localStorage", "sessionStorage", "fetch(", "XMLHttpRequest"):
            self.assertNotIn(forbidden, source)
        for forbidden_key in ('spending:', 'income:', 'portfolio:', 'property_price:', 'total_capital:'):
            self.assertNotIn(forbidden_key, source)

    def test_calculator_is_linked_from_retirement_research_routes(self) -> None:
        routes = [
            ROOT / "artifacts" / "guides" / "index.html",
            ROOT / "artifacts" / "buying-property-abroad-for-retirement" / "index.html",
            ROOT / "artifacts" / "best-places-to-buy-property-abroad-for-retirement" / "index.html",
            ROOT / "artifacts" / "destinations" / "valencia" / "index.html",
            ROOT / "artifacts" / "countries" / "spain-property" / "index.html",
        ]
        for route in routes:
            with self.subTest(route=route):
                self.assertIn('/retirement-abroad-calculator/', route.read_text(encoding="utf-8"))

    def test_calculator_callouts_include_fixed_source_labels(self) -> None:
        routes_and_labels = {
            ROOT / "artifacts" / "guides" / "index.html": "guide hub",
            ROOT / "artifacts" / "buying-property-abroad-for-retirement" / "index.html": "buying guide",
            ROOT / "artifacts" / "countries" / "spain-property" / "index.html": "country hub",
            ROOT / "artifacts" / "destinations" / "valencia" / "index.html": "destination page",
        }
        for route, label in routes_and_labels.items():
            with self.subTest(route=route):
                html = route.read_text(encoding="utf-8")
                self.assertIn(
                    'data-track="retirement_calculator_open" '
                    f'data-track-label="{label}"',
                    html,
                )

    def test_homepage_hero_and_tools_link_to_retirement_calculator(self) -> None:
        homepage = (ROOT / "artifacts" / "index.html").read_text(encoding="utf-8")
        calculator_link = (
            '<a class="secondary-action" href="/retirement-abroad-calculator/" '
            'data-track="retirement_calculator_open" data-track-label="hero calculator">'
            'Calculate retirement needs</a>'
        )
        self.assertIn(calculator_link, homepage)
        self.assertEqual(2, homepage.count('data-track="retirement_calculator_open"'))

    def test_sitemap_contains_one_calculator_url(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            sitemap.count("https://globalhomeatlas.com/retirement-abroad-calculator/"),
        )


if __name__ == "__main__":
    unittest.main()
