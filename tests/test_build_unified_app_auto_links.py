from __future__ import annotations

import unittest

from src import build_unified_app
from scripts import verify_static_site


class AutoInternalLinkTests(unittest.TestCase):
    def test_generated_finder_handoffs_expose_only_destination_household_and_housing(self) -> None:
        destinations = build_unified_app.rank_destinations(
            [build_unified_app.consolidate_destination(item) for item in build_unified_app.load_json("destinations.json")]
        )
        html = build_unified_app.build_retirement_destination_finder_page(
            destinations,
            build_unified_app.load_retirement_costs(),
            build_unified_app.load_mortgage_profiles(),
            build_unified_app.load_fire_abroad(),
        )

        self.assertEqual([], verify_static_site.finder_handoff_privacy_errors(html))

    def test_static_verifier_rejects_sensitive_finder_handoff_parameters(self) -> None:
        html = (
            '<a href="/retirement-abroad-calculator/?destination=valencia&amp;household=couple'
            '&amp;housing=rent&amp;taxMode=destination_estimate&amp;wealthBand=above_threshold">Plan</a>'
        )

        errors = verify_static_site.finder_handoff_privacy_errors(html)

        self.assertEqual(1, len(errors))
        self.assertIn("taxMode", errors[0])
        self.assertIn("wealthBand", errors[0])

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
