from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from scripts.seo_monitor import (
    DEFAULT_OUTPUT,
    DEFAULT_SITE_URL,
    DEFAULT_SITEMAP,
    DEFAULT_TOKEN,
    load_search_console,
    submit_sitemap,
    token_from_env,
)


DEFAULT_RECEIPT = DEFAULT_OUTPUT / "google-sitemap-submission.json"


def _write_receipt(receipt: dict, output_path: Path) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def run_submission(
    *,
    site_url: str,
    sitemap_url: str,
    token_path: Path,
    output_path: Path,
) -> dict:
    submitted_at = dt.datetime.now(dt.timezone.utc).isoformat()
    token_from_env(token_path)
    if not token_path.exists():
        return _write_receipt(
            {
                "error": "Google Search Console credentials are not configured",
                "ok": False,
                "site_url": site_url,
                "sitemap": sitemap_url,
                "submitted_at": submitted_at,
            },
            output_path,
        )

    try:
        service = load_search_console(token_path)
        result = submit_sitemap(service, site_url, sitemap_url)
    except Exception as exc:
        result = {"ok": False, "sitemap": sitemap_url, "error": str(exc)}

    receipt = {
        **result,
        "site_url": site_url,
        "sitemap": sitemap_url,
        "submitted_at": submitted_at,
    }
    return _write_receipt(receipt, output_path)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit the production sitemap to Google Search Console.")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--sitemap", default=DEFAULT_SITEMAP)
    parser.add_argument("--token", type=Path, default=DEFAULT_TOKEN)
    parser.add_argument("--output", type=Path, default=DEFAULT_RECEIPT)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    receipt = run_submission(
        site_url=args.site_url,
        sitemap_url=args.sitemap,
        token_path=args.token,
        output_path=args.output,
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
