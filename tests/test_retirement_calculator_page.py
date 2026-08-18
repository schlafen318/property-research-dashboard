from __future__ import annotations

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
        self.assertIn("Retirement cost benchmarks by destination", self.html)
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
            "ret-income-preset",
            "ret-calculate",
        }
        self.assertTrue(expected_controls.issubset(parser.control_ids))
        self.assertTrue(expected_controls - {"ret-calculate"} <= parser.label_targets)
        self.assertEqual(1, parser.live_regions)
        self.assertGreaterEqual(parser.noscript_sections, 1)

    def test_housing_inputs_match_how_retirees_plan(self) -> None:
        form = self.html.split('id="retirement-calculator"', 1)[1].split("</form>", 1)[0]
        self.assertIn('for="ret-monthly-spending">Monthly spending today (USD)</label>', form)
        self.assertIn('id="ret-monthly-spending" type="number" min="0" step="1"', form)
        self.assertIn('for="ret-property-budget">Home purchase budget today (USD)</label>', form)
        self.assertIn('id="ret-property-budget" type="number" min="0" step="1"', form)
        self.assertIn('id="ret-housing-guidance"', form)
        self.assertIn('for="ret-rental-income">Other net rental income (annual USD)</label>', form)
        self.assertIn("Leave at $0 when your destination home is for your own use", form)
        self.assertNotIn("Annual spending today (USD)", form)
        self.assertNotIn("Destination net rental income", form)

    def test_static_benchmarks_and_methodology_do_not_depend_on_javascript(self) -> None:
        self.assertIn('<section id="benchmarks"', self.html)
        self.assertIn('<section id="methodology"', self.html)
        self.assertIn("How much capital do you need to retire abroad?", self.html)
        self.assertIn("Annual spending", self.html)
        self.assertIn("Liquid portfolio", self.html)
        self.assertIn("Emergency reserve", self.html)
        self.assertIn("Required retirement capital", self.html)
        self.assertIn("Property capital", self.html)

    def test_calculator_contains_all_thirty_destination_options(self) -> None:
        select = self.html.split('id="ret-destination"', 1)[1].split("</select>", 1)[0]
        self.assertEqual(30, select.count("<option"))

    def test_benchmarks_show_ten_rows_then_expand_twenty(self) -> None:
        section = self.html.split('<section id="benchmarks"', 1)[1].split("</section>", 1)[0]
        visible = section.split('<details class="benchmark-more">', 1)[0]
        expandable = section.split('<details class="benchmark-more">', 1)[1]
        self.assertEqual(10, visible.count('class="benchmark-row"'))
        self.assertEqual(20, expandable.count('class="benchmark-row"'))
        self.assertIn("View ranks 11–30", expandable)

    def test_capital_table_uses_guided_methodology_and_ranks_by_couple_requirement(self) -> None:
        section = self.html.split('<section id="benchmarks"', 1)[1].split("</section>", 1)[0]
        self.assertIn("3.5% guided withdrawal rate", section)
        self.assertIn("12 months of expenses", section)
        self.assertIn("no pension or outside passive income", section.lower())
        self.assertIn("$2,359,800", section)
        self.assertIn("$512,947", section)
        ordered_names = [
            "Fukuoka / Itoshima",
            "Hakone / Izu",
            "Crete",
            "Valencia",
            "Algarve / Cascais",
            "Málaga / Costa del Sol",
            "Madeira",
            "Lake Como",
        ]
        positions = [section.index(name) for name in ordered_names]
        self.assertEqual(sorted(positions), positions)

    def test_interactive_contract_and_result_targets_are_embedded(self) -> None:
        required_ids = {
            "ret-pension-indexed",
            "ret-other-indexed",
            "ret-rental-indexed",
            "ret-general-inflation",
            "ret-healthcare-inflation",
            "ret-property-inflation",
            "ret-withdrawal-rate",
            "ret-cash-yield",
            "ret-reserve-months",
            "ret-errors",
            "ret-total-capital",
            "ret-liquid-portfolio",
            "ret-property-capital",
            "ret-emergency-reserve",
            "ret-result-assumptions",
        }
        for element_id in required_ids:
            self.assertIn(f'id="{element_id}"', self.html)
        self.assertIn("GHARetirementCalculatorUI.initRetirementCalculator", self.html)
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

    def test_homepage_hero_links_to_retirement_calculator_once(self) -> None:
        homepage = (ROOT / "artifacts" / "index.html").read_text(encoding="utf-8")
        calculator_link = (
            '<a class="text-action" href="/retirement-abroad-calculator/" '
            'data-track="retirement_calculator_open" data-track-label="hero">'
            'Calculate retirement needs</a>'
        )
        self.assertIn(calculator_link, homepage)
        self.assertEqual(1, homepage.count('href="/retirement-abroad-calculator/"'))

    def test_sitemap_contains_one_calculator_url(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertEqual(
            1,
            sitemap.count("https://globalhomeatlas.com/retirement-abroad-calculator/"),
        )


if __name__ == "__main__":
    unittest.main()
