from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from src.fire_abroad_page import _property_lifecycle


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "artifacts" / "fire-abroad" / "index.html"


class FireAbroadPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(
            ["python3", "src/build_unified_app.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.html = ARTIFACT.read_text(encoding="utf-8")

    def test_page_has_canonical_identity_and_shared_shell(self):
        self.assertIn(
            "<title>FIRE Abroad: Best Places for an Active Life Overseas | Global Home Atlas</title>",
            self.html,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/fire-abroad/">',
            self.html,
        )
        self.assertIn("<h1>FIRE Abroad</h1>", self.html)
        self.assertIn('<body class="gha-mode-utility gha-top-level fire-abroad-page"', self.html)
        self.assertIn('<header class="gha-header">', self.html)
        self.assertIn('<footer class="gha-footer">', self.html)
        self.assertIn('aria-label="Breadcrumb"', self.html)
        self.assertIn('"@type":"BreadcrumbList"', self.html)

    def test_initial_tax_controls_are_plain_and_progressive(self):
        for label in (
            "How will you use the destination?",
            "Approximate time there each year",
            "Main source of spending money",
            "Housing plan",
            "How would you use the home?",
            "Your mobility rights",
            "Current tax-home system",
        ):
            self.assertIn(label, self.html)
        self.assertIn('data-fire-group="property-use" hidden', self.html)
        self.assertNotIn("Cost basis", self.html)
        self.assertNotIn("Treaty tie-breaker", self.html)

    def test_hidden_property_use_overrides_the_grid_label_rule(self):
        head = self.html.split("</head>", 1)[0]
        self.assertIn(".fire-fields [hidden]{display:none!important}", head)

    def test_default_results_explain_tax_without_false_precision(self):
        self.assertIn("Tax Readiness", self.html)
        self.assertIn("Planning tax reserve", self.html)
        self.assertIn("Likely tax residence", self.html)
        self.assertIn("Stay eligibility", self.html)
        self.assertIn("Reference view:", self.html)
        self.assertIn("/5", self.html)
        self.assertIn("not a statutory rate or assessment", self.html)
        self.assertIn("Tax evidence unavailable", self.html)

    def test_property_tax_lifecycle_and_sources_are_available_on_demand(self):
        for stage in ("Purchase", "Annual ownership", "Rental operation", "Sale", "Inheritance or gift"):
            self.assertIn(stage, self.html)
        self.assertIn("Agencia Tributaria", self.html)
        self.assertIn("Data checked 1 September 2026", self.html)
        self.assertNotIn("data-fire-refine", self.html)
        self.assertIn("Property-tax lifecycle by country", self.html)
        self.assertIn("<summary>Spain</summary>", self.html)

    def test_lifecycle_disclosure_scales_to_every_complete_country(self):
        screen = {
            "status": "complete",
            "property_lifecycle": {
                stage: {"summary": f"{stage} summary"}
                for stage in ("purchase", "annual", "rental", "sale", "succession")
            },
        }
        rendered = _property_lifecycle({
            "Spain": {"tax_screen": screen},
            "Portugal": {"tax_screen": screen},
        })
        self.assertIn("Spain", rendered)
        self.assertIn("Portugal", rendered)

    def test_calculator_links_do_not_include_tax_or_financial_inputs(self):
        self.assertIn('href="/retirement-abroad-calculator/"', self.html)
        for forbidden in ("taxHome=", "annualDays=", "planningBase=", "wealthBand="):
            self.assertNotIn(forbidden, self.html)

    def test_sitemap_contains_fire_route(self):
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text(encoding="utf-8")
        self.assertIn("https://globalhomeatlas.com/fire-abroad/", sitemap)

    def test_guide_hub_links_to_fire_screen(self):
        guides = (ROOT / "artifacts" / "guides" / "index.html").read_text(encoding="utf-8")
        self.assertIn('href="/fire-abroad/"', guides)


if __name__ == "__main__":
    unittest.main()
