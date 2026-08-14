# Stale SEO Opportunity Reconciliation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reconcile stale Search Console opportunity issues after two consecutive healthy reports and reopen automatically closed issues when their fingerprint returns.

**Architecture:** Add a comprehensive Search Console reconciliation dataset with explicit completeness per query/page dimension, then place a pure-selection layer around existing issue snapshots plus a mutation orchestrator that uses the established retrying GitHub boundary. Run it before current findings are updated and expose marked/closed/reopened counts and per-issue errors in the feedback summary.

**Tech Stack:** Python 3.11, `unittest`, GitHub CLI, GitHub Actions

## Global Constraints

- Reconcile only `query-ctr-opportunity`, `low-ctr-opportunity`, `near-ranking-opportunity`, and `new-query-content-gap`.
- Never reconcile `implemented-awaiting-google`, indexing, sitemap, tracking, goal, or control-center issues.
- First consecutive absence adds `stale-signal`; second consecutive absence closes as not planned and retains the label.
- A returning fingerprint removes `stale-signal`; an automatically closed returning issue is reopened.
- Search Console unavailable means no reconciliation mutations.
- All GitHub writes use the existing retrying `gh_mutation` boundary.
- Only complete 25,000-row reconciliation result sets may prove absence; the 25-row display lists never do.
- Reopening requires the dedicated `stale-signal-auto-closed` provenance label and `analytics-loop` ownership.
- Mutation failures are isolated per issue and reported without erasing successful counts.

---

### Task 1: Add the stale-opportunity lifecycle

**Files:**
- Modify: `scripts/seo_feedback_loop.py`
- Modify: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: comprehensive `findings: list[Finding]`, `issues: list[dict]`, `complete_kinds: set[str]`, and `dry_run: bool`.
- Produces: `reconcile_stale_opportunity_issues(...)` with `marked`, `closed`, and `reopened` counts plus per-issue `errors`.

- [ ] **Step 1: Write failing lifecycle tests**

Create real `Finding` values and literal GitHub issue snapshots. Patch only `gh_mutation`. Assert a first absent run emits `issue edit --add-label stale-signal`, a second absent run emits `issue close --reason 'not planned'`, a returning open issue removes the label, and a returning closed issue reopens before removing the label.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_stale_opportunity_first_absence_marks_without_closing tests.test_seo_feedback_loop.NotificationCommentTests.test_stale_opportunity_second_absence_closes tests.test_seo_feedback_loop.NotificationCommentTests.test_returning_stale_opportunity_reopens -v`

Expected: FAIL because `reconcile_stale_opportunity_issues` does not exist.

- [ ] **Step 3: Implement the minimal lifecycle function**

Add `stale-signal` to `LABELS`, parse the exact `Kind` and `Fingerprint` fields from machine-generated issue bodies, restrict reconciliation to the four managed kinds, skip protected labels and the control issue, and route mutations through `gh_mutation`.

- [ ] **Step 4: Add safety tests**

Assert unavailable Search Console, `implemented-awaiting-google`, and non-managed kinds produce zero counts and no GitHub calls. Assert manually closed issues without `stale-signal` stay closed.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_seo_feedback_loop -v`

Expected: all feedback-loop tests pass.

- [ ] **Step 6: Commit the lifecycle**

Stage `scripts/seo_feedback_loop.py` and `tests/test_seo_feedback_loop.py`, then commit `Reconcile stale SEO opportunity issues`.

### Task 2: Integrate lifecycle reporting

**Files:**
- Modify: `scripts/seo_feedback_loop.py`
- Modify: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: the Task 1 lifecycle counts.
- Produces: summary JSON field `stale_issue_reconciliation` and control/notification text showing marked, closed, and reopened counts.

- [ ] **Step 1: Write failing integration tests**

Assert `main()` calls reconciliation only with `search_console.available == true`, preserves zero counts when unavailable or reconciliation raises, and writes literal `stale_issue_reconciliation` counts into the JSON summary and control issue body.

- [ ] **Step 2: Run integration tests and verify RED**

Run: `python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_control_issue_reports_stale_reconciliation tests.test_seo_feedback_loop.NotificationCommentTests.test_main_skips_stale_reconciliation_without_search_console -v`

Expected: FAIL because the run summary does not expose lifecycle counts.

- [ ] **Step 3: Integrate before current issue updates**

Call the lifecycle after issue listing and before `create_or_update_issue`. Catch reconciliation exceptions, preserve zero counts, and expose the error as a skipped reason without suppressing the remainder of the SEO run.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_seo_feedback_loop -v`

Expected: all feedback-loop tests pass.

- [ ] **Step 5: Commit integration**

Stage `scripts/seo_feedback_loop.py` and `tests/test_seo_feedback_loop.py`, then commit `Report stale SEO issue reconciliation`.

### Task 3: Verify and publish

**Files:**
- Verify all files changed in Tasks 1 and 2.

**Interfaces:**
- Consumes: the complete lifecycle integration.
- Produces: reviewed, merged automation and evidence from a real dry run or scheduled run.

- [ ] **Step 1: Run full verification**

Run:

```bash
python3 -m unittest discover tests -v
python3 -m py_compile scripts/seo_feedback_loop.py
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
git diff --check
```

Expected: all tests, 65 sitemap URLs, 65 tracked pages, and 21 expected events pass.

- [ ] **Step 2: Independently review the branch**

Review `origin/main..HEAD` for premature issue closure, mutation ordering, accidental reconciliation of protected issue kinds, failure handling, summary accuracy, and GitHub CLI correctness. Resolve every Critical or Important finding.

- [ ] **Step 3: Publish and merge**

Push `codex/reconcile-stale-seo-issues`, open a ready pull request against `main`, and squash-merge after checks and review pass.

- [ ] **Step 4: Verify production behavior**

Run the SEO feedback workflow once after merge. Confirm first-absence opportunities receive `stale-signal`, protected issues are unchanged, the summary counts match actual mutations, and no content-generation PR is created from stale Queenstown data.
