from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
import urllib.parse
import urllib.request
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


@dataclass(frozen=True)
class TelegramConfig:
    bot_token: str
    chat_id: str


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


def telegram_configured_from_env() -> TelegramConfig | None:
    bot_token = os.environ.get("SEO_NOTIFY_TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("SEO_NOTIFY_TELEGRAM_CHAT_ID", "").strip()
    if not bot_token or not chat_id:
        return None
    return TelegramConfig(bot_token=bot_token, chat_id=chat_id)


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


def build_telegram_message(
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
    findings = summary_findings(summary)
    counts = severity_counts(findings)
    generated = str(report.get("generated_at") or "n/a")
    window = report.get("window") or {}
    window_label = f"{window.get('start_date', 'n/a')} to {window.get('end_date', 'n/a')}"
    lines = [
        "Global Home Atlas SEO loop finished",
        "",
        f"Generated: {generated}",
        f"Window: {window_label}",
        f"Sitemap URLs: {sitemap.get('url_count', 'n/a')}",
        f"Warnings/errors: {status.get('warnings', 'n/a')}/{status.get('errors', 'n/a')}",
        f"Google indexed/submitted: {indexing.get('indexed_reported', 'n/a')}/{indexing.get('submitted_reported', 'n/a')}",
        f"Findings: {counts.get('high', 0)} high, {counts.get('medium', 0)} medium, {counts.get('low', 0)} low",
        f"Issues updated: {summary.get('issue_count', len(summary.get('issues', [])))}",
        f"Draft PRs: {summary.get('pr_count', len(summary.get('prs', [])))}",
        f"Auto-merged: {summary.get('auto_merged_count', len(summary.get('auto_merged', [])))}",
        f"IndexNow: {indexnow_summary(indexnow)}",
        "",
        f"Next: {recommended_next_action(findings)}",
        "",
        f"Control: {control_url}",
        f"Dashboard: {dashboard_url}",
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


def send_telegram(config: TelegramConfig, text: str) -> None:
    url = f"https://api.telegram.org/bot{config.bot_token}/sendMessage"
    data = urllib.parse.urlencode(
        {
            "chat_id": config.chat_id,
            "text": text[:4096],
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=30) as response:
        response.read()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send daily SEO feedback loop notifications.")
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
    telegram_message = build_telegram_message(
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
        print()
        print("Telegram")
        print()
        print(telegram_message)
        return 0

    sent = False
    mail_config = configured_from_env()
    if mail_config is None:
        print("SEO email notification skipped: SMTP notification secrets are not configured.")
    else:
        send_email(mail_config, subject, body)
        sent = True
        print(f"SEO email notification sent to {mail_config.recipient}.")

    telegram_config = telegram_configured_from_env()
    if telegram_config is None:
        print("SEO Telegram notification skipped: Telegram notification secrets are not configured.")
    else:
        send_telegram(telegram_config, telegram_message)
        sent = True
        print(f"SEO Telegram notification sent to chat {telegram_config.chat_id}.")

    if not sent:
        print("No direct SEO notifications were sent; configure email or Telegram secrets to enable delivery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
