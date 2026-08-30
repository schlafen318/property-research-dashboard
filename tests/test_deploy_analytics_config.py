from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from src.build_unified_app import analytics_event_script


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "deploy-pages.yml"


class DeployAnalyticsConfigTests(unittest.TestCase):
    def test_static_build_receives_ga4_measurement_secret(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        build_step = workflow.split("- name: Build dashboard", 1)[1].split("- name: Configure Pages", 1)[0]

        self.assertIn("env:", build_step)
        self.assertIn("GA4_MEASUREMENT_ID: ${{ secrets.GA4_MEASUREMENT_ID }}", build_step)

    def test_finder_destination_links_are_not_duplicated_by_global_url_tracking(self) -> None:
        script = analytics_event_script().split("<script>", 1)[1].split("</script>", 1)[0]
        harness = r'''
const vm = require("vm");
const source = process.argv[1];
const handlers = {};
const stored = new Map();
const localStorage = {
  getItem(key) { return stored.get(key) || null; },
  setItem(key, value) { stored.set(key, String(value)); },
};
const document = {
  title: "Finder",
  addEventListener(name, callback) { handlers[name] = callback; },
};
const window = {};
const location = { pathname: "/retirement-destination-finder/", hostname: "globalhomeatlas.com" };
vm.runInNewContext(source, { window, document, localStorage, location, JSON, Date, Math, Object, String, FormData: function () {} });
const target = {
  textContent: "Fukuoka / Itoshima",
  closest() { return this; },
  hasAttribute(name) { return name === "data-finder-destination"; },
  getAttribute(name) { return name === "href" ? "/destinations/fukuoka-itoshima/" : null; },
};
handlers.click({ target });
process.stdout.write(stored.get("gha_event_queue") || "[]");
'''
        result = subprocess.run(
            ["node", "-e", harness, script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual([], json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
