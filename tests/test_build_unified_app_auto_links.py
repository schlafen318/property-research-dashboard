from __future__ import annotations

import unittest

from src import build_unified_app


class AutoInternalLinkTests(unittest.TestCase):
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
