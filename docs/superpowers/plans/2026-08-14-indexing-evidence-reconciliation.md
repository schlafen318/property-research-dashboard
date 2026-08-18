# Indexing Evidence Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use Search Console impressions as valid indexing evidence and automatically reconcile automation-owned goal issues when their status becomes met, unknown, or actionable again.

**Architecture:** Extend the SEO monitor's goal scorecard with a deterministic indexing-status/evidence decision that combines URL Inspection and page performance. Add a separate feedback-loop reconciler that maps machine-owned goal issues to scorecard fields, applies provenance-safe close/reopen transitions, isolates GitHub failures per issue, and reports truthful counts.

**Tech Stack:** Python 3.11, `unittest`, GitHub CLI, GitHub Actions

## Global Constraints

- Positive Search Console page impressions always satisfy the indexing goal.
- Failed or missing URL Inspection evidence with zero impressions is `unknown`, never `at_risk` or `missed`.
- A successful non-`PASS` inspection continues to use the existing calendar thresholds.
- Reconcile only `analytics-loop` issues with kind `seo-goal-at-risk` or `seo-goal-missed`.
- Reopen only issues carrying `goal-status-auto-closed` provenance.
- Isolate mutations per issue and preserve truthful partial counts and errors.
- Keep report markup minimal and text-only.

---

### Task 1: Combine indexing evidence in the scorecard

**Files:**
- Modify: `scripts/seo_monitor.py:356-410`
- Test: `tests/test_seo_monitor.py`

**Interfaces:**
- Consumes: `today: date`, goal deadline fields, an inspection dictionary, and an analytics dictionary.
- Produces: `indexing_status_and_evidence(today, goal, inspection, analytics) -> tuple[str, str]` and scorecard fields `index_status` and `index_evidence`.

- [ ] **Step 1: Write failing status tests**

Add literal cases that expect:

```python
self.assertEqual(
    ("met", "search_console_impressions"),
    seo_monitor.indexing_status_and_evidence(today, goal, {"ok": False, "error": "timeout"}, {"impressions": 27}),
)
self.assertEqual(
    ("unknown", "inspection_unavailable"),
    seo_monitor.indexing_status_and_evidence(today, goal, {"ok": False, "error": "timeout"}, {"impressions": 0}),
)
self.assertEqual(
    ("missed", "url_inspection_not_passed"),
    seo_monitor.indexing_status_and_evidence(today, goal, {"ok": True, "verdict": "FAIL"}, {"impressions": 0}),
)
```

Also assert that `build_goal_scorecard` exposes both literal fields for a tracked page.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_seo_monitor -v`

Expected: FAIL because `indexing_status_and_evidence` and `index_evidence` do not exist.

- [ ] **Step 3: Implement the decision function**

Implement the four ordered evidence rules from the design and call the function once per page goal in `build_goal_scorecard`.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python3 -m unittest tests.test_seo_monitor -v`

Expected: all monitor tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/seo_monitor.py tests/test_seo_monitor.py
git commit -m "Use performance data as indexing evidence"
```

### Task 2: Reconcile goal issue lifecycle

**Files:**
- Modify: `scripts/seo_feedback_loop.py:40-60,740-900,1750-1790`
- Test: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: `report: dict`, current `findings: list[Finding]`, GitHub `issues: list[dict]`, and `dry_run: bool`.
- Produces: `reconcile_goal_issues(report, findings, issues, dry_run) -> dict` with integer `closed`, integer `reopened`, and list `errors`.

- [ ] **Step 1: Write failing lifecycle tests**

Create complete literal issue snapshots with `analytics-loop`, machine `Kind` and `Fingerprint`, and titles containing the goal field and target URL. Assert:

```python
result = seo_feedback_loop.reconcile_goal_issues(report, findings=[], issues=[open_issue], dry_run=False)
self.assertEqual({"closed": 1, "reopened": 0, "errors": []}, result)
self.assertEqual(["gh", "issue", "edit", "107", "--add-label", "goal-status-auto-closed"], calls[0])
self.assertEqual("close", calls[1][2])
```

Add separate cases for `unknown` closing as not planned, actionable recurrence reopening only with provenance, a human-closed issue staying closed, close rollback, and one failed issue not blocking the next.

- [ ] **Step 2: Run tests and verify RED**

Run: `python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests -v`

Expected: FAIL because `reconcile_goal_issues` does not exist.

- [ ] **Step 3: Implement goal parsing and reconciliation**

Add `goal-status-auto-closed` to `LABELS`. Parse the goal field from the title prefix and the URL after ` for `. Build a scorecard lookup keyed by `(field, url)`. Apply close/reopen transitions only to owned goal issues, route writes through `gh_mutation`, roll back provenance on close failure, and continue after per-issue errors.

- [ ] **Step 4: Integrate before issue updates**

Call reconciliation after `list_issues()` and before `create_or_update_issue()`. Extract counts from the result without discarding partial successes. An unexpected top-level exception records an error and leaves the rest of the feedback loop running.

- [ ] **Step 5: Run tests and verify GREEN**

Run: `python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests -v`

Expected: all feedback-loop tests pass.

- [ ] **Step 6: Commit**

```bash
git add scripts/seo_feedback_loop.py tests/test_seo_feedback_loop.py
git commit -m "Reconcile resolved SEO goal issues"
```

### Task 3: Report and verify the lifecycle

**Files:**
- Modify: `scripts/seo_feedback_loop.py:520-675,1000-1080,1790-1860`
- Modify: `docs/superpowers/specs/2026-08-14-indexing-evidence-reconciliation-design.md`
- Test: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: `goal_issue_reconciliation` counts and errors from Task 2.
- Produces: summary JSON field `goal_issue_reconciliation` and concise control/notification text.

- [ ] **Step 1: Write failing reporting tests**

Assert the control body and notification contain literal closed/reopened counts, and assert `main()` writes:

```python
{"closed": 2, "reopened": 1}
```

while preserving a non-empty error string returned from a partial failure.

- [ ] **Step 2: Run tests and verify RED**

Run the new reporting tests by exact unittest names and confirm missing output fields cause the failure.

- [ ] **Step 3: Add minimal reporting**

Add one plain-text `Goal Issue Reconciliation` section to the control issue, two count lines to the notification, and the count/error fields to the JSON summary. Avoid badges, duplicated detail lists, or dashboard-only decoration.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_seo_feedback_loop tests.test_seo_monitor -v`

Expected: all focused tests pass.

- [ ] **Step 5: Run complete verification**

```bash
python3 -m unittest discover tests -v
python3 -m py_compile scripts/seo_monitor.py scripts/seo_feedback_loop.py
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
git diff --check
```

Expected: all tests pass, static verification reports at least 65 sitemap URLs, tracking reports 65 pages and 21 expected events, and the diff check is clean.

- [ ] **Step 6: Run a real-report dry run**

Use the latest successful workflow artifact with `--dry-run`. Confirm issue #107 is counted as a close, genuine conclusive failures remain findings, no GitHub mutations occur, and no content-generation PR is created.

- [ ] **Step 7: Commit**

```bash
git add scripts/seo_feedback_loop.py tests/test_seo_feedback_loop.py docs/superpowers/specs/2026-08-14-indexing-evidence-reconciliation-design.md
git commit -m "Report goal issue reconciliation"
```

- [ ] **Step 8: Review and publish**

Request an independent review of `origin/main..HEAD`, resolve every Critical or Important finding, push `codex/reconcile-indexing-evidence`, open a ready pull request, merge after verification, then run the production workflow once and confirm the receipt and actual issue state agree.
