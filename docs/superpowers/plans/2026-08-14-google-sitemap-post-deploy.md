# Google Sitemap Post-Deploy Submission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Submit the production sitemap to Google Search Console immediately after every successful GitHub Pages deployment and retain a JSON receipt.

**Architecture:** Add a single-purpose Python command that reuses the existing OAuth and sitemap helpers in `scripts/seo_monitor.py`. Add a dependent deployment workflow job that invokes the command after Pages deployment and uploads its receipt; retain the daily SEO workflow as fallback monitoring and retry.

**Tech Stack:** Python 3.11, `unittest`, Google Search Console API, GitHub Actions, GitHub Pages

## Global Constraints

- Use only the existing `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` secret and `https://www.googleapis.com/auth/webmasters` scope.
- Do not use the Google Indexing API or automate Search Console UI clicks.
- A Google notification failure must not undo or block the already completed Pages deployment.
- The daily SEO feedback workflow must remain unchanged.

---

### Task 1: Add the sitemap submission command

**Files:**
- Create: `scripts/google_sitemap_submit.py`
- Create: `tests/test_google_sitemap_submit.py`

**Interfaces:**
- Consumes: `scripts.seo_monitor.token_from_env(Path)`, `load_search_console(Path)`, and `submit_sitemap(service, site_url, sitemap_url)`.
- Produces: `run_submission(site_url: str, sitemap_url: str, token_path: Path, output_path: Path) -> dict` and `main(argv: list[str]) -> int`.

- [ ] **Step 1: Write failing tests for a successful receipt**

Create a temporary token file and output path, patch only the external Google service boundary, call `run_submission`, and assert the JSON receipt contains `ok`, `site_url`, `sitemap`, and `submitted_at`.

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python3 -m unittest tests.test_google_sitemap_submit.GoogleSitemapSubmissionTests.test_success_writes_receipt -v`

Expected: FAIL because `scripts.google_sitemap_submit` does not exist.

- [ ] **Step 3: Write failing tests for missing credentials and rejected submission**

Assert missing credentials produce an unsuccessful receipt without loading Google, and a rejected API response is preserved in the receipt. Assert `main()` returns `1` for both unsuccessful outcomes and `0` for success.

- [ ] **Step 4: Implement the minimal command**

Parse `--site-url`, `--sitemap`, `--token`, and `--output`. Materialize the token from the environment, call the existing Search Console helpers, add a UTC timestamp, write sorted indented JSON, print only the receipt, and return a truthful exit code.

- [ ] **Step 5: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_google_sitemap_submit -v`

Expected: all sitemap-submission command tests pass.

- [ ] **Step 6: Commit the command**

Stage only `scripts/google_sitemap_submit.py` and `tests/test_google_sitemap_submit.py`, then commit `Add Google sitemap submission command`.

### Task 2: Trigger submission after production deployment

**Files:**
- Modify: `.github/workflows/deploy-pages.yml`
- Modify: `tests/test_google_sitemap_submit.py`

**Interfaces:**
- Consumes: the Task 1 CLI and existing repository secret `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON`.
- Produces: a `notify-google` job dependent on `deploy` and artifact `google-sitemap-submission` containing `output/seo/google-sitemap-submission.json`.

- [ ] **Step 1: Write a failing workflow structure test**

Assert the workflow contains `notify-google`, `needs: deploy`, the Google dependency installation, a submission step invoking `scripts/google_sitemap_submit.py`, step-scoped secret exposure, and an `if: always()` receipt upload. Assert the secret is absent from workflow/job-global environment text.

- [ ] **Step 2: Run the workflow test and verify RED**

Run: `python3 -m unittest tests.test_google_sitemap_submit.DeployWorkflowTests -v`

Expected: FAIL because the workflow does not contain `notify-google`.

- [ ] **Step 3: Add the post-deploy job**

Add checkout, Python setup, Google dependency installation, submission, and artifact upload steps. Scope `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` to the submission step and set `needs: deploy`.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run: `python3 -m unittest tests.test_google_sitemap_submit -v`

Expected: all command and workflow tests pass.

- [ ] **Step 5: Commit the workflow integration**

Stage `.github/workflows/deploy-pages.yml` and `tests/test_google_sitemap_submit.py`, then commit `Submit sitemap after production deployment`.

### Task 3: Verify and publish

**Files:**
- Verify all files changed in Tasks 1 and 2.

**Interfaces:**
- Consumes: completed command and workflow.
- Produces: reviewed branch, merged PR, and a successful live post-deploy submission job.

- [ ] **Step 1: Run full verification**

Run:

```bash
python3 -m unittest discover tests -v
python3 -m py_compile scripts/google_sitemap_submit.py scripts/seo_monitor.py
python3 src/build_unified_app.py
python3 scripts/verify_static_site.py --min-sitemap-urls 65
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
git diff --check
```

Expected: all tests and verification commands pass.

- [ ] **Step 2: Independently review the branch**

Review `origin/main..HEAD` for secret exposure, incorrect dependency ordering, swallowed Google errors, missing receipts, and changes to the daily SEO workflow. Resolve every Critical or Important finding.

- [ ] **Step 3: Publish and merge**

Push `codex/automate-google-sitemap-submit`, open a ready PR against `main`, and squash-merge after checks and review pass.

- [ ] **Step 4: Verify production activation**

Inspect the deployment triggered by the merge. Confirm the Pages deployment succeeds, `notify-google` runs afterward, and `google-sitemap-submission.json` reports `ok: true`.
