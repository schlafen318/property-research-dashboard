from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_URL = "sc-domain:globalhomeatlas.com"
DEFAULT_SITEMAP = "https://globalhomeatlas.com/sitemap.xml"
DEFAULT_TOKEN = ROOT / "tmp" / "globalhomeatlas-google-token.json"
DEFAULT_OUTPUT = ROOT / "output" / "seo"


def fetch_sitemap(url: str) -> list[str]:
    with urllib.request.urlopen(url, timeout=30) as response:
        body = response.read()
    root = ET.fromstring(body)
    return [
        node.text or ""
        for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if node.text
    ]


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


def sitemap_status(service, site_url: str, sitemap_url: str) -> dict:
    for item in service.sitemaps().list(siteUrl=site_url).execute().get("sitemap", []):
        if item.get("path") == sitemap_url:
            return item
    return {}


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


def build_report(args: argparse.Namespace) -> tuple[str, Path | None]:
    today = dt.date.today()
    end_date = args.end_date or (today - dt.timedelta(days=1)).isoformat()
    start_date = args.start_date or (dt.date.fromisoformat(end_date) - dt.timedelta(days=args.days - 1)).isoformat()
    sitemap_urls = fetch_sitemap(args.sitemap)
    destination_count = sum("/destinations/" in url for url in sitemap_urls)
    trust_count = sum(url.rstrip("/").split("/")[-1] in {"methodology", "research-standards", "about", "contact"} for url in sitemap_urls)

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
        status = sitemap_status(service, args.site_url, args.sitemap)
        lines.extend(
            [
                "## Search Console Sitemap Status",
                "",
                f"- Last submitted: {status.get('lastSubmitted', 'n/a')}",
                f"- Last downloaded: {status.get('lastDownloaded', 'n/a')}",
                f"- Pending: {status.get('isPending', 'n/a')}",
                f"- Warnings: {status.get('warnings', 'n/a')}",
                f"- Errors: {status.get('errors', 'n/a')}",
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

    report = "\n".join(lines)
    output_path = None
    if args.write:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = args.output_dir / f"seo-monitor-{today.isoformat()}.md"
        output_path.write_text(report, encoding="utf-8")
    return report, output_path


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
    parser.add_argument("--write", action="store_true", help="Write the report to output/seo/.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report, output_path = build_report(args)
    print(report)
    if output_path:
        print(f"\nWrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
