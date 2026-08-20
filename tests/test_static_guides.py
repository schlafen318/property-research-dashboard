from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE_HUB = ROOT / "artifacts" / "guides" / "index.html"
JAPAN_GUIDE = ROOT / "artifacts" / "japan-retirement-property-foreign-buyers" / "index.html"


class GuideHubIndexingTests(unittest.TestCase):
    def guide_text(self) -> str:
        return re.sub(r"\s+", " ", GUIDE_HUB.read_text(encoding="utf-8"))

    def japan_guide_text(self) -> str:
        return re.sub(r"\s+", " ", JAPAN_GUIDE.read_text(encoding="utf-8"))

    def test_japan_guide_has_country_specific_buyer_content_and_primary_sources(self) -> None:
        text = self.japan_guide_text()

        self.assertIn("Compare Japan retirement property for foreign buyers across lifestyle, access, ownership", text)
        self.assertIn("Japan through five retirement lenses", text)
        self.assertIn("Lifestyle magnetism 10%", text)
        self.assertIn("Retirement fit 11%", text)
        self.assertIn("Global access 10%", text)
        self.assertIn("Foreigner fit 7%", text)
        self.assertIn("Ownership clarity 12%", text)
        self.assertIn("Regulatory safety 8%", text)
        self.assertIn("Rental profit 13%", text)
        self.assertIn("Capital upside 9%", text)
        self.assertIn("Exit liquidity 9%", text)
        self.assertIn("Value entry 11%", text)
        self.assertIn("Minpaku is capped nationally at 180 days a year", text)
        self.assertIn("Hakata is a five-minute train ride from Fukuoka Airport", text)
        self.assertIn("ownership alone does not confer that eligibility", text)
        self.assertIn("within 20 days after acquisition", text)
        self.assertIn("Ministry of Finance says", text)
        self.assertIn("mlit.go.jp", text)
        self.assertNotIn("Decision Framework", text)
        self.assertNotIn("Destination Notes for Serious Buyers", text)
        self.assertNotIn("Budget, finance, and operating reality", text)
        self.assertNotIn("What buying in Japan does and does not solve", text)

    def test_guide_hub_presents_an_editorial_reading_path_without_dashboard_chrome(self) -> None:
        text = self.guide_text()

        self.assertIn("A considered guide to buying a home abroad", text)
        self.assertIn('class="guide-section-nav"', text)
        self.assertIn("The featured story", text)
        self.assertIn('class="guide-feature"', text)
        self.assertIn("Retirement or lifestyle base", text)
        self.assertIn("Second home abroad", text)
        self.assertIn("Investment-led shortlist", text)
        self.assertIn("Ownership and risk first", text)
        self.assertNotIn("Approved P1 buyer paths", text)
        self.assertNotIn("Issue #", text)
        self.assertNotIn("Google is starting to index", text)
        self.assertNotIn("<strong>Use when:</strong>", text)
        self.assertNotIn("Route 01", text)
        self.assertNotIn('class="page-button" href="/best-countries-to-retire-abroad/"', text)
        self.assertIn('/best-places-to-buy-vacation-home-abroad/"', text)
        self.assertIn('/best-countries-for-expats-to-buy-property/"', text)
        self.assertIn('/best-countries-to-buy-property-as-a-foreigner/"', text)

    def test_retirement_calculator_callout_precedes_the_full_catalog(self) -> None:
        html = GUIDE_HUB.read_text(encoding="utf-8")

        self.assertEqual(1, html.count('href="/retirement-abroad-calculator/"'))
        self.assertLess(
            html.index('href="/retirement-abroad-calculator/"'),
            html.index('class="guide-catalog"'),
        )


if __name__ == "__main__":
    unittest.main()
