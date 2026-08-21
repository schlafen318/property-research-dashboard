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
            "References and update policy",
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

    def test_fit_guidance_follows_the_opening_residency_section(self) -> None:
        html = rendered_article()

        residency = html.index("Buying property does not give you residency")
        fit = html.index("Who Japan suits")
        owner_updates = html.index("What changed for foreign owners in 2026")

        self.assertLess(residency, fit)
        self.assertLess(fit, owner_updates)

    def test_article_has_one_consolidated_destination_block(self) -> None:
        html = rendered_article()

        self.assertEqual(1, html.count("Four Japanese destinations to compare"))
        self.assertNotIn("Destination notes for serious buyers", html)

    def test_references_are_consolidated_as_the_final_article_section(self) -> None:
        html = rendered_article()

        self.assertNotIn("Primary sources to use with advisers", html)
        self.assertEqual(1, html.count('id="sources"'))
        self.assertGreater(html.index('id="sources"'), html.index('id="faq"'))
        article_end = html.index("</article>")
        sources = html.index('id="sources"')
        self.assertNotIn('<section class="seo-section"', html[sources + 1 : article_end])

    def test_article_uses_premium_editorial_layout(self) -> None:
        html = rendered_article()

        self.assertIn('<body class="seo-page seo-page--japan">', html)
        self.assertIn('class="japan-hero-visual"', html)
        self.assertIn('/assets/market-fukuoka-itoshima-900.webp', html)
        self.assertIn('class="seo-aside japan-guide-rail"', html)
        self.assertIn('href="#residency"', html)
        self.assertIn('href="#comparison"', html)
        self.assertIn('href="#sources"', html)
        self.assertIn('.seo-page--japan .seo-section', html)
        self.assertIn('--editorial-serif:', html)

    def test_editorial_labels_and_guide_rail_use_restrained_typography(self) -> None:
        html = rendered_article()

        self.assertIn('class="seo-eyebrow japan-section-label"', html)
        self.assertIn('.seo-page--japan .japan-section-label { font-weight: 500;', html)
        self.assertIn('.seo-page--japan .japan-guide-rail nav a { padding: 11px 0;', html)
        self.assertIn('font-size: 14px;', html)
        self.assertIn(
            '.seo-page--japan .japan-guide-rail .seo-button { font-weight: 500;',
            html,
        )
        for label in (
            "Lifestyle magnetism 10%",
            "Global access 10%",
            "Ownership clarity 12%",
            "Rental profit 13%",
            "Exit liquidity 9%",
        ):
            self.assertNotIn(label, html)

    def test_guide_rail_links_to_all_major_article_waypoints(self) -> None:
        html = rendered_article()

        for section_id, label in (
            ("residency", "Residency first"),
            ("fit", "Who Japan suits"),
            ("owner-changes", "2026 owner changes"),
            ("costs", "Financing and costs"),
            ("practicality", "Retirement practicality"),
            ("lenses", "Five retirement lenses"),
            ("comparison", "Compare destinations"),
            ("faq", "Common questions"),
            ("sources", "References"),
        ):
            self.assertIn(f'id="{section_id}"', html)
            self.assertIn(f'href="#{section_id}">{label}</a>', html)

    def test_primary_navigation_uses_medium_not_bold_weight(self) -> None:
        html = rendered_article()

        self.assertIn(
            ".seo-page--japan .seo-nav-links a { color: #202825; "
            "font-size: 11px; font-weight: 500;",
            html,
        )

    def test_article_byline_uses_regular_not_bold_weight(self) -> None:
        html = rendered_article()

        self.assertIn(
            'class="seo-byline" style="margin:12px 0 0;color:rgba(36,49,45,.68);'
            'font-size:13px;font-weight:400"',
            html,
        )


if __name__ == "__main__":
    unittest.main()
