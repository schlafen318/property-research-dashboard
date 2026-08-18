# Durable Google Search Console OAuth Design

## Goal

Prevent the scheduled SEO feedback loop from losing Search Console access when the OAuth refresh token issued in Google Cloud Testing mode expires.

## Chosen Approach

Move the existing `global-home-atlas` OAuth consent configuration from Testing to Production. Keep the current installed-application OAuth client and the existing `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` secret contract.

This is the smallest durable change: it avoids application-code changes, preserves the current Search Console authorization flow, and removes the short Testing-mode refresh-token lifetime.

## Rollout

1. Open the Google Cloud project that owns the existing OAuth client.
2. Confirm the app name, requested Search Console scope, support contact, and authorized account are correct.
3. Change the OAuth app publishing status from Testing to Production.
4. Reauthorize the same Google account for the `webmasters` scope and create a fresh authorized-user token.
5. Validate the new token with a read-only Search Console report.
6. Replace the GitHub Actions secret `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON` with the validated token.
7. Run the SEO feedback loop manually and confirm every job step succeeds.

## Data Flow

GitHub Actions reads the encrypted token JSON into `GOOGLE_SEARCH_CONSOLE_TOKEN_JSON`. `scripts/seo_monitor.py` writes it to the ignored temporary token path, refreshes the access token through Google when necessary, and queries Search Console. The long-lived refresh token remains stored only in the local ignored file and the encrypted GitHub secret.

## Failure Handling and Rollback

- If Google requires app verification before Production publishing, stop before broadening access and reassess whether to complete verification or migrate to a service account.
- If reauthorization fails, retain the currently working GitHub secret and do not rerun the workflow with an unvalidated token.
- If the replacement workflow fails, restore the last known working secret if available and inspect the new run logs before making further changes.
- No repository application code or workflow behavior changes as part of this rollout.

## Verification

The rollout is complete only when:

- Google Cloud reports the OAuth app as Production.
- A fresh token successfully runs the local Search Console monitor.
- The GitHub secret shows a new update timestamp.
- A manual SEO feedback-loop run completes successfully, including `Generate SEO monitor report`.

## Security Constraints

- Never print or commit OAuth access tokens, refresh tokens, client secrets, or the GitHub secret value.
- Keep the local OAuth client and token files under the existing ignored `tmp/` path.
- Do not add users, scopes, or redirect URIs beyond those already required by the installed application.
