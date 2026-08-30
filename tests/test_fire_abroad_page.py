from __future__ import annotations

import copy
import html as html_module
import json
import re
import unittest
from urllib.parse import parse_qs, urlsplit

from src.build_unified_app import (
    FIRE_ABROAD_DESCRIPTION,
    FIRE_ABROAD_TITLE,
    PRIMARY_NAV_LINKS,
    build_fire_abroad_page,
    consolidate_destination,
    load_fire_abroad_for_build,
    load_json,
    load_retirement_costs,
)
from src.fire_abroad import CANONICAL_LAUNCH_IDS, load_fire_abroad


class FireAbroadPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.destinations = [
            consolidate_destination(item) for item in load_json("destinations.json")
        ]
        cls.retirement_costs = load_retirement_costs()
        cls.fire_payload = load_fire_abroad()
        cls.html = build_fire_abroad_page(
            cls.destinations,
            cls.retirement_costs,
            cls.fire_payload,
        )

    def test_default_page_answers_the_query_without_javascript(self) -> None:
        self.assertIn("<h1>FIRE Abroad</h1>", self.html)
        self.assertIn("financial independence", self.html.lower())
        self.assertIn('data-default-stay-mode="part_year"', self.html)
        self.assertIn('id="fire-results" aria-live="polite"', self.html)
        self.assertIn('id="fire-results-summary" aria-live="polite"', self.html)
        self.assertIn("Immigration status and tax residence are separate", self.html)
        self.assertIn("Active Life", self.html)
        self.assertIn("Resilience budget", self.html)
        self.assertIn("Algarve / Cascais", self.html)
        self.assertIn("FIRE Abroad score: 3.70 out of 5", self.html)
        self.assertIn("Needs verification", self.html)
        self.assertIn("Healthcare Bridge:", self.html)
        self.assertIn("Stay Flexibility:", self.html)
        self.assertIn("Tax Compatibility:", self.html)
        self.assertIn("Passive income only", self.html)
        self.assertIn("Medium High confidence", self.html)
        self.assertIn("Evidence reviewed 2026-08-29", self.html)
        self.assertEqual(10, self.html.count(">Build your plan</a>"))
        self.assertEqual(10, self.html.count('<tr data-fire-result="'))
        self.assertLess(self.html.index("Algarve / Cascais"), self.html.index("Da Nang / Hoi An"))

    def test_metadata_and_schema_describe_a_page_without_ratings(self) -> None:
        self.assertIn(f"<title>{FIRE_ABROAD_TITLE}</title>", self.html)
        self.assertIn(
            f'<meta name="description" content="{FIRE_ABROAD_DESCRIPTION}">',
            self.html,
        )
        self.assertIn(
            '<link rel="canonical" href="https://globalhomeatlas.com/fire-abroad/">',
            self.html,
        )
        schema_text = re.search(
            r'<script type="application/ld\+json">(.*?)</script>', self.html, re.DOTALL
        ).group(1)
        schema = json.loads(schema_text)
        schema_types = {item.get("@type") for item in schema}
        self.assertTrue({"WebPage", "CollectionPage"} & schema_types)
        self.assertIn("BreadcrumbList", schema_types)
        self.assertNotIn("AggregateRating", self.html)
        self.assertNotIn('"@type":"Review"', self.html)

    def test_profile_controls_use_native_labeled_defaults_and_allowlisted_options(self) -> None:
        expected_fragments = (
            '<label for="fire-stay-mode">Intended stay</label>',
            '<select id="fire-stay-mode">',
            '<option value="part_year" selected>Part-year base</option>',
            '<label for="fire-age">Current age</label>',
            '<input id="fire-age" type="number" min="18" max="100" value="50">',
            '<label for="fire-household">Household</label>',
            '<select id="fire-household"><option value="single" selected>Single</option><option value="couple">Couple</option></select>',
            '<label for="fire-housing">Housing</label>',
            '<option value="own">Already own</option>',
            '<option value="buy_now">Buy now</option>',
            '<option value="buy_retirement">Buy at retirement</option>',
            '<label for="fire-mobility-rights">Mobility rights context (optional)</label>',
            '<label for="fire-home-tax-context">Home tax context (optional)</label>',
            '<label for="fire-annual-days">Approximate days per year (optional)</label>',
            '<label for="fire-income-type">Income type (optional)</label>',
            '<label for="fire-activity-priority">Activity priority (optional)</label>',
            '<button type="submit">Update ranking</button>',
        )
        for fragment in expected_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)
        self.assertNotIn('role="button"', self.html)

    def test_embedded_payload_is_minimal_complete_and_script_safe(self) -> None:
        script_text = re.search(
            r'<script id="fire-abroad-data" type="application/json">(.*?)</script>',
            self.html,
            re.DOTALL,
        ).group(1)
        self.assertNotRegex(script_text, r"[<>&]")
        payload = json.loads(script_text)
        self.assertEqual(
            {"destinations", "retirement_costs", "fire_payload", "profile"},
            set(payload),
        )
        launch_ids = {
            "algarve-cascais",
            "bali",
            "croatia-istria-dalmatia",
            "crete",
            "da-nang-hoi-an",
            "fukuoka-itoshima",
            "madeira",
            "malaga-costa-del-sol",
            "phuket-koh-samui",
            "valencia",
        }
        self.assertEqual(launch_ids, {item["id"] for item in payload["destinations"]})
        self.assertEqual(
            launch_ids,
            {
                item["destination_id"]
                for item in payload["retirement_costs"]["destinations"]
            },
        )
        self.assertEqual(launch_ids, set(payload["fire_payload"]["launch_destination_ids"]))
        self.assertEqual(
            {
                "stay_mode": "part_year",
                "age": 50,
                "household": "single",
                "housing": "rent",
                "mobility_rights": "prefer_not_to_say",
                "home_tax_context": "prefer_not_to_say",
                "annual_days": None,
                "income_type": "prefer_not_to_say",
                "activity_priority": "balanced",
            },
            payload["profile"],
        )

    def test_embedded_json_escapes_html_significant_characters(self) -> None:
        destinations = copy.deepcopy(self.destinations)
        target = next(item for item in destinations if item["id"] == "valencia")
        target["name"] = "Valencia <coast> & city"
        rendered = build_fire_abroad_page(destinations, self.retirement_costs, self.fire_payload)
        script_text = re.search(
            r'<script id="fire-abroad-data" type="application/json">(.*?)</script>',
            rendered,
            re.DOTALL,
        ).group(1)
        self.assertNotRegex(script_text, r"[<>&]")
        self.assertEqual(
            "Valencia <coast> & city",
            next(
                item["name"]
                for item in json.loads(script_text)["destinations"]
                if item["id"] == "valencia"
            ),
        )

    def test_calculator_handoffs_contain_only_allowlisted_prefill_fields(self) -> None:
        hrefs = re.findall(
            r'href="([^"]*retirement-abroad-calculator/\?[^"]+)"', self.html
        )
        self.assertEqual(10, len(hrefs))
        for href in hrefs:
            with self.subTest(href=href):
                query = parse_qs(urlsplit(html_module.unescape(href)).query)
                self.assertEqual({"destination", "household", "housing"}, set(query))
                self.assertIn(query["destination"][0], CANONICAL_LAUNCH_IDS)
                self.assertEqual(["single"], query["household"])
                self.assertEqual(["rent"], query["housing"])

    def test_methodology_evidence_and_no_javascript_fallback_are_visible(self) -> None:
        self.assertIn("25% Active Life", self.html)
        self.assertIn("20% sustainable annual cost", self.html)
        self.assertIn("currency and inflation buffer", self.html.lower())
        self.assertIn("Evidence reviewed 2026-08-29", self.html)
        self.assertIn('<details class="fire-evidence">', self.html)
        self.assertIn("Source evidence and review dates", self.html)
        self.assertIn("<noscript>", self.html)
        self.assertIn(
            "The default part-year ranking remains available below", self.html
        )

    def test_builder_validates_data_before_rendering_with_one_actionable_error_list(self) -> None:
        self.assertEqual(
            set(self.fire_payload["launch_destination_ids"]),
            set(
                load_fire_abroad_for_build(self.destinations, self.retirement_costs)[
                    "launch_destination_ids"
                ]
            ),
        )
        invalid = copy.deepcopy(self.fire_payload)
        invalid["destination_overrides"]["valencia"]["active_life"].pop(
            "everyday_movement"
        )
        invalid["destination_overrides"]["bali"]["source_ids"].append(
            "missing-source"
        )
        with self.assertRaisesRegex(ValueError, r"Invalid FIRE Abroad data:\n- ") as raised:
            build_fire_abroad_page(self.destinations, self.retirement_costs, invalid)
        self.assertIn("bali source_ids[2]", str(raised.exception))
        self.assertIn("missing-source", str(raised.exception))
        self.assertIn(
            "valencia active_life.everyday_movement", str(raised.exception)
        )

    def test_primary_navigation_is_not_expanded(self) -> None:
        self.assertEqual(
            [
                ("/dashboard/", "Destination Rankings"),
                ("/retirement-abroad-calculator/", "Retirement Calculator"),
                ("/countries/", "Country Guides"),
                ("/guides/", "Buying Guides"),
            ],
            PRIMARY_NAV_LINKS,
        )
        header = self.html.split('<header class="gha-header">', 1)[1].split(
            "</header>", 1
        )[0]
        self.assertNotIn('href="/fire-abroad/"', header)


if __name__ == "__main__":
    unittest.main()
