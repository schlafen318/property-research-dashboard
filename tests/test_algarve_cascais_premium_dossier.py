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


class AlgarveCascaisDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier("algarve-cascais")

    def test_registry_contains_the_three_reviewed_dossiers(self) -> None:
        self.assertEqual(
            {"fukuoka-itoshima", "algarve-cascais", "madeira", "malaga-costa-del-sol", "lake-como", "hakone-izu"},
            set(PREMIUM_DESTINATION_DOSSIERS),
        )
        self.assertIsNotNone(self.spec)

    def test_algarve_contract_passes_every_bounded_content_gate(self) -> None:
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

    def test_copy_keeps_cascais_and_the_algarve_economically_distinct(self) -> None:
        prose = " ".join(
            [
                self.spec.lede,
                *self.spec.verdict_paragraphs,
                self.spec.lenses_intro,
                *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
                self.spec.micro_locations_intro,
            ]
        )
        self.assertGreaterEqual(prose.count("Cascais"), 12)
        self.assertGreaterEqual(prose.count("Algarve"), 12)
        self.assertRegex(prose, r"Tavira|eastern Algarve")
        self.assertRegex(prose, r"Lagos|western Algarve")
        self.assertRegex(prose, r"Faro Airport")
        self.assertRegex(prose, r"Lisbon Airport")
        self.assertNotIn("one interchangeable market", prose.lower())
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_all_high_stakes_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "gov.pt",
            "portaldasfinancas.gov.pt",
            "aima.gov.pt",
            "ers.pt",
            "ine.pt",
            "ana.pt",
            "prociv.gov.pt",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)

    def test_research_ledger_records_scope_dates_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs" / "research" / "algarve-cascais-evidence-ledger.md").read_text()
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
        self.assertGreaterEqual(ledger.count("2026-08-22"), 10)
        for trigger in ("law", "municipal", "listing", "transport", "hazard", "statistics"):
            self.assertIn(trigger, ledger.lower())

    def test_three_official_anchors_are_completed_sale_medians_not_asking_prices(self) -> None:
        self.assertEqual(
            {"Cascais", "Loulé", "Lagos"},
            {item["location"] for item in self.spec.market_anchors},
        )
        evidence = " ".join(
            " ".join(str(value) for value in item.values())
            for item in self.spec.market_anchors
        )
        self.assertIn("4,550 EUR/m²", evidence)
        self.assertIn("3,993 EUR/m²", evidence)
        self.assertIn("3,801 EUR/m²", evidence)
        self.assertRegex(evidence.lower(), r"completed|sale")
        self.assertNotIn("asking", evidence.lower())

    def test_score_reads_are_complete_concise_and_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Cascais|Algarve|Tavira|Lagos|Loulé")


class AlgarveCascaisListingTests(unittest.TestCase):
    def test_three_current_euro_listing_observations_have_recorded_fx(self) -> None:
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == "algarve-cascais"]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Cascais Bairro do Rosário T2 apartment",
                "Tavira Porta Nova T2 apartment",
                "Lagos Meia Praia T4 detached house",
            },
            {row["listing_name"] for row in rows},
        )
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertEqual("1 EUR = 1.1567 USD; ECB reference rate, 2026-08-14", row["fx_basis"])
            self.assertAlmostEqual(row["local_price"] * 1.1567, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)


class AlgarveCascaisRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == "algarve-cascais")
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_destination_specific_copy(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [
            self.html.index(f'id="{section_id}"')
            for section_id in ("verdict", "lenses", "scores", "listings", "locations", "checklist", "sources")
        ]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Algarve / Cascais through five destination lenses", self.html)
        self.assertIn("Here’s how Algarve / Cascais scores", self.html)
        self.assertIn("Compare Algarve / Cascais with the full Atlas.", self.html)
        self.assertIn('/countries/portugal-property/', self.html)
        self.assertNotIn("Fukuoka", self.html)
        self.assertNotIn("Japan retirement property guide", self.html)

    def test_two_gateway_orientation_does_not_draw_one_false_corridor(self) -> None:
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("Lisbon gateway", self.html)
        self.assertIn("Lisbon Airport", self.html)
        self.assertIn("Cascais / Estoril", self.html)
        self.assertIn("Faro gateway", self.html)
        self.assertIn("Faro Airport", self.html)
        self.assertIn("Central Algarve", self.html)
        self.assertIn("Eastern Algarve", self.html)
        self.assertIn("Western Algarve", self.html)

    def test_images_tables_and_market_evidence_are_complete(self) -> None:
        spec = get_premium_dossier("algarve-cascais")
        self.assertEqual(3, self.html.count('src="/assets/algarve-cascais-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src" / "site_assets" / Path(image.src).name).exists())
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertIn("completed-sale evidence—not asking prices", self.html)
        self.assertIn('<th>Atlas read</th>', self.html)

    def test_page_retains_the_mobile_quality_contract(self) -> None:
        self.assertIn("@media (max-width: 560px)", self.html)
        self.assertIn('data-label="Atlas read"', self.html)
        self.assertIn('data-label="What it represents"', self.html)
        self.assertIn(".premium-orientation-groups", self.html)
        self.assertIn("grid-template-columns: 1fr;", self.html)


if __name__ == "__main__":
    unittest.main()
