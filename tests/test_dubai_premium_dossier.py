import json
import re
import unittest
from pathlib import Path

from src.premium_destination_dossiers import (
    DECISION_DIMENSION_KEYS,
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


ROOT = Path(__file__).parents[1]
DESTINATION_ID = "dubai"
AED_PER_USD = 3.6725


class DubaiDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_preserves_reviewed_dossiers_and_contains_dubai(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 19)
        self.assertIsNotNone(self.spec)

    def test_contract_passes_every_bounded_content_gate(self):
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(
            (3, 4, 3, 8, 1),
            (
                len(self.spec.market_anchors),
                len(self.spec.micro_locations),
                len(self.spec.images),
                len(self.spec.checklist),
                len(self.spec.orientation_groups),
            ),
        )
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_decision_led_and_locally_specific(self):
        prose = " ".join(
            [
                self.spec.lede,
                *self.spec.verdict_paragraphs,
                self.spec.lenses_intro,
                *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
                self.spec.micro_locations_intro,
            ]
        )
        for term in (
            "Downtown Dubai",
            "Business Bay",
            "Dubai Marina",
            "JBR",
            "Palm Jumeirah",
            "Dubai Hills Estate",
            "Dubai Land Department",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        for pattern in (
            r"freehold|designated area",
            r"AED 2 million|2,000,000",
            r"service charge|Mollak",
            r"holiday home|short.?term",
            r"off.?plan|escrow|completion",
            r"health insurance|healthcare",
            r"heat|summer|flood",
            r"resale|exit|buyer pool",
        ):
            self.assertRegex(prose, pattern)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "dubailand.gov.ae/en/frequently-asked-questions",
            "dubailand.gov.ae/en/eservices/property-sale-registration",
            "dubailand.gov.ae/en/open-data/real-estate-data",
            "annual-report-real-estate-sector-performance-2024",
            "rental-sector-records-strong-growth-in-2025",
            "dlp.dubai.gov.ae/Legislation",
            "u.ae/en/information-and-services/visa-and-emirates-id/residence-visas/golden-visa",
            "dha.gov.ae",
            "dubaiairports.ae",
            "rta.ae/wps/portal/rta/ae/public-transport",
            "tax.gov.ae",
            "centralbank.ae",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-23", self.spec.date_reviewed)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self):
        ledger = (ROOT / "docs/research/dubai-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic",
            "Source owner",
            "Direct URL",
            "Source date / status",
            "Reviewed",
            "Scope",
            "Limitation",
            "Recheck trigger",
            "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-23"), 14)
        self.assertGreaterEqual(ledger.count("https://"), 20)
        for trigger in (
            "ownership",
            "residence",
            "service charge",
            "holiday home",
            "listing",
            "market data",
            "health",
            "transport",
        ):
            self.assertIn(trigger, ledger.lower())

    def test_generated_images_have_a_publication_provenance_record(self):
        provenance = (ROOT / "docs/research/dubai-image-provenance.md").read_text()
        for filename in (
            "dubai-waterfront-daily-life.webp",
            "dubai-metro-city-access.webp",
            "dubai-hills-summer-shade.webp",
        ):
            self.assertIn(filename, provenance)
        for field in (
            "Generation tool",
            "Generation date",
            "Prompt",
            "Publication-rights basis",
            "Visual approval",
        ):
            self.assertIn(field, provenance)
        self.assertNotRegex(provenance, r"(?i)pending|unknown|unverified")

    def test_three_market_anchors_are_current_and_asset_bounded(self):
        evidence = " ".join(
            " ".join(str(value) for value in item.values())
            for item in self.spec.market_anchors
        )
        for value in ("19,138 AED/m²", "14,617 AED/m²", "1.38 million"):
            self.assertIn(value, evidence)
        self.assertIn("2024", evidence)
        self.assertIn("2025", evidence)
        self.assertRegex(evidence.lower(), r"apartment|villa|tenancy")
        self.assertRegex(evidence.lower(), r"not.*candidate|not.*valuation")
        apartment_and_villa = " ".join(
            item["buyer_read"] for item in self.spec.market_anchors[:2]
        ).lower()
        self.assertIn("ready and off-plan", apartment_and_villa)
        self.assertIn("not filtered", apartment_and_villa)

    def test_atlas_reads_are_concise_and_locally_specific(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(
                    atlas_read,
                    r"Dubai|Downtown|Business Bay|Marina|JBR|Palm Jumeirah|Dubai Hills|DLD|Mollak|DXB",
                )


class DubaiListingAndDataTests(unittest.TestCase):
    def test_three_current_direct_aed_observations_are_complete(self):
        rows = [
            item
            for item in json.loads((ROOT / "data/listings.json").read_text())
            if item["destination_id"] == DESTINATION_ID
        ]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Business Bay completed waterfront apartment",
                "Dubai Marina completed waterfront apartment",
                "Dubai Hills completed family villa",
            },
            {item["listing_name"] for item in rows},
        )
        self.assertEqual(
            {
                "https://www.propertyfinder.ae/en/plp/buy/apartment-for-sale-dubai-business-bay-the-bay-128807897.html",
                "https://www.propertyfinder.ae/en/plp/buy/apartment-for-sale-dubai-dubai-marina-5242-5242-tower-2-129312973.html",
                "https://www.propertyfinder.ae/en/plp/buy/villa-for-sale-dubai-dubai-hills-estate-maple-at-dubai-hills-estate-maple-at-dubai-hills-estate-2-131537797.html",
            },
            {item["source_url"] for item in rows},
        )
        for row in rows:
            self.assertEqual("AED", row["local_currency"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertIn("1 USD = 3.6725 AED", row["fx_basis"])
            self.assertIn("structured", row["area_basis"].lower())
            self.assertIn("0.09290304", row["area_basis"])
            self.assertAlmostEqual(row["local_price"] / AED_PER_USD, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        by_name = {row["listing_name"]: row for row in rows}
        business = by_name["Business Bay completed waterfront apartment"]
        self.assertIn("1,591", business["area_basis"])
        self.assertIn("does not define", business["area_basis"])
        self.assertEqual("Medium-low", business["confidence"])
        marina = by_name["Dubai Marina completed waterfront apartment"]
        self.assertIn("does not define", marina["area_basis"])
        self.assertEqual("Medium-low", marina["confidence"])
        hills = by_name["Dubai Hills completed family villa"]
        self.assertIn("2,915", hills["area_basis"])
        self.assertIn("narrative", hills["area_basis"])
        self.assertIn("structured built-up field", hills["area_basis"])
        self.assertEqual("Low", hills["confidence"])
        self.assertEqual(
            {147.7158336, 104.0514048, 228.72728448},
            {row["size_m2"] for row in rows},
        )

    def test_shared_score_price_basis_and_access_are_reconciled(self):
        destination = next(
            item
            for item in json.loads((ROOT / "data/destinations.json").read_text())
            if item["id"] == DESTINATION_ID
        )
        self.assertEqual("available", destination["access_status"])
        self.assertIn("designated freehold", destination["access_summary"].lower())
        self.assertIn("does not itself grant residence", destination["access_summary"].lower())
        self.assertEqual(4.18, destination["overall_score"])
        self.assertEqual(5200.0, destination["usd_per_m2"])
        self.assertEqual("$5,200", destination["quick_metrics"]["usd_m"])
        for text in (
            "19,138 AED/m²",
            "three direct asking observations",
            "3.6725 AED",
            "completed",
        ):
            self.assertIn(text, destination["price_basis"])
        weighted = sum(
            row["score"] * row["weight"]
            for row in __import__("src.build_unified_app", fromlist=["consolidate_destination"])
            .consolidate_destination(destination)["decision_dimensions"]
        )
        self.assertAlmostEqual(4.179, weighted, places=3)


class DubaiRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(item) for item in destinations]
        cls.html = build_destination_page(
            next(item for item in enriched if item["id"] == DESTINATION_ID),
            listings,
            enriched,
            [],
        )

    def test_page_uses_premium_sequence_and_uae_handoff(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [
            self.html.index(f'id="{anchor}"')
            for anchor in ("verdict", "lenses", "scores", "listings", "locations", "checklist", "sources")
        ]
        self.assertEqual(sorted(positions), positions)
        for text in (
            "Dubai through five destination lenses",
            "Here’s how Dubai scores",
            "Compare Dubai with the full Atlas.",
            "/countries/united-arab-emirates-property/",
        ):
            self.assertIn(text, self.html)
        self.assertNotIn("Foreign-buyer access restricted", self.html)

    def test_country_handoff_is_bidirectional_and_decision_useful(self):
        from src.build_unified_app import COUNTRY_HUBS, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "united-arab-emirates-property")
        self.assertEqual("United Arab Emirates", hub["country"])
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn("United Arab Emirates Property Guide for Foreign Buyers", html)
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        for text in (
            "Designated ownership areas",
            "Property and residence are separate",
            "Residential VAT and registration fees",
            "Licensed holiday-home operation",
            "https://dubailand.gov.ae/en/frequently-asked-questions",
            "https://u.ae/en/information-and-services/visa-and-emirates-id/residence-visas/golden-visa",
            "https://www.tax.gov.ae",
            "https://dlp.dubai.gov.ae",
        ):
            self.assertIn(text, html)

    def test_images_tables_and_orientation_are_complete(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/dubai-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src/site_assets" / Path(image.src).name).exists())
        for count, marker in (
            (10, 'class="premium-score-row"'),
            (3, 'class="premium-listing-row"'),
            (3, 'class="premium-market-anchor"'),
            (1, 'class="premium-orientation-group"'),
        ):
            self.assertEqual(count, self.html.count(marker))
        self.assertIn("asking evidence—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)
        self.assertIn("<th>Area / basis</th>", self.html)
        self.assertEqual(3, self.html.count('class="premium-table-wrap premium-card-table-wrap"'))
        for label in ("Micro-location", "Best for", "Daily life", "Primary diligence"):
            self.assertIn(f'data-label="{label}"', self.html)

    def test_quality_review_uses_canonical_scorecard_fields(self):
        review = (ROOT / "docs/research/dubai-quality-review.md").read_text()
        for weight in (
            "| Decision usefulness | 15 |",
            "| Evidence and accuracy | 25 |",
            "| Atlas model integrity | 15 |",
            "| Property and location evidence | 15 |",
            "| Editorial quality | 10 |",
            "| Design, mobile, and accessibility | 10 |",
            "| SEO and trust | 5 |",
            "| Build and maintenance | 5 |",
        ):
            self.assertIn(weight, review)
        for field in ("Reviewer:", "Approval date:", "Console warnings:"):
            self.assertIn(field, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet approved")
        self.assertIn("Result: 100/100", review)


if __name__ == "__main__":
    unittest.main()
