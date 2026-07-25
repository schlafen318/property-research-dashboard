from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE_HUB = ROOT / "artifacts" / "guides" / "index.html"


class GuideHubIndexingTests(unittest.TestCase):
    def guide_text(self) -> str:
        return re.sub(r"\s+", " ", GUIDE_HUB.read_text(encoding="utf-8"))

    def test_guide_hub_exposes_approved_p1_growth_routes(self) -> None:
        text = self.guide_text()

        self.assertIn("Approved P1 buyer paths", text)
        self.assertIn("Vacation-home buyers", text)
        self.assertIn("Foreign and expat buyers", text)
        self.assertIn("Guides indexing fix", text)
        self.assertIn('/best-places-to-buy-vacation-home-abroad/"', text)
        self.assertIn('/best-countries-for-expats-to-buy-property/"', text)
        self.assertIn('/best-countries-to-buy-property-as-a-foreigner/"', text)
        self.assertIn('/guides/#choose-journey"', text)


if __name__ == "__main__":
    unittest.main()
