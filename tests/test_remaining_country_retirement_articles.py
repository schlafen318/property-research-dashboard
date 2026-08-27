from __future__ import annotations

import unittest

from src import build_unified_app


GUIDES = {
    "united-states-retirement-property-foreign-buyers": {
        "country": "United States",
        "hub": "united-states-property",
        "destinations": [
            "park-city-deer-valley",
            "lake-tahoe",
            "jackson-hole",
            "aspen-snowmass",
        ],
    },
    "canada-retirement-property-foreign-buyers": {
        "country": "Canada",
        "hub": "canada-property",
        "destinations": ["vancouver-island-victoria", "whistler"],
    },
    "thailand-retirement-property-foreign-buyers": {
        "country": "Thailand",
        "hub": "thailand-property",
        "destinations": ["phuket-koh-samui"],
    },
    "greece-retirement-property-foreign-buyers": {
        "country": "Greece",
        "hub": "greece-property",
        "destinations": ["crete"],
    },
    "italy-retirement-property-foreign-buyers": {
        "country": "Italy",
        "hub": "italy-property",
        "destinations": ["lake-como", "dolomites-south-tyrol"],
    },
    "switzerland-retirement-property-foreign-buyers": {
        "country": "Switzerland",
        "hub": "switzerland-property",
        "destinations": [
            "andermatt",
            "ticino-lake-lugano",
            "swiss-valais-vaud-alps",
        ],
    },
}


def page_for(slug: str) -> dict:
    return next(page for page in build_unified_app.SEO_PAGES if page["slug"] == slug)


def rendered_article(slug: str) -> str:
    destinations = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.build_seo_page(
        page_for(slug), destinations, build_unified_app.SEO_PAGES
    )


class RemainingCountryRetirementArticleTests(unittest.TestCase):
    def test_each_country_hub_links_to_its_retirement_guide(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                hub = next(
                    item
                    for item in build_unified_app.COUNTRY_HUBS
                    if item["slug"] == expected["hub"]
                )
                self.assertIn(slug, hub["guide_slugs"])

    def test_each_guide_uses_only_its_completed_destination_set(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                self.assertEqual(expected["destinations"], page_for(slug)["destination_ids"])

    def test_each_guide_uses_the_complete_editorial_structure(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                html = rendered_article(slug)
                self.assertIn(
                    '<body class="seo-page seo-page--editorial-retirement">', html
                )
                self.assertIn("By Global Home Atlas Research Team", html)
                self.assertIn('class="seo-aside editorial-guide-rail"', html)
                section_ids = [
                    "residency",
                    "fit",
                    "owner-changes",
                    "costs",
                    "practicality",
                    "lenses",
                    "comparison",
                    "faq",
                    "sources",
                ]
                positions = [html.index(f'id="{section_id}"') for section_id in section_ids]
                self.assertEqual(positions, sorted(positions))

    def test_each_guide_leads_with_residency_and_fit(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                html = rendered_article(slug)
                self.assertIn("Buying property does not give you residency", html)
                self.assertIn(f"Who {expected['country']} suits", html)
                self.assertIn(f"{expected['country']} is a strong fit", html)
                self.assertIn("Look elsewhere first", html)
                self.assertLess(html.index('id="residency"'), html.index('id="fit"'))

    def test_each_guide_has_one_consolidated_destination_comparison(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                html = rendered_article(slug)
                self.assertEqual(1, html.count('id="comparison"'))
                self.assertNotIn("Destination Notes for Serious Buyers", html)
                for destination_id in expected["destinations"]:
                    self.assertIn(f'/destinations/{destination_id}/', html)

    def test_references_are_the_final_section_of_every_article(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                html = rendered_article(slug)
                self.assertEqual(1, html.count('id="sources"'))
                sources = html.index('id="sources"')
                article_end = html.index("</article>", sources)
                self.assertNotIn(
                    '<section class="seo-section"', html[sources + 1 : article_end]
                )

    def test_each_guide_uses_three_distributed_destination_images(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                html = rendered_article(slug)
                self.assertEqual(3, html.count("destination-editorial-figure"))
                self.assertNotIn('class="destination-visual-story__grid"', html)

    def test_each_guide_delivers_five_distinct_retirement_lenses(self) -> None:
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                guide = build_unified_app.COUNTRY_RETIREMENT_GUIDES[slug]
                self.assertEqual(5, len(guide["lenses"]))
                self.assertEqual(2, sum("image" in lens for lens in guide["lenses"]))

    def test_reader_copy_avoids_internal_process_language(self) -> None:
        forbidden = (
            "research-grade destination intelligence",
            "committee read",
            "research inputs",
            "same ten-dimension model",
            "25-destination Atlas",
        )
        for slug, expected in GUIDES.items():
            with self.subTest(country=expected["country"]):
                html = rendered_article(slug)
                for phrase in forbidden:
                    self.assertNotIn(phrase, html)
                self.assertIn(
                    f"Compare {expected['country']} with every destination in the Atlas.",
                    html,
                )

    def test_united_states_explains_immigration_tax_healthcare_and_local_rules(self) -> None:
        html = rendered_article("united-states-retirement-property-foreign-buyers")

        for phrase in (
            "visitor status is not a retirement route",
            "15% of the gross amount realized",
            "five continuous years",
            "short-term rental permission belongs to the exact property",
            "wildfire, snow and insurance",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://travel.state.gov/content/travel/en/us-visas/tourism-visit/visitor.html",
            "https://www.irs.gov/individuals/international-taxpayers/firpta-withholding",
            "https://www.cms.gov/medicare/enrollment-renewal/original-part-a-b",
            "https://www.fema.gov/flood-maps/products-tools",
        ):
            self.assertIn(source, html)

    def test_canada_explains_purchase_ban_bc_tax_healthcare_and_rentals(self) -> None:
        html = rendered_article("canada-retirement-property-foreign-buyers")

        for phrase in (
            "through 1 January 2027",
            "20% additional property transfer tax",
            "3% speculation and vacancy tax",
            "Victoria and Whistler are not interchangeable",
            "MSP follows qualifying residence",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://laws-lois.justice.gc.ca/eng/acts/P-25.2/section-2.html",
            "https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax/additional-property-transfer-tax",
            "https://www.victoria.ca/building-business/business-licensing/short-term-rentals",
            "https://www.whistler.ca/business-development/business-licenses/tourist-accomodation-business-licence/",
        ):
            self.assertIn(source, html)

    def test_thailand_explains_retirement_status_ownership_tax_and_short_lets(self) -> None:
        html = rendered_article("thailand-retirement-property-foreign-buyers")

        for phrase in (
            "age 50 or older",
            "49% foreign ownership ceiling",
            "30-year registered lease",
            "at least 180 days",
            "charged monthly or longer",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://thaiconsulatela.thaiembassy.org/en/publicservice/non-immigrant-type-o-retirement?cate=61a8019ec0e81b444e7a5b52",
            "https://osos.boi.go.th/EN/how-to/215/Other-Legal-Issue/",
            "https://www.rd.go.th/fileadmin/user_upload/porphor/GuideTaxFromAbroad_EN.pdf",
            "https://multi.dopa.go.th/tspd/official_letter/download/2663/EN",
        ):
            self.assertIn(source, html)

    def test_greece_explains_residence_tax_short_lets_and_crete_risk(self) -> None:
        html = rendered_article("greece-retirement-property-foreign-buyers")

        for phrase in (
            "€800,000",
            "€2,000 per month",
            "3.09%",
            "1 October 2025",
            "Crete is not one retirement market",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://apdattikis.gov.gr/en/process/2-2-2-financially-independent-individuals-article-20-paragraph-1-law-4251-14-renewal/",
            "https://stegasi.gov.gr/programs/afxisi-oriou-elachistis-ependysis-se-akinita-gia-apoktisi-golden-visa/",
            "https://aade.gr/en/greeks-abroad-non-residents/property-taxation/real-estate-transfer-tax",
            "https://mintour.gov.gr/yperpsifistike-stin-olomeleia-tis-voylis-toy-ypoyrgeioy-toyrismoy/",
        ):
            self.assertIn(source, html)

    def test_italy_explains_elective_residence_purchase_tax_cin_and_locality(self) -> None:
        html = rendered_article("italy-retirement-property-foreign-buyers")

        for phrase in (
            "elective residence does not permit work",
            "9% registration tax",
            "2 January 2025",
            "CIN",
            "Lake Como and the Dolomites are not interchangeable",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://investorvisa.mise.gov.it/index.php/en/",
            "https://www1.agenziaentrate.gov.it/web_app_entrate/guida_acquisto_casa.html",
            "https://www.ministeroturismo.gov.it/faq-banca-dati-strutture-ricettive-bdsr/",
            "https://www.notariato.it/it/casa/lista-documenti-da-fornire-caso-di-compravendita-immobiliare/",
        ):
            self.assertIn(source, html)

    def test_switzerland_explains_residence_lex_koller_health_and_proposals(self) -> None:
        html = rendered_article("switzerland-retirement-property-foreign-buyers")

        for phrase in (
            "age 55 or older",
            "does not create a right to live in Switzerland",
            "end of 2040",
            "within three months",
            "proposal, not current law",
        ):
            self.assertIn(phrase, html)
        for source in (
            "https://www.bj.admin.ch/en/acquisition-of-property-by-foreign-non-residents",
            "https://www.sem.admin.ch/dam/sem/en/data/eu/fza/personenfreizuegigkeit/factsheets/fs-nichterwerbstaetige-e.pdf.download.pdf/fs-nichterwerbstaetige-e.pdf",
            "https://www.ur.ch/wirtschaft/6658",
            "https://www.bag.admin.ch/en/health-insurance-requirement-to-obtain-insurance-for-persons-resident-in-switzerland",
        ):
            self.assertIn(source, html)


if __name__ == "__main__":
    unittest.main()
