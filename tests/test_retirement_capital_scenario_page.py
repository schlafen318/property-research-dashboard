from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

from tests.test_retirement_destination_finder import (
    cost_record,
    destination,
    mortgage_profile,
    run_finder,
    user_payload,
)


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_retirement_capital_scenarios.js"
SCENARIOS = {
    "retire-abroad-with-500k": 500_000,
    "retire-abroad-with-750k": 750_000,
    "retire-abroad-with-1-million": 1_000_000,
    "retire-abroad-with-1-5-million": 1_500_000,
    "retire-abroad-with-2-million": 2_000_000,
}
SCENARIO_LABELS = {
    500_000: "$500,000",
    750_000: "$750,000",
    1_000_000: "$1 million",
    1_500_000: "$1.5 million",
    2_000_000: "$2 million",
}


def run_generator(payload: dict) -> dict:
    result = subprocess.run(
        ["node", str(GENERATOR)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT,
    )
    return json.loads(result.stdout)


class RetirementCapitalScenarioPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run(["python3", "src/build_unified_app.py"], cwd=ROOT, check=True, capture_output=True)

    def test_every_capital_page_has_unique_search_metadata_and_outcomes(self) -> None:
        titles = set()
        headings = set()
        for slug, capital in SCENARIOS.items():
            html = (ROOT / "artifacts" / slug / "index.html").read_text()
            title = html.split("<title>", 1)[1].split("</title>", 1)[0]
            heading = html.split("<h1>", 1)[1].split("</h1>", 1)[0]
            titles.add(title)
            headings.add(heading)
            self.assertIn(f'<link rel="canonical" href="https://globalhomeatlas.com/{slug}/">', html)
            self.assertIn("Planning estimate", html)
            self.assertIn("Required capital", html)
            self.assertIn("Test your retirement plan", html)
            self.assertIn('"@type":"FAQPage"', html)
            self.assertNotIn("how this page was generated", html.lower())
            self.assertIn(SCENARIO_LABELS[capital], html)
        self.assertEqual(5, len(titles))
        self.assertEqual(5, len(headings))

    def test_capital_pages_are_in_the_sitemap_and_cross_linked(self) -> None:
        sitemap = (ROOT / "artifacts" / "sitemap.xml").read_text()
        one_million = (ROOT / "artifacts" / "retire-abroad-with-1-million" / "index.html").read_text()
        for slug in SCENARIOS:
            self.assertIn(f"https://globalhomeatlas.com/{slug}/", sitemap)
            self.assertIn(f'href="/{slug}/"', one_million)

    def test_calculators_and_guide_hub_link_to_capital_pages(self) -> None:
        pages = [
            ROOT / "artifacts" / "retirement-abroad-calculator" / "index.html",
            ROOT / "artifacts" / "retirement-destination-finder" / "index.html",
            ROOT / "artifacts" / "guides" / "index.html",
        ]
        for path in pages:
            html = path.read_text()
            for slug in SCENARIOS:
                self.assertIn(f'href="/{slug}/"', html)

    def test_build_time_generator_matches_the_shared_engine(self) -> None:
        destinations = [destination("low"), destination("high")]
        base_input = {
            "user": user_payload(currentAge=65, retirementAge=65, retirementBeginsNow=True, horizonYears=30),
            "destinations": destinations,
            "retirementCosts": [cost_record("low", 25_000), cost_record("high", 50_000)],
            "mortgageProfiles": {item["id"]: mortgage_profile() for item in destinations},
        }
        generated = run_generator({"capitalValues": [1_000_000], "baseInput": base_input})["1000000"]
        expected = run_finder("recommendProjectedCapital", {**base_input, "projectedCapitalUsd": 1_000_000})
        self.assertEqual(expected["summary"], generated["summary"])
        self.assertEqual(
            [item["destinationId"] for item in expected["recommendations"]],
            [item["destinationId"] for item in generated["recommendations"]],
        )


if __name__ == "__main__":
    unittest.main()
