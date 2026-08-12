from __future__ import annotations

import unittest

from src import build_unified_app


def seo_page(slug: str) -> dict:
    return next(page for page in build_unified_app.SEO_PAGES if page["slug"] == slug)


def content_override(canonical: str, *, title: str, description: str, intro: str, faq=None) -> dict:
    return {
        "target_url": canonical,
        "finding_fingerprint": "gha-low-ctr-opportunity-render",
        "base_content_hash": "a" * 64,
        "generated_at": "2026-08-12T00:00:00+00:00",
        "model": "test-model",
        "signal": {},
        "lifecycle": "proposed",
        "cooldown_until": "2026-09-09T00:00:00+00:00",
        "content": {
            "title": title,
            "meta_description": description,
            "intro": intro,
            "faq_question": faq[0] if faq else None,
            "faq_answer": faq[1] if faq else None,
            "internal_link_target": "https://globalhomeatlas.com/guides/",
            "internal_link_anchor": "global property buying guides",
        },
    }


def destinations() -> list[dict]:
    return [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]


class SeoCtrContentTests(unittest.TestCase):
    def test_seo_page_override_updates_visible_content_and_schema(self) -> None:
        page = seo_page("best-places-to-buy-property-in-europe")
        canonical = build_unified_app.page_url(page["slug"])
        overrides = [
            content_override(
                canonical,
                title="Europe Property Markets for Foreign Buyers | Global Home Atlas",
                description="Compare Europe property markets for foreign buyers using lifestyle, ownership clarity, value, and resale depth.",
                intro="Compare Europe property markets for foreign buyers before choosing destinations.",
                faq=("How should buyers compare Europe?", "Compare access, ownership clarity, and resale depth."),
            )
        ]
        html = build_unified_app.build_seo_page(
            page,
            destinations(),
            build_unified_app.SEO_PAGES,
            content_overrides=overrides,
        )
        self.assertIn("<title>Europe Property Markets for Foreign Buyers | Global Home Atlas</title>", html)
        self.assertIn("Compare Europe property markets for foreign buyers before choosing destinations.", html)
        self.assertIn("How should buyers compare Europe?", html)
        self.assertIn('"@type":"FAQPage"', html)
        self.assertIn("global property buying guides", html)

    def test_home_country_and_destination_accept_overrides(self) -> None:
        all_destinations = destinations()
        homepage = build_unified_app.build_landing_page(
            all_destinations,
            build_unified_app.SEO_PAGES,
            [],
            10,
            content_overrides=[content_override(
                build_unified_app.SITE_URL,
                title="Global Property Markets for International Buyers",
                description="Compare global property markets for international buyers using lifestyle, ownership clarity, budget, and exit planning.",
                intro="Compare international property markets with the Atlas decision framework.",
            )],
        )
        country = build_unified_app.build_country_hub_page(
            build_unified_app.COUNTRY_HUBS[0],
            all_destinations,
            build_unified_app.SEO_PAGES,
            content_overrides=[content_override(
                build_unified_app.country_url(build_unified_app.COUNTRY_HUBS[0]),
                title="Spain Property Markets for Foreign Buyers | Global Home Atlas",
                description="Compare Spain property markets for foreign buyers across lifestyle, ownership, retirement fit, and resale depth.",
                intro="Compare Spain property markets before selecting a destination.",
            )],
        )
        destination = build_unified_app.build_destination_page(
            all_destinations[0],
            [],
            all_destinations,
            build_unified_app.SEO_PAGES,
            content_overrides=[content_override(
                build_unified_app.destination_url(all_destinations[0]),
                title="Destination Property Research for Global Buyers | Global Home Atlas",
                description="Review destination property research for global buyers using lifestyle, ownership clarity, risk, and resale evidence.",
                intro="Review this destination through the Atlas decision framework.",
            )],
        )
        self.assertIn("Global Property Markets for International Buyers", homepage)
        self.assertIn("Compare Spain property markets before selecting a destination.", country)
        self.assertIn("Review this destination through the Atlas decision framework.", destination)
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
