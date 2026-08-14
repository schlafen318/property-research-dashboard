# Stale SEO Opportunity Reconciliation Design

## Goal

Prevent old Search Console opportunity issues and queue pull requests from appearing actionable after their underlying signal has disappeared, while avoiding closure after a single noisy report.

## Context

Queenstown issues #91 and #92 and queue pull requests #93 and #94 retained a 92–95 impression signal from an earlier reporting window. The latest healthy 28-day Search Console artifact contains only two Queenstown query impressions. Because the feedback loop updates current fingerprints but never reconciles missing fingerprints, the stale queue looked like the repository's largest opportunity.

## Approaches Considered

1. **Two-report grace period (selected).** Mark an open opportunity stale after its first absence from a healthy Search Console report. Close it only if it remains absent in the next healthy run. If the fingerprint returns, clear the stale marker and reopen an issue that the automation previously closed.
2. **Close on first absence.** This is simple but would churn issues when Search Console rows fluctuate around result limits or reporting windows.
3. **Never close missing findings.** This preserves history but leaves the working queue misleading and requires repeated manual cleanup.

## Scope

Reconcile only Search Console content-opportunity kinds:

- `query-ctr-opportunity`
- `low-ctr-opportunity`
- `near-ranking-opportunity`
- `new-query-content-gap`

Do not automatically reconcile indexing, sitemap, tracking, goal, control-center, or `implemented-awaiting-google` issues. Those have different evidence and lifecycle requirements.

## Lifecycle

Add `stale-signal` and the machine-only provenance label `stale-signal-auto-closed` to the managed label registry.

The monitor requests up to 25,000 query rows and 25,000 page rows separately from the 25-row display lists. It records completeness per dimension. A response that reaches the limit is treated as truncated. Absence may advance stale state only for kinds whose source dimension is complete; a positive fingerprint may still clear or reopen stale state even in a truncated report.

For each healthy applied run:

1. Build the set of current fingerprints for the managed kinds.
2. For each open managed issue whose fingerprint is absent:
   - first consecutive absence: add `stale-signal` and leave the issue open;
   - second consecutive absence: add `stale-signal-auto-closed`, then close the issue as not planned.
3. For each current fingerprint:
   - remove `stale-signal` if the issue is still open;
   - if an issue carrying `stale-signal-auto-closed` returns, reopen it and remove both lifecycle labels before updating its current body.

An unavailable, legacy, or capped Search Console result must not advance stale absence for affected kinds. Issues without the `analytics-loop` ownership label are never reconciled. A human-closed issue that has only the first-warning label is never reopened. Dry runs report intended counts without GitHub mutations.

## Interfaces and Reporting

Add a focused reconciliation function that consumes current `Finding` objects and the existing GitHub issue snapshots. It returns counts for marked, closed, and reopened issues. Include these counts in the feedback summary JSON and control-issue generated-content/status section so the lifecycle remains observable.

GitHub mutations continue through the existing retrying `gh_mutation` boundary. Failures are isolated per issue, successful writes retain truthful counts, and later issues continue. If closing fails after the provenance label is added, the automation attempts to remove that label. All errors appear in the run summary.

## Testing

Use controlled issue snapshots and intercept only the GitHub mutation boundary. Tests must prove:

- first absence adds `stale-signal` but does not close;
- second absence closes as not planned and retains provenance;
- a returning fingerprint clears the marker;
- an automatically closed returning issue reopens;
- a human-closed issue does not reopen;
- capped or legacy reports never advance absence state;
- a qualifying signal outside the 25 displayed rows remains active;
- one failed GitHub mutation does not block later issues or erase successful counts;
- `implemented-awaiting-google`, indexing/goal issues, and unavailable Search Console reports are skipped;
- lifecycle counts appear in the run summary.

Run the complete unit suite, Python compilation, static-site verification, tracking verification, and diff checks before publishing.

## Release

Publish through a reviewed pull request. Do not trigger a content deployment solely for Queenstown. The next scheduled SEO feedback run will apply the lifecycle to the current opportunity queue; any future Queenstown work must be created from a fresh qualifying signal.
