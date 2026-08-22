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
DESTINATION_ID = "crete"
REVIEWED_DOSSIERS = {
    "fukuoka-itoshima", "valencia", "algarve-cascais", "madeira",
    "malaga-costa-del-sol", "hakone-izu", "lake-como", "hakuba",
    "costa-brava-girona", "park-city-deer-valley", DESTINATION_ID, "niseko", "annecy",
}


class CreteDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_the_eleven_reviewed_dossiers(self) -> None:
        self.assertEqual(REVIEWED_DOSSIERS, set(PREMIUM_DESTINATION_DOSSIERS))
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
            "Chania", "Akrotiri", "Apokoronas", "Rethymno", "Heraklion",
            "Agios Nikolaos", "Elounda", "Lasithi",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"airport|flight|ferry|road")
        self.assertRegex(prose.lower(), r"short-term|registry|registration|rental")
        self.assertRegex(prose.lower(), r"wildfire|heat|water|earthquake|flood")
        self.assertRegex(prose.lower(), r"hospital|health|emergency")
        self.assertRegex(prose.lower(), r"resale|exit|season|manager")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "aade.gr", "migration.gov.gr", "ktimatologio.gr",
            "hc-crete.gr", "civilprotection.gov.gr", "bankofgreece.gr",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs/research/crete-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-22"), 12)
        for trigger in ("tax", "planning", "listing", "transport", "hazard", "market data"):
            self.assertIn(trigger, ledger.lower())

    def test_three_market_anchors_are_bounded_not_valuations(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("€2,579/m²", "€3,110/m²", "€4,049/m²"):
            self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"asking")
        self.assertRegex(evidence.lower(), r"july 2026")

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Crete|Chania|Apokoronas|Rethymno|Heraklion|Agios Nikolaos|Lasithi|Elounda")


class CreteListingTests(unittest.TestCase):
    def test_three_current_direct_eur_observations_are_complete(self) -> None:
        listings = json.loads((ROOT / "data/listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {"Armeni Apokoronas 2-bedroom house", "Rethymno centre renovation apartment", "Ammoudara Agios Nikolaos renovated house"},
            {row["listing_name"] for row in rows},
        )
        expected_urls = {
            "https://islescout.com/property/house-in-armeni-apokoronas-with-2-bedrooms-127-m2",
            "https://www.terrarealestate.gr/en/properties/1820994",
            "https://www.indomio.gr/en/aggelies/11086013/",
        }
        self.assertEqual(expected_urls, {row["source_url"] for row in rows})
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertIn("1 EUR = 1.14784 USD", row["fx_basis"])
            self.assertAlmostEqual(row["local_price"] * 1.14784, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)


class CreteRenderingTests(unittest.TestCase):
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
        self.assertIn("Crete through five destination lenses", self.html)
        self.assertIn("Here’s how Crete scores", self.html)
        self.assertIn("Compare Crete with the full Atlas.", self.html)
        self.assertIn("/countries/greece-property/", self.html)
        self.assertIn("/retirement-abroad-calculator/", self.html)

    def test_images_tables_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/crete-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src/site_assets" / Path(image.src).name).exists())
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("asking evidence—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)

    def test_long_names_cannot_force_mobile_horizontal_overflow(self) -> None:
        self.assertIn(".premium-hero-copy { min-width: 0;", self.html)
        self.assertIn("grid-template-columns: minmax(0, 1fr)", self.html)
        self.assertIn("overflow-wrap: anywhere", self.html)


if __name__ == "__main__":
    unittest.main()
