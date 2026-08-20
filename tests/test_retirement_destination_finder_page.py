from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "retirement-destination-finder" / "index.html"


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
            '<link rel="canonical" href="https://globalhomeatlas.com/retirement-destination-finder/">',
            self.html,
        )
        self.assertIn('href="/retirement-abroad-calculator/">Plan for a destination</a>', self.html)
        self.assertIn('aria-current="page">Find destinations I can afford</a>', self.html)

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

    def test_results_are_concise_and_accessible(self) -> None:
        self.assertIn('id="finder-within-count"', self.html)
        self.assertIn('id="finder-projection" role="img"', self.html)
        self.assertIn('id="finder-chart-tooltip" role="status"', self.html)
        self.assertIn('id="finder-recommendations"', self.html)
        self.assertIn('id="finder-exclusions"', self.html)
        self.assertIn("Projected portfolio", self.html)
        self.assertIn("Retirement target", self.html)
        self.assertIn("Surplus or gap", self.html)
        self.assertNotIn("Retirement score", self.html)

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
