# Google Sitemap Post-Deploy Submission Design

## Goal

Notify Google Search Console immediately after a successful production deployment by resubmitting the public sitemap through Google's supported Search Console API. Preserve the daily SEO feedback loop as the monitoring and retry fallback.

## Context

The daily SEO feedback workflow already calls `scripts/seo_monitor.py --submit-sitemap`, inspects priority URLs, and reports indexing state. That means sitemap submission is automated today, but it may occur hours after a content deployment. Google does not expose a supported general-purpose API for the Search Console **Request indexing** button, and the Indexing API is not applicable to ordinary property pages.

## Approaches Considered

1. **Post-deploy sitemap submission (selected).** Run a small authenticated command after GitHub Pages deploys. This is immediate, supported by Google, observable, and reuses the existing OAuth secret.
2. **Rely only on the daily SEO workflow.** This requires no code, but delays notification until the next scheduled run.
3. **Automate Search Console UI clicks.** This is fragile, depends on an interactive Google session, and is not suitable for unattended GitHub Actions.

## Architecture

Create a focused command at `scripts/google_sitemap_submit.py`. It will reuse `token_from_env`, `load_search_console`, and `submit_sitemap` from `scripts/seo_monitor.py`, write a JSON receipt, and return a non-zero exit code when credentials are missing or Google rejects the submission.

Extend `.github/workflows/deploy-pages.yml` with a `notify-google` job that depends on the successful `deploy` job. The job will:

1. check out the deployed revision;
2. install the existing Google API dependencies;
3. expose only `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` to the submission step;
4. submit `https://globalhomeatlas.com/sitemap.xml` for the `sc-domain:globalhomeatlas.com` Search Console property;
5. upload the JSON receipt even if submission fails.

The existing scheduled SEO workflow remains unchanged. It continues to resubmit the sitemap, inspect priority URLs, monitor crawl status, and raise alerts.

## Failure Handling

- Missing OAuth credentials fail the notification job with a clear error.
- A rejected Google API request writes an unsuccessful receipt and exits non-zero.
- The Pages deployment job is not rolled back; the content remains live even if notification fails.
- The receipt artifact is uploaded with `if: always()` so failure evidence remains available.
- The next daily SEO run retries sitemap submission automatically.

## Security

- Reuse the existing `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` repository secret and `webmasters` scope.
- Do not print or persist the token.
- Do not add the Google Indexing API, service accounts, new OAuth scopes, or browser automation.

## Testing

- Unit-test successful submission, rejected submission, and missing-token behavior.
- Assert the deployment workflow runs notification only after deployment, scopes the secret to the submission step, and uploads the receipt on failure.
- Run the full Python test suite, compilation checks, static-site verification, and tracking verification.

## Success Criteria

- Every successful production deployment triggers one Search Console sitemap submission.
- The workflow stores a machine-readable submission receipt.
- Submission failures are visible without undoing the completed site deployment.
- Daily inspection and retry behavior continues unchanged.
