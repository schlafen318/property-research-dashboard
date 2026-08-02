from __future__ import annotations

import unittest

from src import build_unified_app


def seo_page(slug: str) -> dict:
    return next(page for page in build_unified_app.SEO_PAGES if page["slug"] == slug)


class SeoCtrContentTests(unittest.TestCase):
    def test_vacation_home_page_targets_location_query_intent(self) -> None:
        page = seo_page("best-places-to-buy-vacation-home-abroad")
        text = " ".join(
            [
                page["title"],
                page["description"],
                page["h1"],
                " ".join(question + " " + answer for question, answer in page["faqs"]),
            ]
        ).lower()

        self.assertIn("vacation home", text)
        self.assertIn("locations", text)
        self.assertIn("best locations for vacation homes", text)

    def test_expats_and_europe_pages_have_buyer_specific_snippets(self) -> None:
        expat = seo_page("best-countries-for-expats-to-buy-property")
        foreigner = seo_page("best-countries-to-buy-property-as-a-foreigner")
        europe = seo_page("best-places-to-buy-property-in-europe")

        self.assertIn("expats", expat["title"].lower())
        self.assertIn("buy property", expat["description"].lower())
        self.assertIn("foreign-buyer", expat["description"].lower())
        self.assertIn("countries to buy property as a foreigner", foreigner["title"].lower())
        self.assertIn("foreigners can buy property", foreigner["description"].lower())
        self.assertIn("best countries to buy property as a foreigner", " ".join(q for q, _ in foreigner["faqs"]).lower())
        self.assertIn("europe", europe["title"].lower())
        self.assertIn("foreign buyers", europe["description"].lower())
        self.assertIn("2026", europe["title"])
        self.assertIn("compare Europe property markets", " ".join(answer for _, answer in europe["faqs"]))

    def test_homepage_snippet_includes_global_property_and_vacation_home_intent(self) -> None:
        html = build_unified_app.build_landing_page([], [], [], 0)

        self.assertIn("Global Property Markets", html)
        self.assertIn("vacation homes", html)
        self.assertIn("buying property abroad", html)
        self.assertIn("Best Places to Buy Property Abroad", html)

    def test_destination_query_match_sections_use_search_phrasing(self) -> None:
        pages = [
            {"slug": "best-places-to-buy-vacation-home-abroad", "h1": "Best Vacation Home Locations Abroad"},
            {"slug": "best-places-to-buy-a-second-home-abroad", "h1": "Best Places to Buy a Second Home Abroad"},
            {"slug": "best-places-to-buy-property-in-europe", "h1": "Best Places to Buy Property in Europe"},
            {"slug": "foreign-property-investment-risks", "h1": "Foreign Property Investment Risks"},
            {"slug": "where-can-foreigners-buy-property", "h1": "Where Can Foreigners Buy Property?"},
        ]

        andermatt = build_unified_app.destination_query_match_html({"id": "andermatt", "name": "Andermatt"}, pages)
        annecy = build_unified_app.destination_query_match_html({"id": "annecy", "name": "Annecy"}, pages)

        self.assertIn("Andermatt property for foreign buyers", andermatt)
        self.assertIn("Andermatt real estate", andermatt)
        self.assertIn("Swiss resort property", andermatt)
        self.assertIn("Annecy vacation home and second-home shortlist", annecy)
        self.assertIn("Annecy real estate", annecy)
        self.assertIn("French Alps", annecy)


if __name__ == "__main__":
    unittest.main()
