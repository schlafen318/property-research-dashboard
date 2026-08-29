from __future__ import annotations

import re
import unittest

from src import build_unified_app


def rendered_destinations() -> list[dict]:
    rows = [
        build_unified_app.consolidate_destination(item)
        for item in build_unified_app.load_json("destinations.json")
    ]
    return build_unified_app.rank_destinations(rows)


def title_from(html: str) -> str:
    match = re.search(r"<title>(.*?)</title>", html)
    if not match:
        raise AssertionError("rendered page has no title")
    return match.group(1)


def description_from(html: str) -> str:
    match = re.search(r'<meta name="description" content="([^"]+)">', html)
    if not match:
        raise AssertionError("rendered page has no meta description")
    return match.group(1)


class NearRankingSnippetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = rendered_destinations()
        listings = build_unified_app.load_json("listings.json")
        cls.listings_by_destination: dict[str, list[dict]] = {}
        for listing in listings:
            cls.listings_by_destination.setdefault(listing["destination_id"], []).append(listing)

    def render_destination(self, destination_id: str) -> str:
        destination = next(item for item in self.destinations if item["id"] == destination_id)
        return build_unified_app.build_destination_page(
            destination,
            self.listings_by_destination.get(destination_id, []),
            self.destinations,
            build_unified_app.SEO_PAGES,
        )

    def test_near_ranking_destinations_render_search_focused_snippets(self) -> None:
        expected = {
            "crete": (
                "Crete Property for Retirement: Areas, Costs &amp; Buyer Guide",
                "Compare Crete property for retirement across Chania, Rethymno, Heraklion and eastern Crete, including buyer rules, costs, healthcare, hazards and resale.",
            ),
            "dolomites-south-tyrol": (
                "Dolomites &amp; South Tyrol Property: Buyer Guide 2026",
                "Compare Dolomites and South Tyrol property markets, buyer restrictions, prices, year-round access, tourist letting, hazards and resale using current evidence.",
            ),
            "croatia-istria-dalmatia": (
                "Croatia Property: Istria vs Dalmatia Retirement Guide",
                "Compare Croatia retirement property in Istria and Dalmatia across foreign-buyer access, prices, title checks, healthcare, tourist rules, hazards and resale.",
            ),
            "annecy": (
                "Annecy Property Guide: Prices, Areas &amp; Buyer Rules",
                "Compare Annecy property across the city and Lake Annecy villages, including prices, French buyer rules, Geneva access, tourist letting, hazards and resale.",
            ),
        }

        for destination_id, (expected_title, expected_description) in expected.items():
            with self.subTest(destination_id=destination_id):
                html = self.render_destination(destination_id)
                self.assertEqual(expected_title, title_from(html))
                self.assertEqual(expected_description, description_from(html))
                self.assertIn(
                    f'<link rel="canonical" href="https://globalhomeatlas.com/destinations/{destination_id}/">',
                    html,
                )

    def test_homepage_snippet_leads_with_the_brand_and_property_abroad_intent(self) -> None:
        html = build_unified_app.build_landing_page(
            self.destinations,
            build_unified_app.SEO_PAGES,
            build_unified_app.load_json("listings.json"),
            len({item["country"] for item in self.destinations}),
        )

        self.assertEqual(
            "Global Home Atlas: Compare Property Abroad",
            title_from(html),
        )
        self.assertEqual(
            "Compare property abroad across 37 global destinations with buyer-access rules, costs, rankings, representative listings, retirement tools and research guides.",
            description_from(html),
        )
        self.assertIn('<link rel="canonical" href="https://globalhomeatlas.com/">', html)
        self.assertIn('<h1 id="landing-title">Find the right place to buy property abroad</h1>', html)

    def test_protected_pages_keep_their_current_experiment_metadata(self) -> None:
        vacation_page = next(
            page
            for page in build_unified_app.SEO_PAGES
            if page["slug"] == "best-places-to-buy-vacation-home-abroad"
        )
        vacation_html = build_unified_app.build_seo_page(
            vacation_page,
            self.destinations,
            build_unified_app.SEO_PAGES,
        )

        self.assertEqual(
            "Best Locations for Vacation Homes: 10 Global Markets",
            title_from(vacation_html),
        )
        self.assertIn(
            '<h1>Best Places to Buy a Vacation Home in the World</h1>',
            vacation_html,
        )


if __name__ == "__main__":
    unittest.main()
