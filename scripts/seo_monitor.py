from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_URL = "sc-domain:globalhomeatlas.com"
DEFAULT_SITEMAP = "https://globalhomeatlas.com/sitemap.xml"
DEFAULT_TOKEN = ROOT / "tmp" / "globalhomeatlas-google-token.json"
DEFAULT_OUTPUT = ROOT / "output" / "seo"
DEFAULT_JSON_OUTPUT = DEFAULT_OUTPUT / "latest.json"
PRIORITY_INDEXING_PATHS = [
    "/",
    "/guides/",
    "/countries/spain-property/",
    "/countries/portugal-property/",
    "/countries/japan-property/",
    "/countries/thailand-property/",
    "/countries/greece-property/",
    "/countries/italy-property/",
    "/countries/switzerland-property/",
    "/buy-property-abroad/",
    "/best-countries-to-buy-property-as-a-foreigner/",
    "/buying-property-abroad-for-retirement/",
    "/best-places-to-buy-a-second-home-abroad/",
    "/foreign-property-investment-risks/",
    "/where-can-foreigners-buy-property/",
    "/overseas-property-investment/",
    "/best-places-to-buy-property-abroad-for-retirement/",
    "/best-places-to-buy-vacation-home-abroad/",
]
TRACKED_SEO_GOALS = [
    {
        "name": "Spain country hub",
        "url": "https://globalhomeatlas.com/countries/spain-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Portugal country hub",
        "url": "https://globalhomeatlas.com/countries/portugal-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Japan country hub",
        "url": "https://globalhomeatlas.com/countries/japan-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Thailand country hub",
        "url": "https://globalhomeatlas.com/countries/thailand-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Greece country hub",
        "url": "https://globalhomeatlas.com/countries/greece-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Italy country hub",
        "url": "https://globalhomeatlas.com/countries/italy-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Switzerland country hub",
        "url": "https://globalhomeatlas.com/countries/switzerland-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Buying guides hub",
        "url": "https://globalhomeatlas.com/guides/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Foreign-buyer landing page",
        "url": "https://globalhomeatlas.com/best-countries-to-buy-property-as-a-foreigner/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Retirement abroad landing page",
        "url": "https://globalhomeatlas.com/buying-property-abroad-for-retirement/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Second-home abroad landing page",
        "url": "https://globalhomeatlas.com/best-places-to-buy-a-second-home-abroad/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Foreign property risks landing page",
        "url": "https://globalhomeatlas.com/foreign-property-investment-risks/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
    {
        "name": "Where foreigners can buy landing page",
        "url": "https://globalhomeatlas.com/where-can-foreigners-buy-property/",
        "launch_date": "2026-06-23",
        "indexed_deadline": "2026-06-30",
        "impressions_at_risk_date": "2026-07-07",
        "impressions_deadline": "2026-07-23",
    },
]
SEED_TEMPLATE_PAGES = [
    {
        "title": "Buying Property Abroad for Retirement",
        "url": "https://globalhomeatlas.com/buying-property-abroad-for-retirement/",
        "status": "published",
    },
    {
        "title": "Best Places to Buy a Second Home Abroad",
        "url": "https://globalhomeatlas.com/best-places-to-buy-a-second-home-abroad/",
        "status": "published",
    },
    {
        "title": "Foreign Property Investment Risks",
        "url": "https://globalhomeatlas.com/foreign-property-investment-risks/",
        "status": "published",
    },
    {
        "title": "Where Can Foreigners Buy Property",
        "url": "https://globalhomeatlas.com/where-can-foreigners-buy-property/",
        "status": "published",
    },
]


def fetch_sitemap(url: str) -> list[str]:
    with urllib.request.urlopen(url, timeout=30) as response:
        body = response.read()
    root = ET.fromstring(body)
    return [
        node.text or ""
        for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if node.text
    ]


def token_from_env(token_path: Path) -> None:
    token_json = os.environ.get("GOOGLE_SEARCH_CONSOLE_TOKEN_JSON", "").strip()
    if not token_json or token_path.exists():
        return
    token_path.parent.mkdir(parents=True, exist_ok=True)
    token_path.write_text(token_json, encoding="utf-8")


def load_search_console(token_path: Path):
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise SystemExit(
            "Google API libraries are not installed in this environment. "
            "Install google-api-python-client and google-auth, or run sitemap-only mode."
        ) from exc

    creds = Credentials.from_authorized_user_file(
        str(token_path),
        scopes=["https://www.googleapis.com/auth/webmasters"],
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("searchconsole", "v1", credentials=creds)


def search_analytics(service, site_url: str, start_date: str, end_date: str, dimensions: list[str], row_limit: int = 25):
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit,
    }
    return service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])


def page_analytics(service, site_url: str, start_date: str, end_date: str, page_url: str) -> dict:
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "dimensionFilterGroups": [
            {
                "filters": [
                    {
                        "dimension": "page",
                        "operator": "equals",
                        "expression": page_url,
                    }
                ]
            }
        ],
        "rowLimit": 1,
    }
    rows = service.searchanalytics().query(siteUrl=site_url, body=body).execute().get("rows", [])
    if not rows:
        return {"page": page_url, "clicks": 0, "impressions": 0, "ctr": 0, "position": 0}
    return row_to_dict(rows[0], ["page"])


def sitemap_status(service, site_url: str, sitemap_url: str) -> dict:
    for item in service.sitemaps().list(siteUrl=site_url).execute().get("sitemap", []):
        if item.get("path") == sitemap_url:
            return item
    return {}


def submit_sitemap(service, site_url: str, sitemap_url: str) -> dict:
    try:
        service.sitemaps().submit(siteUrl=site_url, feedpath=sitemap_url).execute()
        return {"ok": True, "sitemap": sitemap_url}
    except Exception as exc:
        return {"ok": False, "sitemap": sitemap_url, "error": str(exc)}


def sitemap_index_counts(status: dict) -> tuple[int | None, int | None]:
    submitted = None
    indexed = None
    for item in status.get("contents", []) or []:
        if item.get("type") != "web":
            continue
        try:
            submitted = int(item.get("submitted"))
        except (TypeError, ValueError):
            submitted = None
        try:
            indexed = int(item.get("indexed"))
        except (TypeError, ValueError):
            indexed = None
    return submitted, indexed


def priority_indexing_urls(sitemap_urls: list[str]) -> list[dict]:
    sitemap_set = set(sitemap_urls)
    rows = []
    for path in PRIORITY_INDEXING_PATHS:
        url = "https://globalhomeatlas.com/" if path == "/" else f"https://globalhomeatlas.com{path}"
        rows.append({"url": url, "in_sitemap": url in sitemap_set})
    return rows


def inspect_url(service, site_url: str, url: str) -> dict:
    try:
        response = (
            service.urlInspection()
            .index()
            .inspect(body={"inspectionUrl": url, "siteUrl": site_url, "languageCode": "en-US"})
            .execute()
        )
    except Exception as exc:  # Google client exceptions vary by transport/version.
        return {"url": url, "ok": False, "error": str(exc)}

    result = response.get("inspectionResult", {})
    index_status = result.get("indexStatusResult", {})
    mobile_status = result.get("mobileUsabilityResult", {})
    rich_results = result.get("richResultsResult", {})
    return {
        "url": url,
        "ok": True,
        "verdict": index_status.get("verdict"),
        "coverage_state": index_status.get("coverageState"),
        "indexing_state": index_status.get("indexingState"),
        "robots_txt_state": index_status.get("robotsTxtState"),
        "page_fetch_state": index_status.get("pageFetchState"),
        "last_crawl_time": index_status.get("lastCrawlTime"),
        "google_canonical": index_status.get("googleCanonical"),
        "user_canonical": index_status.get("userCanonical"),
        "sitemap": index_status.get("sitemap"),
        "referring_urls": index_status.get("referringUrls", []),
        "mobile_verdict": mobile_status.get("verdict"),
        "rich_results_verdict": rich_results.get("verdict"),
    }


def inspect_priority_urls(service, site_url: str, priority_urls: list[dict], enabled: bool) -> list[dict]:
    if not enabled:
        return []
    return [inspect_url(service, site_url, item["url"]) for item in priority_urls if item.get("in_sitemap")]


def fmt_inspections(inspections: list[dict]) -> str:
    if not inspections:
        return "_Priority URL inspection was skipped._\n"
    out = [
        "| URL | Verdict | Coverage | Fetch | Last crawl | Canonical |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in inspections:
        if not item.get("ok"):
            out.append(f"| {item.get('url')} | error | {str(item.get('error', 'n/a'))[:120]} | n/a | n/a | n/a |")
            continue
        out.append(
            "| "
            + " | ".join(
                [
                    item.get("url") or "",
                    item.get("verdict") or "n/a",
                    item.get("coverage_state") or "n/a",
                    item.get("page_fetch_state") or "n/a",
                    item.get("last_crawl_time") or "n/a",
                    item.get("google_canonical") or item.get("user_canonical") or "n/a",
                ]
            )
            + " |"
        )
    return "\n".join(out) + "\n"


def inspection_by_url(inspections: list[dict], url: str) -> dict:
    for item in inspections:
        if item.get("url") == url:
            return item
    return {}


def status_for_indexing(today: dt.date, goal: dict, inspection: dict) -> str:
    if inspection.get("verdict") == "PASS":
        return "met"
    launch = dt.date.fromisoformat(goal["launch_date"])
    deadline = dt.date.fromisoformat(goal["indexed_deadline"])
    if today > deadline:
        return "missed"
    if (today - launch).days >= 5:
        return "at_risk"
    return "on_track"


def status_for_impressions(today: dt.date, goal: dict, analytics: dict) -> str:
    if int(analytics.get("impressions") or 0) > 0:
        return "met"
    at_risk = dt.date.fromisoformat(goal["impressions_at_risk_date"])
    deadline = dt.date.fromisoformat(goal["impressions_deadline"])
    if today > deadline:
        return "missed"
    if today >= at_risk:
        return "at_risk"
    return "on_track"


def build_goal_scorecard(today: dt.date, inspections: list[dict], page_metrics: dict[str, dict]) -> dict:
    page_goals = []
    for goal in TRACKED_SEO_GOALS:
        inspection = inspection_by_url(inspections, goal["url"])
        analytics = page_metrics.get(goal["url"], {"page": goal["url"], "clicks": 0, "impressions": 0, "ctr": 0, "position": 0})
        page_goals.append(
            {
                **goal,
                "index_status": status_for_indexing(today, goal, inspection),
                "impression_status": status_for_impressions(today, goal, analytics),
                "inspection": inspection,
                "analytics": analytics,
            }
        )
    return {
        "generated_for": today.isoformat(),
        "page_goals": page_goals,
        "template_reuse": {
            "target_count": 4,
            "completed_count": sum(1 for item in SEED_TEMPLATE_PAGES if item["status"] == "published"),
            "pages": SEED_TEMPLATE_PAGES,
        },
    }


def fmt_goal_scorecard(scorecard: dict) -> str:
    rows = [
        "| Goal | Launch | Deadline | Current signal | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for goal in scorecard.get("page_goals", []):
        inspection = goal.get("inspection") or {}
        analytics = goal.get("analytics") or {}
        rows.append(
            "| "
            + " | ".join(
                [
                    f"Index {goal['url']}",
                    goal["launch_date"],
                    goal["indexed_deadline"],
                    inspection.get("coverage_state") or "n/a",
                    goal["index_status"],
                ]
            )
            + " |"
        )
        rows.append(
            "| "
            + " | ".join(
                [
                    f"First impressions {goal['url']}",
                    goal["launch_date"],
                    goal["impressions_deadline"],
                    str(analytics.get("impressions", 0)),
                    goal["impression_status"],
                ]
            )
            + " |"
        )
    template = scorecard.get("template_reuse", {})
    rows.append(
        f"| Reuse template for next 4 seed pages | n/a | n/a | {template.get('completed_count', 0)}/{template.get('target_count', 4)} published | on_track |"
    )
    return "\n".join(rows) + "\n"


def fmt_rows(rows: list[dict], headers: list[str]) -> str:
    if not rows:
        return "_No rows returned for this period._\n"
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        keys = row.get("keys", [])
        metric_cells = [
            str(row.get("clicks", 0)),
            str(row.get("impressions", 0)),
            f"{row.get('ctr', 0) * 100:.2f}%",
            f"{row.get('position', 0):.1f}",
        ]
        out.append("| " + " | ".join([*(str(item) for item in keys), *metric_cells]) + " |")
    return "\n".join(out) + "\n"


def row_to_dict(row: dict, dimensions: list[str]) -> dict:
    keys = row.get("keys", [])
    result = {dimension: keys[index] if index < len(keys) else "" for index, dimension in enumerate(dimensions)}
    result.update(
        {
            "clicks": row.get("clicks", 0),
            "impressions": row.get("impressions", 0),
            "ctr": row.get("ctr", 0),
            "position": row.get("position", 0),
        }
    )
    return result


def page_matches_query(query: str, page_url: str) -> bool:
    query_terms = {part for part in re_words(query) if len(part) > 2}
    page_terms = {part for part in re_words(page_url.replace("https://globalhomeatlas.com/", "")) if len(part) > 2}
    if not query_terms:
        return False
    return len(query_terms & page_terms) >= min(2, len(query_terms))


def re_words(value: str) -> list[str]:
    return [part.lower() for part in re_find_words(value)]


def re_find_words(value: str) -> list[str]:
    import re

    return re.findall(r"[a-zA-Z0-9]+", value)


def build_report(args: argparse.Namespace) -> tuple[str, dict, Path | None, Path | None]:
    today = dt.date.today()
    end_date = args.end_date or (today - dt.timedelta(days=1)).isoformat()
    start_date = args.start_date or (dt.date.fromisoformat(end_date) - dt.timedelta(days=args.days - 1)).isoformat()
    token_from_env(args.token)
    sitemap_urls = fetch_sitemap(args.sitemap)
    destination_count = sum("/destinations/" in url for url in sitemap_urls)
    trust_count = sum(url.rstrip("/").split("/")[-1] in {"methodology", "research-standards", "about", "contact"} for url in sitemap_urls)
    status: dict = {}
    sitemap_submission: dict = {}
    priority_urls = priority_indexing_urls(sitemap_urls)
    priority_inspections: list[dict] = []
    tracked_page_metrics: dict[str, dict] = {}
    query_rows: list[dict] = []
    page_rows: list[dict] = []
    low_ctr_rows: list[dict] = []
    near_ranking_rows: list[dict] = []
    content_gap_rows: list[dict] = []

    lines = [
        f"# Global Home Atlas SEO Monitor - {today.isoformat()}",
        "",
        "## Sitemap",
        "",
        f"- Sitemap: `{args.sitemap}`",
        f"- URLs: {len(sitemap_urls)}",
        f"- Destination pages: {destination_count}",
        f"- Trust pages: {trust_count}",
        f"- Reporting window: {start_date} to {end_date}",
        "",
    ]

    if args.token.exists():
        service = load_search_console(args.token)
        if args.submit_sitemap:
            sitemap_submission = submit_sitemap(service, args.site_url, args.sitemap)
        status = sitemap_status(service, args.site_url, args.sitemap)
        submitted_count, indexed_count = sitemap_index_counts(status)
        priority_inspections = inspect_priority_urls(service, args.site_url, priority_urls, args.inspect_priority_urls)
        lines.extend(
            [
                "## Search Console Sitemap Status",
                "",
                f"- Last submitted: {status.get('lastSubmitted', 'n/a')}",
                f"- Last downloaded: {status.get('lastDownloaded', 'n/a')}",
                f"- Pending: {status.get('isPending', 'n/a')}",
                f"- Warnings: {status.get('warnings', 'n/a')}",
                f"- Errors: {status.get('errors', 'n/a')}",
                f"- Submitted URLs reported by Google: {submitted_count if submitted_count is not None else 'n/a'}",
                f"- Indexed URLs reported by Google: {indexed_count if indexed_count is not None else 'n/a'}",
                f"- Sitemap resubmitted this run: {sitemap_submission.get('ok', False)}",
                "",
            ]
        )
        query_rows = search_analytics(service, args.site_url, start_date, end_date, ["query"], args.row_limit)
        page_rows = search_analytics(service, args.site_url, start_date, end_date, ["page"], args.row_limit)
        low_ctr_rows = [
            row
            for row in page_rows
            if row.get("impressions", 0) >= args.low_ctr_impressions and row.get("ctr", 0) < args.low_ctr_threshold
        ]
        near_ranking_rows = [
            row
            for row in page_rows
            if row.get("impressions", 0) >= args.near_ranking_impressions
            and args.near_ranking_min_position <= row.get("position", 999) <= args.near_ranking_max_position
        ]
        content_gap_rows = [
            row
            for row in query_rows
            if row.get("impressions", 0) >= args.content_gap_impressions
            and not any(page_matches_query(row.get("keys", [""])[0], url) for url in sitemap_urls)
        ]
        tracked_page_metrics = {
            goal["url"]: page_analytics(service, args.site_url, start_date, end_date, goal["url"])
            for goal in TRACKED_SEO_GOALS
        }
        goal_scorecard = build_goal_scorecard(today, priority_inspections, tracked_page_metrics)
        lines.extend(
            [
                "## Top Queries",
                "",
                fmt_rows(query_rows, ["Query", "Clicks", "Impressions", "CTR", "Position"]),
                "## Top Pages",
                "",
                fmt_rows(page_rows, ["Page", "Clicks", "Impressions", "CTR", "Position"]),
                "## Pages With Impressions But Low CTR",
                "",
                fmt_rows(low_ctr_rows, ["Page", "Clicks", "Impressions", "CTR", "Position"]),
                "## Pages Ranking 8-30",
                "",
                fmt_rows(near_ranking_rows, ["Page", "Clicks", "Impressions", "CTR", "Position"]),
                "## New Query Content Gaps",
                "",
                fmt_rows(content_gap_rows, ["Query", "Clicks", "Impressions", "CTR", "Position"]),
                "## Priority Indexing Checklist",
                "",
                "| URL | In sitemap | Manual action |",
                "| --- | --- | --- |",
                *[
                    f"| {item['url']} | {item['in_sitemap']} | Inspect URL and request indexing if not indexed |"
                    for item in priority_urls
                ],
                "",
                "## Priority URL Inspection API Results",
                "",
                fmt_inspections(priority_inspections),
                "## SEO Goal Scorecard",
                "",
                fmt_goal_scorecard(goal_scorecard),
            ]
        )
    else:
        lines.extend(
            [
                "## Search Console",
                "",
                f"_Skipped because token file was not found at `{args.token}`._",
                "",
            ]
        )

    goal_scorecard = build_goal_scorecard(today, priority_inspections, tracked_page_metrics)
    report = "\n".join(lines)
    data = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "site_url": args.site_url,
        "sitemap": {
            "url": args.sitemap,
            "url_count": len(sitemap_urls),
            "destination_count": destination_count,
            "trust_count": trust_count,
            "urls": sitemap_urls,
            "status": status,
            "submission": sitemap_submission,
            "indexing": {
                "submitted_reported": sitemap_index_counts(status)[0],
                "indexed_reported": sitemap_index_counts(status)[1],
                "priority_urls": priority_urls,
                "priority_inspections": priority_inspections,
            },
        },
        "window": {"start_date": start_date, "end_date": end_date, "days": args.days},
        "thresholds": {
            "low_ctr_impressions": args.low_ctr_impressions,
            "low_ctr_threshold": args.low_ctr_threshold,
            "near_ranking_impressions": args.near_ranking_impressions,
            "near_ranking_min_position": args.near_ranking_min_position,
            "near_ranking_max_position": args.near_ranking_max_position,
            "content_gap_impressions": args.content_gap_impressions,
        },
        "search_console": {
            "available": args.token.exists(),
            "top_queries": [row_to_dict(row, ["query"]) for row in query_rows],
            "top_pages": [row_to_dict(row, ["page"]) for row in page_rows],
            "low_ctr_pages": [row_to_dict(row, ["page"]) for row in low_ctr_rows],
            "near_ranking_pages": [row_to_dict(row, ["page"]) for row in near_ranking_rows],
            "content_gap_queries": [row_to_dict(row, ["query"]) for row in content_gap_rows],
        },
        "goals": goal_scorecard,
    }
    output_path = None
    json_output_path = None
    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output_dir / f"seo-monitor-{today.isoformat()}.md"
        output_path.write_text(report, encoding="utf-8")
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        json_output_path = args.json_output
    return report, data, output_path, json_output_path


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Global Home Atlas SEO monitoring report.")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--sitemap", default=DEFAULT_SITEMAP)
    parser.add_argument("--token", type=Path, default=DEFAULT_TOKEN)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--row-limit", type=int, default=25)
    parser.add_argument("--low-ctr-impressions", type=int, default=20)
    parser.add_argument("--low-ctr-threshold", type=float, default=0.01)
    parser.add_argument("--near-ranking-impressions", type=int, default=20)
    parser.add_argument("--near-ranking-min-position", type=float, default=8)
    parser.add_argument("--near-ranking-max-position", type=float, default=30)
    parser.add_argument("--content-gap-impressions", type=int, default=20)
    parser.add_argument("--inspect-priority-urls", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--submit-sitemap", action="store_true")
    parser.add_argument("--json-output", type=Path, default=None)
    parser.add_argument("--write", action="store_true", help="Write the report to output/seo/.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.write and args.json_output is None:
        args.json_output = DEFAULT_JSON_OUTPUT
    report, _, output_path, json_output_path = build_report(args)
    print(report)
    if output_path:
        print(f"\nWrote {output_path}")
    if json_output_path:
        print(f"Wrote {json_output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
