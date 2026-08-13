from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import seo_email_notification


class SeoEmailNotificationTests(unittest.TestCase):
    def test_build_email_body_summarizes_run_and_feedback_actions(self) -> None:
        report = {
            "generated_at": "2026-07-25T01:25:00Z",
            "window": {"start_date": "2026-07-22", "end_date": "2026-07-24"},
            "sitemap": {
                "url_count": 65,
                "status": {"isPending": False, "warnings": 0, "errors": 0},
                "indexing": {"submitted_reported": 65, "indexed_reported": 12},
            },
            "search_console": {
                "top_queries": [{"query": "buy property abroad"}],
                "top_pages": [{"page": "https://globalhomeatlas.com/guides/"}],
                "low_ctr_pages": [],
                "near_ranking_pages": [{}],
                "content_gap_queries": [{}],
            },
        }
        indexnow = {"url_count": 65, "response": {"ok": True, "status": 200}}
        summary = {
            "findings": [
                {"kind": "priority-page-not-indexed", "severity": "medium"},
                {"kind": "seo-goal-missed", "severity": "high"},
            ],
            "issue_count": 2,
            "pr_count": 1,
            "auto_merged_count": 0,
            "generated_content": {
                "accepted_count": 2,
                "rejected": [{"reason": "stale hash"}],
                "skipped_reason": None,
                "pr": "https://github.com/example/pull/101",
            },
        }

        body = seo_email_notification.build_email_body(
            report=report,
            indexnow=indexnow,
            summary=summary,
            control_url="https://github.com/example/issues/1",
            dashboard_url="https://globalhomeatlas.com/seo-status/",
        )

        self.assertIn("Generated: 2026-07-25T01:25:00Z", body)
        self.assertIn("Search Console window: 2026-07-22 to 2026-07-24", body)
        self.assertIn("Sitemap URLs: 65", body)
        self.assertIn("High severity: 1", body)
        self.assertIn("Medium severity: 1", body)
        self.assertIn("Issues created or updated: 2", body)
        self.assertIn("Draft PRs opened: 1", body)
        self.assertIn("Generated content accepted: 2", body)
        self.assertIn("stale hash", body)
        self.assertIn("https://github.com/example/pull/101", body)
        self.assertIn("request indexing", body)

    def test_main_skips_cleanly_when_smtp_is_not_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "latest.json"
            summary_path = Path(tmp) / "summary.json"
            indexnow_path = Path(tmp) / "indexnow.json"
            report_path.write_text('{"generated_at":"2026-07-25T01:25:00Z"}', encoding="utf-8")
            summary_path.write_text('{"findings":[]}', encoding="utf-8")
            indexnow_path.write_text("{}", encoding="utf-8")

            with mock.patch.dict(os.environ, {}, clear=True):
                completed = seo_email_notification.main(
                    [
                        "--report",
                        str(report_path),
                        "--feedback-summary",
                        str(summary_path),
                        "--indexnow-report",
                        str(indexnow_path),
                    ]
                )

        self.assertEqual(completed, 0)

    def test_build_telegram_message_summarizes_actions(self) -> None:
        report = {
            "generated_at": "2026-07-25T01:25:00Z",
            "window": {"start_date": "2026-07-22", "end_date": "2026-07-24"},
            "sitemap": {
                "url_count": 65,
                "status": {"warnings": 0, "errors": 0},
                "indexing": {"submitted_reported": 65, "indexed_reported": 12},
            },
        }
        summary = {
            "findings": [{"kind": "query-ctr-opportunity", "severity": "medium"}],
            "issue_count": 1,
            "pr_count": 0,
            "auto_merged_count": 0,
        }

        message = seo_email_notification.build_telegram_message(
            report=report,
            indexnow={"url_count": 65, "response": {"ok": True, "status": 200}},
            summary=summary,
            control_url="https://github.com/example/issues/1",
            dashboard_url="https://globalhomeatlas.com/seo-status/",
        )

        self.assertIn("Global Home Atlas SEO loop finished", message)
        self.assertIn("Findings: 0 high, 1 medium, 0 low", message)
        self.assertIn("Issues updated: 1", message)
        self.assertIn("Review the human-review issues", message)
        self.assertIn("Control: https://github.com/example/issues/1", message)

    def test_main_sends_telegram_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report_path = Path(tmp) / "latest.json"
            summary_path = Path(tmp) / "summary.json"
            indexnow_path = Path(tmp) / "indexnow.json"
            report_path.write_text('{"generated_at":"2026-07-25T01:25:00Z"}', encoding="utf-8")
            summary_path.write_text('{"findings":[]}', encoding="utf-8")
            indexnow_path.write_text("{}", encoding="utf-8")

            env = {
                "SEO_NOTIFY_TELEGRAM_BOT_TOKEN": "token",
                "SEO_NOTIFY_TELEGRAM_CHAT_ID": "123",
            }
            with mock.patch.dict(os.environ, env, clear=True):
                with mock.patch.object(seo_email_notification, "send_telegram") as send_telegram:
                    completed = seo_email_notification.main(
                        [
                            "--report",
                            str(report_path),
                            "--feedback-summary",
                            str(summary_path),
                            "--indexnow-report",
                            str(indexnow_path),
                        ]
                    )

        self.assertEqual(completed, 0)
        send_telegram.assert_called_once()


if __name__ == "__main__":
    unittest.main()
