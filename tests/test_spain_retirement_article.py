from __future__ import annotations

import unittest

from src import build_unified_app


def spain_page() -> dict:
    return next(
        page
        for page in build_unified_app.SEO_PAGES
        if page["slug"] == "spain-retirement-property-foreign-buyers"
    )


def rendered_article() -> str:
    destinations = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.build_seo_page(
        spain_page(), destinations, build_unified_app.SEO_PAGES
    )


class SpainRetirementArticleTests(unittest.TestCase):
    def test_spain_country_hub_links_to_the_retirement_guide(self) -> None:
        hub = next(
            item for item in build_unified_app.COUNTRY_HUBS if item["slug"] == "spain-property"
        )

        self.assertIn("spain-retirement-property-foreign-buyers", hub["guide_slugs"])

    def test_primary_comparison_contains_four_distinct_spain_destinations(self) -> None:
        self.assertEqual(
            ["valencia", "m-laga-costa-del-sol", "costa-brava-girona", "mallorca"],
            spain_page()["destination_ids"],
        )

    def test_article_leads_with_residency_and_ended_investor_route(self) -> None:
        html = rendered_article()

        residency = html.index("Buying property does not give you residency")
        comparison = html.index('id="comparison"')

        self.assertLess(residency, comparison)
        self.assertIn("ended on 3 April 2025", html)
        self.assertIn("non-lucrative residence", html)
        self.assertIn(
            "https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/vivienda-agenda-urbana/Paginas/2025/020425-fin-golden-visa.aspx",
            html,
        )
        self.assertIn(
            "https://www.inclusion.gob.es/en/web/migraciones/w/autorizacion-inicial-de-residencia-temporal-no-lucrativa",
            html,
        )

    def test_fit_guidance_follows_the_controlling_constraint(self) -> None:
        html = rendered_article()

        self.assertLess(html.index("Who Spain suits"), html.index("What changed in 2025 and 2026"))
        self.assertIn("Spain is a strong fit", html)
        self.assertIn("Look elsewhere first", html)

    def test_article_explains_current_short_rental_rule_uncertainty(self) -> None:
        html = rendered_article()

        self.assertIn("three-fifths approval", html)
        self.assertIn("19 May 2026", html)
        self.assertIn("national registration procedure", html)
        self.assertIn("regional and municipal rules remain", html)
        self.assertIn("https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-11152", html)
        self.assertIn("https://www.boe.es/boe/dias/2026/06/08/", html)

    def test_article_covers_tax_cost_healthcare_and_hazard_diligence(self) -> None:
        html = rendered_article()

        for phrase in (
            "Financing and ownership costs",
            "10% VAT",
            "3% of the agreed consideration",
            "more than 183 days",
            "Healthcare follows residence and entitlement",
            "Flood, wildfire and heat diligence",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://sede.agenciatributaria.gob.es/Sede/iva/iva-operaciones-inmobiliarias/compro-vivienda-tengo-que-pagar-itp.html",
            "https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/irnr-sin-establecimiento-permanente/retenciones-irnr-sin-establecimiento-permanente/retencion-adquirente-inmueble.html",
            "https://www.seg-social.es/wps/portal/wss/internet/Trabajadores/PrestacionesPensionesTrabajadores/10938/30476/177505",
            "https://www.miteco.gob.es/es/agua/temas/gestion-de-los-riesgos-de-inundacion/snczi.html",
        ):
            self.assertIn(source, html)

    def test_article_uses_one_consolidated_destination_comparison(self) -> None:
        html = rendered_article()

        self.assertEqual(1, html.count("Four Spanish destinations to compare"))
        self.assertNotIn("Destination notes for serious buyers", html)
        for name in ("Valencia", "Málaga / Costa del Sol", "Costa Brava / Girona", "Mallorca"):
            self.assertIn(name, html)

    def test_references_are_the_final_article_section(self) -> None:
        html = rendered_article()

        self.assertEqual(1, html.count('id="sources"'))
        self.assertGreater(html.index('id="sources"'), html.index('id="faq"'))
        article_end = html.index("</article>")
        sources = html.index('id="sources"')
        self.assertNotIn('<section class="seo-section"', html[sources + 1 : article_end])

    def test_article_has_authorship_schema_and_restrained_editorial_layout(self) -> None:
        html = rendered_article()

        self.assertIn('<body class="seo-page seo-page--editorial-retirement">', html)
        self.assertIn("By Global Home Atlas Research Team", html)
        self.assertIn('"datePublished":"2026-08-21"', html)
        self.assertIn(
            '"author":{"@type":"Organization","name":"Global Home Atlas Research Team"}',
            html,
        )
        self.assertIn('class="editorial-hero-visual destination-editorial-figure"', html)
        self.assertIn('class="seo-aside editorial-guide-rail"', html)
        self.assertIn(".seo-page--editorial-retirement .seo-section", html)

    def test_destination_images_are_distributed_through_relevant_sections(self) -> None:
        html = rendered_article()

        self.assertNotIn('class="destination-visual-story__grid"', html)
        for asset in (
            "/assets/spain-valencia-coast-hero.webp",
            "/assets/spain-malaga-daily-life.webp",
            "/assets/spain-mallorca-access-lifestyle.webp",
        ):
            self.assertEqual(1, html.count(asset))

        header_end = html.index("</header>")
        daily_life = html.index("Live well, year after year")
        access = html.index("Reach Spain easily—and choose the right rhythm")
        ownership = html.index("Own and operate with regional discipline")
        self.assertLess(html.index("/assets/spain-valencia-coast-hero.webp"), header_end)
        self.assertGreater(html.index("/assets/spain-malaga-daily-life.webp"), daily_life)
        self.assertLess(html.index("/assets/spain-malaga-daily-life.webp"), access)
        self.assertGreater(html.index("/assets/spain-mallorca-access-lifestyle.webp"), access)
        self.assertLess(html.index("/assets/spain-mallorca-access-lifestyle.webp"), ownership)

    def test_first_narrative_destination_mentions_link_to_their_dossiers(self) -> None:
        html = rendered_article()

        expected_links = (
            ('/destinations/valencia/', 'Valencia'),
            ('/destinations/malaga-costa-del-sol/', 'Málaga and the Costa del Sol'),
            ('/destinations/costa-brava-girona/', 'Girona and the Costa Brava'),
            ('/destinations/mallorca/', 'Mallorca'),
        )
        for href, label in expected_links:
            anchor = (
                f'<a class="editorial-destination-link" href="{href}" '
                f'data-track="destination_click">{label}</a>'
            )
            self.assertEqual(1, html.count(anchor))

        live_well_start = html.index("Live well, year after year")
        live_well_end = html.index("Reach Spain easily—and choose the right rhythm")
        live_well = html[live_well_start:live_well_end]
        self.assertEqual(4, live_well.count('class="editorial-destination-link"'))
        self.assertIn(".editorial-destination-link", html)

    def test_guide_rail_links_to_every_major_waypoint(self) -> None:
        html = rendered_article()

        for section_id, label in (
            ("residency", "Residency first"),
            ("fit", "Who Spain suits"),
            ("owner-changes", "2025–2026 changes"),
            ("costs", "Financing and costs"),
            ("practicality", "Retirement practicality"),
            ("lenses", "Five retirement lenses"),
            ("comparison", "Compare destinations"),
            ("faq", "Common questions"),
            ("sources", "References"),
        ):
            self.assertIn(f'id="{section_id}"', html)
            self.assertIn(f'href="#{section_id}">{label}</a>', html)


if __name__ == "__main__":
    unittest.main()
