from __future__ import annotations

import unittest

from src import build_unified_app


class CompactDashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = [
            build_unified_app.consolidate_destination(item)
            for item in build_unified_app.load_json("destinations.json")
        ]

    def test_yield_sort_value_uses_range_midpoint(self) -> None:
        cases = (
            ("3.5–6.5% est. net after management/OPEX", 5.0),
            ("3–5% est. net; 10-year context", 4.0),
            ("4.2% est. net", 4.2),
            (None, 0.0),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(build_unified_app.percentish(value), expected)

    def test_market_result_is_a_reader_first_row(self) -> None:
        destination = build_unified_app.consolidate_destination(
            {
                "id": "test-market",
                "name": "Test Market",
                "country": "Test Country",
                "category": "City",
                "rank": 1,
                "usd_per_m2": 5000,
                "net_yield_estimate": "3-4% est. net",
                "scores": {
                    "ownership_clarity": {"score": 4.2},
                    "retirement_suitability": {"score": 3.8},
                },
            }
        )

        html = build_unified_app.build_destination_card(destination, [], {"test-market"})

        self.assertIn('class="market-row"', html)
        self.assertIn('<h3><a href="/destinations/test-market/">Test Market</a></h3>', html)
        self.assertIn("Overall rating", html)
        self.assertIn("Price guide", html)
        self.assertNotIn(">Compare<", html)
        self.assertNotIn(">Available<", html)
        self.assertNotIn('class="memo-add"', html)
        self.assertNotIn("Shortlist", html)
        self.assertNotIn("View profile", html)
        self.assertNotIn("<details", html)
        self.assertNotIn("10-Dimension Rating", html)
        self.assertNotIn("Representative Live-Market References", html)

    def test_market_row_shows_only_the_numeric_yield_range(self) -> None:
        destination = build_unified_app.consolidate_destination(
            {
                "id": "yield-market",
                "name": "Yield Market",
                "country": "Test Country",
                "category": "City",
                "rank": 1,
                "net_yield_estimate": "3.5–6.5% est. net after management/OPEX",
                "scores": {},
            }
        )

        html = build_unified_app.build_destination_card(destination, [], set())

        self.assertIn('data-yield="5.0"', html)
        self.assertIn('<strong>3.5–6.5%</strong>', html)
        self.assertNotIn("after management/OPEX", html)

    def test_dashboard_prioritizes_browsing_over_editorial_sections(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        self.assertIn("<h1>Destinations</h1>", html)
        self.assertIn('class="filter-bar"', html)
        self.assertIn('class="advanced-controls"', html)
        self.assertEqual(html.count('class="market-row"'), 37)
        self.assertIn('class="compare-panel hidden" id="compare"', html)
        for removed_copy in (
            "Credibility snapshot",
            "Clarity is the ultimate luxury",
            "Use the dashboard when you are ready to compare",
            "Priority Shortlist",
            "Paid buyer memo adds the decision layer",
            "Destination Dossiers",
            "Buyer Guides",
        ):
            with self.subTest(removed_copy=removed_copy):
                self.assertNotIn(removed_copy, html)

    def test_dashboard_exposes_sortable_market_headers(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        for sort_key in ("rank", "name", "score", "price", "yield", "ownership"):
            with self.subTest(sort_key=sort_key):
                self.assertIn(f'data-column-sort="{sort_key}"', html)
        self.assertEqual(html.count('data-column-sort="'), 6)
        self.assertIn('<option value="name">Destination name</option>', html)
        self.assertIn('<option value="access">Buyer access</option>', html)

    def test_place_collections_use_destination_terminology(self) -> None:
        output = build_unified_app.build()
        dashboard_html = output.read_text(encoding="utf-8")
        landing_html = (output.parent / "index.html").read_text(encoding="utf-8")

        for expected_copy in (
            "<h1>Destinations</h1>",
            "Compare selected destinations",
            "Choose a destination name for the full research.",
            'data-sort-label="destination name">Destination',
        ):
            with self.subTest(surface="dashboard", expected_copy=expected_copy):
                self.assertIn(expected_copy, dashboard_html)

        for expected_copy in (
            "Find your destination fit",
            "three destinations worth comparing",
            "Compare all destinations",
            "Three destinations to start with",
            "More destinations",
            "View destination",
        ):
            with self.subTest(surface="landing", expected_copy=expected_copy):
                self.assertIn(expected_copy, landing_html)

    def test_dashboard_has_one_destination_heading_and_four_primary_filters(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        self.assertEqual(html.count("<h1>Destinations</h1>"), 1)
        self.assertNotIn("<h2>Destinations</h2>", html)
        for control_id in ("search", "category", "sort", "buyerGoal"):
            self.assertIn(f'id="{control_id}"', html)
        self.assertIn("Location type", html)
        self.assertIn("Buying goal", html)

    def test_dashboard_marks_numeric_columns_for_shared_alignment(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        self.assertEqual(html.count('class="market-sort market-sort--numeric"'), 4)
        for sort_key in ("score", "price", "yield", "ownership"):
            with self.subTest(sort_key=sort_key):
                self.assertIn(
                    f'class="market-sort market-sort--numeric" data-column-sort="{sort_key}"',
                    html,
                )
        self.assertEqual(html.count('class="market-sort market-sort--text"'), 2)
        for sort_key in ("rank", "name"):
            with self.subTest(sort_key=sort_key):
                self.assertIn(
                    f'class="market-sort market-sort--text" data-column-sort="{sort_key}"',
                    html,
                )

    def test_dashboard_has_no_browser_shortlist_feature(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        for removed_marker in (
            'class="memo-add"',
            'id="savedShortlistStatus"',
            'id="savedBriefOutput"',
            'id="clearMemoShortlist"',
            'id="copyShortlistLink"',
        ):
            with self.subTest(removed_marker=removed_marker):
                self.assertNotIn(removed_marker, html)

    def test_compare_and_advanced_tools_are_progressively_disclosed(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        self.assertEqual(html.count('id="compareModeToggle"'), 1)
        self.assertEqual(html.count('id="compareSelectionBar"'), 1)
        self.assertIn('aria-pressed="false"', html)
        self.assertEqual(html.count('class="compare-toggle"'), 37)
        self.assertIn("Advanced research tools", html)
        self.assertGreater(html.index("Advanced research tools"), html.index('id="markets"'))
        self.assertNotIn("No saved destinations yet.", html)
        self.assertNotIn("Save markets to preview them here.", html)

    def test_location_types_can_overlap_for_real_cities(self) -> None:
        by_id = {item["id"]: item for item in self.destinations}

        self.assertEqual(
            set(build_unified_app.destination_location_types(by_id["valencia"])),
            {"city", "coast-island"},
        )
        self.assertEqual(
            set(build_unified_app.destination_location_types(by_id["fukuoka-itoshima"])),
            {"city", "coast-island"},
        )
        self.assertEqual(
            set(build_unified_app.destination_location_types(by_id["lake-como"])),
            {"mountain", "lake"},
        )
        self.assertEqual(
            set(build_unified_app.destination_location_types(by_id["dubai"])),
            {"city", "coast-island"},
        )

    def test_every_buying_goal_scores_the_full_destination_universe(self) -> None:
        expected_ids = {item["id"] for item in self.destinations}

        for goal in ("retirement", "second-home", "investment", "ownership"):
            with self.subTest(goal=goal):
                ranked = build_unified_app.rank_destinations_for_goal(self.destinations, goal)
                self.assertEqual(len(ranked), 37)
                self.assertEqual({item["id"] for item in ranked}, expected_ids)
                self.assertTrue(all(0 <= item["goal_score"] <= 5 for item in ranked))

        ownership_ranked = build_unified_app.rank_destinations_for_goal(self.destinations, "ownership")
        self.assertIn("bali", {item["id"] for item in ownership_ranked})

    def test_dashboard_uses_goal_lenses_without_hiding_candidates(self) -> None:
        output = build_unified_app.build()
        html = output.read_text(encoding="utf-8")

        self.assertIn('data-location-types="city coast-island"', html)
        self.assertEqual(html.count('data-goal-retirement="'), 37)
        self.assertEqual(html.count('data-goal-second-home="'), 37)
        self.assertEqual(html.count('data-goal-investment="'), 37)
        self.assertEqual(html.count('data-goal-ownership="'), 37)
        self.assertIn('<option value="retirement">Retirement / lifestyle</option>', html)
        self.assertIn('<option value="second-home">Second home</option>', html)
        self.assertIn('<option value="investment">Investment-led</option>', html)
        self.assertNotIn('buyerGoal.value === "shortlist"', html)
        self.assertNotIn('card.dataset.topRetirement === "yes"', html)


if __name__ == "__main__":
    unittest.main()
