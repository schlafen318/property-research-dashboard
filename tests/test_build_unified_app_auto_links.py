from __future__ import annotations

import json
import unittest
from datetime import date

from src import build_unified_app
from scripts import verify_static_site


class AutoInternalLinkTests(unittest.TestCase):
    def test_calculator_serializes_deterministic_freshness_separately_from_evidence_review(self) -> None:
        destinations = build_unified_app.rank_destinations(
            [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]
        )
        html = build_unified_app.build_retirement_calculator_page(
            destinations,
            build_unified_app.load_retirement_costs(),
            build_unified_app.load_fire_abroad(),
            tax_as_of=date(2027, 9, 2),
        )
        payload_text = html.split(
            '<script id="retirement-destination-data" type="application/json">', 1
        )[1].split("</script>", 1)[0]
        tax_planning = json.loads(payload_text)["tax_planning"]

        self.assertEqual("2027-09-02", tax_planning["as_of"])
        self.assertEqual("2026-09-01", tax_planning["reviewed_on"])

    def test_fire_page_serializes_build_date_and_retains_stale_destinations_unranked(self) -> None:
        destinations = build_unified_app.rank_destinations(
            [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]
        )
        fire_payload = build_unified_app.load_fire_abroad()
        html = build_unified_app.build_fire_abroad_page(
            destinations,
            build_unified_app.load_retirement_costs(),
            fire_payload,
            tax_as_of=date(2027, 9, 3),
        )
        payload_text = html.split('id="fire-abroad-data">', 1)[1].split("</script>", 1)[0]
        results = html.split('<tbody id="fire-results-body"', 1)[1].split("</tbody>", 1)[0]

        self.assertEqual("2027-09-03", json.loads(payload_text)["asOf"])
        self.assertEqual(len(fire_payload["launch_destination_ids"]), results.count('<th scope="row">'))
        self.assertIn("stale", results.lower())
        self.assertIn("remains visible but is not ranked", results)
        self.assertNotIn("/5", results)
        self.assertNotIn("Build your plan", results)

    def test_finder_serializes_deterministic_build_date_as_tax_freshness_anchor(self) -> None:
        destinations = build_unified_app.rank_destinations(
            [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]
        )
        html = build_unified_app.build_retirement_destination_finder_page(
            destinations,
            build_unified_app.load_retirement_costs(),
            build_unified_app.load_mortgage_profiles(),
            build_unified_app.load_fire_abroad(),
            tax_as_of=date(2027, 9, 3),
        )
        payload_text = html.split('id="retirement-finder-data">', 1)[1].split("</script>", 1)[0]

        self.assertEqual("2027-09-03", json.loads(payload_text)["taxPlanning"]["asOf"])

    def test_generated_finder_runtime_handoffs_cover_every_result_and_are_private(self) -> None:
        destinations = build_unified_app.rank_destinations(
            [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]
        )
        html = build_unified_app.build_retirement_destination_finder_page(
            destinations,
            build_unified_app.load_retirement_costs(),
            build_unified_app.load_mortgage_profiles(),
            build_unified_app.load_fire_abroad(),
        )

        evidence = verify_static_site.finder_runtime_handoff_evidence(html)

        self.assertGreater(evidence["recommendation_count"], 0)
        self.assertEqual(evidence["recommendation_count"], len(evidence["links"]))
        self.assertEqual([], verify_static_site.finder_handoff_privacy_errors(html))

    def test_static_verifier_rejects_sensitive_finder_handoff_parameters(self) -> None:
        links = [
            "/retirement-abroad-calculator/?destination=valencia&household=couple"
            "&housing=rent&taxMode=destination_estimate&wealthBand=above_threshold"
        ]

        errors = verify_static_site.finder_handoff_link_errors(links)

        self.assertEqual(1, len(errors))
        self.assertIn("taxMode", errors[0])
        self.assertIn("wealthBand", errors[0])

    def test_static_verifier_executes_detailed_tax_routing_and_privacy_contract(self) -> None:
        destinations = build_unified_app.rank_destinations(
            [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]
        )
        html = build_unified_app.build_retirement_calculator_page(
            destinations,
            build_unified_app.load_retirement_costs(),
            build_unified_app.load_fire_abroad(),
        )

        evidence = verify_static_site.detailed_tax_runtime_evidence(html)

        self.assertGreater(evidence["destination_count"], 0)
        self.assertGreater(evidence["supported_profile_count"], 0)
        self.assertTrue(evidence["selected_destination_present"])
        self.assertTrue(evidence["dom_initialized"])
        self.assertTrue(evidence["result_rendered"])
        self.assertTrue(evidence["official_source_link_rendered"])
        self.assertTrue(evidence["plain_branch_rendered"])
        self.assertFalse(evidence["unsupported_pair_available"])
        self.assertEqual(0, evidence["privacy_calls"])
        self.assertFalse(evidence["synthetic_probe_available"])
        self.assertEqual([], verify_static_site.detailed_tax_runtime_errors(html))

    def test_static_verifier_rejects_a_claimed_enabled_bundle_that_cannot_run(self) -> None:
        html = (
            '<script id="retirement-destination-data" type="application/json">'
            '{"destinations":[{"destination_id":"dubai"}]}</script>'
            '<script id="fire-tax-detailed-data" type="application/json">'
            '{"supported_profiles":{"broken-pair":{"id":"broken-pair","detailed_enabled":true,"synthetic":false,'
            '"destination_id":"dubai","home_jurisdiction_id":"hong-kong","source_ids":[]}},"sources":[]}</script>'
        )

        errors = verify_static_site.detailed_tax_runtime_errors(html)

        self.assertTrue(any("broken-pair" in error and "not executable" in error for error in errors))

    def test_contextual_related_guides_includes_machine_approved_links_first(self) -> None:
        source = {
            "slug": "buy-property-abroad",
            "theme": "global purchase process",
            "keyword": "buy property abroad",
            "destination_ids": ["algarve-cascais"],
        }
        target = {
            "slug": "best-places-to-buy-vacation-home-abroad",
            "h1": "Best Countries and Places to Buy a Vacation Home Abroad",
            "description": "Compare vacation-home markets.",
            "theme": "vacation-home acquisition",
            "keyword": "best places to buy a vacation home abroad",
            "destination_ids": ["algarve-cascais"],
        }
        fallback = {
            "slug": "foreign-property-investment-risks",
            "h1": "Foreign Property Investment Risks",
            "description": "Compare investment risks.",
            "theme": "risk framework",
            "keyword": "foreign property investment risks",
            "destination_ids": ["algarve-cascais"],
        }
        html = build_unified_app.contextual_related_guides(
            source,
            [source, fallback, target],
            auto_links=[
                {
                    "source_slug": "buy-property-abroad",
                    "target_slug": "best-places-to-buy-vacation-home-abroad",
                    "anchor": "Best places to buy a vacation home abroad",
                    "fingerprint": "gha-near-ranking-opportunity-abc123",
                }
            ],
        )

        self.assertIn('/best-places-to-buy-vacation-home-abroad/', html)
        self.assertLess(
            html.index('/best-places-to-buy-vacation-home-abroad/'),
            html.index('/foreign-property-investment-risks/'),
        )


if __name__ == "__main__":
    unittest.main()
