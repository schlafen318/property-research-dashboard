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
DESTINATION_ID = "hakone-izu"
REVIEWED_DOSSIERS = {
    "fukuoka-itoshima",
    "valencia",
    "algarve-cascais",
    "madeira",
    "malaga-costa-del-sol",
    "lake-como",
    "hakuba",
    DESTINATION_ID,
    "costa-brava-girona",
    "park-city-deer-valley",
    "crete",
    "niseko",
    "annecy",
    "mallorca",
}


class HakoneIzuDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_the_six_reviewed_dossiers(self) -> None:
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
        for term in (
            "Atami",
            "Hakone-Yumoto",
            "Gora",
            "Sengokuhara",
            "Ito",
            "Izu-Kogen",
            "Shimoda",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        self.assertRegex(prose.lower(), r"rail|bus|car")
        self.assertRegex(prose.lower(), r"minpaku|rental")
        self.assertRegex(prose.lower(), r"volcano|landslide|tsunami|slope")
        self.assertRegex(prose.lower(), r"resale|exit")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_primary_sources_cover_high_stakes_and_local_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "mofa.go.jp",
            "mof.go.jp",
            "nta.go.jp",
            "mlit.go.jp",
            "jma.go.jp",
            "town.hakone.kanagawa.jp",
            "city.atami.lg.jp",
            "city.ito.shizuoka.jp",
            "pref.shizuoka.jp",
            "odakyu.jp",
            "izukyu.co.jp",
            "atami.iuhw.ac.jp",
            "ito-shimin-hp.jp",
            "reinfolib.mlit.go.jp",
            "ecb.europa.eu",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)
        self.assertIn("22 February 2027", self.spec.references_intro)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self) -> None:
        ledger = (ROOT / "docs" / "research" / "hakone-izu-evidence-ledger.md").read_text()
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
        for trigger in ("law", "municipal", "listing", "transport", "hazard", "land value"):
            self.assertIn(trigger, ledger.lower())

    def test_three_official_anchors_are_2026_bare_land_observations(self) -> None:
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("26,600 JPY/m²", "20,500 JPY/m²", "63,200 JPY/m²"):
            self.assertIn(value, evidence)
        self.assertIn("1 January 2026", evidence)
        self.assertRegex(evidence.lower(), r"bare land|land value")

    def test_atlas_reads_are_concise_and_locally_specific(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(atlas_read, r"Atami|Hakone|Ito|Izu-Kogen|Shimoda")


class HakoneIzuListingTests(unittest.TestCase):
    def test_three_current_direct_jpy_listing_observations_have_recorded_fx(self) -> None:
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Atami Kaikocho 1LDK apartment",
                "Hakone Miyagino 3LDK house",
                "Izu-Kogen Yawatano 2SLDK house",
            },
            {row["listing_name"] for row in rows},
        )
        for row in rows:
            self.assertEqual("JPY", row["local_currency"])
            self.assertEqual("Real Estate Japan", row["source_name"])
            self.assertTrue(row["source_url"].startswith("https://realestate.co.jp/en/forsale/view/"))
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertEqual(
                "1 JPY = 0.00628880552384 USD; derived from ECB EUR/USD and EUR/JPY reference rates, 2026-08-14",
                row["fx_basis"],
            )
            self.assertAlmostEqual(row["local_price"] * 0.00628880552384, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)


class HakoneIzuRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data" / "destinations.json").read_text())
        listings = json.loads((ROOT / "data" / "listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_the_premium_sequence_and_corridor_copy(self) -> None:
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [self.html.index(f'id="{section_id}"') for section_id in (
            "verdict", "lenses", "scores", "listings", "locations", "checklist", "sources",
        )]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Hakone and Izu through five destination lenses", self.html)
        self.assertIn("Here’s how Hakone and Izu score", self.html)
        self.assertIn("Compare Hakone and Izu with the full Atlas.", self.html)
        self.assertIn("/countries/japan-property/", self.html)

    def test_images_tables_market_evidence_and_orientation_are_complete(self) -> None:
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/hakone-izu-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src" / "site_assets" / Path(image.src).name).exists())
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("official land-value observations—not built-home valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)


if __name__ == "__main__":
    unittest.main()
