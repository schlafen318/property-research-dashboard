from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SITE_URL = "https://globalhomeatlas.com/"
DEFAULT_SITEMAP = "https://globalhomeatlas.com/sitemap.xml"
DEFAULT_OUTPUT = ROOT / "output" / "seo" / "indexnow-latest.json"
DEFAULT_ENDPOINT = "https://api.indexnow.org/indexnow"
DEFAULT_KEY = "5f0b9a6d2c134e8790a1b8c3d4e5f607"


def indexnow_key() -> str:
    return os.environ.get("INDEXNOW_KEY", "").strip() or DEFAULT_KEY


def fetch_sitemap(url: str) -> list[str]:
    with urllib.request.urlopen(url, timeout=30) as response:
        body = response.read()
    root = ET.fromstring(body)
    return [
        node.text or ""
        for node in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if node.text
    ]


def submit_indexnow(endpoint: str, host: str, key: str, key_location: str, urls: list[str], timeout: int) -> dict:
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return {
                "ok": response.status in {200, 202},
                "status": response.status,
                "reason": response.reason,
                "body": body,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "reason": exc.reason, "body": body}
    except Exception as exc:
        return {"ok": False, "status": None, "reason": type(exc).__name__, "body": str(exc)}


def build_result(args: argparse.Namespace) -> dict:
    site = args.site_url.rstrip("/")
    host = site.replace("https://", "").replace("http://", "").split("/")[0]
    key = args.key or indexnow_key()
    urls = fetch_sitemap(args.sitemap)
    if args.limit:
        urls = urls[: args.limit]
    key_location = args.key_location or f"{site}/{key}.txt"
    response = submit_indexnow(args.endpoint, host, key, key_location, urls, args.timeout)
    return {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "endpoint": args.endpoint,
        "host": host,
        "key_location": key_location,
        "url_count": len(urls),
        "response": response,
        "urls": urls,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Submit Global Home Atlas URLs to IndexNow.")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL)
    parser.add_argument("--sitemap", default=DEFAULT_SITEMAP)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--key", default=None)
    parser.add_argument("--key-location", default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--allow-failure", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    result = build_result(args)
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        print(f"Wrote {args.output}")
    if result["response"]["ok"] or args.allow_failure:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
