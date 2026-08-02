from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "output" / "seo" / "latest.json"
DEFAULT_INDEXNOW_REPORT = ROOT / "output" / "seo" / "indexnow-latest.json"
SEO_AUTO_INTERNAL_LINKS_PATH = ROOT / "data" / "seo_auto_internal_links.json"
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
    "seo-goal-at-risk": "fbca04",
    "seo-goal-missed": "b60205",
    "content-refresh": "fbca04",
    "landing-page-candidate": "5319e7",
    "query-ctr-opportunity": "fbca04",
    "implementation-queued": "5319e7",
    "implemented-awaiting-google": "fbca04",
    "validated-by-gsc": "0e8a16",
}
QUERY_CTR_MIN_IMPRESSIONS = 4
QUERY_CTR_MAX_CTR = 0.01
QUERY_CTR_MAX_POSITION = 20.0
IMPLEMENTATION_PR_KINDS = {"query-ctr-opportunity", "low-ctr-opportunity", "near-ranking-opportunity"}
AUTO_IMPLEMENTATION_KINDS = {"near-ranking-opportunity"}
AUTO_INTERNAL_LINK_SOURCE_SLUG = "buy-property-abroad"


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
    implementation_pr: bool = False
    auto_implementation_safe: bool = False
    payload: dict | None = None


def run(cmd: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    if check and completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout, file=sys.stdout)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
        completed.check_returncode()
    return completed


def gh_json(args: list[str]) -> object:
    completed = run(["gh", *args])
    text = completed.stdout.strip()
    return json.loads(text) if text else None


def is_transient_github_failure(completed: subprocess.CompletedProcess) -> bool:
    text = f"{completed.stdout or ''}\n{completed.stderr or ''}".lower()
    return completed.returncode != 0 and any(
        marker in text
        for marker in (
            "502",
            "503",
            "504",
            "gateway timeout",
            "try resubmitting",
            "temporarily unavailable",
        )
    )


def gh_mutation(cmd: list[str], attempts: int = 3) -> subprocess.CompletedProcess:
    completed = subprocess.CompletedProcess(cmd, 1)
    for attempt in range(1, attempts + 1):
        completed = run(cmd, check=False)
        if completed.returncode == 0:
            return completed
        if attempt == attempts or not is_transient_github_failure(completed):
            break
        time.sleep(attempt * 2)
    if completed.stdout:
        print(completed.stdout, file=sys.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    completed.check_returncode()
    return completed


def stable_fingerprint(kind: str, key: str) -> str:
    digest = hashlib.sha1(f"{kind}:{key}".encode("utf-8")).hexdigest()[:12]
    return f"gha-{kind}-{digest}"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", value)[:72] or "seo-opportunity"


def load_report(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> dict:
    if not path.exists():
        return {}
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


def best_url_match(query: str, urls: list[str]) -> tuple[str | None, int]:
    terms = {part for part in re.findall(r"[a-z0-9]+", query.lower()) if len(part) > 2}
    if not terms:
        return None, 0
    best_url = None
    best_score = 0
    for url in urls:
        page_terms = set(re.findall(r"[a-z0-9]+", url.lower()))
        score = len(terms & page_terms)
        if score > best_score:
            best_url = url
            best_score = score
    return best_url, best_score


def ctr_recommendations(query: str, page: str | None) -> list[str]:
    target = page.replace("https://globalhomeatlas.com", "") if page else "the best matching page"
    return [
        f"Rewrite the title tag to make `{query}` or its buyer intent visible near the front.",
        "Rewrite the meta description with a concrete buyer promise, eligibility/risk cue, and destination-specific wording.",
        f"Add one query-matched internal anchor pointing to `{target}` from the guide hub or a closely related guide.",
        "Add or sharpen one FAQ that answers the exact query language without keyword stuffing.",
    ]


def slug_from_site_url(url: str) -> str | None:
    if not url.startswith("https://globalhomeatlas.com/"):
        return None
    path = url.replace("https://globalhomeatlas.com/", "", 1).strip("/")
    if not path or "/" in path:
        return None
    return path


def seo_page_slugs() -> set[str]:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from src.build_unified_app import SEO_PAGES

    return {str(page["slug"]) for page in SEO_PAGES}


def auto_internal_link_entry(finding: Finding) -> dict | None:
    if finding.kind not in AUTO_IMPLEMENTATION_KINDS:
        return None
    payload = finding.payload or {}
    target_slug = slug_from_site_url(str(payload.get("page") or ""))
    if not target_slug:
        return None
    if target_slug not in seo_page_slugs():
        return None
    source_slug = AUTO_INTERNAL_LINK_SOURCE_SLUG
    if source_slug == target_slug:
        source_slug = "best-countries-to-buy-property-as-a-foreigner"
    return {
        "type": "internal-link",
        "source_slug": source_slug,
        "target_slug": target_slug,
        "anchor": target_slug.replace("-", " "),
        "fingerprint": finding.fingerprint,
        "reason": finding.summary,
    }


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
    goals = report.get("goals", {})
    for goal in goals.get("page_goals", []):
        for field, label in (("index_status", "Indexing"), ("impression_status", "First impressions")):
            status_value = goal.get(field)
            if status_value not in {"at_risk", "missed"}:
                continue
            kind = "seo-goal-missed" if status_value == "missed" else "seo-goal-at-risk"
            severity = "high" if status_value == "missed" else "medium"
            findings.append(
                Finding(
                    kind=kind,
                    title=f"{label} goal {status_value.replace('_', ' ')} for {goal.get('url')}",
                    summary=(
                        f"{label} goal for `{goal.get('url')}` is `{status_value}`. "
                        f"Launch date: {goal.get('launch_date')}. "
                        f"Index deadline: {goal.get('indexed_deadline')}. "
                        f"Impression deadline: {goal.get('impressions_deadline')}."
                    ),
                    severity=severity,
                    labels=("analytics-loop", kind, "seo-opportunity", "needs-human-review"),
                    fingerprint=stable_fingerprint(kind, f"{field}:{goal.get('url')}"),
                    payload=goal,
                )
            )

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

    for row in sc.get("top_queries", []):
        query = row.get("query", "")
        impressions = int(row.get("impressions", 0) or 0)
        ctr = float(row.get("ctr", 0) or 0)
        position = float(row.get("position", 999) or 999)
        if impressions < QUERY_CTR_MIN_IMPRESSIONS or ctr >= QUERY_CTR_MAX_CTR or position > QUERY_CTR_MAX_POSITION:
            continue
        recommended_page, match_score = best_url_match(query, urls)
        if not recommended_page or match_score < 2:
            continue
        clicks = int(row.get("clicks", 0) or 0)
        findings.append(
            Finding(
                kind="query-ctr-opportunity",
                title=f"Improve query CTR for `{query}`",
                summary=(
                    f"Query `{query}` has {impressions} impressions, {clicks} clicks, "
                    f"{ctr * 100:.2f}% CTR, and average position {position:.1f}. "
                    f"Recommended page: {recommended_page}."
                ),
                severity="medium",
                labels=("analytics-loop", "seo-opportunity", "content-refresh", "query-ctr-opportunity", "needs-human-review"),
                fingerprint=stable_fingerprint("query-ctr-opportunity", f"{query}:{recommended_page}"),
                implementation_pr=True,
                payload={
                    **row,
                    "recommended_page": recommended_page,
                    "match_score": match_score,
                    "recommended_actions": ctr_recommendations(query, recommended_page),
                },
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
                implementation_pr=True,
                payload=row,
            )
        )

    for row in sc.get("near_ranking_pages", []):
        page = row.get("page", "")
        fingerprint = stable_fingerprint("near-ranking-opportunity", page)
        summary = (
            f"Page is ranking around position {row.get('position', 0):.1f} "
            f"with {row.get('impressions', 0)} impressions. Add internal links, sharpen title/meta, or improve page intent match."
        )
        provisional = Finding(
            kind="near-ranking-opportunity",
            title=f"Push near-ranking page higher: {page.replace('https://globalhomeatlas.com/', '/')}",
            summary=summary,
            severity="medium",
            labels=("analytics-loop", "seo-opportunity", "content-refresh", "needs-human-review"),
            fingerprint=fingerprint,
            implementation_pr=True,
            payload=row,
        )
        auto_entry = auto_internal_link_entry(provisional)
        labels = provisional.labels
        payload = row
        auto_safe = False
        if auto_entry:
            labels = ("analytics-loop", "seo-opportunity", "content-refresh", "auto-merge-safe")
            payload = {**row, "auto_implementation": auto_entry}
            auto_safe = True
        findings.append(
            Finding(
                kind="near-ranking-opportunity",
                title=provisional.title,
                summary=summary,
                severity="medium",
                labels=labels,
                fingerprint=fingerprint,
                auto_merge_safe=auto_safe,
                implementation_pr=True,
                auto_implementation_safe=auto_safe,
                payload=payload,
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
- Implementation PR candidate: `{finding.implementation_pr}`
- Auto implementation safe: `{finding.auto_implementation_safe}`

## Acceptance Criteria
- The issue is either fixed in a linked PR or explicitly closed as not actionable.
- The next analytics loop run does not recreate a duplicate issue with the same fingerprint.

## Raw Signal
```json
{payload}
```
"""


def control_issue_body(
    report: dict,
    findings: list[Finding],
    issue_links: list[str],
    pr_links: list[str],
    auto_merged: list[str],
    indexnow: dict,
) -> str:
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
- Sitemap resubmitted this run: `{sitemap.get('submission', {}).get('ok')}`
- Submitted URLs reported by Google: `{sitemap.get('indexing', {}).get('submitted_reported')}`
- Indexed URLs reported by Google: `{sitemap.get('indexing', {}).get('indexed_reported')}`
- Priority URLs in sitemap: `{sum(1 for item in sitemap.get('indexing', {}).get('priority_urls', []) if item.get('in_sitemap'))}`
- Priority URL inspections: `{len(priority_inspections)}`

## Priority URL Inspection Results
{format_priority_inspections(priority_inspections)}

## IndexNow Summary
{format_indexnow(indexnow)}

## SEO Goal Scorecard
{format_goal_scorecard(report.get('goals', {}))}

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


def normalize_github_mention(notify_user: str) -> str:
    return f"@{notify_user.strip().lstrip('@')}"


def build_notification_comment(
    *,
    notify_user: str,
    report: dict,
    findings: list[Finding],
    issue_links: list[str],
    pr_links: list[str],
    auto_merged: list[str],
    control_link: str,
) -> str:
    by_severity = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        by_severity[finding.severity] = by_severity.get(finding.severity, 0) + 1
    window = report.get("window", {})
    window_label = f"{window.get('start_date', 'n/a')} to {window.get('end_date', 'n/a')}"
    return f"""{normalize_github_mention(notify_user)} SEO feedback loop finished.

## Run Summary
- Generated: `{report.get('generated_at', 'n/a')}`
- Window: `{window_label}`
- High severity: `{by_severity.get('high', 0)}`
- Medium severity: `{by_severity.get('medium', 0)}`
- Low severity: `{by_severity.get('low', 0)}`
- Issues created or updated: `{len(issue_links)}`
- Draft PRs opened: `{len(pr_links)}`
- Auto-merged fixes: `{len(auto_merged)}`

## Next Action
{recommended_next_action(findings)}

[Control issue]({control_link})
"""


def format_indexnow(indexnow: dict) -> str:
    if not indexnow:
        return "- Not run"
    response = indexnow.get("response") or {}
    return "\n".join(
        [
            f"- Generated: `{indexnow.get('generated_at')}`",
            f"- Endpoint: `{indexnow.get('endpoint')}`",
            f"- Submitted URLs: `{indexnow.get('url_count')}`",
            f"- Key location: `{indexnow.get('key_location')}`",
            f"- Accepted: `{response.get('ok')}`",
            f"- HTTP status: `{response.get('status')}`",
            f"- Reason: `{response.get('reason')}`",
        ]
    )


def format_goal_scorecard(goals: dict) -> str:
    if not goals:
        return "- Not configured"
    lines = []
    for goal in goals.get("page_goals", []):
        inspection = goal.get("inspection") or {}
        analytics = goal.get("analytics") or {}
        lines.extend(
            [
                f"- Page: `{goal.get('url')}`",
                f"  - Launch date: `{goal.get('launch_date')}`",
                f"  - Indexed by: `{goal.get('indexed_deadline')}`; status `{goal.get('index_status')}`; signal `{inspection.get('coverage_state') or 'n/a'}`",
                f"  - First impressions by: `{goal.get('impressions_deadline')}`; status `{goal.get('impression_status')}`; impressions `{analytics.get('impressions', 0)}`",
            ]
        )
    template = goals.get("template_reuse") or {}
    lines.append(f"- Template reuse: `{template.get('completed_count', 0)}/{template.get('target_count', 4)}` seed pages published")
    for page in template.get("pages", []):
        lines.append(f"  - `{page.get('status')}` {page.get('url')}")
    return "\n".join(lines)


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
    if kinds & IMPLEMENTATION_PR_KINDS:
        return "Review implementation queue PRs for CTR, title, meta, FAQ, and internal-link changes."
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


def issue_label_names(issue: dict | None) -> set[str]:
    labels = (issue or {}).get("labels") or []
    names = set()
    for label in labels:
        if isinstance(label, dict) and label.get("name"):
            names.add(str(label["name"]))
        elif isinstance(label, str):
            names.add(label)
    return names


def implemented_awaiting_google(finding: Finding, issues: list[dict]) -> bool:
    issue = find_issue_by_fingerprint(issues, finding.fingerprint)
    return "implemented-awaiting-google" in issue_label_names(issue)


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
        gh_mutation(["gh", "issue", "edit", str(existing["number"]), "--body", body, "--add-label", labels])
        return existing.get("url", f"issue:{existing['number']}")
    completed = gh_mutation(["gh", "issue", "create", "--title", finding.title, "--body", body, "--label", labels])
    return completed.stdout.strip()


def create_or_update_control_issue(
    report: dict,
    findings: list[Finding],
    issue_links: list[str],
    pr_links: list[str],
    auto_merged: list[str],
    indexnow: dict,
    dry_run: bool,
) -> str:
    issues = list_issues() if not dry_run else []
    body = control_issue_body(report, findings, issue_links, pr_links, auto_merged, indexnow)
    existing = find_control_issue(issues)
    if dry_run:
        print(f"[dry-run] update control issue with {len(findings)} findings")
        return "dry-run:control-issue"
    labels = ",".join(CONTROL_LABELS)
    if existing:
        gh_mutation(["gh", "issue", "edit", str(existing["number"]), "--body", body, "--add-label", labels])
        return existing.get("url", f"issue:{existing['number']}")
    completed = gh_mutation(["gh", "issue", "create", "--title", CONTROL_ISSUE_TITLE, "--body", body, "--label", labels])
    return completed.stdout.strip()


def post_notification_comment(
    *,
    notify_user: str | None,
    report: dict,
    findings: list[Finding],
    issue_links: list[str],
    pr_links: list[str],
    auto_merged: list[str],
    control_link: str,
    dry_run: bool,
) -> str | None:
    if not notify_user:
        return None
    body = build_notification_comment(
        notify_user=notify_user,
        report=report,
        findings=findings,
        issue_links=issue_links,
        pr_links=pr_links,
        auto_merged=auto_merged,
        control_link=control_link,
    )
    if dry_run:
        print(f"[dry-run] comment on control issue and mention {normalize_github_mention(notify_user)}")
        return "dry-run:notification-comment"
    gh_mutation(["gh", "issue", "comment", control_link, "--body", body])
    return control_link


def implementation_candidate_content(finding: Finding, issue_url: str | None) -> str:
    payload = finding.payload or {}
    query = payload.get("query") or payload.get("page") or finding.title
    recommended_page = payload.get("recommended_page") or payload.get("page") or "Review the best matching page from the signal."
    actions = payload.get("recommended_actions") or ctr_recommendations(str(query), str(recommended_page))
    issue_line = issue_url or "Created or updated by the SEO feedback loop"
    action_lines = "\n".join(f"- {action}" for action in actions)
    payload_json = json.dumps(payload, indent=2, sort_keys=True)
    return f"""# SEO Implementation Candidate: {finding.title}

## Source Issue
{issue_line}

## Signal
{finding.summary}

## Target
- Query or page: `{query}`
- Recommended page: `{recommended_page}`
- Kind: `{finding.kind}`
- Severity: `{finding.severity}`

## Proposed Implementation
{action_lines}

## Acceptance Criteria
- Implement the approved title, meta, intro, FAQ, or internal-link updates in `src/build_unified_app.py`.
- Regenerate static artifacts.
- Run `python3 scripts/verify_static_site.py --min-sitemap-urls 65`.
- Run `python3 codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py`.
- Leave this PR as draft unless a human approves the content changes.
- After merge, keep the source issue open as `implemented-awaiting-google` until Search Console validates CTR, impressions, or position improvement.

## Fingerprint
`{finding.fingerprint}`

## Raw Signal
```json
{payload_json}
```
"""


def existing_pr_for_branch(branch: str, dry_run: bool) -> str | None:
    if dry_run:
        return None
    completed = run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            github_repository(),
            "--head",
            branch,
            "--state",
            "open",
            "--json",
            "url",
            "--limit",
            "1",
        ],
        check=False,
    )
    if completed.returncode != 0:
        return None
    try:
        rows = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        return None
    if rows:
        return rows[0].get("url")
    return None


def remote_branch_exists(branch: str, dry_run: bool) -> bool:
    if dry_run:
        return False
    completed = run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch], check=False)
    return completed.returncode == 0


def implementation_branch(finding: Finding) -> str:
    payload = finding.payload or {}
    key = str(payload.get("query") or payload.get("page") or finding.title)
    kind = slugify(finding.kind.replace("-opportunity", ""))
    fingerprint_suffix = finding.fingerprint.rsplit("-", 1)[-1]
    return f"analytics/implementation-{kind}-{slugify(key)[:40]}-{fingerprint_suffix}"


def auto_internal_link_branch(finding: Finding) -> str:
    entry = (finding.payload or {}).get("auto_implementation") or {}
    target = str(entry.get("target_slug") or (finding.payload or {}).get("page") or finding.title)
    fingerprint_suffix = finding.fingerprint.rsplit("-", 1)[-1]
    return f"analytics/auto-internal-link-{slugify(target)[:48]}-{fingerprint_suffix}"


def auto_internal_links_branch(findings: list[Finding]) -> str:
    fingerprints = sorted(finding.fingerprint for finding in findings)
    digest = hashlib.sha1(f"auto-internal-links:{'|'.join(fingerprints)}".encode("utf-8")).hexdigest()[:12]
    return f"analytics/auto-internal-links-{len(findings)}-{digest}"


def github_repository() -> str:
    return os.environ.get("GITHUB_REPOSITORY", "schlafen318/property-research-dashboard")


def base_branch() -> str:
    current = run(["git", "branch", "--show-current"]).stdout.strip()
    if current:
        return current
    return os.environ.get("GITHUB_REF_NAME") or os.environ.get("GITHUB_BASE_REF") or "main"


def implementation_pr_create_args(finding: Finding, branch: str, pr_body: str, base: str) -> list[str]:
    return [
        "gh",
        "pr",
        "create",
        "--repo",
        github_repository(),
        "--base",
        base,
        "--head",
        branch,
        "--draft",
        "--title",
        f"Queue SEO implementation: {finding.title}",
        "--body",
        pr_body,
        "--label",
        ",".join([*finding.labels, "implementation-queued"]),
    ]


def auto_internal_link_pr_create_args(finding: Finding, branch: str, pr_body: str, base: str) -> list[str]:
    return [
        "gh",
        "pr",
        "create",
        "--repo",
        github_repository(),
        "--base",
        base,
        "--head",
        branch,
        "--title",
        f"Auto-implement SEO internal link: {finding.title}",
        "--body",
        pr_body,
        "--label",
        ",".join([*finding.labels, "implementation-queued"]),
    ]


def load_auto_internal_link_entries(path: Path = SEO_AUTO_INTERNAL_LINKS_PATH) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def upsert_auto_internal_link_entry(entry: dict, path: Path = SEO_AUTO_INTERNAL_LINKS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = load_auto_internal_link_entries(path)
    fingerprint = entry.get("fingerprint")
    rows = [row for row in rows if row.get("fingerprint") != fingerprint]
    rows.append(entry)
    rows.sort(key=lambda row: (str(row.get("source_slug") or ""), str(row.get("target_slug") or ""), str(row.get("fingerprint") or "")))
    path.write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pending_auto_internal_link_pairs(
    pairs: list[tuple[Finding, str | None]],
    path: Path = SEO_AUTO_INTERNAL_LINKS_PATH,
) -> list[tuple[Finding, str | None]]:
    existing = {
        str(row.get("fingerprint")): row
        for row in load_auto_internal_link_entries(path)
        if row.get("fingerprint")
    }
    pending = []
    for finding, issue_url in pairs:
        entry = ((finding.payload or {}).get("auto_implementation") or {})
        fingerprint = str(entry.get("fingerprint") or "")
        if not fingerprint:
            continue
        current = existing.get(fingerprint)
        if current and current.get("source_slug") == entry.get("source_slug") and current.get("target_slug") == entry.get("target_slug"):
            continue
        pending.append((finding, issue_url))
    return pending


def scaffold_auto_internal_links_pr(
    pairs: list[tuple[Finding, str | None]],
    dry_run: bool,
    path: Path = SEO_AUTO_INTERNAL_LINKS_PATH,
) -> str | None:
    pending_pairs = pending_auto_internal_link_pairs(pairs, path)
    if not pending_pairs:
        return None
    findings = [finding for finding, _ in pending_pairs]
    branch = auto_internal_links_branch(findings)
    existing = existing_pr_for_branch(branch, dry_run)
    if existing:
        return existing
    if dry_run:
        print(f"[dry-run] create batched auto implementation PR branch {branch} with {len(findings)} internal links")
        return f"dry-run:auto-implementation-pr:{branch}"

    rows = []
    for finding, issue_url in pending_pairs:
        entry = (finding.payload or {}).get("auto_implementation") or {}
        rows.append(
            f"- `{entry.get('source_slug')}` -> `{entry.get('target_slug')}` "
            f"({issue_url or finding.fingerprint})"
        )
    pr_body = (
        "## Auto Implementation\n"
        "Adds approved internal links between existing guide pages. This PR is non-draft because it does not rewrite editorial copy.\n\n"
        "## Links\n"
        + "\n".join(rows)
        + f"\n\n## Machine-owned file\n`{SEO_AUTO_INTERNAL_LINKS_PATH.relative_to(ROOT)}`\n"
    )
    base = base_branch()
    if remote_branch_exists(branch, dry_run):
        completed = run(auto_internal_link_pr_create_args(findings[0], branch, pr_body, base))
        return completed.stdout.strip()

    run(["git", "switch", "-c", branch])
    try:
        for finding, _ in pending_pairs:
            upsert_auto_internal_link_entry((finding.payload or {}).get("auto_implementation") or {})
        run(["python3", "src/build_unified_app.py"])
        run(["python3", "scripts/verify_static_site.py", "--min-sitemap-urls", "65"])
        run(["python3", "codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py"])
        run(["git", "add", str(SEO_AUTO_INTERNAL_LINKS_PATH.relative_to(ROOT)), "artifacts"])
        if run(["git", "diff", "--cached", "--quiet"], check=False).returncode == 0:
            return None
        run(["git", "commit", "-m", f"Auto-add {len(findings)} SEO internal links"])
        run(["git", "push", "--set-upstream", "origin", branch])
        completed = run(auto_internal_link_pr_create_args(findings[0], branch, pr_body, base))
        return completed.stdout.strip()
    finally:
        run(["git", "switch", base], check=False)


def scaffold_auto_internal_link_pr(finding: Finding, issue_url: str | None, dry_run: bool) -> str | None:
    entry = ((finding.payload or {}).get("auto_implementation") or {})
    if not finding.auto_implementation_safe or entry.get("type") != "internal-link":
        return None
    branch = auto_internal_link_branch(finding)
    existing = existing_pr_for_branch(branch, dry_run)
    if existing:
        return existing
    if dry_run:
        print(f"[dry-run] create auto implementation PR branch {branch} with {SEO_AUTO_INTERNAL_LINKS_PATH.relative_to(ROOT)}")
        return f"dry-run:auto-implementation-pr:{branch}"

    pr_body = (
        f"{issue_body(finding)}\n"
        "## Auto Implementation\n"
        f"- Source issue: {issue_url or 'n/a'}\n"
        f"- Change: add approved internal link `{entry.get('source_slug')}` -> `{entry.get('target_slug')}`\n"
        f"- Machine-owned file: `{SEO_AUTO_INTERNAL_LINKS_PATH.relative_to(ROOT)}`\n"
        "- This PR is non-draft because it only links existing pages and does not rewrite editorial copy.\n"
    )
    base = base_branch()
    if remote_branch_exists(branch, dry_run):
        completed = run(auto_internal_link_pr_create_args(finding, branch, pr_body, base))
        return completed.stdout.strip()

    run(["git", "switch", "-c", branch])
    try:
        upsert_auto_internal_link_entry(entry)
        run(["python3", "src/build_unified_app.py"])
        run(["python3", "scripts/verify_static_site.py", "--min-sitemap-urls", "65"])
        run(["python3", "codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py"])
        run(["git", "add", str(SEO_AUTO_INTERNAL_LINKS_PATH.relative_to(ROOT)), "artifacts"])
        run(["git", "commit", "-m", f"Auto-add SEO internal link for {entry.get('target_slug')}"])
        run(["git", "push", "--set-upstream", "origin", branch])
        completed = run(auto_internal_link_pr_create_args(finding, branch, pr_body, base))
        return completed.stdout.strip()
    finally:
        run(["git", "switch", base], check=False)


def scaffold_implementation_pr(finding: Finding, issue_url: str | None, dry_run: bool) -> str | None:
    if not finding.implementation_pr or finding.kind not in IMPLEMENTATION_PR_KINDS:
        return None
    payload = finding.payload or {}
    key = str(payload.get("query") or payload.get("page") or finding.title)
    slug = slugify(key)
    branch = implementation_branch(finding)
    existing = existing_pr_for_branch(branch, dry_run)
    if existing:
        return existing
    path = ROOT / "docs" / "seo-implementation-queue" / f"{slug}.md"
    content = implementation_candidate_content(finding, issue_url)
    if dry_run:
        print(f"[dry-run] create implementation draft PR branch {branch} with {path.relative_to(ROOT)}")
        return f"dry-run:implementation-pr:{branch}"

    pr_body = (
        f"{issue_body(finding)}\n"
        "## Implementation Queue\n"
        f"- Source issue: {issue_url or 'n/a'}\n"
        f"- Candidate file: `{path.relative_to(ROOT)}`\n"
        "- Status: `implementation-queued`\n"
        "- This PR is intentionally draft until a human approves content changes.\n"
    )
    base = base_branch()
    if remote_branch_exists(branch, dry_run):
        completed = run(implementation_pr_create_args(finding, branch, pr_body, base))
        return completed.stdout.strip()

    run(["git", "switch", "-c", branch])
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        run(["git", "add", str(path.relative_to(ROOT))])
        run(["git", "commit", "-m", f"Queue SEO implementation for {key[:48]}"])
        run(["git", "push", "--set-upstream", "origin", branch])
        completed = run(implementation_pr_create_args(finding, branch, pr_body, base))
        return completed.stdout.strip()
    finally:
        run(["git", "switch", base], check=False)


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
    completed = run(["gh", "pr", "merge", pr_url, "--squash", "--auto"], check=False)
    if completed.returncode != 0:
        stderr = getattr(completed, "stderr", "")
        if stderr:
            print(stderr, file=sys.stderr)
        return None
    return pr_url


def tracking_status() -> bool:
    completed = run(["python3", "codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py"], check=False)
    return completed.returncode == 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Turn SEO monitor output into GitHub issues and draft PRs.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--indexnow-report", type=Path, default=DEFAULT_INDEXNOW_REPORT)
    parser.add_argument("--summary-output", type=Path, help="Write a JSON summary of findings, issues, PRs, and notifications.")
    parser.add_argument("--notify-user", help="GitHub username to mention on the control issue after each run.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.dry_run and not args.apply:
        raise SystemExit("Pass --dry-run or --apply.")
    report = load_report(args.report)
    indexnow = load_optional_json(args.indexnow_report)
    dry_run = args.dry_run
    tracking_ok = tracking_status()
    findings = classify(report, tracking_ok)

    ensure_labels(dry_run)
    issues = list_issues() if not dry_run else []
    issue_links = [create_or_update_issue(finding, issues, dry_run) for finding in findings]
    pr_links: list[str] = []
    auto_merged: list[str] = []
    auto_internal_link_pairs: list[tuple[Finding, str | None]] = []
    for finding, issue_link in zip(findings, issue_links):
        pr_url = scaffold_landing_page_pr(finding, dry_run)
        if pr_url:
            pr_links.append(pr_url)
        if finding.auto_implementation_safe:
            auto_internal_link_pairs.append((finding, issue_link))
            continue
        if implemented_awaiting_google(finding, issues):
            continue
        implementation_pr_url = scaffold_implementation_pr(finding, issue_link, dry_run)
        if implementation_pr_url:
            pr_links.append(implementation_pr_url)
        merge_url = maybe_auto_merge(pr_url, finding, dry_run)
        if merge_url:
            auto_merged.append(merge_url)
    auto_pr_url = scaffold_auto_internal_links_pr(auto_internal_link_pairs, dry_run)
    if auto_pr_url:
        pr_links.append(auto_pr_url)
        auto_finding = auto_internal_link_pairs[0][0]
        merge_url = maybe_auto_merge(auto_pr_url, auto_finding, dry_run)
        if merge_url:
            auto_merged.append(merge_url)
    control_link = create_or_update_control_issue(report, findings, issue_links, pr_links, auto_merged, indexnow, dry_run)
    notification = post_notification_comment(
        notify_user=args.notify_user,
        report=report,
        findings=findings,
        issue_links=issue_links,
        pr_links=pr_links,
        auto_merged=auto_merged,
        control_link=control_link,
        dry_run=dry_run,
    )
    summary = {
        "findings": [
            {
                "kind": finding.kind,
                "title": finding.title,
                "summary": finding.summary,
                "severity": finding.severity,
                "labels": list(finding.labels),
                "fingerprint": finding.fingerprint,
                "auto_merge_safe": finding.auto_merge_safe,
                "draft_pr": finding.draft_pr,
                "implementation_pr": finding.implementation_pr,
                "auto_implementation_safe": finding.auto_implementation_safe,
            }
            for finding in findings
        ],
        "issue_count": len(issue_links),
        "issues": issue_links,
        "pr_count": len(pr_links),
        "prs": pr_links,
        "auto_merged_count": len(auto_merged),
        "auto_merged": auto_merged,
        "control": control_link,
        "notification": notification,
    }
    if args.summary_output:
        args.summary_output.parent.mkdir(parents=True, exist_ok=True)
        args.summary_output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
