from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "output" / "seo" / "latest.json"
CONTROL_ISSUE_TITLE = "Global Home Atlas Analytics Control Center"
CONTROL_LABELS = ["analytics-loop"]
LABELS = {
    "analytics-loop": "5319e7",
    "auto-merge-safe": "0e8a16",
    "needs-human-review": "d93f0b",
    "seo-opportunity": "1d76db",
    "growth-opportunity": "a371f7",
    "tracking-regression": "b60205",
    "sitemap-regression": "b60205",
    "indexing-stalled": "b60205",
    "no-search-console-rows": "d93f0b",
    "priority-page-not-indexed": "fbca04",
    "trust-signal-gap": "fbca04",
    "content-refresh": "fbca04",
    "landing-page-candidate": "5319e7",
}


@dataclass(frozen=True)
class Finding:
    kind: str
    title: str
    summary: str
    severity: str
    labels: tuple[str, ...]
    fingerprint: str
    auto_merge_safe: bool = False
    draft_pr: bool = False
    payload: dict | None = None


def run(cmd: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def gh_json(args: list[str]) -> object:
    completed = run(["gh", *args])
    text = completed.stdout.strip()
    return json.loads(text) if text else None


def stable_fingerprint(kind: str, key: str) -> str:
    digest = hashlib.sha1(f"{kind}:{key}".encode("utf-8")).hexdigest()[:12]
    return f"gha-{kind}-{digest}"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", value)[:72] or "seo-opportunity"


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def existing_url_match(query: str, urls: list[str]) -> str | None:
    terms = {part for part in re.findall(r"[a-z0-9]+", query.lower()) if len(part) > 2}
    if not terms:
        return None
    best_url = None
    best_score = 0
    for url in urls:
        page_terms = set(re.findall(r"[a-z0-9]+", url.lower()))
        score = len(terms & page_terms)
        if score > best_score:
            best_url = url
            best_score = score
    return best_url if best_score >= min(2, len(terms)) else None


def classify(report: dict, tracking_ok: bool) -> list[Finding]:
    findings: list[Finding] = []
    sitemap = report.get("sitemap", {})
    status = sitemap.get("status") or {}
    indexing = sitemap.get("indexing") or {}
    warnings = int(status.get("warnings") or 0)
    errors = int(status.get("errors") or 0)
    urls = sitemap.get("urls") or []
    indexed_reported = indexing.get("indexed_reported")
    submitted_reported = indexing.get("submitted_reported")
    priority_inspections = indexing.get("priority_inspections") or []

    if errors or warnings:
        key = f"{sitemap.get('url')}:{errors}:{warnings}"
        findings.append(
            Finding(
                kind="sitemap-regression",
                title="Fix sitemap warnings or errors",
                summary=f"Search Console reports {errors} sitemap errors and {warnings} warnings for {sitemap.get('url')}.",
                severity="high",
                labels=("analytics-loop", "sitemap-regression", "auto-merge-safe"),
                fingerprint=stable_fingerprint("sitemap-regression", key),
                auto_merge_safe=True,
                payload={"errors": errors, "warnings": warnings, "sitemap": sitemap.get("url")},
            )
        )

    inspected_priority_urls = [item for item in priority_inspections if item.get("ok")]
    inspected_priority_passes = [item for item in inspected_priority_urls if item.get("verdict") == "PASS"]

    if (
        submitted_reported
        and indexed_reported == 0
        and status.get("isPending") is False
        and len(inspected_priority_passes) < max(1, len(inspected_priority_urls))
    ):
        findings.append(
            Finding(
                kind="indexing-stalled",
                title="Indexing is stalled after sitemap submission",
                summary=(
                    f"Search Console reports {submitted_reported} submitted sitemap URLs but 0 indexed URLs. "
                    "Inspect the homepage and priority guide URLs, then request indexing for pages that are live and crawlable."
                ),
                severity="high",
                labels=("analytics-loop", "indexing-stalled", "seo-opportunity", "needs-human-review"),
                fingerprint=stable_fingerprint("indexing-stalled", f"{sitemap.get('url')}:{submitted_reported}:0"),
                payload={
                    "submitted_reported": submitted_reported,
                    "indexed_reported": indexed_reported,
                    "priority_inspections": priority_inspections,
                },
            )
        )

    priority_urls = [item for item in indexing.get("priority_urls", []) if item.get("in_sitemap")]
    not_indexed_inspections = [
        item
        for item in priority_inspections
        if item.get("ok")
        and item.get("verdict") not in {"PASS"}
    ]
    inspection_errors = [item for item in priority_inspections if not item.get("ok")]
    if priority_urls and submitted_reported and (not_indexed_inspections or inspection_errors or (not priority_inspections and (indexed_reported or 0) < len(priority_urls))):
        findings.append(
            Finding(
                kind="priority-page-not-indexed",
                title="Request indexing for priority SEO pages",
                summary=(
                    "Priority URLs are present in the sitemap, but Search Console has not confirmed that the homepage "
                    "and highest-intent guide pages are indexed."
                ),
                severity="medium",
                labels=("analytics-loop", "priority-page-not-indexed", "seo-opportunity", "needs-human-review"),
                fingerprint=stable_fingerprint("priority-page-not-indexed", sitemap.get("url") or "priority-pages"),
                payload={
                    "priority_urls": priority_urls,
                    "priority_inspections": priority_inspections,
                    "not_indexed_inspections": not_indexed_inspections,
                    "inspection_errors": inspection_errors,
                    "indexed_reported": indexed_reported,
                    "submitted_reported": submitted_reported,
                },
            )
        )

    if not tracking_ok:
        findings.append(
            Finding(
                kind="tracking-regression",
                title="Restore analytics tracking coverage",
                summary="The local tracking verifier failed. Restore `window.GHA.track`, `gha_event_queue`, expected events, and the custom shortlist form.",
                severity="high",
                labels=("analytics-loop", "tracking-regression", "auto-merge-safe"),
                fingerprint=stable_fingerprint("tracking-regression", "verify_tracking"),
                auto_merge_safe=True,
            )
        )

    sc = report.get("search_console", {})
    if sc.get("available") and not sc.get("top_queries") and not sc.get("top_pages"):
        findings.append(
            Finding(
                kind="no-search-console-rows",
                title="No Search Console performance rows yet",
                summary=(
                    "Search Console access is working, but the latest reporting window returned no query or page rows. "
                    "Keep indexing work active and review again after Google has crawled and tested the site in search results."
                ),
                severity="low",
                labels=("analytics-loop", "no-search-console-rows", "seo-opportunity"),
                fingerprint=stable_fingerprint("no-search-console-rows", str(report.get("site_url") or "globalhomeatlas")),
                payload={"window": report.get("window"), "sitemap": sitemap.get("url")},
            )
        )

    for row in sc.get("low_ctr_pages", []):
        page = row.get("page", "")
        findings.append(
            Finding(
                kind="low-ctr-opportunity",
                title=f"Improve CTR for {page.replace('https://globalhomeatlas.com/', '/')}",
                summary=(
                    f"Page has {row.get('impressions', 0)} impressions, "
                    f"{row.get('ctr', 0) * 100:.2f}% CTR, and average position {row.get('position', 0):.1f}."
                ),
                severity="medium",
                labels=("analytics-loop", "seo-opportunity", "content-refresh", "needs-human-review"),
                fingerprint=stable_fingerprint("low-ctr-opportunity", page),
                payload=row,
            )
        )

    for row in sc.get("near_ranking_pages", []):
        page = row.get("page", "")
        findings.append(
            Finding(
                kind="near-ranking-opportunity",
                title=f"Push near-ranking page higher: {page.replace('https://globalhomeatlas.com/', '/')}",
                summary=(
                    f"Page is ranking around position {row.get('position', 0):.1f} "
                    f"with {row.get('impressions', 0)} impressions. Add internal links, sharpen title/meta, or improve page intent match."
                ),
                severity="medium",
                labels=("analytics-loop", "seo-opportunity", "content-refresh", "needs-human-review"),
                fingerprint=stable_fingerprint("near-ranking-opportunity", page),
                payload=row,
            )
        )

    for row in sc.get("content_gap_queries", []):
        query = row.get("query", "")
        if existing_url_match(query, urls):
            continue
        findings.append(
            Finding(
                kind="new-query-content-gap",
                title=f"Create landing page candidate for `{query}`",
                summary=(
                    f"Query has {row.get('impressions', 0)} impressions, "
                    f"{row.get('ctr', 0) * 100:.2f}% CTR, and average position {row.get('position', 0):.1f}, "
                    "but no existing sitemap URL appears to match it."
                ),
                severity="medium",
                labels=("analytics-loop", "growth-opportunity", "landing-page-candidate", "needs-human-review"),
                fingerprint=stable_fingerprint("new-query-content-gap", query),
                draft_pr=True,
                payload=row,
            )
        )

    return findings


def issue_body(finding: Finding) -> str:
    payload = json.dumps(finding.payload or {}, indent=2, sort_keys=True)
    return f"""## Summary
{finding.summary}

## Classification
- Kind: `{finding.kind}`
- Severity: `{finding.severity}`
- Fingerprint: `{finding.fingerprint}`
- Auto-merge safe: `{finding.auto_merge_safe}`
- Draft PR candidate: `{finding.draft_pr}`

## Acceptance Criteria
- The issue is either fixed in a linked PR or explicitly closed as not actionable.
- The next analytics loop run does not recreate a duplicate issue with the same fingerprint.

## Raw Signal
```json
{payload}
```
"""


def control_issue_body(report: dict, findings: list[Finding], issue_links: list[str], pr_links: list[str], auto_merged: list[str]) -> str:
    sitemap = report.get("sitemap", {})
    status = sitemap.get("status") or {}
    sc = report.get("search_console", {})
    by_severity = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
    priority_inspections = sitemap.get("indexing", {}).get("priority_inspections", [])
    return f"""## Latest Run
- Generated: `{report.get('generated_at')}`
- Window: `{report.get('window', {}).get('start_date')}` to `{report.get('window', {}).get('end_date')}`
- Sitemap URLs: `{sitemap.get('url_count')}`
- Sitemap pending: `{status.get('isPending', 'n/a')}`
- Sitemap warnings: `{status.get('warnings', 'n/a')}`
- Sitemap errors: `{status.get('errors', 'n/a')}`

## Search Console Summary
- Top queries returned: `{len(sc.get('top_queries', []))}`
- Top pages returned: `{len(sc.get('top_pages', []))}`
- Low CTR pages: `{len(sc.get('low_ctr_pages', []))}`
- Near-ranking pages: `{len(sc.get('near_ranking_pages', []))}`
- Content-gap queries: `{len(sc.get('content_gap_queries', []))}`

## Indexing Summary
- Submitted URLs reported by Google: `{sitemap.get('indexing', {}).get('submitted_reported')}`
- Indexed URLs reported by Google: `{sitemap.get('indexing', {}).get('indexed_reported')}`
- Priority URLs in sitemap: `{sum(1 for item in sitemap.get('indexing', {}).get('priority_urls', []) if item.get('in_sitemap'))}`
- Priority URL inspections: `{len(priority_inspections)}`

## Priority URL Inspection Results
{format_priority_inspections(priority_inspections)}

## Findings
- High severity: `{by_severity.get('high', 0)}`
- Medium severity: `{by_severity.get('medium', 0)}`
- Low severity: `{by_severity.get('low', 0)}`

## Issues Created Or Updated
{chr(10).join(f'- {link}' for link in issue_links) if issue_links else '- None'}

## Draft PRs Opened
{chr(10).join(f'- {link}' for link in pr_links) if pr_links else '- None'}

## Auto-Merged Fixes
{chr(10).join(f'- {link}' for link in auto_merged) if auto_merged else '- None'}

## Recommended Next Action
{recommended_next_action(findings)}
"""


def format_priority_inspections(inspections: list[dict]) -> str:
    if not inspections:
        return "- Not run"
    rows = []
    for item in inspections:
        if not item.get("ok"):
            rows.append(f"- `{item.get('url')}`: inspection error: {item.get('error')}")
            continue
        rows.append(
            "- "
            f"`{item.get('url')}`: verdict `{item.get('verdict') or 'n/a'}`, "
            f"coverage `{item.get('coverage_state') or 'n/a'}`, "
            f"fetch `{item.get('page_fetch_state') or 'n/a'}`, "
            f"last crawl `{item.get('last_crawl_time') or 'n/a'}`"
        )
    return "\n".join(rows)


def recommended_next_action(findings: list[Finding]) -> str:
    kinds = {finding.kind for finding in findings}
    if "indexing-stalled" in kinds or "priority-page-not-indexed" in kinds:
        return "Use Search Console URL inspection for the homepage and priority guide pages, then request indexing where available."
    if "no-search-console-rows" in kinds:
        return "Continue daily monitoring; no content-growth action should be automated until query or page rows appear."
    if findings:
        return "Review draft landing-page PRs and human-review issues."
    return "No action needed; continue monitoring."


def ensure_labels(dry_run: bool) -> None:
    for label, color in LABELS.items():
        if dry_run:
            print(f"[dry-run] ensure label {label}")
            continue
        run(["gh", "label", "create", label, "--color", color, "--force"], check=False)


def list_issues() -> list[dict]:
    result = gh_json(["issue", "list", "--state", "all", "--limit", "200", "--json", "number,title,body,url,state,labels"])
    return result if isinstance(result, list) else []


def find_issue_by_fingerprint(issues: list[dict], fingerprint: str) -> dict | None:
    for issue in issues:
        if fingerprint in (issue.get("body") or ""):
            return issue
    return None


def find_control_issue(issues: list[dict]) -> dict | None:
    for issue in issues:
        if issue.get("title") == CONTROL_ISSUE_TITLE:
            return issue
    return None


def create_or_update_issue(finding: Finding, issues: list[dict], dry_run: bool) -> str:
    body = issue_body(finding)
    labels = ",".join(finding.labels)
    existing = find_issue_by_fingerprint(issues, finding.fingerprint)
    if dry_run:
        action = "update issue" if existing else "create issue"
        print(f"[dry-run] {action}: {finding.title} [{finding.fingerprint}]")
        return existing.get("url", f"dry-run:{finding.fingerprint}") if existing else f"dry-run:{finding.fingerprint}"
    if existing:
        run(["gh", "issue", "edit", str(existing["number"]), "--body", body, "--add-label", labels])
        return existing.get("url", f"issue:{existing['number']}")
    completed = run(["gh", "issue", "create", "--title", finding.title, "--body", body, "--label", labels])
    return completed.stdout.strip()


def create_or_update_control_issue(report: dict, findings: list[Finding], issue_links: list[str], pr_links: list[str], auto_merged: list[str], dry_run: bool) -> str:
    issues = list_issues() if not dry_run else []
    body = control_issue_body(report, findings, issue_links, pr_links, auto_merged)
    existing = find_control_issue(issues)
    if dry_run:
        print(f"[dry-run] update control issue with {len(findings)} findings")
        return "dry-run:control-issue"
    labels = ",".join(CONTROL_LABELS)
    if existing:
        run(["gh", "issue", "edit", str(existing["number"]), "--body", body, "--add-label", labels])
        return existing.get("url", f"issue:{existing['number']}")
    completed = run(["gh", "issue", "create", "--title", CONTROL_ISSUE_TITLE, "--body", body, "--label", labels])
    return completed.stdout.strip()


def scaffold_landing_page_pr(finding: Finding, dry_run: bool) -> str | None:
    if not finding.draft_pr:
        return None
    query = str((finding.payload or {}).get("query") or finding.title)
    slug = slugify(query)
    branch = f"analytics/landing-page-{slug[:48]}"
    path = ROOT / "docs" / "seo-opportunities" / f"{slug}.md"
    content = f"""# Landing Page Candidate: {query}

## Analytics Signal
{finding.summary}

## Proposed URL
`/{slug}/`

## Target Keyword
`{query}`

## Proposed Internal Links
- Homepage buyer guides section
- Relevant destination pages from `/destinations/`
- Related buyer guide pages with overlapping intent

## FAQ Candidates
- What should buyers know about {query}?
- Which destinations should be compared first?
- What risks should foreign buyers verify before purchase?

## Acceptance Criteria
- Generated static page is added through `src/build_unified_app.py`.
- Page has a unique title, meta description, canonical, H1, internal links, and FAQ schema where appropriate.
- Page is added to `artifacts/sitemap.xml`.
- Tracking verifier and build pass.

## Fingerprint
`{finding.fingerprint}`
"""
    if dry_run:
        print(f"[dry-run] create draft PR branch {branch} with {path.relative_to(ROOT)}")
        return f"dry-run:pr:{branch}"

    current = run(["git", "branch", "--show-current"]).stdout.strip()
    run(["git", "switch", "-c", branch])
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        run(["git", "add", str(path.relative_to(ROOT))])
        run(["git", "commit", "-m", f"Add landing page candidate for {query[:48]}"])
        run(["git", "push", "--set-upstream", "origin", branch])
        pr_body = issue_body(finding)
        completed = run(
            [
                "gh",
                "pr",
                "create",
                "--draft",
                "--title",
                finding.title,
                "--body",
                pr_body,
                "--label",
                ",".join(finding.labels),
            ]
        )
        return completed.stdout.strip()
    finally:
        run(["git", "switch", current], check=False)


def maybe_auto_merge(pr_url: str | None, finding: Finding, dry_run: bool) -> str | None:
    if not pr_url or not finding.auto_merge_safe:
        return None
    if dry_run:
        print(f"[dry-run] would enable auto-merge for {pr_url}")
        return f"dry-run:auto-merge:{pr_url}"
    run(["gh", "pr", "merge", pr_url, "--squash", "--auto"], check=False)
    return pr_url


def tracking_status() -> bool:
    completed = run(["python3", "codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py"], check=False)
    return completed.returncode == 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn SEO monitor output into GitHub issues and draft PRs.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.dry_run and not args.apply:
        raise SystemExit("Pass --dry-run or --apply.")
    report = load_report(args.report)
    dry_run = args.dry_run
    tracking_ok = tracking_status()
    findings = classify(report, tracking_ok)

    ensure_labels(dry_run)
    issues = list_issues() if not dry_run else []
    issue_links = [create_or_update_issue(finding, issues, dry_run) for finding in findings]
    pr_links: list[str] = []
    auto_merged: list[str] = []
    for finding in findings:
        pr_url = scaffold_landing_page_pr(finding, dry_run)
        if pr_url:
            pr_links.append(pr_url)
        merge_url = maybe_auto_merge(pr_url, finding, dry_run)
        if merge_url:
            auto_merged.append(merge_url)
    control_link = create_or_update_control_issue(report, findings, issue_links, pr_links, auto_merged, dry_run)
    print(json.dumps({"findings": len(findings), "issues": issue_links, "prs": pr_links, "control": control_link}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
