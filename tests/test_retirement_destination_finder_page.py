from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "retirement-destination-finder" / "index.html"
UI_MODULE = ROOT / "src" / "retirement_destination_finder_ui.js"


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


class RetirementDestinationFinderPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", "src/build_unified_app.py"], cwd=ROOT, check=True, capture_output=True)
        cls.html = ARTIFACT.read_text()
        cls.builder = (ROOT / "src" / "build_unified_app.py").read_text()
        cls.retirement_count = len(
            json.loads((ROOT / "data" / "retirement_costs.json").read_text())["destinations"]
        )

    def test_route_has_canonical_and_reciprocal_mode_link(self) -> None:
        self.assertIn(
            "<title>Retirement Destination Finder: Where Can I Afford to Retire? | Global Home Atlas</title>",
            self.html,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/retirement-destination-finder/">',
            self.html,
        )
        self.assertIn('href="/retirement-abroad-calculator/">Plan for a destination</a>', self.html)
        self.assertIn('aria-current="page">Find destinations I can afford</a>', self.html)

    def test_page_uses_shared_editorial_shell_and_final_design_layer(self) -> None:
        self.assertIn('<body class="gha-mode-utility retirement-finder-page" data-design-system="gha-v1">', self.html)
        self.assertIn('<header class="gha-header">', self.html)
        self.assertIn('class="gha-mobile-menu"', self.html)
        self.assertIn('<footer class="gha-footer">', self.html)
        self.assertNotIn('class="page-nav"', self.html)
        head = self.html.split("</head>", 1)[0]
        marker = '<style id="gha-retirement-finder-design">'
        self.assertEqual(head.rfind("<style"), head.index(marker))
        design_css = head.split(marker, 1)[1].split("</style>", 1)[0]
        self.assertIn('--gha-display-serif: "Iowan Old Style"', design_css)
        self.assertRegex(
            design_css,
            r"\.retirement-finder-page \.finder-section\s*\{[^}]*border-radius:\s*0;[^}]*\}",
        )
        self.assertRegex(
            design_css,
            r"\.retirement-finder-page input,[^{]*\{[^}]*border-radius:\s*0;[^}]*font-weight:\s*400;",
        )

    def test_calculator_mode_links_share_one_aligned_tab_treatment(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(
            ".gha-mode-utility .calc-modes, .gha-mode-utility .finder-modes",
            design_css,
        )
        self.assertIn(
            ".gha-mode-utility .calc-modes a, .gha-mode-utility .finder-modes a",
            design_css,
        )
        self.assertIn("text-decoration: none", design_css)
        self.assertIn("box-shadow: inset 0 -2px 0 var(--gha-accent)", design_css)

    def test_finder_uses_the_landing_page_left_grid_without_overstretching_content(self) -> None:
        head = self.html.split("</head>", 1)[0]
        design_css = head.split('<style id="gha-retirement-finder-design">', 1)[1].split("</style>", 1)[0]
        self.assertIn(
            ".retirement-finder-page .gha-shell, .retirement-finder-page .page-shell",
            design_css,
        )
        self.assertIn("width: min(1220px, calc(100% - 48px))", design_css)
        self.assertIn(
            ".retirement-finder-page .finder-form, .retirement-finder-page .finder-results, .retirement-finder-page .finder-editorial",
            design_css,
        )
        self.assertIn("max-width: 960px", design_css)

    def test_form_uses_top_down_human_reading_order(self) -> None:
        ordered_ids = [
            'id="finder-current-resources"',
            'id="finder-housing"',
            'id="finder-retirement-income"',
            'id="finder-preferences"',
            'id="finder-submit"',
            'id="finder-results"',
        ]
        positions = [self.html.index(value) for value in ordered_ids]
        self.assertEqual(sorted(positions), positions)

    def test_housing_and_conditional_fields_exist(self) -> None:
        for option in (
            '<option value="rent">Rent</option>',
            '<option value="buy_now">Buy now</option>',
            '<option value="buy_retirement">Buy at retirement</option>',
            '<option value="own">Already own</option>',
        ):
            self.assertIn(option, self.html)
        for field_id in (
            "finder-property-allocation",
            "finder-purchase-method",
            "finder-buyer-residency",
            "finder-income-source",
            "finder-requested-ltv",
            "finder-mortgage-rate",
            "finder-mortgage-term",
            "finder-use-before-retirement",
            "finder-rental-yield",
            "finder-vacancy-rate",
            "finder-operating-cost-rate",
            "finder-mortgage-treatment",
        ):
            self.assertIn(f'id="{field_id}"', self.html)
        self.assertIn('<option value="not_sure">Not sure</option>', self.html)

    def test_finder_tax_controls_are_plain_progressive_and_after_tax_explicit(self) -> None:
        form = self.html.split('id="retirement-destination-finder-form"', 1)[1].split("</form>", 1)[0]
        self.assertIn('id="finder-tax-planning"', form)
        self.assertIn('value="destination_estimate" checked', form)
        self.assertIn('value="user_after_tax"', form)
        self.assertIn("Use destination planning estimates", form)
        self.assertIn("I know my after-tax figures", form)
        self.assertIn("Dependable annual income", form)
        self.assertIn("Expected annual portfolio withdrawals", form)
        self.assertIn("How much of those withdrawals may be realized gains?", form)
        self.assertIn('id="finder-tax-property-use-field" hidden', form)
        self.assertIn('id="finder-tax-wealth-band-field"', form)
        self.assertIn("Expected annual portfolio return after fees and tax (%)", form)

    def test_finder_tax_profile_explains_live_tax_adjusted_ranking(self) -> None:
        tax_section = self.html.split('id="finder-tax-planning"', 1)[1].split("</fieldset>", 1)[0]

        self.assertIn("change finder rankings and retirement targets", tax_section)
        self.assertIn("central tax-adjusted target", tax_section)
        self.assertIn("Destination planning estimates also show favorable and adverse bounds", tax_section)
        self.assertNotIn("each result also shows", tax_section)
        self.assertIn('href="/retirement-abroad-calculator/"', tax_section)
        self.assertNotIn("do not yet change", tax_section)

    def test_finder_tax_control_visibility_disables_inapplicable_fields(self) -> None:
        renting = run_ui(
            "taxControlVisibility",
            {"taxMode": "destination_estimate", "housingPlan": "rent", "wealthTaxRelevant": True},
        )
        self.assertEqual(
            {"estimate": True, "propertyUse": False, "wealthBand": True, "afterTax": False},
            renting,
        )
        bypass = run_ui(
            "taxControlVisibility",
            {"taxMode": "user_after_tax", "housingPlan": "buy_retirement", "wealthTaxRelevant": True},
        )
        self.assertEqual(
            {"estimate": False, "propertyUse": False, "wealthBand": False, "afterTax": True},
            bypass,
        )

    def test_results_are_concise_and_accessible(self) -> None:
        self.assertIn('id="finder-within-count"', self.html)
        self.assertIn('id="finder-projection" role="img"', self.html)
        self.assertIn('id="finder-chart-tooltip" role="status"', self.html)
        self.assertIn('id="finder-recommendations"', self.html)
        self.assertIn('id="finder-exclusions"', self.html)
        self.assertIn("Projected portfolio", self.html)
        self.assertIn("Central tax-adjusted target", self.html)
        self.assertIn("Favorable–adverse target range", self.html)
        self.assertIn("Favorable gap", self.html)
        self.assertIn("Adverse gap", self.html)
        self.assertNotIn("Retirement score", self.html)

    def test_results_lead_with_a_plain_language_decision_and_progressive_list(self) -> None:
        self.assertIn('id="finder-result-read"', self.html)
        self.assertIn('id="finder-closest-match"', self.html)
        self.assertIn('id="finder-show-all"', self.html)
        self.assertIn("View all destinations", self.html)
        self.assertIn("View destination dossier", self.html)
        self.assertIn('data-finder-dossier', self.html)

    def test_page_adds_specific_search_supporting_content_and_faq_schema(self) -> None:
        self.assertIn('id="how-matching-works"', self.html)
        self.assertIn('id="within-reach"', self.html)
        self.assertIn('id="rent-or-buy"', self.html)
        self.assertIn('id="finder-faq"', self.html)
        self.assertIn("Projected liquid capital covers the central tax-adjusted retirement target", self.html)
        self.assertIn("Buying requires separate property capital", self.html)
        self.assertIn('"@type":"FAQPage"', self.html)

    def test_mobile_navigation_and_results_use_touch_sized_controls(self) -> None:
        self.assertIn(".mobile-menu>nav{position:absolute", self.html)
        self.assertIn(".mobile-menu>nav a{display:flex;min-height:44px", self.html)
        self.assertIn(".finder-projection{overflow-x:auto", self.html)
        self.assertIn(".finder-chart-bar{min-width:44px", self.html)
        self.assertIn(".finder-result header a{display:flex;min-height:44px", self.html)
        self.assertIn(".finder-results{min-width:0", self.html)
        self.assertIn(".finder-projection-wrap{min-width:0", self.html)

    def test_embeds_complete_dynamic_universe(self) -> None:
        self.assertIn(f'data-universe-count="{self.retirement_count}"', self.html)
        self.assertNotIn("All 30 current destinations", self.html)
        self.assertNotIn('RETIREMENT_FINDER_DESTINATION_COUNT = 30', self.builder)
        for region in ("Asia", "Europe", "North America", "Oceania"):
            self.assertIn(f">{region}</option>", self.html)

    def test_page_explains_financing_evidence_and_privacy(self) -> None:
        self.assertIn("Mortgage availability is indicative", self.html)
        self.assertIn("Your financial details stay in this browser", self.html)
        self.assertIn('id="finder-financing-evidence"', self.html)

    def test_script_disabled_page_keeps_context_and_warns_that_results_need_javascript(self) -> None:
        self.assertIn("The interactive destination comparison requires JavaScript", self.html)
        self.assertIn("The tax controls below remain a planning checklist", self.html)

    def test_sitemap_contains_route(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text()
        self.assertIn("https://globalhomeatlas.com/retirement-destination-finder/", sitemap)

    def test_existing_retirement_journey_links_back_to_discovery(self) -> None:
        calculator = (ROOT / "artifacts" / "retirement-abroad-calculator" / "index.html").read_text()
        homepage = (ROOT / "artifacts" / "index.html").read_text()
        ranking = (ROOT / "artifacts" / "retirement-destinations-ranked-by-cost" / "index.html").read_text()
        expected = 'href="/retirement-destination-finder/"'
        self.assertIn(expected, calculator)
        self.assertIn(expected, homepage)
        self.assertIn(expected, ranking)


if __name__ == "__main__":
    unittest.main()
