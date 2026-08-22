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
DESTINATION_ID = "costa-brava-girona"
REVIEWED_DOSSIERS = {
    "fukuoka-itoshima",
    "valencia",
    "algarve-cascais",
    "madeira",
    "malaga-costa-del-sol",
    "hakone-izu",
    "lake-como",
    "hakuba",
    "costa-brava-girona",
    "park-city-deer-valley",
    "crete",
    "niseko",
    "annecy",
    "mallorca", "croatia-istria-dalmatia",
}


class CostaBravaGironaDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_the_nine_reviewed_dossiers(self) -> None:
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

    def test_copy_is_costa_brava_girona_specific_and_decision_grade(self) -> None:
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
            "Girona",
            "Begur",
            "Palafrugell",
            "Pals",
            "Palamós",
            "Sant Feliu de Guíxols",
            "Platja d'Aro",
            "L'Escala",
            "Roses",
            "Cadaqués",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"bus|rail|train|drive")
        self.assertRegex(prose.lower(), r"tourist|hut|licen[cs]e")
        self.assertRegex(prose.lower(), r"wildfire|flood|coastal|tramuntana")
        self.assertRegex(prose.lower(), r"hospital|clinic|ambulance")
        self.assertRegex(prose.lower(), r"resale|exit|operator|staff")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_high_stakes_and_local_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "administracion.gob.es",
            "sede.agenciatributaria.gob.es",
            "atc.gencat.cat",
            "canalempresa.gencat.cat",
            "habitatge.gencat.cat",
            "territori.gencat.cat",
            "rodalies.gencat.cat",
            "aena.es",
            "icsgirona.cat",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs" / "research" / "costa-brava-girona-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic",
            "Source owner",
            "Source date / status",
            "Reviewed",
            "Scope",
            "Limitation",
            "Recheck trigger",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-22"), 12)
        for trigger in ("law", "municipal", "listing", "transport", "hazard", "market data"):
            self.assertIn(trigger, ledger.lower())

    def test_three_public_market_anchors_are_not_presented_as_valuations(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("2,565.82 EUR/m²", "3,525.81 EUR/m²", "4,839.29 EUR/m²"):
            self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"registered sale|registered home")
        self.assertRegex(evidence.lower(), r"all homes|new homes")

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Girona|Begur|Palafrugell|Pals|Palamós|Sant Feliu|S'Agaró|Platja d'Aro|L'Escala|Roses|Cadaqués")


class CostaBravaGironaListingTests(unittest.TestCase):
    def test_three_current_direct_eur_listing_observations_have_recorded_fx(self) -> None:
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Girona Cathedral apartment",
                "Sa Roda house no. 1",
                "Sant Feliu / S'Agaró penthouse",
            },
            {row["listing_name"] for row in rows},
        )
        expected_urls = {
            "https://www.engelvoelkers.com/es/en/exposes/35d363ca-c155-543a-8ac1-a0e6958ed064",
            "https://www.costabravahouse.com/en/luxury-house-begur-sale-pool-sea-view-sa-roda-6170",
            "https://www.lucasfox.com/property-for-sale/spain/costa-brava/sant-feliu-de-guixols/apartment/pda66170.html",
        }
        self.assertEqual(expected_urls, {row["source_url"] for row in rows})
        rate = 1.14784
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertEqual(
                "1 EUR = 1.14784 USD; repository reference rate, 2026-07-22",
                row["fx_basis"],
            )
            self.assertAlmostEqual(row["local_price"] * rate, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)


class CostaBravaGironaRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_costa_brava_girona_copy(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{section_id}"') for section_id in (
            "verdict", "lenses", "scores", "listings", "locations", "checklist", "sources",
        )]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Costa Brava / Girona through five destination lenses", self.html)
        self.assertIn("Here’s how Costa Brava / Girona scores", self.html)
        self.assertIn("Compare Costa Brava / Girona with the full Atlas.", self.html)
        self.assertIn("/countries/spain-property/", self.html)
        self.assertIn("/retirement-abroad-calculator/", self.html)
        self.assertIn('data-track="retirement_calculator_open"', self.html)

    def test_images_tables_market_evidence_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/costa-brava-girona-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src" / "site_assets" / Path(image.src).name).exists())
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


if __name__ == "__main__":
    unittest.main()
