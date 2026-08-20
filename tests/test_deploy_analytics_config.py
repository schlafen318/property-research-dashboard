from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"


class DeployAnalyticsConfigTests(unittest.TestCase):
    def test_static_build_receives_ga4_measurement_secret(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        build_step = workflow.split("- name: Build dashboard", 1)[1].split("- name: Configure Pages", 1)[0]

        self.assertIn("env:", build_step)
        self.assertIn("GA4_MEASUREMENT_ID: ${{ secrets.GA4_MEASUREMENT_ID }}", build_step)


if __name__ == "__main__":
    unittest.main()
