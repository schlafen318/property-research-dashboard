from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import google_sitemap_submit


class GoogleSitemapSubmissionTests(unittest.TestCase):
    def test_cli_runs_from_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            output_path = root / "receipt.json"
            env = dict(os.environ)
            env.pop("GOOGLE_SEARCH_CONSOLE_TOKEN_JSON", None)
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/google_sitemap_submit.py",
                    "--token",
                    str(root / "missing-token.json"),
                    "--output",
                    str(output_path),
                ],
                cwd=Path(__file__).resolve().parents[1],
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )

            receipt = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(1, completed.returncode)
        self.assertNotIn("ModuleNotFoundError", completed.stderr)
        self.assertFalse(receipt["ok"])

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
                ) as submit,
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
        submit.assert_called_once_with(
            service,
            "sc-domain:globalhomeatlas.com",
            "https://globalhomeatlas.com/sitemap.xml",
        )

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
        with (
            patch.object(google_sitemap_submit, "run_submission", return_value={"ok": True}),
            patch("builtins.print"),
        ):
            self.assertEqual(0, google_sitemap_submit.main([]))
        with (
            patch.object(google_sitemap_submit, "run_submission", return_value={"ok": False}),
            patch("builtins.print"),
        ):
            self.assertEqual(1, google_sitemap_submit.main([]))


class DeployWorkflowTests(unittest.TestCase):
    def test_google_submission_runs_after_deploy_with_step_scoped_secret_and_receipt(self) -> None:
        workflow = Path(".github/workflows/deploy-pages.yml").read_text(encoding="utf-8")
        notify_job = workflow.split("\n  notify-google:\n", 1)[1]
        notify_job_header, notify_steps = notify_job.split("    steps:\n", 1)
        submission_step = notify_steps.split("      - name: Submit sitemap to Google Search Console\n", 1)[1]
        submission_step = submission_step.split("      - name:", 1)[0]
        receipt_step = notify_steps.split("      - name: Upload sitemap submission receipt\n", 1)[1]

        self.assertIn("needs: deploy", notify_job_header)
        self.assertIn("google-api-python-client", notify_steps)
        self.assertIn("python3 scripts/google_sitemap_submit.py", submission_step)
        self.assertIn("GOOGLE_SEARCH_CONSOLE_TOKEN_JSON: ${{ secrets.GOOGLE_SEARCH_CONSOLE_TOKEN_JSON }}", submission_step)
        self.assertNotIn("GOOGLE_SEARCH_CONSOLE_TOKEN_JSON", workflow.split("jobs:", 1)[0])
        self.assertNotIn("GOOGLE_SEARCH_CONSOLE_TOKEN_JSON", notify_job_header)
        self.assertIn("if: always()", receipt_step)
        self.assertIn("name: google-sitemap-submission", receipt_step)
        self.assertIn("output/seo/google-sitemap-submission.json", receipt_step)


if __name__ == "__main__":
    unittest.main()
