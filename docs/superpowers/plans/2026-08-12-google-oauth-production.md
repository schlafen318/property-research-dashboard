# Durable Google Search Console OAuth Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the existing `global-home-atlas` OAuth app to Production, replace its short-lived Testing token, and prove the scheduled SEO workflow remains operational.

**Architecture:** Preserve the existing installed-application OAuth client and authorized-user token format. Change only the Google Cloud publishing status and credential instances; validate locally before replacing the encrypted GitHub Actions secret, then verify the production workflow end to end.

**Tech Stack:** Google Cloud OAuth consent configuration, Google Search Console API, Python `google-auth-oauthlib`, GitHub Actions, GitHub repository secrets

## Global Constraints

- Do not change repository application code or workflow behavior.
- Never print, commit, or include OAuth access tokens, refresh tokens, client secrets, or GitHub secret values in browser snapshots or command output.
- Keep local OAuth client and token files under the ignored `tmp/` directory.
- Do not add users, scopes, redirect URIs, or permissions beyond the existing Search Console `webmasters` scope.
- Stop before publishing if Google requires a verification workflow that broadens access or needs unprovided legal/branding information.

---

### Task 1: Publish the Existing OAuth App

**Files:**
- Read: `tmp/globalhomeatlas-google-oauth-client.json`
- Modify externally: Google Cloud OAuth consent configuration for `global-home-atlas`

**Interfaces:**
- Consumes: Existing OAuth client ID from the ignored client configuration.
- Produces: The same OAuth client under a Google Cloud app whose publishing status is `In production`.

- [x] **Step 1: Identify the owning Google Cloud project safely**

Read only the client ID and project-identifying metadata needed to select the matching project. Do not print the client secret.

- [x] **Step 2: Inspect the OAuth overview**

Open Google Cloud Console, select the project that owns the client, and confirm:

```text
App name: global-home-atlas
Current publishing status: Testing
Requested scope: https://www.googleapis.com/auth/webmasters
```

- [x] **Step 3: Check the publishing preconditions**

Confirm the configured support email and developer contact are valid. If Google requires verification, a privacy-policy URL, branding changes, domain ownership changes, or additional scopes, stop without publishing and report the exact requirement.

- [x] **Step 4: Publish to Production**

Use the Google Cloud publishing control and confirm the publishing status changes to:

```text
In production
```

- [x] **Step 5: Verify the status after a fresh page load**

Reload the OAuth overview and confirm it still displays `In production`.

### Task 2: Issue and Validate a Production-Mode Token

**Files:**
- Read: `tmp/globalhomeatlas-google-oauth-client.json`
- Modify (ignored): `tmp/globalhomeatlas-google-token.json`
- Generate (ignored): `output/seo/latest.json`
- Generate (ignored): `output/seo/*.md`

**Interfaces:**
- Consumes: Production OAuth client from Task 1 and the existing authorized Google account.
- Produces: Valid authorized-user JSON containing the Search Console scope and a refresh token.

- [x] **Step 1: Start the installed-app authorization flow**

Run a localhost callback flow using `google_auth_oauthlib.flow.InstalledAppFlow`, with:

```text
scope=https://www.googleapis.com/auth/webmasters
access_type=offline
prompt=consent
```

Write the returned credentials only to `tmp/globalhomeatlas-google-token.json`.

- [x] **Step 2: Authorize the existing Search Console account**

Choose the same Google account used by the working Search Console integration and approve only `View and manage Search Console data for your verified sites`.

- [x] **Step 3: Validate credential structure without revealing values**

Check that the JSON contains non-empty `refresh_token`, `client_id`, and `client_secret` fields and the exact `webmasters` scope. Output only booleans and scope names.

- [x] **Step 4: Run the read-only Search Console monitor**

Run:

```bash
python3 scripts/seo_monitor.py --write --json-output output/seo/latest.json
```

Expected result: exit code `0`, with `output/seo/latest.json` created and no `invalid_grant` error.

### Task 3: Replace the GitHub Secret and Verify CI

**Files:**
- Read: `tmp/globalhomeatlas-google-token.json`
- Modify externally: GitHub Actions repository secret `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON`
- Verify externally: `.github/workflows/seo-feedback-loop.yml`

**Interfaces:**
- Consumes: Validated production-mode token from Task 2.
- Produces: A successful manual `SEO feedback loop` workflow run using the updated encrypted secret.

- [x] **Step 1: Update the repository secret**

Open the repository Actions secret settings, replace `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` with the complete validated token JSON, and submit the update without displaying the value afterward.

- [x] **Step 2: Verify GitHub accepted the update**

Confirm the Actions secrets list shows `Secret updated` and a current `Last updated` timestamp for `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON`.

- [x] **Step 3: Trigger a manual workflow run**

Open `SEO feedback loop`, choose `Run workflow`, keep branch `main`, and start the run.

- [x] **Step 4: Verify the former failure point**

Open the new job and confirm `Generate SEO monitor report` completes successfully without:

```text
google.auth.exceptions.RefreshError
invalid_grant
Token has been expired or revoked
```

- [x] **Step 5: Verify the complete workflow**

Wait for the job to finish and confirm all required steps complete with overall status `Success`. Record the run URL and duration in the handoff.

- [x] **Step 6: Confirm the repository worktree remains clean**

Run:

```bash
git status --short --branch
```

Expected result: no uncommitted files other than the plan document if it has not yet been committed.

## Verified Outcome

- Google Cloud OAuth publishing status: `In production`
- Local Search Console monitor: exit code `0`
- GitHub secret update: confirmed by `Secret updated`
- Manual workflow run: [SEO feedback loop #99](https://github.com/schlafen318/property-research-dashboard/actions/runs/31548486700)
- Workflow result: `Success` in 2m 57s
- `Generate SEO monitor report`: completed in 1m 59s without `invalid_grant`
