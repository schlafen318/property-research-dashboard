# Automatic SEO Growth System

Global Home Atlas has a closed-loop SEO workflow that monitors Google Search
Console, submits the sitemap, creates issues and PRs for opportunities, applies
low-risk fixes automatically, and reports the result back to the owner.

## Current State

- The workflow runs automatically every day at 09:17 HKT.
- A backup scheduled run is configured for 10:47 HKT if GitHub delays or drops
  the primary scheduled event.
- The workflow can also be started manually from GitHub Actions.
- Low-risk internal-link fixes can be implemented, opened as PRs, and merged by
  the automation.
- Higher-risk title, meta, FAQ, and editorial content changes are queued as
  implementation PRs for review unless explicitly approved and implemented.
- Telegram and email notifications are optional. The workflow does not fail if
  notification secrets are missing.

## Daily Loop

The scheduled workflow is `.github/workflows/seo-feedback-loop.yml`.

Each run does this:

1. Reads the live sitemap and Search Console data.
2. Submits the sitemap to Google Search Console.
3. Submits live URLs to IndexNow where supported.
4. Generates `artifacts/seo-status/index.html`.
5. Verifies tracking coverage across the static site.
6. Runs `scripts/seo_feedback_loop.py --apply`.
7. Updates the GitHub control issue.
8. Creates or updates deduplicated analytics issues.
9. Opens implementation PRs where a code/content change is needed.
10. Auto-implements approved low-risk internal links.
11. Sends Telegram or email notifications when configured.
12. Uploads the JSON and Markdown SEO reports as workflow artifacts.

## Inputs

The loop uses:

- Google Search Console token from `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON`.
- The generated sitemap and canonical URLs.
- IndexNow key from `INDEXNOW_KEY`, or the repo default key when omitted.
- Existing guide, country, destination, and landing-page metadata.
- Existing internal-link queue data in `data/seo_auto_internal_links.json`.

Search Console data includes:

- top queries
- top pages
- low-CTR pages
- near-ranking pages
- content-gap queries
- sitemap submission and indexing signals
- priority URL inspection results

## Outputs

The loop writes or updates:

- `output/seo/latest.json`
- `output/seo/indexnow-latest.json`
- `output/seo/feedback-loop-summary.json`
- `artifacts/seo-status/index.html`
- GitHub control issue: `Global Home Atlas Analytics Control Center`
- deduplicated GitHub issues for each finding
- draft implementation PRs for human-review changes
- non-draft auto-implementation PRs for low-risk internal links

`output/seo/` is ignored locally. GitHub uploads those reports as workflow
artifacts after each run.

## Auto-Implementation Rules

The automation may implement low-risk internal links automatically when:

- Search Console shows an existing page is near-ranking.
- The target page already exists.
- The source page already exists.
- The change only adds a contextual internal link between existing pages.
- No editorial rewrite, new factual claim, or new page is required.

These changes are stored in `data/seo_auto_internal_links.json`, the static site
is regenerated, checks are run, and the PR can be auto-merged.

## Human-Review Rules

The system queues human-review work when the change may affect editorial quality
or buyer trust, including:

- title tag rewrites
- meta description rewrites
- H1 or intro changes
- FAQ additions or edits
- new landing pages
- new claims about countries, laws, taxes, visas, property rules, or returns
- query-intent decisions where the best target page is ambiguous

Those findings become GitHub issues and draft implementation PRs labeled
`implementation-queued`.

## Notifications

Every scheduled run comments on the control issue and mentions `@schlafen318`.
That can trigger GitHub's normal notification email.

Optional direct Telegram notifications use:

```text
SEO_NOTIFY_TELEGRAM_BOT_TOKEN
SEO_NOTIFY_TELEGRAM_CHAT_ID
```

Optional direct email notifications use:

```text
SEO_NOTIFY_SMTP_HOST
SEO_NOTIFY_SMTP_PORT
SEO_NOTIFY_SMTP_USERNAME
SEO_NOTIFY_SMTP_PASSWORD
SEO_NOTIFY_EMAIL_FROM
SEO_NOTIFY_EMAIL_TO
SEO_NOTIFY_SMTP_TLS
```

If Telegram or SMTP secrets are not configured, the workflow skips that channel
without failing the SEO loop.

## Required Repository Settings

GitHub Actions needs write access so the loop can update issues, push
auto-implementation branches, open PRs, and merge approved low-risk fixes.

Required secret:

```text
GOOGLE_SEARCH_CONSOLE_TOKEN_JSON
```

Optional secrets:

```text
INDEXNOW_KEY
SEO_NOTIFY_TELEGRAM_BOT_TOKEN
SEO_NOTIFY_TELEGRAM_CHAT_ID
SEO_NOTIFY_SMTP_HOST
SEO_NOTIFY_SMTP_PORT
SEO_NOTIFY_SMTP_USERNAME
SEO_NOTIFY_SMTP_PASSWORD
SEO_NOTIFY_EMAIL_FROM
SEO_NOTIFY_EMAIL_TO
SEO_NOTIFY_SMTP_TLS
```

## Manual Commands

Generate a local SEO report:

```bash
python3 scripts/seo_monitor.py --write --json-output output/seo/latest.json
```

Submit URLs to IndexNow:

```bash
python3 scripts/indexnow_submit.py --write --output output/seo/indexnow-latest.json --allow-failure
```

Run the feedback loop without making GitHub changes:

```bash
python3 scripts/seo_feedback_loop.py --dry-run
```

Run static-site verification:

```bash
python3 scripts/verify_static_site.py --min-sitemap-urls 65
```

Verify tracking coverage:

```bash
python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py
```

## How To Check A Run

1. Open GitHub Actions and select `SEO feedback loop`.
2. Confirm the latest run completed successfully.
3. Open the uploaded `seo-monitor-report` artifact if detailed JSON or Markdown
   reports are needed.
4. Check the `Global Home Atlas Analytics Control Center` issue for the latest
   summary.
5. Review any newly opened `implementation-queued` PRs.
6. Check Telegram if notification secrets are configured.

## Failure Recovery

- If the workflow fails before Search Console runs, check
  `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON`.
- If Search Console returns no data, wait for Google to refresh the reporting
  window before making content changes.
- If notification delivery fails, check Telegram or SMTP secrets. The SEO loop
  can still be healthy even when notifications are skipped.
- If auto-implementation PRs conflict, close superseded single-link PRs after a
  batched PR merges.
- If deployment fails after a merged SEO change, rerun `Deploy static dashboard`
  after confirming the static verification passes.

## Definition Of Done

The system is operating end to end when:

- the scheduled SEO feedback loop completes successfully
- Search Console data is read from the GitHub secret
- sitemap and IndexNow submissions run
- the SEO status dashboard is generated
- the control issue is updated
- findings become deduplicated issues or PRs
- low-risk internal-link fixes can auto-implement
- human-review changes are queued rather than silently published
- Telegram or email notification succeeds when secrets are configured
- the static deploy after merged changes succeeds

