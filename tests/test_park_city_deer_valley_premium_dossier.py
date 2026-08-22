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
DESTINATION_ID = "park-city-deer-valley"
REVIEWED_DOSSIERS = {
    "fukuoka-itoshima", "valencia", "algarve-cascais", "madeira",
    "malaga-costa-del-sol", "hakone-izu", "lake-como", "hakuba",
    "costa-brava-girona", DESTINATION_ID, "crete", "niseko", "annecy", "mallorca", "croatia-istria-dalmatia", "queenstown", "phuket-koh-samui",
}


class ParkCityDeerValleyDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_the_ten_reviewed_dossiers(self) -> None:
        self.assertTrue(REVIEWED_DOSSIERS.issubset(set(PREMIUM_DESTINATION_DOSSIERS)))
        self.assertIsNotNone(self.spec)

    def test_contract_passes_every_bounded_content_gate(self) -> None:
        self.assertIsNotNone(self.spec)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(3, len(self.spec.market_anchors))
        self.assertEqual(4, len(self.spec.micro_locations))
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
            "Old Town", "Lower Deer Valley", "Upper Deer Valley",
            "Canyons Village", "Snyderville Basin", "Park Meadows",
            "Prospector", "Kimball Junction", "Jordanelle",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"airport|salt lake|transit|bus")
        self.assertRegex(prose.lower(), r"nightly|short-term|licen[cs]e|zoning")
        self.assertRegex(prose.lower(), r"wildfire|snow|flood|insurance")
        self.assertRegex(prose.lower(), r"hospital|emergency|health")
        self.assertRegex(prose.lower(), r"resale|exit|hoa|manager")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_high_stakes_and_local_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "irs.gov", "parkcity.org", "summitcountyutah.gov",
            "parkcityrealtors.com", "intermountainhealth.org",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-23", self.spec.date_reviewed)
        self.assertIn("23 February 2027", self.spec.references_intro)
        self.assertIn("/medical-services", urls)
        self.assertIn("parkcity.gov/services/transit/about/", urls)
        self.assertIn("parkcity.gov/services/transit/routes_schedules/", urls)
        self.assertIn("parkcity.gov/services/planning/", urls)
        self.assertIn("parkcity.gov/services/building/community_code_compliance/", urls)
        self.assertNotIn("parkcity.org/departments/transit-bus", urls)
        self.assertNotIn("showpublisheddocument/76542", urls)
        self.assertNotIn("parkcity.org/departments/planning", urls)
        self.assertNotIn("parkcity.org/departments/building-department/community-code-compliance", urls)
        self.assertNotIn("open U.S. ownership", self.spec.score_reads["ownership_clarity"])
        self.assertIn("restricted foreign entities", self.spec.score_reads["ownership_clarity"])
        dossier_copy = " ".join(self.spec.verdict_paragraphs) + " " + " ".join(
            paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs
        )
        self.assertNotIn("dependable U.S. ownership", dossier_copy)
        self.assertNotIn("allowed land-use area", dossier_copy)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs/research/park-city-deer-valley-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-23"), 16)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        for trigger in ("tax", "zoning", "listing", "transport", "hazard", "market data"):
            self.assertIn(trigger, ledger.lower())

    def test_generated_images_have_a_publication_provenance_record(self) -> None:
        provenance = (ROOT / "docs/research/park-city-deer-valley-image-provenance.md").read_text()
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
        self.assertNotRegex(provenance, r"(?i)pending|unknown|unverified")

    def test_three_market_anchors_are_bounded_not_valuations(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("$4.016 million", "$1.34 million", "$2.85 million"):
            self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"median")
        self.assertRegex(evidence.lower(), r"26 sales|53 sales|q1 2026")

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Park City|Old Town|Deer Valley|Canyons|Snyderville|Prospector|Kimball|Jordanelle")


class ParkCityDeerValleyListingTests(unittest.TestCase):
    def test_three_current_direct_usd_observations_are_complete(self) -> None:
        listings = json.loads((ROOT / "data/listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {"Prospector Carriage House studio", "Canyons Fairway Springs townhouse", "Lower Deer Valley Hidden Oaks home"},
            {row["listing_name"] for row in rows},
        )
        expected_urls = {
            "https://www.parkcity-realestate.com/property-search/detail/50/12601822/1940-prospector-ave-park-city-ut-84060/",
            "https://www.parkcity-realestate.com/property-search/detail/50/12603567/4232-fairway-ln-park-city-ut-84098/",
            "https://www.parkcity-realestate.com/property-search/detail/50/12600813/35-hidden-oaks-ln-park-city-ut-84060/",
        }
        self.assertEqual(expected_urls, {row["source_url"] for row in rows})
        for row in rows:
            self.assertEqual("USD", row["local_currency"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertEqual(row["local_price"], row["usd_price"])
            self.assertIn("area_basis", row)
            self.assertRegex(row["area_basis"], r"(?i)portal|MLS|finished|square feet|sq ft")
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)

    def test_shared_score_price_and_yield_are_reconciled(self) -> None:
        from src.build_unified_app import consolidate_destination

        destination = next(
            row for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        enriched = consolidate_destination(destination)
        self.assertEqual(3.83, destination["overall_score"])
        self.assertEqual(destination["overall_score"], enriched["decision_score"])
        self.assertEqual(8200.0, destination["usd_per_m2"])
        self.assertNotIn("clean US ownership", destination["pros"])
        self.assertIn("three direct", destination["price_basis"])
        self.assertIn("asking", destination["price_basis"])
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])


class ParkCityDeerValleyRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_local_copy(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{section_id}"') for section_id in (
            "verdict", "lenses", "scores", "listings", "locations", "checklist", "sources",
        )]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Park City / Deer Valley through five destination lenses", self.html)
        self.assertIn("Here’s how Park City / Deer Valley scores", self.html)
        self.assertIn("Compare Park City / Deer Valley with the full Atlas.", self.html)
        self.assertIn("/countries/united-states-property/", self.html)
        self.assertIn("/retirement-abroad-calculator/", self.html)

    def test_images_tables_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/park-city-deer-valley-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src/site_assets" / Path(image.src).name).exists())
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("public market signals—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)

    def test_long_names_cannot_force_mobile_horizontal_overflow(self) -> None:
        self.assertIn(".premium-hero-copy { min-width: 0;", self.html)
        self.assertIn("grid-template-columns: minmax(0, 1fr)", self.html)
        self.assertIn("overflow-wrap: anywhere", self.html)

    def test_us_country_handoff_is_substantive_and_bidirectional(self) -> None:
        from src.build_unified_app import COUNTRY_HUBS, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "united-states-property")
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        self.assertGreaterEqual(len(hub["country_rules"]), 4)
        source_urls = " ".join(item["url"] for item in hub["primary_sources"])
        for fragment in ("travel.state.gov", "irs.gov", "le.utah.gov"):
            self.assertIn(fragment, source_urls)
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        self.assertIn("Utah restricts defined foreign entities", html)

    def test_quality_review_uses_canonical_scorecard_fields(self) -> None:
        review = (ROOT / "docs/research/park-city-deer-valley-quality-review.md").read_text()
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
