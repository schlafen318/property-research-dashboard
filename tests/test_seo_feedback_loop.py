from __future__ import annotations

import unittest

from scripts import seo_feedback_loop


class NotificationCommentTests(unittest.TestCase):
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
