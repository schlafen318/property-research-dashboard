from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE_HUB = ROOT / "artifacts" / "guides" / "index.html"


class GuideHubIndexingTests(unittest.TestCase):
    def guide_text(self) -> str:
        return re.sub(r"\s+", " ", GUIDE_HUB.read_text(encoding="utf-8"))

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


if __name__ == "__main__":
    unittest.main()
