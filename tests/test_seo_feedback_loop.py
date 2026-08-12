from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts import seo_feedback_loop


class NotificationCommentTests(unittest.TestCase):
    def editorial_pair(
        self,
        *,
        impressions: int,
        position: float,
        target: str,
        suffix: str,
        auto_implementation_safe: bool = False,
    ):
        finding = seo_feedback_loop.Finding(
            kind="low-ctr-opportunity",
            title=f"Improve CTR for {target}",
            summary="Page has weak CTR.",
            severity="medium",
            labels=("analytics-loop", "needs-human-review"),
            fingerprint=f"gha-low-ctr-opportunity-{suffix}",
            implementation_pr=True,
            auto_implementation_safe=auto_implementation_safe,
            payload={"page": target, "impressions": impressions, "position": position},
        )
        return finding, f"https://github.com/schlafen318/property-research-dashboard/issues/{impressions}"

    def test_select_generated_content_candidates_prioritizes_and_caps_five(self) -> None:
        pairs = [
            self.editorial_pair(impressions=value, position=position, target=f"https://globalhomeatlas.com/p{index}/", suffix=str(index))
            for index, (value, position) in enumerate([(10, 8), (80, 12), (30, 5), (60, 9), (50, 7), (40, 6)])
        ]
        selected = seo_feedback_loop.select_generated_content_candidates(
            pairs,
            issues=[],
            open_targets=set(),
            override_entries=[],
            now=datetime(2026, 8, 12, tzinfo=timezone.utc),
            limit=5,
        )
        self.assertEqual(5, len(selected))
        self.assertEqual(80, selected[0][0].payload["impressions"])

    def test_selection_skips_auto_open_implemented_and_cooldown_targets(self) -> None:
        eligible = self.editorial_pair(impressions=25, position=8, target="https://globalhomeatlas.com/eligible/", suffix="eligible")
        auto_link = self.editorial_pair(impressions=60, position=6, target="https://globalhomeatlas.com/auto/", suffix="auto", auto_implementation_safe=True)
        open_pr = self.editorial_pair(impressions=55, position=6, target="https://globalhomeatlas.com/open/", suffix="open")
        implemented = self.editorial_pair(impressions=50, position=6, target="https://globalhomeatlas.com/implemented/", suffix="implemented")
        cooldown = self.editorial_pair(impressions=45, position=6, target="https://globalhomeatlas.com/cooldown/", suffix="cooldown")
        issues = [{
            "body": f"Fingerprint `{implemented[0].fingerprint}`",
            "labels": [{"name": "implemented-awaiting-google"}],
        }]
        selected = seo_feedback_loop.select_generated_content_candidates(
            [eligible, auto_link, open_pr, implemented, cooldown],
            issues=issues,
            open_targets={"https://globalhomeatlas.com/open/"},
            override_entries=[{
                "target_url": "https://globalhomeatlas.com/cooldown/",
                "cooldown_until": "2026-09-01T00:00:00+00:00",
            }],
            now=datetime(2026, 8, 12, tzinfo=timezone.utc),
            limit=5,
        )
        self.assertEqual([eligible], selected)

    def test_generated_content_pr_is_draft_and_never_auto_merge_safe(self) -> None:
        args = seo_feedback_loop.generated_content_pr_create_args(
            branch="analytics/generated-content-2-abc123",
            base="main",
            title="Generate SEO content for 2 pages",
            body="body",
        )
        self.assertIn("--draft", args)
        labels = args[args.index("--label") + 1]
        self.assertIn("generated-content", labels)
        self.assertIn("needs-human-review", labels)
        self.assertNotIn("auto-merge-safe", labels)

    def test_generated_content_dry_run_returns_one_stable_batch_pr(self) -> None:
        pairs = [
            self.editorial_pair(impressions=40, position=8, target="https://globalhomeatlas.com/a/", suffix="a"),
            self.editorial_pair(impressions=30, position=9, target="https://globalhomeatlas.com/b/", suffix="b"),
        ]
        result = seo_feedback_loop.scaffold_generated_content_pr(
            pairs,
            sitemap_urls=[pair[0].payload["page"] for pair in pairs],
            dry_run=True,
        )
        self.assertTrue(result.pr_url.startswith("dry-run:generated-content-pr:analytics/generated-content-2-"))
        self.assertEqual(0, result.accepted_count)

    def test_reconcile_merged_generated_pr_marks_source_issue_once(self) -> None:
        issue = {
            "number": 95,
            "body": "Fingerprint `gha-low-ctr-opportunity-portugal`",
            "labels": [{"name": "implementation-queued"}],
        }
        prs = [{
            "body": "### https://globalhomeatlas.com/countries/portugal-property/\n- Fingerprint: `gha-low-ctr-opportunity-portugal`",
        }]
        calls = []
        original = seo_feedback_loop.gh_mutation
        seo_feedback_loop.gh_mutation = lambda cmd, attempts=3: calls.append(cmd)
        try:
            count = seo_feedback_loop.reconcile_merged_generated_content_prs(issues=[issue], prs=prs, dry_run=False)
            issue["labels"] = [{"name": "implemented-awaiting-google"}]
            second = seo_feedback_loop.reconcile_merged_generated_content_prs(issues=[issue], prs=prs, dry_run=False)
        finally:
            seo_feedback_loop.gh_mutation = original
        self.assertEqual(1, count)
        self.assertEqual(0, second)
        self.assertEqual(1, len(calls))
        self.assertIn("implemented-awaiting-google", calls[0])
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
        self.assertFalse(finding.auto_implementation_safe)

    def test_classify_marks_near_ranking_internal_link_as_auto_safe(self) -> None:
        report = {
            "site_url": "https://globalhomeatlas.com",
            "sitemap": {"urls": ["https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/"]},
            "search_console": {
                "available": True,
                "top_queries": [],
                "top_pages": [],
                "low_ctr_pages": [],
                "near_ranking_pages": [
                    {
                        "page": "https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/",
                        "clicks": 0,
                        "impressions": 36,
                        "ctr": 0,
                        "position": 10.4,
                    }
                ],
                "content_gap_queries": [],
            },
        }

        findings = seo_feedback_loop.classify(report, tracking_ok=True)
        near_ranking = [finding for finding in findings if finding.kind == "near-ranking-opportunity"]

        self.assertEqual(1, len(near_ranking))
        finding = near_ranking[0]
        self.assertTrue(finding.implementation_pr)
        self.assertTrue(finding.auto_implementation_safe)
        self.assertTrue(finding.auto_merge_safe)
        self.assertIn("auto-merge-safe", finding.labels)
        self.assertEqual("internal-link", finding.payload["auto_implementation"]["type"])

    def test_classify_keeps_non_guide_near_ranking_pages_in_human_review(self) -> None:
        report = {
            "site_url": "https://globalhomeatlas.com",
            "sitemap": {"urls": ["https://globalhomeatlas.com/guides/"]},
            "search_console": {
                "available": True,
                "top_queries": [],
                "top_pages": [],
                "low_ctr_pages": [],
                "near_ranking_pages": [
                    {
                        "page": "https://globalhomeatlas.com/guides/",
                        "clicks": 0,
                        "impressions": 36,
                        "ctr": 0,
                        "position": 10.4,
                    }
                ],
                "content_gap_queries": [],
            },
        }

        findings = seo_feedback_loop.classify(report, tracking_ok=True)
        finding = [item for item in findings if item.kind == "near-ranking-opportunity"][0]

        self.assertFalse(finding.auto_implementation_safe)
        self.assertFalse(finding.auto_merge_safe)
        self.assertIn("needs-human-review", finding.labels)

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

    def test_implemented_awaiting_google_issue_skips_implementation_queue(self) -> None:
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
        issues = [
            {
                "body": "Fingerprint\n`gha-query-ctr-opportunity-c6417e4c5792`",
                "labels": [{"name": "implemented-awaiting-google"}],
            }
        ]

        self.assertTrue(seo_feedback_loop.implemented_awaiting_google(finding, issues))

    def test_create_or_update_issue_retries_transient_github_failure(self) -> None:
        finding = seo_feedback_loop.Finding(
            kind="seo-goal-missed",
            title="Missed guide hub goal",
            summary="Guide hub missed first impressions goal.",
            severity="high",
            labels=("analytics-loop", "needs-human-review"),
            fingerprint="gha-seo-goal-missed-abc123",
        )
        issues = [
            {
                "number": 38,
                "url": "https://github.com/schlafen318/property-research-dashboard/issues/38",
                "body": "Fingerprint `gha-seo-goal-missed-abc123`",
                "labels": [],
            }
        ]
        calls = []
        original_run = seo_feedback_loop.run

        def flaky_run(cmd: list[str], *args, **kwargs):
            calls.append(cmd)
            if len(calls) == 1:
                return subprocess.CompletedProcess(cmd, 1, "", "504 Gateway Timeout")
            return subprocess.CompletedProcess(cmd, 0, "", "")

        seo_feedback_loop.run = flaky_run
        try:
            result = seo_feedback_loop.create_or_update_issue(finding, issues, dry_run=False)
        finally:
            seo_feedback_loop.run = original_run

        self.assertEqual("https://github.com/schlafen318/property-research-dashboard/issues/38", result)
        self.assertEqual(2, len(calls))

    def test_scaffold_auto_internal_link_pr_dry_run_returns_auto_merge_branch(self) -> None:
        finding = seo_feedback_loop.Finding(
            kind="near-ranking-opportunity",
            title="Push near-ranking page higher: /best-places-to-buy-vacation-home-abroad/",
            summary="Page is ranking near page one.",
            severity="medium",
            labels=("analytics-loop", "auto-merge-safe"),
            fingerprint="gha-near-ranking-opportunity-91918964e43f",
            auto_merge_safe=True,
            implementation_pr=True,
            auto_implementation_safe=True,
            payload={
                "page": "https://globalhomeatlas.com/best-places-to-buy-vacation-home-abroad/",
                "auto_implementation": {
                    "type": "internal-link",
                    "source_slug": "buy-property-abroad",
                    "target_slug": "best-places-to-buy-vacation-home-abroad",
                    "anchor": "best places to buy vacation home abroad",
                    "fingerprint": "gha-near-ranking-opportunity-91918964e43f",
                    "reason": "Page is ranking near page one.",
                },
            },
        )

        result = seo_feedback_loop.scaffold_auto_internal_link_pr(
            finding,
            issue_url="https://github.com/schlafen318/property-research-dashboard/issues/99",
            dry_run=True,
        )

        self.assertEqual(
            "dry-run:auto-implementation-pr:analytics/auto-internal-link-best-places-to-buy-vacation-home-abroad-91918964e43f",
            result,
        )

    def test_scaffold_auto_internal_links_pr_dry_run_batches_multiple_findings(self) -> None:
        findings = [
            seo_feedback_loop.Finding(
                kind="near-ranking-opportunity",
                title="Push near-ranking page higher: /best-places-to-buy-a-second-home-abroad/",
                summary="Second-home page is near-ranking.",
                severity="medium",
                labels=("analytics-loop", "auto-merge-safe"),
                fingerprint="gha-near-ranking-opportunity-28da3b13e19f",
                auto_merge_safe=True,
                implementation_pr=True,
                auto_implementation_safe=True,
                payload={
                    "auto_implementation": {
                        "type": "internal-link",
                        "source_slug": "buy-property-abroad",
                        "target_slug": "best-places-to-buy-a-second-home-abroad",
                        "fingerprint": "gha-near-ranking-opportunity-28da3b13e19f",
                    }
                },
            ),
            seo_feedback_loop.Finding(
                kind="near-ranking-opportunity",
                title="Push near-ranking page higher: /best-places-to-buy-vacation-home-abroad/",
                summary="Vacation-home page is near-ranking.",
                severity="medium",
                labels=("analytics-loop", "auto-merge-safe"),
                fingerprint="gha-near-ranking-opportunity-91918964e43f",
                auto_merge_safe=True,
                implementation_pr=True,
                auto_implementation_safe=True,
                payload={
                    "auto_implementation": {
                        "type": "internal-link",
                        "source_slug": "buy-property-abroad",
                        "target_slug": "best-places-to-buy-vacation-home-abroad",
                        "fingerprint": "gha-near-ranking-opportunity-91918964e43f",
                    }
                },
            ),
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            result = seo_feedback_loop.scaffold_auto_internal_links_pr(
                [(findings[0], "https://github.com/schlafen318/property-research-dashboard/issues/1"), (findings[1], None)],
                dry_run=True,
                path=Path(tmpdir) / "seo_auto_internal_links.json",
            )

        self.assertEqual(
            "dry-run:auto-implementation-pr:analytics/auto-internal-links-2-8ff9a393e8de",
            result,
        )

    def test_upsert_auto_internal_link_entry_dedupes_by_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "seo_auto_internal_links.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "type": "internal-link",
                            "source_slug": "buy-property-abroad",
                            "target_slug": "best-places-to-buy-vacation-home-abroad",
                            "anchor": "old anchor",
                            "fingerprint": "gha-near-ranking-opportunity-91918964e43f",
                        }
                    ]
                ),
                encoding="utf-8",
            )

            seo_feedback_loop.upsert_auto_internal_link_entry(
                {
                    "type": "internal-link",
                    "source_slug": "buy-property-abroad",
                    "target_slug": "best-places-to-buy-vacation-home-abroad",
                    "anchor": "new anchor",
                    "fingerprint": "gha-near-ranking-opportunity-91918964e43f",
                },
                path=path,
            )

            rows = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(1, len(rows))
            self.assertEqual("new anchor", rows[0]["anchor"])

    def test_maybe_auto_merge_returns_none_when_github_refuses_merge(self) -> None:
        calls = []
        original_run = seo_feedback_loop.run

        class FailedCommand:
            returncode = 1

        def fake_run(cmd, *, check=True, capture=True):
            calls.append(cmd)
            return FailedCommand()

        try:
            seo_feedback_loop.run = fake_run
            result = seo_feedback_loop.maybe_auto_merge(
                "https://github.com/schlafen318/property-research-dashboard/pull/100",
                seo_feedback_loop.Finding(
                    kind="near-ranking-opportunity",
                    title="Push near-ranking page higher",
                    summary="Internal link only.",
                    severity="medium",
                    labels=("auto-merge-safe",),
                    fingerprint="gha-near-ranking-opportunity-abc123",
                    auto_merge_safe=True,
                ),
                dry_run=False,
            )
        finally:
            seo_feedback_loop.run = original_run

        self.assertIsNone(result)
        self.assertEqual(1, len(calls))

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
