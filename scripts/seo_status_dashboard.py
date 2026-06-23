from __future__ import annotations

import argparse
import datetime as dt
import json
from html import escape
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "output" / "seo" / "latest.json"
DEFAULT_INDEXNOW = ROOT / "output" / "seo" / "indexnow-latest.json"
DEFAULT_OUTPUT = ROOT / "artifacts" / "seo-status" / "index.html"
SITE_URL = "https://globalhomeatlas.com/"


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def page_path(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "/"
    return path if path == "/" else path.rstrip("/") + "/"


def status_label(value: str | None) -> str:
    labels = {
        "met": "Met",
        "on_track": "On track",
        "at_risk": "At risk",
        "missed": "Missed",
    }
    return labels.get(value or "", value or "Unknown")


def status_class(value: str | None) -> str:
    if value in {"met", "on_track"}:
        return "good"
    if value == "at_risk":
        return "warn"
    if value == "missed":
        return "bad"
    return "neutral"


def fmt_int(value: object) -> str:
    if value is None:
        return "n/a"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def fmt_pct(value: object) -> str:
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return "n/a"


def fmt_position(value: object) -> str:
    try:
        number = float(value)
        return "n/a" if number == 0 else f"{number:.1f}"
    except (TypeError, ValueError):
        return "n/a"


def generated_label(value: str | None) -> str:
    if not value:
        return "n/a"
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return parsed.strftime("%Y-%m-%d %H:%M UTC")


def summarize_goals(goals: list[dict]) -> dict:
    indexed_met = sum(1 for goal in goals if goal.get("index_status") == "met")
    impression_met = sum(1 for goal in goals if goal.get("impression_status") == "met")
    at_risk = sum(
        1
        for goal in goals
        if goal.get("index_status") in {"at_risk", "missed"}
        or goal.get("impression_status") in {"at_risk", "missed"}
    )
    return {
        "tracked": len(goals),
        "indexed_met": indexed_met,
        "impression_met": impression_met,
        "at_risk": at_risk,
    }


def build_goal_rows(goals: list[dict]) -> str:
    rows = []
    for goal in goals:
        inspection = goal.get("inspection") or {}
        analytics = goal.get("analytics") or {}
        rows.append(
            f"""
            <tr>
              <td><a href="{escape(goal.get("url", ""))}">{escape(page_path(goal.get("url", "")))}</a><span>{escape(goal.get("name", ""))}</span></td>
              <td><strong>{escape(inspection.get("coverage_state") or "n/a")}</strong><span>{escape(inspection.get("verdict") or "n/a")}</span></td>
              <td><i class="pill {status_class(goal.get("index_status"))}">{escape(status_label(goal.get("index_status")))}</i><span>By {escape(goal.get("indexed_deadline", "n/a"))}</span></td>
              <td><i class="pill {status_class(goal.get("impression_status"))}">{escape(status_label(goal.get("impression_status")))}</i><span>{fmt_int(analytics.get("impressions"))} impressions by {escape(goal.get("impressions_deadline", "n/a"))}</span></td>
              <td>{fmt_int(analytics.get("clicks"))}<span>CTR {fmt_pct(analytics.get("ctr"))}, pos {fmt_position(analytics.get("position"))}</span></td>
            </tr>
            """
        )
    return "\n".join(rows) or '<tr><td colspan="5">No tracked goals yet.</td></tr>'


def build_priority_rows(priority_inspections: list[dict]) -> str:
    rows = []
    for item in priority_inspections:
        rows.append(
            f"""
            <tr>
              <td><a href="{escape(item.get("url", ""))}">{escape(page_path(item.get("url", "")))}</a></td>
              <td>{escape(item.get("coverage_state") or "n/a")}</td>
              <td><i class="pill {status_class("met" if item.get("verdict") == "PASS" else "on_track")}">{escape(item.get("verdict") or "n/a")}</i></td>
              <td>{escape(item.get("last_crawl_time") or "n/a")}</td>
            </tr>
            """
        )
    return "\n".join(rows) or '<tr><td colspan="4">No priority inspections available.</td></tr>'


def build_metric_rows(rows: list[dict], dimension: str) -> str:
    out = []
    for row in rows[:8]:
        key = row.get(dimension, "")
        out.append(
            f"""
            <tr>
              <td>{escape(str(key))}</td>
              <td>{fmt_int(row.get("clicks"))}</td>
              <td>{fmt_int(row.get("impressions"))}</td>
              <td>{fmt_pct(row.get("ctr"))}</td>
              <td>{fmt_position(row.get("position"))}</td>
            </tr>
            """
        )
    return "\n".join(out) or '<tr><td colspan="5">No Search Console rows returned yet.</td></tr>'


def next_action(report: dict, goals: list[dict]) -> str:
    missed = [goal for goal in goals if goal.get("index_status") == "missed"]
    at_risk = [goal for goal in goals if goal.get("index_status") == "at_risk"]
    unknown = [
        goal
        for goal in goals
        if (goal.get("inspection") or {}).get("coverage_state") == "URL is unknown to Google"
    ]
    if missed:
        return "Escalate missed indexing goals: add stronger homepage links, inspect manually in Search Console, and consider consolidating weak pages."
    if at_risk:
        return "Request indexing for at-risk pages and add one contextual internal link from the homepage or guide hub."
    if unknown:
        return "Inspect unknown URLs in Search Console and request indexing where available."
    if not report.get("search_console", {}).get("top_queries"):
        return "Wait for first query rows while continuing light internal-link and sitemap resubmission checks."
    return "Review top queries and prioritize CTR/title improvements for pages with impressions."


def build_html(report: dict, indexnow: dict) -> str:
    sitemap = report.get("sitemap", {})
    indexing = sitemap.get("indexing", {})
    search = report.get("search_console", {})
    goals_data = report.get("goals", {})
    goals = goals_data.get("page_goals", [])
    summary = summarize_goals(goals)
    indexnow_response = indexnow.get("response") or {}
    accepted = indexnow_response.get("accepted")
    title = "SEO Indexing Status | Global Home Atlas"
    description = "Operational SEO status dashboard for Global Home Atlas indexing, Search Console signals, and launch goals."

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="{SITE_URL}seo-status/">
  <meta name="robots" content="noindex,follow">
  <style>
    :root {{
      color: #16231f;
      background: #f7f4ee;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --ink: #16231f;
      --muted: #65736d;
      --line: rgba(22, 35, 31, .14);
      --paper: #fffdf8;
      --deep: #10241f;
      --teal: #176b62;
      --gold: #a77a35;
      --bad: #a33d2f;
      --warn: #9b6b18;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-width: 320px; }}
    a {{ color: var(--teal); text-underline-offset: 3px; overflow-wrap: anywhere; }}
    .shell {{ width: min(1180px, calc(100% - 32px)); margin: 0 auto; }}
    header {{ padding: 18px 0 46px; color: #fffdf8; background: linear-gradient(135deg, #10241f, #176b62 62%, #a77a35); }}
    nav {{ display: flex; justify-content: space-between; gap: 18px; align-items: center; margin-bottom: 54px; }}
    nav a {{ color: rgba(255, 253, 248, .88); font-weight: 850; text-decoration: none; }}
    .brand {{ color: #fffdf8; font-weight: 950; }}
    h1 {{ margin: 0; font-family: Georgia, "Times New Roman", serif; font-size: clamp(40px, 7vw, 82px); line-height: .96; letter-spacing: 0; }}
    .lede {{ max-width: 760px; color: rgba(255, 253, 248, .84); font-size: 18px; line-height: 1.6; }}
    main {{ margin-top: -28px; padding-bottom: 48px; }}
    .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1px; overflow: hidden; border: 1px solid var(--line); border-radius: 8px; background: var(--line); box-shadow: 0 18px 50px rgba(16, 36, 31, .08); }}
    .summary div {{ min-width: 0; padding: 16px; background: var(--paper); }}
    span, .eyebrow {{ display: block; color: var(--muted); font-size: 11px; font-weight: 900; letter-spacing: .06em; text-transform: uppercase; }}
    strong {{ display: block; margin-top: 5px; font-size: 22px; overflow-wrap: anywhere; }}
    .layout {{ display: grid; grid-template-columns: minmax(0, 1fr) 310px; gap: 22px; padding-top: 24px; align-items: start; }}
    .stack {{ display: grid; gap: 18px; min-width: 0; }}
    section, aside {{ border: 1px solid var(--line); border-radius: 8px; background: var(--paper); padding: 20px; }}
    h2 {{ margin: 0 0 12px; font-family: Georgia, "Times New Roman", serif; font-size: 30px; line-height: 1.05; }}
    p, li {{ color: #3f4d48; line-height: 1.65; }}
    .table-wrap {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 8px; background: #fff; }}
    table {{ width: 100%; min-width: 820px; border-collapse: collapse; }}
    th, td {{ padding: 12px; border-top: 1px solid var(--line); text-align: left; vertical-align: top; font-size: 13px; }}
    th {{ color: var(--muted); font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }}
    td span {{ margin-top: 5px; }}
    .pill {{ display: inline-flex; min-height: 24px; align-items: center; border-radius: 999px; padding: 0 9px; font-style: normal; font-size: 12px; font-weight: 900; }}
    .pill.good {{ color: #0f4f47; background: #dcefe8; }}
    .pill.warn {{ color: var(--warn); background: #f3e7c8; }}
    .pill.bad {{ color: var(--bad); background: #f3d5cf; }}
    .pill.neutral {{ color: #4d5854; background: #e9e5dc; }}
    .side {{ position: sticky; top: 16px; display: grid; gap: 14px; }}
    .side section {{ padding: 16px; }}
    .side h2, .side h3 {{ margin: 0 0 10px; font-size: 17px; }}
    .actions {{ display: grid; gap: 9px; }}
    .button {{ display: inline-flex; min-height: 42px; align-items: center; justify-content: center; border-radius: 6px; background: var(--deep); color: #fffdf8; padding: 0 14px; text-decoration: none; font-weight: 850; }}
    footer {{ padding: 28px 0 42px; color: var(--muted); border-top: 1px solid var(--line); }}
    @media (max-width: 860px) {{
      nav {{ align-items: flex-start; margin-bottom: 36px; }}
      .summary {{ grid-template-columns: repeat(2, 1fr); }}
      .layout {{ grid-template-columns: 1fr; }}
      .side {{ position: static; }}
    }}
    @media (max-width: 560px) {{
      .shell {{ width: min(100% - 28px, 1180px); }}
      .summary {{ grid-template-columns: 1fr; }}
      section, aside {{ padding: 16px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="shell">
      <nav aria-label="Primary">
        <a class="brand" href="/">Global Home Atlas</a>
        <a href="/guides/">Guides</a>
      </nav>
      <p class="eyebrow">Operational SEO dashboard</p>
      <h1>SEO Indexing Status</h1>
      <p class="lede">Tracks indexing, first-impression goals, sitemap submission, and Search Console signals for the current Global Home Atlas SEO launch cycle.</p>
    </div>
  </header>
  <main>
    <div class="shell">
      <section class="summary" aria-label="SEO status summary">
        <div><span>Generated</span><strong>{escape(generated_label(report.get("generated_at")))}</strong></div>
        <div><span>Sitemap URLs</span><strong>{fmt_int(sitemap.get("url_count"))}</strong></div>
        <div><span>Tracked goals</span><strong>{summary["tracked"]}</strong></div>
        <div><span>At risk</span><strong>{summary["at_risk"]}</strong></div>
      </section>
      <div class="layout">
        <div class="stack">
          <section>
            <h2>Launch Goals</h2>
            <p>Measurable targets: index tracked pages within seven days of launch, then generate first impressions within 14-30 days.</p>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Page</th><th>Google signal</th><th>Index target</th><th>Impression target</th><th>Traffic</th></tr></thead>
                <tbody>{build_goal_rows(goals)}</tbody>
              </table>
            </div>
          </section>
          <section>
            <h2>Priority URL Inspections</h2>
            <div class="table-wrap">
              <table>
                <thead><tr><th>URL</th><th>Coverage</th><th>Verdict</th><th>Last crawl</th></tr></thead>
                <tbody>{build_priority_rows(indexing.get("priority_inspections", []))}</tbody>
              </table>
            </div>
          </section>
          <section>
            <h2>Top Queries</h2>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Query</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Position</th></tr></thead>
                <tbody>{build_metric_rows(search.get("top_queries", []), "query")}</tbody>
              </table>
            </div>
          </section>
          <section>
            <h2>Top Pages</h2>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Page</th><th>Clicks</th><th>Impressions</th><th>CTR</th><th>Position</th></tr></thead>
                <tbody>{build_metric_rows(search.get("top_pages", []), "page")}</tbody>
              </table>
            </div>
          </section>
        </div>
        <aside class="side">
          <section>
            <h2>Next Action</h2>
            <p>{escape(next_action(report, goals))}</p>
            <div class="actions">
              <a class="button" href="https://search.google.com/search-console" rel="noreferrer">Open Search Console</a>
              <a class="button" href="https://github.com/schlafen318/property-research-dashboard/issues/1" rel="noreferrer">Control issue</a>
            </div>
          </section>
          <section>
            <h3>Sitemap</h3>
            <p>Submitted reported by Google: <strong>{fmt_int(indexing.get("submitted_reported"))}</strong></p>
            <p>Indexed reported by Google: <strong>{fmt_int(indexing.get("indexed_reported"))}</strong></p>
            <p>Pending: <strong>{escape(str((sitemap.get("status") or {}).get("isPending", "n/a")))}</strong></p>
          </section>
          <section>
            <h3>IndexNow</h3>
            <p>Submitted URLs: <strong>{fmt_int(indexnow.get("url_count"))}</strong></p>
            <p>Accepted: <strong>{escape(str(accepted if accepted is not None else "n/a"))}</strong></p>
            <p>HTTP status: <strong>{escape(str(indexnow_response.get("status") or "n/a"))}</strong></p>
          </section>
          <section>
            <h3>Template Reuse</h3>
            <p><strong>{fmt_int((goals_data.get("template_reuse") or {}).get("completed_count"))}/{fmt_int((goals_data.get("template_reuse") or {}).get("target_count"))}</strong> seed pages published.</p>
          </section>
        </aside>
      </div>
    </div>
  </main>
  <footer>
    <div class="shell">
      <strong>Global Home Atlas</strong>
      <p>This operational page is generated from Search Console and IndexNow reports. It is marked noindex because it is for workflow transparency, not search acquisition.</p>
    </div>
  </footer>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the Global Home Atlas SEO status dashboard.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--indexnow-report", type=Path, default=DEFAULT_INDEXNOW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = load_json(args.report)
    if not report:
        raise SystemExit(f"SEO report not found or empty: {args.report}")
    indexnow = load_json(args.indexnow_report)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_html(report, indexnow), encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
