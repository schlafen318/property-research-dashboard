from __future__ import annotations

import unittest

from scripts import seo_feedback_loop


class NotificationCommentTests(unittest.TestCase):
    def test_classify_creates_query_ctr_opportunity_for_zero_click_top_query(self) -> None:
        report = {
            "site_url": "https://globalhomeatlas.com",
            "sitemap": {
                "urls": [
                    "https://globalhomeatlas.com/thailand-villa-ownership-foreigners/",
                    "https://globalhomeatlas.com/buy-property-abroad/",
                ],
                "status": {},
                "indexing": {},
            },
            "search_console": {
                "available": True,
                "top_queries": [
                    {
                        "query": "foreign buyer guide thailand villa",
                        "clicks": 0,
                        "impressions": 50,
                        "ctr": 0,
                        "position": 7.4,
                    }
                ],
                "top_pages": [],
                "low_ctr_pages": [],
                "near_ranking_pages": [],
                "content_gap_queries": [],
            },
        }

        findings = seo_feedback_loop.classify(report, tracking_ok=True)
        query_findings = [finding for finding in findings if finding.kind == "query-ctr-opportunity"]

        self.assertEqual(1, len(query_findings))
        finding = query_findings[0]
        self.assertIn("foreign buyer guide thailand villa", finding.title)
        self.assertIn("50 impressions", finding.summary)
        self.assertIn("0 clicks", finding.summary)
        self.assertIn("needs-human-review", finding.labels)
        self.assertEqual(
            "https://globalhomeatlas.com/thailand-villa-ownership-foreigners/",
            finding.payload["recommended_page"],
        )
        self.assertIn("title", finding.payload["recommended_actions"][0].lower())
        self.assertFalse(finding.auto_merge_safe)

    def test_build_notification_comment_mentions_user_and_summarizes_run(self) -> None:
        findings = [
            seo_feedback_loop.Finding(
                kind="low-ctr-opportunity",
                title="Improve CTR for /",
                summary="Homepage has impressions but low CTR.",
                severity="medium",
                labels=("analytics-loop",),
                fingerprint="gha-low-ctr-123",
            ),
            seo_feedback_loop.Finding(
                kind="seo-goal-missed",
                title="Indexing goal missed",
                summary="Guides page missed its indexing goal.",
                severity="high",
                labels=("analytics-loop",),
                fingerprint="gha-goal-456",
            ),
        ]
        report = {
            "generated_at": "2026-07-15T03:56:00Z",
            "window": {"start_date": "2026-07-12", "end_date": "2026-07-14"},
        }

        body = seo_feedback_loop.build_notification_comment(
            notify_user="schlafen318",
            report=report,
            findings=findings,
            issue_links=["https://github.com/schlafen318/property-research-dashboard/issues/18"],
            pr_links=[],
            auto_merged=[],
            control_link="https://github.com/schlafen318/property-research-dashboard/issues/1",
        )

        self.assertIn("@schlafen318", body)
        self.assertIn("2026-07-15T03:56:00Z", body)
        self.assertIn("2026-07-12 to 2026-07-14", body)
        self.assertIn("High severity: `1`", body)
        self.assertIn("Medium severity: `1`", body)
        self.assertIn("Issues created or updated: `1`", body)
        self.assertIn("Control issue", body)

    def test_build_notification_comment_normalizes_at_prefix(self) -> None:
        body = seo_feedback_loop.build_notification_comment(
            notify_user="@schlafen318",
            report={},
            findings=[],
            issue_links=[],
            pr_links=[],
            auto_merged=[],
            control_link="https://github.com/schlafen318/property-research-dashboard/issues/1",
        )

        self.assertTrue(body.startswith("@schlafen318"))
        self.assertNotIn("@@schlafen318", body)


if __name__ == "__main__":
    unittest.main()
