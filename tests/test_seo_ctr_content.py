from __future__ import annotations

import json
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
    def test_user_facing_scores_use_one_decimal_place(self) -> None:
        destination = {
            "id": "valencia",
            "name": "Valencia",
            "country": "Spain",
            "category": "Water",
            "decision_score": 4.09,
            "red_flags": "Check local rental rules.",
            "decision_dimensions": [
                {"key": "ownership_clarity", "score": 4.26},
                {"key": "retirement_fit", "score": 4.14},
            ],
        }

        recommendation_html = build_unified_app.build_landing_recommendations([destination])
        finder_data = json.loads(build_unified_app.build_market_finder_data([destination]))
        table_html = build_unified_app.build_seo_destination_table([destination])

        self.assertIn("4.1/5", recommendation_html)
        self.assertEqual(finder_data["retirement"][0]["score"], "4.1")
        self.assertIn("<td>4.1</td>", table_html)
        self.assertNotIn("4.09", recommendation_html + table_html + json.dumps(finder_data))

    def test_build_rejects_stale_override_hash(self) -> None:
        original_loader = build_unified_app.load_content_overrides
        stale = content_override(
            "https://globalhomeatlas.com/", title="New title", description="New description", intro="New intro"
        )
        stale["base_content_hash"] = "0" * 64
        build_unified_app.load_content_overrides = lambda: [stale]
        try:
            with self.assertRaisesRegex(ValueError, "Stale SEO content base hash"):
                build_unified_app.build()
        finally:
            build_unified_app.load_content_overrides = original_loader

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
    def test_vacation_home_page_targets_exact_world_query(self) -> None:
        page = seo_page("best-places-to-buy-vacation-home-abroad")
        query = "best places to buy a vacation home in the world"

        self.assertIn(query, page["title"].lower())
        self.assertIn(query, page["description"].lower())
        self.assertIn(query, page["h1"].lower())
        self.assertIn(query, page["faqs"][0][0].lower())

        html = build_unified_app.build_seo_page(
            page,
            destinations(),
            build_unified_app.SEO_PAGES,
        ).lower()
        self.assertIn(f"<title>{query}</title>", html)
        self.assertIn(
            f'<meta name="description" content="compare the {query} by lifestyle use, ownership clarity, rental-rule risk, value discipline, and resale depth.">',
            html,
        )
        self.assertIn(f'<h1>{query}</h1>', html)
        self.assertIn(f'<p class="seo-lede">compare the {query}', html)
        self.assertIn(f'"name":"what are the {query}?"', html)

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

    def test_homepage_uses_the_consolidated_research_journey(self) -> None:
        html = build_unified_app.build_landing_page([], [], [], 0)

        section_ids = [
            'id="market-finder"',
            'id="recommendations"',
            'id="explore"',
            'id="method"',
            'id="conversion"',
        ]
        positions = [html.find(section_id) for section_id in section_ids]

        self.assertNotIn(-1, positions)
        self.assertEqual(positions, sorted(positions))
        self.assertNotIn('id="premium-briefs"', html)
        self.assertNotIn('id="start"', html)
        self.assertNotIn('id="inspiration"', html)
        self.assertNotIn('id="mid-conversion"', html)
        self.assertNotIn('id="countries"', html)
        self.assertNotIn('id="guides"', html)
        self.assertEqual(html.count('href="/shortlist-review/"'), 1)
        self.assertIn("Explore the research", html)
        self.assertIn("By buying goal", html)
        self.assertIn("By country", html)
        self.assertIn("Buying guides", html)

    def test_homepage_hero_groups_useful_actions_without_a_proof_badge(self) -> None:
        html = build_unified_app.build_landing_page([], [], [], 0)

        self.assertNotIn('class="hero-proof"', html)
        self.assertEqual(1, html.count('data-track="homepage_start_click"'))
        self.assertIn('<nav class="hero-secondary-actions" aria-label="Explore Global Home Atlas">', html)
        self.assertIn('href="/guides/#country-selection"', html)
        self.assertIn('href="/retirement-abroad-calculator/"', html)
        self.assertIn('href="/methodology/"', html)

    def test_homepage_limits_editorial_recommendations_to_three(self) -> None:
        destinations = [
            {
                "id": destination_id,
                "name": destination_id.replace("-", " ").title(),
                "country": "Test country",
                "category": "Test category",
                "decision_score": 4.0,
            }
            for destination_id in [
                "fukuoka-itoshima",
                "valencia",
                "algarve-cascais",
                "lake-como",
                "madeira",
            ]
        ]

        html = build_unified_app.build_landing_recommendations(destinations)

        self.assertEqual(html.count('class="recommendation-card"'), 3)
        self.assertNotIn("<details", html)

    def test_homepage_preserves_compact_links_to_research_hubs_and_markets(self) -> None:
        destinations = [
            {"id": destination_id, "name": name}
            for destination_id, name in [
                ("crete", "Crete"),
                ("lake-como", "Lake Como"),
                ("madeira", "Madeira"),
                ("phuket-koh-samui", "Phuket / Koh Samui"),
                ("queenstown", "Queenstown"),
                ("whistler", "Whistler"),
            ]
        ]

        html = build_unified_app.build_landing_page(destinations, build_unified_app.SEO_PAGES, [], 0)

        required_targets = [
            "/best-countries-to-buy-property-as-a-foreigner/",
            "/countries/greece-property/",
            "/countries/switzerland-property/",
            "/countries/thailand-property/",
            "/destinations/crete/",
            "/destinations/lake-como/",
            "/destinations/madeira/",
            "/destinations/phuket-koh-samui/",
            "/destinations/queenstown/",
            "/destinations/whistler/",
        ]

        for target in required_targets:
            with self.subTest(target=target):
                self.assertIn(f'href="{target}"', html)

    def test_homepage_keeps_explanatory_content_compact(self) -> None:
        destinations = [
            {
                "id": destination_id,
                "name": destination_id.replace("-", " ").title(),
                "country": "Test country",
                "category": "Test category",
                "decision_score": 4.0,
            }
            for destination_id in ["fukuoka-itoshima", "valencia", "algarve-cascais"]
        ]

        html = build_unified_app.build_landing_page(destinations, build_unified_app.SEO_PAGES, [], 0)

        self.assertNotIn("<details>", build_unified_app.build_landing_recommendations(destinations))
        self.assertNotIn("bulletList(", html)
        self.assertIn('class="finder-signal"', html)
        self.assertNotIn('class="trust-card"', html)
        self.assertIn("We look at ownership rules, realistic returns, daily life and resale potential.", html)
        self.assertEqual(html.count('class="explore-primary"'), 9)
        self.assertEqual(html.count('class="explore-more"'), 3)
        self.assertIn("More buying goals", html)
        self.assertIn("More countries", html)
        self.assertIn("More guides", html)
        self.assertIn('href="/research-standards/" data-track="trust_click" data-track-label="landing standards">Research standards</a>', html)

    def test_homepage_recommendations_include_editorial_images(self) -> None:
        destinations = [
            {
                "id": destination_id,
                "name": destination_id.replace("-", " ").title(),
                "country": "Test country",
                "category": "Test category",
                "decision_score": 4.0,
            }
            for destination_id in ["fukuoka-itoshima", "valencia", "algarve-cascais"]
        ]

        html = build_unified_app.build_landing_recommendations(destinations)

        self.assertEqual(html.count('class="recommendation-card__image"'), 3)
        self.assertIn('src="/assets/market-fukuoka-itoshima.jpg"', html)
        self.assertIn('src="/assets/market-valencia.jpg"', html)
        self.assertIn('src="/assets/market-algarve-cascais.jpg"', html)
        self.assertEqual(html.count('type="image/webp"'), 3)
        self.assertIn('/assets/market-fukuoka-itoshima-600.webp 600w', html)
        self.assertIn('/assets/market-valencia-900.webp 900w', html)
        self.assertIn('/assets/market-algarve-cascais-900.webp 900w', html)
        self.assertNotIn('<a class="recommendation-card__visual"', html)
        self.assertEqual(html.count('<div class="recommendation-card__visual">'), 3)
        self.assertIn('alt="Fukuoka waterfront and city skyline"', html)
        self.assertIn('alt="Valencia streetscape opening toward the Mediterranean"', html)
        self.assertIn('alt="Portuguese coastal town overlooking the Atlantic"', html)

    def test_homepage_recommendation_images_use_a_restrained_shared_treatment(self) -> None:
        html = build_unified_app.build_landing_page([], [], [], 0)

        self.assertIn(".recommendation-card__visual { position: relative;", html)
        self.assertIn("height: clamp(210px, 19vw, 265px);", html)
        self.assertIn("filter: saturate(.72) contrast(.94) brightness(.97) sepia(.06);", html)
        self.assertNotIn(".recommendation-card__visual::after", html)
        self.assertIn(".recommendation-card__image { width: 100%; height: 100%;", html)

    def test_market_finder_uses_consistent_editorial_thumbnails_without_a_decorative_map_cue(self) -> None:
        destinations = [
            {
                "id": destination_id,
                "name": destination_id.replace("-", " ").title(),
                "country": "Test country",
                "decision_score": 4.0,
            }
            for destination_id in ["fukuoka-itoshima", "valencia", "algarve-cascais", "madeira"]
        ]

        data = json.loads(build_unified_app.build_market_finder_data(destinations))
        html = build_unified_app.build_landing_page(destinations, [], [], 0)

        expected_images = {
            "/assets/market-fukuoka-itoshima-600.webp",
            "/assets/market-valencia-600.webp",
            "/assets/market-algarve-cascais-600.webp",
            "/assets/market-madeira-600.webp",
        }
        for matches in data.values():
            self.assertEqual(3, len(matches))
            for match in matches:
                self.assertIn(match["image"], expected_images)
                self.assertTrue(match["imageAlt"])
        self.assertIn('class="finder-map-cue" aria-hidden="true"', html)
        self.assertIn(".gha-mode-landing .finder-map-cue { display: none;", html)
        self.assertIn('class="finder-result__thumb"', html)
        self.assertIn("height: 112px;", html)

    def test_all_destination_profiles_have_responsive_editorial_image_assets(self) -> None:
        destinations = build_unified_app.load_json("destinations.json")

        self.assertEqual(len(destinations), 37)
        asset_sets = [build_unified_app.destination_image_assets(dest) for dest in destinations]
        self.assertEqual(len({assets["slug"] for assets in asset_sets}), 37)
        for assets in asset_sets:
            self.assertTrue((build_unified_app.SOURCE_ASSETS / assets["jpg"].removeprefix("/assets/")).exists())
            self.assertTrue((build_unified_app.SOURCE_ASSETS / assets["webp_600"].removeprefix("/assets/")).exists())
            self.assertTrue((build_unified_app.SOURCE_ASSETS / assets["webp_900"].removeprefix("/assets/")).exists())

        page = build_unified_app.build_destination_page(destinations[0], [], destinations, build_unified_app.SEO_PAGES)
        self.assertIn('style="--destination-hero-image: url(\'/assets/market-fukuoka-itoshima-900.webp\')"', page)

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
