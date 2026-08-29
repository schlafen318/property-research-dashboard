from __future__ import annotations

import json
import re
import unittest

from src import build_unified_app


class FindYourFitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = [
            build_unified_app.consolidate_destination(item)
            for item in build_unified_app.load_json("destinations.json")
        ]

    def test_fit_ranking_considers_every_destination_but_recommends_buyable_markets(self) -> None:
        ranked = build_unified_app.rank_destinations_for_fit(
            self.destinations,
            {
                "goal": "retirement",
                "budget": "low",
                "setting": "city",
                "use": "personal",
                "tradeoff": "clarity",
            },
        )

        self.assertEqual(len(self.destinations), len(ranked))
        self.assertEqual({item["id"] for item in self.destinations}, {item["id"] for item in ranked})
        self.assertTrue(all(0 <= item["fit_score"] <= 5 for item in ranked))
        self.assertTrue(all(item["fit_label"] for item in ranked))
        self.assertIn("fukuoka-itoshima", {item["id"] for item in ranked[:5]})
        self.assertNotIn("vancouver", {item["id"] for item in ranked[:5]})
        self.assertFalse(next(item for item in ranked if item["id"] == "vancouver")["recommendable"])

    def test_fit_ranking_accepts_any_selected_setting_as_a_match(self) -> None:
        base_preferences = {
            "goal": "retirement",
            "budget": "flexible",
            "use": "balanced",
            "tradeoff": "balanced",
        }

        multi_setting = build_unified_app.rank_destinations_for_fit(
            self.destinations,
            {**base_preferences, "setting": ["city", "lake"]},
        )
        city_only = build_unified_app.rank_destinations_for_fit(
            self.destinations,
            {**base_preferences, "setting": "city"},
        )
        lake_only = build_unified_app.rank_destinations_for_fit(
            self.destinations,
            {**base_preferences, "setting": "lake"},
        )

        multi_scores = {item["id"]: item["fit_score"] for item in multi_setting}
        city_scores = {item["id"]: item["fit_score"] for item in city_only}
        lake_scores = {item["id"]: item["fit_score"] for item in lake_only}
        self.assertEqual(city_scores["fukuoka-itoshima"], multi_scores["fukuoka-itoshima"])
        self.assertEqual(lake_scores["lake-como"], multi_scores["lake-como"])

    def test_setting_question_allows_multiple_choices(self) -> None:
        html = build_unified_app.build_find_your_fit_page(self.destinations)
        setting_inputs = re.findall(
            r'<input type="([^"]+)" name="setting" value="([^"]+)"([^>]*)>',
            html,
        )

        self.assertEqual(
            ["any", "city", "coast-island", "mountain", "lake"],
            [value for _input_type, value, _attributes in setting_inputs],
        )
        self.assertTrue(all(input_type == "checkbox" for input_type, _value, _attributes in setting_inputs))
        self.assertIn("checked", setting_inputs[0][2])
        self.assertIn('<script src="/assets/find-your-fit-ui.js"></script>', html)

    def test_dedicated_finder_is_a_five_question_data_driven_flow(self) -> None:
        html = build_unified_app.build_find_your_fit_page(self.destinations)

        self.assertIn("<h1>Find your destination fit</h1>", html)
        self.assertEqual(5, html.count("data-fit-step="))
        self.assertIn('id="fitResults"', html)
        self.assertIn('id="fitOtherResults"', html)
        self.assertNotIn('type="email"', html)

        payload_match = re.search(
            r'<script type="application/json" id="fit-data">(.*?)</script>',
            html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(payload_match)
        payload = json.loads(payload_match.group(1))
        self.assertEqual(len(self.destinations), len(payload["destinations"]))
        self.assertEqual(
            {item["id"] for item in self.destinations},
            {item["id"] for item in payload["destinations"]},
        )

    def test_finder_is_a_generated_route_linked_from_the_homepage_and_navigation(self) -> None:
        build_unified_app.build()
        root = build_unified_app.ARTIFACTS
        finder = root / "find-your-fit" / "index.html"
        homepage = (root / "index.html").read_text(encoding="utf-8")
        sitemap = (root / "sitemap.xml").read_text(encoding="utf-8")

        self.assertTrue(finder.exists())
        self.assertIn('href="/find-your-fit/?goal=', homepage)
        self.assertIn("https://globalhomeatlas.com/find-your-fit/", sitemap)
        self.assertNotIn(("/find-your-fit/", "Find your fit"), build_unified_app.PRIMARY_NAV_LINKS)
        self.assertEqual(("/dashboard/", "Destination Rankings"), build_unified_app.PRIMARY_NAV_LINKS[0])

    def test_finder_universe_expands_when_a_destination_is_added(self) -> None:
        future = dict(self.destinations[0])
        future.update({"id": "future-market", "name": "Future Market"})
        html = build_unified_app.build_find_your_fit_page([*self.destinations, future])
        payload_match = re.search(
            r'<script type="application/json" id="fit-data">(.*?)</script>',
            html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(payload_match)
        payload = json.loads(payload_match.group(1))

        self.assertEqual(len(self.destinations) + 1, payload["universeCount"])
        self.assertIn("future-market", {item["id"] for item in payload["destinations"]})

    def test_homepage_goal_matches_are_ranked_from_new_destinations(self) -> None:
        future = dict(self.destinations[0])
        future.update(
            {
                "id": "future-market",
                "name": "Future Market",
                "decision_score": 5.0,
                "access_status": "available",
                "decision_dimensions": [
                    {"key": key, "score": 5.0}
                    for key in {
                        dimension
                        for weights in build_unified_app.GOAL_DIMENSION_WEIGHTS.values()
                        for dimension in weights
                    }
                ],
            }
        )

        homepage_matches = json.loads(
            build_unified_app.build_market_finder_data([*self.destinations, future])
        )

        self.assertEqual(
            {"retirement", "second-home", "investment", "ownership"},
            set(homepage_matches),
        )
        for goal, matches in homepage_matches.items():
            with self.subTest(goal=goal):
                self.assertEqual(3, len(matches))
                self.assertIn("Future Market", {item["name"] for item in matches})

    def test_homepage_match_signal_remains_a_complete_phrase(self) -> None:
        homepage_matches = json.loads(
            build_unified_app.build_market_finder_data(self.destinations)
        )

        retirement_match = homepage_matches["retirement"][0]
        self.assertEqual(
            "Strong retirement and long-stay fit",
            retirement_match["reasonBullets"][0],
        )


if __name__ == "__main__":
    unittest.main()
