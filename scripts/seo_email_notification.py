from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "output" / "seo" / "latest.json"
DEFAULT_INDEXNOW_REPORT = ROOT / "output" / "seo" / "indexnow-latest.json"
DEFAULT_FEEDBACK_SUMMARY = ROOT / "output" / "seo" / "feedback-loop-summary.json"
DEFAULT_CONTROL_URL = "https://github.com/schlafen318/property-research-dashboard/issues/1"
DEFAULT_DASHBOARD_URL = "https://globalhomeatlas.com/seo-status/"


@dataclass(frozen=True)
class MailConfig:
    host: str
    port: int
    username: str
    password: str
    sender: str
    recipient: str
    use_tls: bool


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def configured_from_env() -> MailConfig | None:
    host = os.environ.get("SEO_NOTIFY_SMTP_HOST", "").strip()
    username = os.environ.get("SEO_NOTIFY_SMTP_USERNAME", "").strip()
    password = os.environ.get("SEO_NOTIFY_SMTP_PASSWORD", "").strip()
    sender = os.environ.get("SEO_NOTIFY_EMAIL_FROM", "").strip()
    recipient = os.environ.get("SEO_NOTIFY_EMAIL_TO", "").strip()
    if not all([host, username, password, sender, recipient]):
        return None
    port = os.environ.get("SEO_NOTIFY_SMTP_PORT", "").strip() or "587"
    return MailConfig(
        host=host,
        port=int(port),
        username=username,
        password=password,
        sender=sender,
        recipient=recipient,
        use_tls=os.environ.get("SEO_NOTIFY_SMTP_TLS", "true").strip().lower() != "false",
    )


def severity_counts(findings: list[dict]) -> dict[str, int]:
    counts = {"high": 0, "medium": 0, "low": 0}
    for finding in findings:
        severity = str(finding.get("severity") or "low").lower()
        counts[severity] = counts.get(severity, 0) + 1
    return counts


def recommended_next_action(findings: list[dict]) -> str:
    kinds = {finding.get("kind") for finding in findings}
    if "indexing-stalled" in kinds or "priority-page-not-indexed" in kinds:
        return "Open Search Console URL inspection for the homepage and priority guide pages, then request indexing where available."
    if "no-search-console-rows" in kinds:
        return "Continue daily monitoring; wait for Google to return query or page rows before automating new content decisions."
    if findings:
        return "Review the human-review issues and draft PRs linked from the control issue."
    return "No action needed; continue monitoring."


def indexnow_summary(indexnow: dict) -> str:
    if not indexnow:
        return "not run"
    response = indexnow.get("response") or {}
    accepted = response.get("ok")
    status = response.get("status")
    return f"{indexnow.get('url_count', 0)} URLs submitted, accepted={accepted}, status={status}"


def build_email_subject(report: dict, summary: dict) -> str:
    findings = summary_findings(summary)
    counts = severity_counts(findings)
    generated = str(report.get("generated_at") or "latest run")
    date_label = generated.split("T", 1)[0]
    return (
        "Global Home Atlas SEO loop: "
        f"{counts.get('high', 0)} high, {counts.get('medium', 0)} medium, "
        f"{counts.get('low', 0)} low findings ({date_label})"
    )


def build_email_body(
    *,
    report: dict,
    indexnow: dict,
    summary: dict,
    control_url: str,
    dashboard_url: str,
) -> str:
    sitemap = report.get("sitemap") or {}
    status = sitemap.get("status") or {}
    indexing = sitemap.get("indexing") or {}
    search_console = report.get("search_console") or {}
    findings = summary_findings(summary)
    counts = severity_counts(findings)
    window = report.get("window") or {}
    window_label = f"{window.get('start_date', 'n/a')} to {window.get('end_date', 'n/a')}"
    lines = [
        "Global Home Atlas SEO feedback loop finished.",
        "",
        "Run summary",
        f"- Generated: {report.get('generated_at', 'n/a')}",
        f"- Search Console window: {window_label}",
        f"- Sitemap URLs: {sitemap.get('url_count', 'n/a')}",
        f"- Sitemap pending: {status.get('isPending', 'n/a')}",
        f"- Sitemap warnings: {status.get('warnings', 'n/a')}",
        f"- Sitemap errors: {status.get('errors', 'n/a')}",
        f"- Submitted URLs reported by Google: {indexing.get('submitted_reported', 'n/a')}",
        f"- Indexed URLs reported by Google: {indexing.get('indexed_reported', 'n/a')}",
        f"- Top queries returned: {len(search_console.get('top_queries', []))}",
        f"- Top pages returned: {len(search_console.get('top_pages', []))}",
        f"- Low CTR pages: {len(search_console.get('low_ctr_pages', []))}",
        f"- Near-ranking pages: {len(search_console.get('near_ranking_pages', []))}",
        f"- Content gaps: {len(search_console.get('content_gap_queries', []))}",
        f"- IndexNow: {indexnow_summary(indexnow)}",
        "",
        "Findings",
        f"- High severity: {counts.get('high', 0)}",
        f"- Medium severity: {counts.get('medium', 0)}",
        f"- Low severity: {counts.get('low', 0)}",
        f"- Issues created or updated: {summary.get('issue_count', len(summary.get('issues', [])))}",
        f"- Draft PRs opened: {summary.get('pr_count', len(summary.get('prs', [])))}",
        f"- Auto-merged fixes: {summary.get('auto_merged_count', len(summary.get('auto_merged', [])))}",
        "",
        "Next action",
        recommended_next_action(findings),
        "",
        f"Control issue: {control_url}",
        f"SEO dashboard: {dashboard_url}",
    ]
    return "\n".join(lines)


def summary_findings(summary: dict) -> list[dict]:
    findings = summary.get("findings") or []
    return findings if isinstance(findings, list) else []


def send_email(config: MailConfig, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = config.recipient
    message["Subject"] = subject
    message.set_content(body)

    if config.use_tls:
        context = ssl.create_default_context()
        with smtplib.SMTP(config.host, config.port, timeout=30) as smtp:
            smtp.starttls(context=context)
            smtp.login(config.username, config.password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(config.host, config.port, timeout=30) as smtp:
            smtp.login(config.username, config.password)
            smtp.send_message(message)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send the daily SEO feedback loop email notification.")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--indexnow-report", type=Path, default=DEFAULT_INDEXNOW_REPORT)
    parser.add_argument("--feedback-summary", type=Path, default=DEFAULT_FEEDBACK_SUMMARY)
    parser.add_argument("--control-url", default=DEFAULT_CONTROL_URL)
    parser.add_argument("--dashboard-url", default=DEFAULT_DASHBOARD_URL)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = load_json(args.report)
    indexnow = load_json(args.indexnow_report)
    summary = load_json(args.feedback_summary)
    subject = build_email_subject(report, summary)
    body = build_email_body(
        report=report,
        indexnow=indexnow,
        summary=summary,
        control_url=args.control_url,
        dashboard_url=args.dashboard_url,
    )
    if args.dry_run:
        print(subject)
        print()
        print(body)
        return 0

    config = configured_from_env()
    if config is None:
        print("SEO email notification skipped: SMTP notification secrets are not configured.")
        return 0
    send_email(config, subject, body)
    print(f"SEO email notification sent to {config.recipient}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
