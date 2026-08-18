from __future__ import annotations

import json
import unittest
from pathlib import Path

from src import build_unified_app


ROOT = Path(__file__).resolve().parents[1]


class GatewayCityDestinationTests(unittest.TestCase):
    def test_gateway_city_profiles_are_complete_and_access_is_explicit(self) -> None:
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
        by_id = {item["id"]: item for item in destinations}

        self.assertEqual(len(destinations), 37)
        expected_access = {
            "miami-fort-lauderdale": "available",
            "los-angeles-orange-county": "available",
            "dubai": "available",
            "vancouver": "restricted",
            "sydney-melbourne": "restricted",
        }
        for destination_id, access_status in expected_access.items():
            with self.subTest(destination_id=destination_id):
                destination = by_id[destination_id]
                self.assertEqual(len(destination["scores"]), 14)
                self.assertEqual(destination["access_status"], access_status)
                self.assertTrue(destination["access_summary"])

    def test_restricted_destinations_are_excluded_from_best_fit_results(self) -> None:
        restricted_valencia = {
            "id": "valencia",
            "name": "Valencia",
            "country": "Spain",
            "access_status": "restricted",
            "decision_score": 4.1,
            "red_flags": "Foreign-buyer access is restricted.",
        }

        finder_data = build_unified_app.build_market_finder_data([restricted_valencia])

        self.assertNotIn("Valencia", finder_data)

    def test_restricted_profile_notice_uses_plain_language(self) -> None:
        destination = {
            "access_status": "restricted",
            "access_summary": "Established homes are generally unavailable to foreign buyers through June 2029.",
        }

        notice = build_unified_app.destination_access_notice_html(destination)

        self.assertIn("Foreign-buyer access restricted", notice)
        self.assertIn("Established homes are generally unavailable", notice)

    def test_generated_ranks_follow_decision_scores_not_stale_data_ranks(self) -> None:
        destinations = [
            {"name": "Lower score", "decision_score": 3.1, "rank": 1},
            {"name": "Higher score", "decision_score": 4.2, "rank": 99},
        ]

        ranked = build_unified_app.rank_destinations(destinations)

        self.assertEqual([(item["name"], item["rank"]) for item in ranked], [("Higher score", 1), ("Lower score", 2)])


if __name__ == "__main__":
    unittest.main()
