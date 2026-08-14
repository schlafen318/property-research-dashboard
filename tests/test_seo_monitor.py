from __future__ import annotations

import unittest
from datetime import date

from scripts import seo_monitor


class SearchConsoleCompletenessTests(unittest.TestCase):
    def test_full_result_page_is_not_complete(self) -> None:
        self.assertFalse(seo_monitor.result_set_complete([{}] * 25, 25))

    def test_short_result_page_is_complete(self) -> None:
        self.assertTrue(seo_monitor.result_set_complete([{}] * 24, 25))

    def test_reconciliation_limit_uses_search_console_maximum(self) -> None:
        args = seo_monitor.parse_args([])
        self.assertEqual(25, args.row_limit)
        self.assertEqual(25000, args.reconciliation_row_limit)


class IndexingEvidenceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.today = date(2026, 8, 14)
        self.goal = {
            "launch_date": "2026-06-23",
            "indexed_deadline": "2026-06-30",
        }

    def test_impressions_override_failed_inspection(self) -> None:
        self.assertEqual(
            ("met", "search_console_impressions"),
            seo_monitor.indexing_status_and_evidence(
                self.today,
                self.goal,
                {"ok": False, "error": "timeout"},
                {"impressions": 27},
            ),
        )

    def test_impressions_override_successful_non_pass_inspection(self) -> None:
        self.assertEqual(
            ("met", "search_console_impressions"),
            seo_monitor.indexing_status_and_evidence(
                self.today,
                self.goal,
                {"ok": True, "verdict": "FAIL"},
                {"impressions": 1},
            ),
        )

    def test_unavailable_inspection_without_impressions_is_unknown(self) -> None:
        for inspection in ({}, {"ok": False, "error": "timeout"}):
            with self.subTest(inspection=inspection):
                self.assertEqual(
                    ("unknown", "inspection_unavailable"),
                    seo_monitor.indexing_status_and_evidence(
                        self.today,
                        self.goal,
                        inspection,
                        {"impressions": 0},
                    ),
                )

    def test_successful_non_pass_inspection_still_uses_deadline(self) -> None:
        self.assertEqual(
            ("missed", "url_inspection_not_passed"),
            seo_monitor.indexing_status_and_evidence(
                self.today,
                self.goal,
                {"ok": True, "verdict": "FAIL"},
                {"impressions": 0},
            ),
        )

    def test_goal_scorecard_exposes_indexing_evidence(self) -> None:
        tracked = seo_monitor.TRACKED_SEO_GOALS[0]
        scorecard = seo_monitor.build_goal_scorecard(
            self.today,
            [{"url": tracked["url"], "ok": False, "error": "timeout"}],
            {tracked["url"]: {"page": tracked["url"], "impressions": 3}},
        )
        first = scorecard["page_goals"][0]
        self.assertEqual("met", first["index_status"])
        self.assertEqual("search_console_impressions", first["index_evidence"])


if __name__ == "__main__":
    unittest.main()
