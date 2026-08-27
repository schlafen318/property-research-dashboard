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
        self.assertIn("<h1>Retirement Abroad Calculator</h1>", self.html)
        self.assertIn('"@type":"WebApplication"', self.compact_html)
        self.assertIn('"@type":"FAQPage"', self.compact_html)
        self.assertIn("Fukuoka / Itoshima", self.html)
        self.assertIn("Málaga / Costa del Sol", self.html)
        self.assertIn("Portfolio dividends and interest", self.html)

    def test_form_controls_are_labeled_and_results_are_accessible(self) -> None:
        parser = CalculatorMarkupParser()
        parser.feed(self.html)
        expected_controls = {
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

    def test_housing_inputs_match_how_retirees_plan(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn('id="ret-monthly-spending-label" for="ret-monthly-spending">Monthly retirement living expenses including rent</label>', form)
        self.assertIn('id="ret-monthly-spending" type="number" min="0" step="1"', form)
        self.assertIn('for="ret-property-budget">Home purchase budget today</label>', form)
        self.assertIn('id="ret-property-budget" type="number" min="0" step="1"', form)
        self.assertIn('id="ret-acquisition-cost-guidance"', form)
        self.assertIn("explicit exclusion", form)
        self.assertIn('id="ret-housing-guidance"', form)
        self.assertIn('<option value="rent" selected>Rent</option>', form)
        self.assertIn('id="ret-cost-compare-open" type="button">Compare destination retirement costs</button>', form)
        self.assertIn("Leave at $0 when your destination home is for your own use", form)
        self.assertNotIn("Annual spending today (USD)", form)
        self.assertNotIn("Destination net rental income", form)

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

    def test_personalized_form_uses_cash_flow_inputs(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn("Monthly retirement living expenses including rent", form)
        self.assertIn('<option value="buy_now">Buy now</option>', form)
        self.assertIn('<option value="buy_retirement">Buy at retirement</option>', form)
        self.assertNotIn('<option value="buy_retirement" selected>', form)
        self.assertIn("Expected annual portfolio return after fees (%)", form)
        self.assertIn('id="ret-expected-return" type="number" min="-5" max="15" step="0.1" required', form)
        for removed in ("ret-withdrawal-rate", "ret-income-preset", "ret-cash-yield"):
            self.assertNotIn(f'id="{removed}"', form)

    def test_pre_retirement_income_is_monthly_and_inflation_adjusted(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn("<legend>Income you receive now (monthly)</legend>", form)
        self.assertIn('for="ret-monthly-income">After-tax monthly income</label>', form)
        self.assertIn('id="ret-monthly-income" type="number" min="0" step="100" value="0"', form)
        self.assertIn('for="ret-income-invested-rate">Share invested from income (%)</label>', form)
        self.assertIn('id="ret-monthly-investment-preview">Monthly contribution: $0</p>', form)
        self.assertIn('id="ret-income-invested-rate" type="number" min="0" max="100" step="1" value="20"', form)
        self.assertIn("Income rises annually with general inflation and the selected share is invested monthly.", form)

    def test_page_states_currency_once_and_leads_with_a_decisive_result(self) -> None:
        self.assertIn("All amounts are in today's USD unless marked “at retirement”", self.html)
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
        self.assertIn('id="ret-total-today"', result_panel)
        self.assertIn('id="ret-total-retirement-summary"', result_panel)
        self.assertIn('id="ret-monthly-contribution"', result_panel)
        self.assertIn('id="ret-home-summary" hidden', result_panel)
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
        self.assertIn('id="ret-current-monthly-spending" type="number" min="1" step="1"', section)
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
        self.assertNotIn("localStorage", source)
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
            "ret-total-today",
            "ret-invest-today",
            "ret-home-today",
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
        self.assertIn("Needed today", results)
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
            "ret-total-today",
            "ret-invest-today",
            "ret-home-today",
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
        self.assertEqual(2, homepage.count('href="/retirement-abroad-calculator/"'))

    def test_sitemap_contains_one_calculator_url(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            sitemap.count("https://globalhomeatlas.com/retirement-abroad-calculator/"),
        )


if __name__ == "__main__":
    unittest.main()
