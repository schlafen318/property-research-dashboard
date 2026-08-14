# First-Impression Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Route one indexed page with a missed first-impression goal into the existing safe generated-content pipeline per SEO run, beginning with the retirement guide.

**Architecture:** Enrich impression-goal findings with explicit recovery metadata, recognize that metadata through a focused eligibility helper, and let the existing selector prioritize exactly one recovery target. Keep implementation-queue scaffolding restricted to existing CTR/ranking kinds while reusing all generated-content validation, cooldown, PR, and issue-lifecycle behavior.

**Tech Stack:** Python 3.11, `unittest`, GitHub CLI orchestration, existing OpenAI structured-output generator, static HTML renderer.

## Global Constraints

- Recovery requires `kind == "seo-goal-missed"`, `goal_field == "impression_status"`, `recovery_type == "first-impression"`, `index_status == "met"`, and zero impressions.
- Select at most one recovery page per SEO run.
- Prefer guide pages over country hubs; use canonical URL and fingerprint for deterministic ties.
- Do not route recovery findings through implementation-queue scaffolding.
- Preserve open-PR suppression, `implemented-awaiting-google`, and the 28-day cooldown.
- Generated changes remain draft-only and must pass the existing deterministic content validator and site checks.

---

### Task 1: Classify first-impression recovery findings

**Files:**
- Modify: `scripts/seo_feedback_loop.py`
- Test: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: `classify(report: dict, tracking_ok: bool) -> list[Finding]`
- Produces: `is_first_impression_recovery(finding: Finding) -> bool`

- [ ] **Step 1: Write the failing classification tests**

Add tests that build goal records and assert that only an indexed, missed impression goal carries:

```python
{
    "goal_field": "impression_status",
    "recovery_type": "first-impression",
    "page": goal["url"],
    "impressions": 0,
}
```

Assert `implementation_pr is True` for that finding. Assert indexing misses, `at_risk` impression goals, non-indexed pages, and positive-impression pages are not recovery findings.

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_classify_marks_only_indexed_missed_impression_goals_for_recovery
```

Expected: FAIL because recovery metadata and eligibility do not exist.

- [ ] **Step 3: Implement minimal classification and eligibility**

Add:

```python
GENERATED_CONTENT_KINDS = {*IMPLEMENTATION_PR_KINDS, "seo-goal-missed"}

def is_first_impression_recovery(finding: Finding) -> bool:
    payload = finding.payload or {}
    analytics = payload.get("analytics") or {}
    return (
        finding.kind == "seo-goal-missed"
        and payload.get("goal_field") == "impression_status"
        and payload.get("recovery_type") == "first-impression"
        and payload.get("index_status") == "met"
        and int(analytics.get("impressions") or payload.get("impressions") or 0) == 0
    )
```

When classifying a missed `impression_status` goal with `index_status == "met"` and zero impressions, copy the goal payload, add the four recovery fields, and set `implementation_pr=True`. Leave all other goal findings unchanged.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_classify_marks_only_indexed_missed_impression_goals_for_recovery
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/seo_feedback_loop.py tests/test_seo_feedback_loop.py
git commit -m "Classify first-impression recovery candidates"
```

### Task 2: Select one recovery target safely

**Files:**
- Modify: `scripts/seo_feedback_loop.py`
- Test: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: `is_first_impression_recovery(finding: Finding) -> bool`
- Produces: updated `select_generated_content_candidates(...) -> list[tuple[Finding, str | None]]`

- [ ] **Step 1: Write failing selection tests**

Add real `Finding` fixtures for the retirement guide, Japan, Italy, and Thailand. Assert:

```python
selected = select_generated_content_candidates(
    pairs,
    issues=[],
    open_targets=set(),
    override_entries=[],
    now=datetime(2026, 8, 14, tzinfo=timezone.utc),
)
self.assertEqual([retirement_pair], selected)
```

Add subtests proving the retirement target is skipped for an open PR, an `implemented-awaiting-google` source issue, an active override cooldown, and a merged-PR cooldown. In each case, the selector may choose the next eligible recovery target but must still return one item. Retain the existing ordinary-candidate cap and priority assertions.

- [ ] **Step 2: Run the tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_recovery_selection_prefers_one_guide tests.test_seo_feedback_loop.NotificationCommentTests.test_recovery_selection_preserves_suppression_controls
```

Expected: FAIL because `seo-goal-missed` is currently rejected by the selector.

- [ ] **Step 3: Implement minimal recovery selection**

Update target extraction to accept the explicit `page` field. Accept either an existing implementation kind or `is_first_impression_recovery(finding)`. After applying all existing suppression controls, partition eligible pairs:

```python
recovery = [pair for pair in eligible if is_first_impression_recovery(pair[0])]
if recovery:
    recovery.sort(key=lambda pair: (
        "/countries/" in (finding_target_url(pair[0]) or ""),
        finding_target_url(pair[0]) or "",
        pair[0].fingerprint,
    ))
    return recovery[:1]
```

Keep the existing impressions/position ordering and `limit` behavior unchanged when no recovery candidate is eligible.

- [ ] **Step 4: Run focused and selector tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/seo_feedback_loop.py tests/test_seo_feedback_loop.py
git commit -m "Prioritize one first-impression recovery"
```

### Task 3: Route recovery only through generated content

**Files:**
- Modify: `scripts/seo_feedback_loop.py`
- Test: `tests/test_seo_feedback_loop.py`

**Interfaces:**
- Consumes: `GENERATED_CONTENT_KINDS`, recovery-enriched `Finding`
- Produces: main-loop routing into `scaffold_generated_content_pr()` only

- [ ] **Step 1: Write the failing orchestration test**

Run `main()` with a temporary report containing an indexed, missed retirement impression goal. Patch GitHub and generation boundaries, then assert:

```python
self.assertEqual([retirement_url], generated_targets)
self.assertEqual([], implementation_queue_targets)
```

Also assert dry run causes no model call or GitHub mutation and reports one generated-content draft candidate.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests.test_main_routes_recovery_only_to_generated_content
```

Expected: FAIL because main currently appends only `IMPLEMENTATION_PR_KINDS` to `editorial_pairs`.

- [ ] **Step 3: Implement minimal routing**

Change only the `editorial_pairs` condition:

```python
if finding.implementation_pr and (
    finding.kind in IMPLEMENTATION_PR_KINDS or is_first_impression_recovery(finding)
):
    editorial_pairs.append((finding, issue_link))
```

Do not change `scaffold_implementation_pr`; goal findings must never enter that legacy queue.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_seo_feedback_loop.NotificationCommentTests
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/seo_feedback_loop.py tests/test_seo_feedback_loop.py
git commit -m "Route first-impression recovery generation"
```

### Task 4: Verify and publish

**Files:**
- Verify: all changed files and generated artifacts

**Interfaces:**
- Consumes: completed implementation
- Produces: reviewed pull request and production workflow evidence

- [ ] **Step 1: Run full verification**

```bash
python3 -m unittest discover tests
python3 -m py_compile src/build_unified_app.py src/seo_content_overrides.py scripts/seo_monitor.py scripts/seo_content_generator.py scripts/seo_feedback_loop.py
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
git diff --check origin/main...HEAD
```

Expected: all commands pass; restore regenerated artifacts if their only changes are verification timestamps.

- [ ] **Step 2: Run a production-shaped dry run**

Use the latest SEO report and current issue snapshots. Assert the selector chooses `https://globalhomeatlas.com/buying-property-abroad-for-retirement/`, selects one recovery target, and performs no mutation.

- [ ] **Step 3: Request independent review**

Review `origin/main...HEAD` against the design and fix all Critical or Important findings with new failing regression tests.

- [ ] **Step 4: Publish and verify production**

Push the branch, open a draft PR, mark it ready after review, wait for checks, merge, run the SEO feedback loop, and verify that one generated-content draft PR targets the retirement guide while issue #89 remains open without `implemented-awaiting-google` until that content PR merges.
