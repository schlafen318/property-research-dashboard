from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
VERIFIER_PATH = ROOT / "codex-skills/global-home-atlas-analytics/scripts/verify_tracking.py"
SPEC = importlib.util.spec_from_file_location("verify_tracking", VERIFIER_PATH)
verify_tracking = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(verify_tracking)


class TrackingVerifierTests(unittest.TestCase):
    def tracking_html(self, *, include_queue: bool, include_interface: bool) -> str:
        tracking = ""
        if include_interface:
            tracking += "<script>function track(eventName, params) {} window.GHA = { track };</script>"
        if include_queue:
            tracking += "<script>const gha_event_queue = [];</script>"
        return tracking

    def page_html(self, tracking: str) -> str:
        events = " ".join(verify_tracking.EXPECTED_EVENTS)
        return f"""<!doctype html><html><head><title>Test page</title>
        <meta name=\"description\" content=\"Test\"><link rel=\"canonical\" href=\"https://globalhomeatlas.com/test/\">
        <script type=\"application/ld+json\">{{}}</script></head><body><h1>Test page</h1><form id=\"custom-shortlist-form\"></form>{events}{tracking}</body></html>"""

    def run_verifier(self, url: str, tracking: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            artifacts = Path(directory)
            original_artifacts = verify_tracking.ARTIFACTS
            original_sitemap_urls = verify_tracking.sitemap_urls
            verify_tracking.ARTIFACTS = artifacts
            verify_tracking.sitemap_urls = lambda: [url]
            try:
                baseline = self.page_html(self.tracking_html(include_queue=True, include_interface=True))
                for relative in (
                    "index.html",
                    "dashboard/index.html",
                    "contact/index.html",
                    "shortlist-review/index.html",
                    "reports/index.html",
                    "countries/spain-property/index.html",
                ):
                    path = artifacts / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(baseline, encoding="utf-8")
                target = verify_tracking.path_for_url(url)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(self.page_html(tracking), encoding="utf-8")
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    result = verify_tracking.main()
                return result, output.getvalue()
            finally:
                verify_tracking.ARTIFACTS = original_artifacts
                verify_tracking.sitemap_urls = original_sitemap_urls

    def test_non_fire_page_without_queue_fails(self) -> None:
        url = "https://globalhomeatlas.com/other/"
        result, output = self.run_verifier(url, self.tracking_html(include_queue=False, include_interface=True))
        self.assertEqual(1, result)
        self.assertIn(f"{url}: missing persistent tracking queue", output)

    def test_non_fire_page_with_queue_and_interface_passes(self) -> None:
        result, output = self.run_verifier(
            "https://globalhomeatlas.com/other/",
            self.tracking_html(include_queue=True, include_interface=True),
        )
        self.assertEqual(0, result)
        self.assertIn("tracking_verification=pass", output)

    def test_fire_page_without_queue_and_with_interface_passes(self) -> None:
        result, output = self.run_verifier(
            "https://globalhomeatlas.com/fire-abroad/",
            self.tracking_html(include_queue=False, include_interface=True),
        )
        self.assertEqual(0, result)
        self.assertIn("tracking_verification=pass", output)

    def test_fire_page_without_interface_fails(self) -> None:
        url = "https://globalhomeatlas.com/fire-abroad/"
        result, output = self.run_verifier(url, self.tracking_html(include_queue=False, include_interface=False))
        self.assertEqual(1, result)
        self.assertIn(f"{url}: missing public tracking interface", output)


if __name__ == "__main__":
    unittest.main()
