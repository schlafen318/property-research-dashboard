import json
import re
import unittest
from pathlib import Path

from PIL import Image

from src.premium_destination_dossiers import (
    DECISION_DIMENSION_KEYS,
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


ROOT = Path(__file__).parents[1]
DESTINATION_ID = "lake-tahoe"


class LakeTahoeDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_lake_tahoe(self) -> None:
        self.assertIn(DESTINATION_ID, PREMIUM_DESTINATION_DOSSIERS)
        self.assertIsNotNone(self.spec)

    def test_contract_passes_every_bounded_content_gate(self) -> None:
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(3, len(self.spec.market_anchors))
        self.assertEqual(4, len(self.spec.micro_locations))
        self.assertNotIn("vacancy tax", " ".join(item["diligence"] for item in self.spec.micro_locations).lower())
        self.assertEqual(3, len(self.spec.images))
        self.assertEqual(8, len(self.spec.checklist))
        self.assertEqual(2, len(self.spec.orientation_groups))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_locally_specific_and_decision_grade(self) -> None:
        prose = " ".join([
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
            self.spec.micro_locations_intro,
        ])
        for term in (
            "South Lake Tahoe", "Tahoe City", "Kings Beach", "Truckee",
            "Incline Village", "Crystal Bay", "Stateline", "Glenbrook",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"reno|airport|chain control|drive")
        self.assertRegex(prose.lower(), r"short-term|vacation home|permit|zoning")
        self.assertRegex(prose.lower(), r"wildfire|insurance|snow|evacuation")
        self.assertRegex(prose.lower(), r"hospital|emergency|health")
        self.assertRegex(prose.lower(), r"resale|exit|hoa|manager")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_each_operating_jurisdiction(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "irs.gov", "cityofslt.us", "placer.ca.gov", "washoecounty.gov",
            "douglascountynv.gov", "trpa.gov", "fire.ca.gov", "eldoradocounty.ca.gov",
            "leginfo.legislature.ca.gov", "leg.state.nv.us",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-23", self.spec.date_reviewed)
        self.assertIn("https://www.cityofslt.us/2510/Vacation-Home-Rentals", urls)
        self.assertIn("https://www.trpa.gov/wp-content/uploads/documents/Permitting-Procedure-Manual.pdf", urls)
        self.assertNotIn("Measure-T-updated-642025", urls)
        self.assertIn("23 February 2027", self.spec.references_intro)
        dossier_copy = " ".join(self.spec.verdict_paragraphs) + " " + " ".join(
            paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs
        )
        self.assertIn("Ordinance 2026-1203", dossier_copy)
        for jurisdiction in ("South Lake Tahoe", "Placer County", "Washoe County", "Douglas County"):
            self.assertIn(jurisdiction, dossier_copy)
        self.assertNotRegex(dossier_copy, r"(?i)one Tahoe permit|uniform Tahoe rules")

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs/research/lake-tahoe-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-23"), 18)
        self.assertGreaterEqual(ledger.count("https://"), 20)
        for trigger in ("tax", "zoning", "listing", "transport", "hazard", "market data", "insurance"):
            self.assertIn(trigger, ledger.lower())

    def test_generated_images_have_a_publication_provenance_record(self) -> None:
        provenance = (ROOT / "docs/research/lake-tahoe-image-provenance.md").read_text()
        for image in self.spec.images:
            filename = Path(image.src).name
            self.assertIn(filename, provenance)
            with Image.open(ROOT / "src/site_assets" / filename) as rendered:
                self.assertEqual((1672, 941), rendered.size)
        for field in (
            "Generation tool", "Generation date", "Prompt", "Generation output",
            "Publication-rights basis", "Visual approval",
        ):
            self.assertIn(field, provenance)
        self.assertEqual(3, provenance.count("/Users/steph-tmp/.codex/generated_images/"))
        self.assertNotRegex(provenance, r"(?i)pending|unknown|unverified")

    def test_market_anchors_are_scoped_public_signals_not_valuations(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        self.assertRegex(evidence.lower(), r"median|average")
        self.assertRegex(evidence.lower(), r"2025|2026")
        self.assertRegex(evidence.lower(), r"south lake|north lake|incline|tahoe")
        self.assertRegex(evidence.lower(), r"not a valuation|public market")

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Tahoe|Truckee|Incline|Stateline|Glenbrook|Placer|Washoe|Douglas")


class LakeTahoeListingTests(unittest.TestCase):
    def test_three_current_direct_usd_observations_are_complete(self) -> None:
        listings = json.loads((ROOT / "data/listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("USD", row["local_currency"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertEqual(row["local_price"], row["usd_price"])
            self.assertIn("area_basis", row)
            self.assertRegex(row["area_basis"], r"(?i)portal|MLS|living|square feet|sq ft")
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
            self.assertNotRegex(row["source_url"], r"zillow\.com/[^/]+/$|redfin\.com/city/|realtor\.com/realestateandhomes-search")

    def test_shared_score_price_yield_and_calculator_are_reconciled(self) -> None:
        from src.build_unified_app import consolidate_destination

        destination = next(
            row for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        enriched = consolidate_destination(destination)
        self.assertEqual(3.63, destination["overall_score"])
        self.assertEqual(destination["overall_score"], enriched["decision_score"])
        self.assertIn("three direct", destination["price_basis"])
        self.assertIn("asking", destination["price_basis"])
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])
        costs = json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
        cost = next(row for row in costs if row["destination_id"] == DESTINATION_ID)
        self.assertIn("three direct", cost["property"]["price_basis"])
        self.assertEqual(destination["representative_price_usd"], cost["property"]["representative_price_usd"])


class LakeTahoeRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_handoffs(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{section_id}"') for section_id in (
            "verdict", "lenses", "scores", "listings", "locations", "checklist", "sources",
        )]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Lake Tahoe through five destination lenses", self.html)
        self.assertIn("Here’s how Lake Tahoe scores", self.html)
        self.assertIn("Compare Lake Tahoe with the full Atlas.", self.html)
        self.assertIn("/countries/united-states-property/", self.html)
        self.assertIn("/retirement-abroad-calculator/", self.html)

    def test_images_tables_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/lake-tahoe-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("public market signals—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)

    def test_us_country_handoff_is_substantive_and_bidirectional(self) -> None:
        from src.build_unified_app import COUNTRY_HUBS, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "united-states-property")
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        self.assertGreaterEqual(len(hub["country_rules"]), 4)
        self.assertTrue(any("Tahoe crosses two states" in rule["heading"] for rule in hub["country_rules"]))
        source_urls = " ".join(source["url"] for source in hub["primary_sources"])
        for domain in ("trpa.gov", "boe.ca.gov", "tax.nv.gov", "leginfo.legislature.ca.gov", "leg.state.nv.us"):
            self.assertIn(domain, source_urls)
        self.assertIn("https://www.boe.ca.gov/pdf/pub800-10.pdf", source_urls)
        self.assertIn("https://tax.nv.gov/faqs/locally-assessed-property-tax-faqs/", source_urls)
        self.assertIn("https://www.trpa.gov/wp-content/uploads/documents/Permitting-Procedure-Manual.pdf", source_urls)
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)

    def test_quality_review_uses_canonical_scorecard_fields(self) -> None:
        review = (ROOT / "docs/research/lake-tahoe-quality-review.md").read_text()
        for weight in (
            "| Decision usefulness | 15 |", "| Evidence and accuracy | 25 |",
            "| Atlas model integrity | 15 |", "| Property and location evidence | 15 |",
            "| Editorial quality | 10 |", "| Design, mobile, and accessibility | 10 |",
            "| SEO and trust | 5 |", "| Build and maintenance | 5 |",
        ):
            self.assertIn(weight, review)
        for field in ("Reviewer:", "Approval date:", "Console warnings:"):
            self.assertIn(field, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet approved")
        self.assertIn("Result: 100/100", review)


if __name__ == "__main__":
    unittest.main()
