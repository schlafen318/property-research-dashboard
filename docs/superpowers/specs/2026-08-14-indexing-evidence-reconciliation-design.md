# Indexing Evidence Reconciliation Design

## Goal

Stop the SEO feedback loop from reporting an indexing goal as missed when Search Console performance proves the page appeared in Google, and retire old goal issues when the evidence is no longer actionable.

## Context

Issue #107 reports that `where-can-foreigners-buy-property` missed its indexing goal even though the same report records 27 impressions and an average position of 13.7. The contradiction occurs because indexing status currently considers only the URL Inspection verdict. A timeout, API error, or missing inspection response falls through to the calendar deadline and becomes `missed`.

## Approaches Considered

1. **Combine independent evidence and reconcile issue state (selected).** Treat positive page impressions as proof that Google surfaced the URL. Preserve successful URL Inspection as the preferred signal, classify unavailable inspection evidence as `unknown`, and close or reopen automation-owned goal issues as the evidence changes.
2. **Retry URL Inspection more aggressively.** This may reduce transient failures but cannot remove the contradiction when the inspection service remains unavailable, and it ignores stronger performance evidence already in the report.
3. **Suppress only issue #107.** This fixes one symptom and allows the same false alert to recur for other pages.

## Indexing Status Rules

Evaluate indexing evidence in this order:

1. A successful URL Inspection verdict of `PASS` returns `met`.
2. One or more Search Console page impressions returns `met`, even if URL Inspection failed or timed out.
3. An absent or failed URL Inspection response returns `unknown`; it must never become `at_risk` or `missed` solely because a deadline passed.
4. A successful non-`PASS` inspection response continues to use the existing launch/deadline rules and may return `on_track`, `at_risk`, or `missed`.

The scorecard records a concise indexing evidence value so reports can distinguish `url_inspection`, `search_console_impressions`, `inspection_unavailable`, and `url_inspection_not_passed`.

## Goal-Issue Lifecycle

Reconcile only automation-owned open or closed issues with kind `seo-goal-at-risk` or `seo-goal-missed` and the `analytics-loop` label.

- When the matching scorecard field is `met`, close the issue as completed.
- When indexing status is `unknown`, close an existing indexing-goal issue as not planned because the current report does not prove failure.
- Before either automatic close, add `goal-status-auto-closed` as machine provenance.
- When the same goal later returns to `at_risk` or `missed`, reopen only issues carrying that provenance label, then remove the label.
- Never reopen a human-closed goal issue.
- Keep impression-goal behavior unchanged except that a genuinely `met` impression goal may close its old automation issue.

Mutations are isolated per issue. Counts increment only after successful writes, close provenance is rolled back when close fails, and errors are surfaced without preventing later issues from being reconciled.

## Reporting

Add `goal_issue_reconciliation` to the feedback summary with `closed`, `reopened`, and `errors`. Show the counts in the control issue and notification using plain text. Do not add new dashboard decorations.

## Testing

Tests must prove:

- impressions override a failed inspection response;
- impressions override a successful non-`PASS` inspection response;
- a failed or absent inspection with zero impressions returns `unknown`;
- a successful non-`PASS` inspection still follows deadline rules;
- a contradictory open goal issue closes with provenance;
- an unknown indexing result retires an existing indexing alert without claiming success;
- an automatically closed recurring alert reopens, while a human-closed issue remains closed;
- one failed GitHub mutation does not block later issues or falsify counts;
- summary and control reporting show the actual reconciliation outcome.

Run the complete unit suite, Python compilation, static-site verification, tracking verification, and a dry run before publishing. After merge, run the workflow once and verify #107 closes while genuine conclusive failures remain actionable.
