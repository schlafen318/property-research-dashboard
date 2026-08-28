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
DESTINATION_ID = "vancouver-island-victoria"
FX = 1.1699 / 1.6074


class VancouverIslandVictoriaDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_preserves_reviewed_dossiers_and_contains_vancouver_island(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 18)
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

    def test_copy_leads_with_legal_geography_and_is_locally_specific(self):
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
            "Victoria Core",
            "Sidney",
            "Saanich Peninsula",
            "Sooke",
            "Nanaimo",
            "Parksville",
            "Vancouver Island",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        for pattern in (
            r"1 January 2027|January 1, 2027",
            r"census metropolitan|census agglomeration|CMA|CA",
            r"20%|additional property transfer tax",
            r"principal residence|short.?term rental",
            r"earthquake|tsunami|flood|wildfire",
            r"MSP|healthcare|hospital",
            r"resale|exit|buyer pool",
        ):
            self.assertRegex(prose, pattern)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "cmhc-schl.gc.ca",
            "AnnualStatutes/2024_17/page-15.html",
            "laws-lois.justice.gc.ca",
            "canada.ca/en/services/taxes",
            "www2.gov.bc.ca/gov/content/taxes/property-taxes",
            "short-term-rentals/principal-residence-requirement",
            "health-drug-coverage/msp",
            "preparedbc/know-your-hazards",
            "islandhealth.ca/locations/hospitals-health-centre-locations/royal-jubilee",
            "transportation-projects/other-transportation-projects/highway-14",
            "bctransit.com/victoria/schedules-and-maps",
            "bcferries.com",
            "vreb.org/current-statistics",
            "bcassessment.ca/news",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self):
        ledger = (ROOT / "docs/research/vancouver-island-victoria-evidence-ledger.md").read_text()
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
        self.assertGreaterEqual(ledger.count("2026-08-22"), 14)
        self.assertGreaterEqual(ledger.count("https://"), 23)
        for trigger in (
            "purchase ban",
            "tax",
            "short-term rental",
            "listing",
            "transport",
            "hazard",
            "market data",
        ):
            self.assertIn(trigger, ledger.lower())

    def test_generated_images_have_a_publication_provenance_record(self):
        provenance = (
            ROOT / "docs/research/vancouver-island-victoria-image-provenance.md"
        ).read_text()
        for filename in (
            "vancouver-island-victoria-daily-life.webp",
            "vancouver-island-victoria-island-access.webp",
            "vancouver-island-victoria-coastal-risk.webp",
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
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("1,311,000 CAD", "548,600 CAD", "786,000 CAD"):
            self.assertIn(value, evidence)
        self.assertIn("July 2026", evidence)
        self.assertIn("July 1, 2025", evidence)
        self.assertRegex(evidence.lower(), r"benchmark|assessed|not.*candidate")

    def test_atlas_reads_are_concise_and_locally_specific(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(
                    atlas_read,
                    r"Victoria|Sidney|Saanich|Sooke|Nanaimo|Parksville|Vancouver Island|Capital Regional District",
                )


class VancouverIslandVictoriaListingTests(unittest.TestCase):
    def test_three_current_direct_cad_observations_are_complete(self):
        rows = [
            item
            for item in json.loads((ROOT / "data/listings.json").read_text())
            if item["destination_id"] == DESTINATION_ID
        ]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Downtown Victoria renovated strata apartment",
                "Sidney new-build strata townhouse",
                "Sooke oceanfront strata townhouse",
            },
            {item["listing_name"] for item in rows},
        )
        self.assertEqual(
            {
                "https://www.realtor.ca/real-estate/30169955/403-1015-johnson-st-victoria-downtown",
                "https://www.realtor.ca/real-estate/29877007/2-2312-orchard-ave-sidney-sidney-south-east",
                "https://www.realtor.ca/real-estate/29896327/3-6995-nordin-rd-sooke-whiffin-spit",
            },
            {item["source_url"] for item in rows},
        )
        for row in rows:
            self.assertEqual("CAD", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertIn("1 EUR = 1.1699 USD and 1 EUR = 1.6074 CAD", row["fx_basis"])
            self.assertIn("finished internal area", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * FX, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        self.assertEqual({91.60239744, 116.87202432, 272.48461632}, {row["size_m2"] for row in rows})

    def test_shared_price_basis_access_status_and_calculator_are_reconciled(self):
        destination = next(
            item
            for item in json.loads((ROOT / "data/destinations.json").read_text())
            if item["id"] == DESTINATION_ID
        )
        self.assertEqual("restricted", destination["access_status"])
        self.assertIn("January 1, 2027", destination["access_summary"])
        self.assertEqual(3.15, destination["overall_score"])
        self.assertEqual(5300.0, destination["usd_per_m2"])
        self.assertEqual("$5,300", destination["quick_metrics"]["usd_m"])
        for text in ("three direct asking observations", "mixed-asset", "0.7278213"):
            self.assertIn(text, destination["price_basis"])
        retirement = next(
            item
            for item in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
            if item["destination_id"] == DESTINATION_ID
        )
        self.assertAlmostEqual(FX, retirement["fx_to_usd"], places=12)
        self.assertEqual(625781, retirement["property"]["representative_price_usd"])
        self.assertIn("median of three current direct asking observations", retirement["property"]["price_basis"].lower())
        self.assertEqual(0.22, retirement["property"]["acquisition_cost_rate"])
        self.assertIn("20% additional property transfer tax", retirement["property"]["acquisition_cost_basis"])
        source_urls = {source["url"] for source in retirement["sources"]}
        self.assertIn("https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax/additional-property-transfer-tax", source_urls)
        self.assertIn("https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html", source_urls)


class VancouverIslandVictoriaRenderingTests(unittest.TestCase):
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

    def test_page_uses_premium_sequence_and_canada_handoff(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [
            self.html.index(f'id="{anchor}"')
            for anchor in ("verdict", "lenses", "scores", "listings", "locations", "checklist", "sources")
        ]
        self.assertEqual(sorted(positions), positions)
        for text in (
            "Vancouver Island / Victoria through five destination lenses",
            "Here’s how Vancouver Island / Victoria scores",
            "Compare Vancouver Island / Victoria with the full Atlas.",
            "/countries/canada-property/",
            "/retirement-abroad-calculator/",
            "Foreign-buyer access restricted",
        ):
            self.assertIn(text, self.html)

    def test_country_handoff_is_bidirectional_and_decision_useful(self):
        from src.build_unified_app import COUNTRY_HUBS, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "canada-property")
        self.assertEqual("Canada", hub["country"])
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn("Buying Property in Canada as a Foreigner", html)
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        for text in (
            "Purchase prohibition through 1 January 2027",
            "Census geography controls eligibility",
            "Residence and healthcare are separate",
            "Foreign-buyer and vacancy taxes stack",
            "https://www.cmhc-schl.gc.ca/professionals/housing-markets-data-and-research/housing-research/consultations/prohibition-purchase-residential-property-non-canadians-act",
            "https://laws-lois.justice.gc.ca/eng/AnnualStatutes/2024_17/page-15.html",
            "https://laws-lois.justice.gc.ca/eng/regulations/SOR-2022-250/section-3.html",
            "https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax/additional-property-transfer-tax",
            "https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/uhtn1/introduction-underused-housing-tax.html",
        ):
            self.assertIn(text, html)

    def test_images_tables_and_orientation_are_complete(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/vancouver-island-victoria-'))
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
        review = (ROOT / "docs/research/vancouver-island-victoria-quality-review.md").read_text()
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
