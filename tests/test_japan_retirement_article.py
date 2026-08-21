from __future__ import annotations

import unittest

from src import build_unified_app


def japan_page() -> dict:
    return next(
        page
        for page in build_unified_app.SEO_PAGES
        if page["slug"] == "japan-retirement-property-foreign-buyers"
    )


def rendered_article() -> str:
    destinations = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.build_seo_page(
        japan_page(), destinations, build_unified_app.SEO_PAGES
    )


class JapanRetirementArticleTests(unittest.TestCase):
    def test_primary_comparison_contains_only_japan_destinations(self) -> None:
        self.assertEqual(
            ["fukuoka-itoshima", "hakone-izu", "hakuba", "niseko"],
            japan_page()["destination_ids"],
        )

    def test_article_leads_with_residency_before_property_selection(self) -> None:
        html = rendered_article()

        residency = html.index("Buying property does not give you residency")
        comparison = html.index('id="comparison"')
        calculator = html.index("Estimate your retirement capital")

        self.assertLess(residency, comparison)
        self.assertLess(residency, calculator)
        self.assertNotIn('<section class="decision-path"', html)
        self.assertIn("¥30 million", html)
        self.assertIn("six months", html)
        self.assertIn("maximum of one year", html)
        self.assertIn(
            "https://www.mofa.go.jp/ca/fna/page22e_000738.html", html
        )

    def test_article_explains_current_nonresident_owner_obligations(self) -> None:
        html = rendered_article()

        self.assertIn("within 20 days", html)
        self.assertIn(
            "https://www.mof.go.jp/english/policy/international_policy/real_property/index.html",
            html,
        )
        self.assertIn("within two years", html)
        self.assertIn(
            "https://www.moj.go.jp/EN/MINJI/m_minji07_00004.html", html
        )

    def test_article_covers_retirement_property_due_diligence_with_sources(self) -> None:
        html = rendered_article()

        for phrase in (
            "Healthcare follows residence status",
            "Financing and ownership costs",
            "Earthquake, flood and building diligence",
            "Short-term rentals are regulated",
            "Sources and update policy",
        ):
            self.assertIn(phrase, html)
        self.assertIn("https://disaportal.gsi.go.jp/", html)
        self.assertIn(
            "https://www.mlit.go.jp/kankocho/minpaku/overview/minpaku/law1_en.html",
            html,
        )

    def test_article_does_not_present_unsourced_price_or_yield_estimates(self) -> None:
        html = rendered_article()

        self.assertNotIn("$2,620/m2", html)
        self.assertNotIn("3–4.8% est. net", html)
        self.assertNotIn("research-grade destination intelligence", html)

    def test_article_has_visible_authorship_and_complete_article_schema(self) -> None:
        html = rendered_article()

        self.assertIn("By Global Home Atlas Research Team", html)
        self.assertIn('"datePublished":"2026-06-23"', html)
        self.assertIn(
            '"author":{"@type":"Organization","name":"Global Home Atlas Research Team"}',
            html,
        )


if __name__ == "__main__":
    unittest.main()
