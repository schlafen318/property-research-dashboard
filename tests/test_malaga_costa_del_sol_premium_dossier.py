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
DESTINATION_ID = "malaga-costa-del-sol"


class MalagaCostaDelSolDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_the_four_reviewed_dossiers(self) -> None:
        self.assertEqual(
            {"fukuoka-itoshima", "algarve-cascais", "madeira", DESTINATION_ID},
            set(PREMIUM_DESTINATION_DOSSIERS),
        )
        self.assertIsNotNone(self.spec)

    def test_destination_data_uses_the_canonical_id_everywhere(self) -> None:
        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        retirement_costs = json.loads((ROOT / "data" / "retirement_costs.json").read_text())
        self.assertEqual(1, sum(row["id"] == DESTINATION_ID for row in destinations))
        self.assertFalse(any(row["id"] == "m-laga-costa-del-sol" for row in destinations))
        self.assertEqual(3, sum(row["destination_id"] == DESTINATION_ID for row in listings))
        self.assertFalse(any(row["destination_id"] == "m-laga-costa-del-sol" for row in listings))
        self.assertIn(DESTINATION_ID, {row["destination_id"] for row in retirement_costs["destinations"]})

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

    def test_copy_is_corridor_specific_and_decision_grade(self) -> None:
        prose = " ".join(
            [
                self.spec.lede,
                *self.spec.verdict_paragraphs,
                self.spec.lenses_intro,
                *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
                self.spec.micro_locations_intro,
            ]
        )
        for term in ("Málaga city", "Benalmádena", "Fuengirola", "Marbella", "Estepona", "C1"):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"rail|road|car")
        self.assertRegex(prose.lower(), r"tourist|rental|licen[cs]")
        self.assertRegex(prose.lower(), r"resale|exit")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_high_stakes_and_local_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "inclusion.gob.es", "agenciatributaria.gob.es", "registradores.org",
            "juntadeandalucia.es", "malaga.eu", "aena.es", "renfe.com",
            "sspa.juntadeandalucia.es", "aemet.es",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs" / "research" / "malaga-costa-del-sol-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Source date / status", "Reviewed",
            "Scope", "Limitation", "Recheck trigger",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-22"), 10)
        for trigger in ("law", "municipal", "listing", "transport", "hazard", "statistics"):
            self.assertIn(trigger, ledger.lower())

    def test_three_official_anchors_are_registered_sale_evidence(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("3,101 EUR/m²", "3,387 EUR/m²", "2,964 EUR/m²"):
            self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"registered|sale|transaction")
        self.assertNotIn("asking", evidence.lower())

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Málaga|Benalmádena|Fuengirola|Marbella|Estepona|Costa del Sol")


class MalagaCostaDelSolListingTests(unittest.TestCase):
    def test_three_current_euro_listing_observations_have_recorded_fx(self) -> None:
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Málaga Centro Histórico T2 apartment",
                "Fuengirola Los Boliches T2 apartment",
                "Estepona El Paraíso T3 detached house",
            },
            {row["listing_name"] for row in rows},
        )
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("Idealista", row["source_name"])
            self.assertTrue(row["source_url"].startswith("https://www.idealista.com/inmueble/"))
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertEqual("1 EUR = 1.1567 USD; ECB reference rate, 2026-08-14", row["fx_basis"])
            self.assertAlmostEqual(row["local_price"] * 1.1567, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)


class MalagaCostaDelSolRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_malaga_copy(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{section_id}"') for section_id in (
            "verdict", "lenses", "scores", "listings", "locations", "checklist", "sources",
        )]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Málaga / Costa del Sol through five destination lenses", self.html)
        self.assertIn("Here’s how Málaga / Costa del Sol scores", self.html)
        self.assertIn("Compare Málaga / Costa del Sol with the full Atlas.", self.html)
        self.assertIn('/countries/spain-property/', self.html)
        self.assertNotIn("Fukuoka", self.html)

    def test_images_tables_market_evidence_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/malaga-costa-del-sol-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src" / "site_assets" / Path(image.src).name).exists())
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("registered-sale evidence—not asking prices", self.html)
        self.assertIn('<th>Atlas read</th>', self.html)


if __name__ == "__main__":
    unittest.main()
