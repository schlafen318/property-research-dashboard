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
        self.assertTrue(finding.implementation_pr)
        self.assertEqual(
            "https://globalhomeatlas.com/thailand-villa-ownership-foreigners/",
            finding.payload["recommended_page"],
        )
        self.assertIn("title", finding.payload["recommended_actions"][0].lower())
        self.assertFalse(finding.auto_merge_safe)

    def test_build_implementation_candidate_content_links_issue_and_actions(self) -> None:
        finding = seo_feedback_loop.Finding(
            kind="query-ctr-opportunity",
            title="Improve query CTR for `best locations for vacation homes`",
            summary="Query has impressions and weak CTR.",
            severity="medium",
            labels=("analytics-loop", "needs-human-review"),
            fingerprint="gha-query-ctr-opportunity-c6417e4c5792",
            implementation_pr=True,
            payload={
                "query": "best locations for vacation homes",
                "recommended_page": "https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/",
                "recommended_actions": [
                    "Rewrite the title tag.",
                    "Rewrite the meta description.",
                ],
            },
        )

        content = seo_feedback_loop.implementation_candidate_content(
            finding,
            issue_url="https://github.com/schlafen318/property-research-dashboard/issues/45",
        )

        self.assertIn("Implementation Candidate", content)
        self.assertIn("best locations for vacation homes", content)
        self.assertIn("https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/", content)
        self.assertIn("https://github.com/schlafen318/property-research-dashboard/issues/45", content)
        self.assertIn("Rewrite the title tag.", content)
        self.assertIn("Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`", content)
        self.assertIn("gha-query-ctr-opportunity-c6417e4c5792", content)

    def test_scaffold_implementation_pr_dry_run_returns_stable_queue_branch(self) -> None:
        finding = seo_feedback_loop.Finding(
            kind="query-ctr-opportunity",
            title="Improve query CTR for `best locations for vacation homes`",
            summary="Query has impressions and weak CTR.",
            severity="medium",
            labels=("analytics-loop", "needs-human-review"),
            fingerprint="gha-query-ctr-opportunity-c6417e4c5792",
            implementation_pr=True,
            payload={"query": "best locations for vacation homes"},
        )

        result = seo_feedback_loop.scaffold_implementation_pr(
            finding,
            issue_url="https://github.com/schlafen318/property-research-dashboard/issues/45",
            dry_run=True,
        )

        self.assertEqual(
            "dry-run:implementation-pr:analytics/implementation-query-ctr-best-locations-for-vacation-homes-c6417e4c5792",
            result,
        )

    def test_implementation_pr_create_args_pins_repo_base_and_head(self) -> None:
        finding = seo_feedback_loop.Finding(
            kind="query-ctr-opportunity",
            title="Improve query CTR for `best locations for vacation homes`",
            summary="Query has impressions and weak CTR.",
            severity="medium",
            labels=("analytics-loop", "needs-human-review"),
            fingerprint="gha-query-ctr-opportunity-c6417e4c5792",
            implementation_pr=True,
            payload={"query": "best locations for vacation homes"},
        )

        args = seo_feedback_loop.implementation_pr_create_args(
            finding,
            branch="analytics/implementation-query-ctr-best-locations-for-vacation-homes-c6417e4c5792",
            pr_body="body",
            base="main",
        )

        self.assertIn("--repo", args)
        self.assertIn("schlafen318/property-research-dashboard", args)
        self.assertIn("--base", args)
        self.assertIn("main", args)
        self.assertIn("--head", args)
        self.assertIn(
            "analytics/implementation-query-ctr-best-locations-for-vacation-homes-c6417e4c5792",
            args,
        )

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
