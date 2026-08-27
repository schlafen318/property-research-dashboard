from __future__ import annotations

import unittest

from src import build_unified_app


def portugal_page() -> dict:
    return next(
        page
        for page in build_unified_app.SEO_PAGES
        if page["slug"] == "portugal-retirement-property-foreign-buyers"
    )


def rendered_article() -> str:
    destinations = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.build_seo_page(
        portugal_page(), destinations, build_unified_app.SEO_PAGES
    )


class PortugalRetirementArticleTests(unittest.TestCase):
    def test_portugal_country_hub_links_to_the_retirement_guide(self) -> None:
        hub = next(
            item
            for item in build_unified_app.COUNTRY_HUBS
            if item["slug"] == "portugal-property"
        )

        self.assertIn("portugal-retirement-property-foreign-buyers", hub["guide_slugs"])

    def test_primary_comparison_contains_the_two_portugal_dossiers(self) -> None:
        self.assertEqual(
            ["algarve-cascais", "madeira"],
            portugal_page()["destination_ids"],
        )

    def test_article_separates_residency_from_property_ownership(self) -> None:
        html = rendered_article()

        self.assertLess(
            html.index("Buying property does not give you residency"),
            html.index('id="comparison"'),
        )
        self.assertIn("residence visa for retirees", html)
        self.assertIn("property purchase is not a qualifying ARI investment", html)
        self.assertIn(
            "https://www.gov.pt/servicos/pedir-um-visto-de-residencia-para-fixacao-de-residencia-de-reformados-religiosos-e-pessoas-que-vivem-de-rendimentos-proprios",
            html,
        )
        self.assertIn(
            "https://aima.gov.pt/pt/a-aima/perguntas-frequentes-faqs/autorizacao-de-residencia-para-investimento-ari",
            html,
        )

    def test_fit_guidance_follows_the_controlling_constraint(self) -> None:
        html = rendered_article()

        self.assertLess(html.index("Who Portugal suits"), html.index("What changed in 2026"))
        self.assertIn("Portugal is a strong fit", html)
        self.assertIn("Look elsewhere first", html)

    def test_article_explains_the_2026_nonresident_imt_change(self) -> None:
        html = rendered_article()

        self.assertIn("7.5% IMT rate", html)
        self.assertIn("becomes Portuguese tax resident within two years", html)
        self.assertIn("Decree-Law 97/2026", html)
        self.assertIn(
            "https://diariodarepublica.pt/dr/detalhe/decreto-lei/97-2026-1124493227",
            html,
        )

    def test_article_covers_cost_healthcare_title_rental_and_hazard_diligence(self) -> None:
        html = rendered_article()

        for phrase in (
            "Financing and ownership costs",
            "0.8% stamp duty",
            "IMI and AIMI",
            "Healthcare follows legal residence",
            "Title, planning and condominium records",
            "Wildfire, flood and coastal diligence",
            "Local accommodation is municipality-specific",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Compra_da_casa/Paginas/default.aspx",
            "https://info.portaldasfinancas.gov.pt/pt/apoio_ao_contribuinte/Cidadaos/Casa_e_propriedades/Imposto_anual/Paginas/default.aspx",
            "https://www.gov.pt/guias/migrantes-cuidados-de-saude-em-portugal",
            "https://justica.gov.pt/Servicos/Pedir-certidao-permanente-predial",
            "https://diariodarepublica.pt/dr/legislacao-consolidada/decreto-lei/2024-892307454",
        ):
            self.assertIn(source, html)

    def test_article_uses_one_consolidated_destination_comparison(self) -> None:
        html = rendered_article()

        self.assertEqual(1, html.count("Two Portuguese destinations to compare"))
        self.assertNotIn("Destination notes for serious buyers", html)
        for name in ("Algarve / Cascais", "Madeira"):
            self.assertIn(name, html)

    def test_references_are_the_final_article_section(self) -> None:
        html = rendered_article()

        self.assertEqual(1, html.count('id="sources"'))
        self.assertGreater(html.index('id="sources"'), html.index('id="faq"'))
        sources = html.index('id="sources"')
        article_end = html.index("</article>", sources)
        self.assertNotIn('<section class="seo-section"', html[sources + 1 : article_end])

    def test_article_has_editorial_layout_authorship_and_complete_rail(self) -> None:
        html = rendered_article()

        self.assertIn('<body class="seo-page seo-page--editorial-retirement">', html)
        self.assertIn("By Global Home Atlas Research Team", html)
        self.assertIn(
            '"author":{"@type":"Organization","name":"Global Home Atlas Research Team"}',
            html,
        )
        self.assertIn('class="editorial-hero-visual destination-editorial-figure"', html)
        self.assertIn('class="seo-aside editorial-guide-rail"', html)
        for section_id, label in (
            ("residency", "Residency first"),
            ("fit", "Who Portugal suits"),
            ("owner-changes", "2026 changes"),
            ("costs", "Financing and costs"),
            ("practicality", "Retirement practicality"),
            ("lenses", "Five retirement lenses"),
            ("comparison", "Compare destinations"),
            ("faq", "Common questions"),
            ("sources", "References"),
        ):
            self.assertIn(f'id="{section_id}"', html)
            self.assertIn(f'href="#{section_id}">{label}</a>', html)

    def test_images_are_varied_and_distributed_through_the_article(self) -> None:
        html = rendered_article()

        self.assertNotIn('class="destination-visual-story__grid"', html)
        assets = (
            "/assets/algarve-cascais-coast-hero.webp",
            "/assets/algarve-cascais-tavira-daily-life.webp",
            "/assets/madeira-funchal-hero.webp",
        )
        for asset in assets:
            self.assertEqual(1, html.count(asset))

        header_end = html.index("</header>")
        daily_life = html.index("Live well beyond the holiday season")
        access = html.index("Reach Portugal—and choose mainland or island life")
        ownership = html.index("Own and operate with municipal discipline")
        self.assertLess(html.index(assets[0]), header_end)
        self.assertGreater(html.index(assets[1]), daily_life)
        self.assertLess(html.index(assets[1]), access)
        self.assertGreater(html.index(assets[2]), access)
        self.assertLess(html.index(assets[2]), ownership)

    def test_first_destination_mentions_link_to_the_completed_dossiers(self) -> None:
        html = rendered_article()

        for href, label in (
            ("/destinations/algarve-cascais/", "Algarve and Cascais"),
            ("/destinations/madeira/", "Madeira"),
        ):
            anchor = (
                f'<a class="editorial-destination-link" href="{href}" '
                f'data-track="destination_click">{label}</a>'
            )
            self.assertEqual(1, html.count(anchor))

    def test_reader_copy_avoids_process_and_internal_research_language(self) -> None:
        html = rendered_article()

        for phrase in (
            "research-grade destination intelligence",
            "committee read",
            "research inputs",
            "same ten-dimension model",
            "25-destination Atlas",
        ):
            self.assertNotIn(phrase, html)
        self.assertIn("Compare Portugal with every destination in the Atlas.", html)


if __name__ == "__main__":
    unittest.main()
