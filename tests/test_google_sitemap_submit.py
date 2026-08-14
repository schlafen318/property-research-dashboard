from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import google_sitemap_submit


class GoogleSitemapSubmissionTests(unittest.TestCase):
    def test_success_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            token_path = root / "token.json"
            token_path.write_text("{}", encoding="utf-8")
            output_path = root / "receipt.json"
            service = object()

            with (
                patch.object(google_sitemap_submit, "load_search_console", return_value=service),
                patch.object(
                    google_sitemap_submit,
                    "submit_sitemap",
                    return_value={"ok": True, "sitemap": "https://globalhomeatlas.com/sitemap.xml"},
                ),
            ):
                receipt = google_sitemap_submit.run_submission(
                    site_url="sc-domain:globalhomeatlas.com",
                    sitemap_url="https://globalhomeatlas.com/sitemap.xml",
                    token_path=token_path,
                    output_path=output_path,
                )

            written = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(receipt, written)
        self.assertTrue(receipt["ok"])
        self.assertEqual("sc-domain:globalhomeatlas.com", receipt["site_url"])
        self.assertEqual("https://globalhomeatlas.com/sitemap.xml", receipt["sitemap"])
        self.assertRegex(receipt["submitted_at"], r"^\d{4}-\d{2}-\d{2}T")

    def test_missing_credentials_write_failure_without_loading_google(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_path = root / "receipt.json"
            with (
                patch.dict("os.environ", {}, clear=True),
                patch.object(google_sitemap_submit, "load_search_console") as load_service,
            ):
                receipt = google_sitemap_submit.run_submission(
                    site_url="sc-domain:globalhomeatlas.com",
                    sitemap_url="https://globalhomeatlas.com/sitemap.xml",
                    token_path=root / "missing-token.json",
                    output_path=output_path,
                )

            written = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(receipt, written)
        self.assertFalse(receipt["ok"])
        self.assertEqual("Google Search Console credentials are not configured", receipt["error"])
        load_service.assert_not_called()

    def test_google_rejection_is_written_to_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            token_path = root / "token.json"
            token_path.write_text("{}", encoding="utf-8")
            output_path = root / "receipt.json"

            with (
                patch.object(google_sitemap_submit, "load_search_console", return_value=object()),
                patch.object(
                    google_sitemap_submit,
                    "submit_sitemap",
                    return_value={
                        "ok": False,
                        "sitemap": "https://globalhomeatlas.com/sitemap.xml",
                        "error": "permission denied",
                    },
                ),
            ):
                receipt = google_sitemap_submit.run_submission(
                    site_url="sc-domain:globalhomeatlas.com",
                    sitemap_url="https://globalhomeatlas.com/sitemap.xml",
                    token_path=token_path,
                    output_path=output_path,
                )

            written = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(receipt, written)
        self.assertFalse(receipt["ok"])
        self.assertEqual("permission denied", receipt["error"])

    def test_main_exit_code_matches_receipt(self) -> None:
        with patch.object(google_sitemap_submit, "run_submission", return_value={"ok": True}):
            self.assertEqual(0, google_sitemap_submit.main([]))
        with patch.object(google_sitemap_submit, "run_submission", return_value={"ok": False}):
            self.assertEqual(1, google_sitemap_submit.main([]))


if __name__ == "__main__":
    unittest.main()
