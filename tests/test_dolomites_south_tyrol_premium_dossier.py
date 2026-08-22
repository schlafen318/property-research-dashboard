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
DESTINATION_ID = "dolomites-south-tyrol"
EUR_USD = 1.1699


class DolomitesDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_and_bounded_contract(self):
        self.assertIn(DESTINATION_ID, PREMIUM_DESTINATION_DOSSIERS)
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

    def test_copy_is_local_decision_grade_and_bounded(self):
        prose = " ".join(
            [
                self.spec.lede,
                *self.spec.verdict_paragraphs,
                self.spec.lenses_intro,
                *(p for lens in self.spec.lenses for p in lens.paragraphs),
                self.spec.micro_locations_intro,
            ]
        )
        for term in (
            "Ortisei",
            "Selva",
            "Corvara",
            "Brunico",
            "Valdaora",
            "San Candido",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        for pattern in (
            r"reciprocity|reciprocità",
            r"resident|conventioned|convenzion",
            r"tourist|holiday|short.?term",
            r"rail|bus|car",
            r"hospital|healthcare",
            r"avalanche|flood|landslide|hazard",
            r"resale|exit|buyer pool",
        ):
            self.assertRegex(prose.lower(), pattern)
        self.assertIn("9% registration tax", prose)
        self.assertIn("written notarial closing statement", prose)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "esteri.it/en/temi/diplomazia_giuridica/condizreciprocita",
            "agenziaentrate.gov.it",
            "wohnbauaufsicht.provinz.bz.it",
            "wohnen.provinz.bz.it",
            "tourismus.provinz.bz.it",
            "suedtirolmobil.info",
            "sabes.it",
            "naturgefahren.provinz.bz.it",
            "ecb.europa.eu",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-23", self.spec.date_reviewed)
        self.assertIn("23 February 2027", self.spec.references_intro)

    def test_evidence_ledger_has_direct_urls_scope_limits_and_recheck(self):
        ledger = (ROOT / "docs/research/dolomites-south-tyrol-evidence-ledger.md").read_text()
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
        self.assertGreaterEqual(ledger.count("2026-08-23"), 16)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        for trigger in (
            "reciprocity",
            "resident housing",
            "tourist rental",
            "transport",
            "hazard",
            "market data",
            "listing",
        ):
            self.assertIn(trigger, ledger.lower())

    def test_generated_images_have_complete_provenance(self):
        provenance = (ROOT / "docs/research/dolomites-south-tyrol-image-provenance.md").read_text()
        for filename in (
            "dolomites-south-tyrol-val-gardena-life.webp",
            "dolomites-south-tyrol-pusteria-rail.webp",
            "dolomites-south-tyrol-village-routine.webp",
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

    def test_three_omi_anchors_state_period_zone_asset_and_area_basis(self):
        evidence = " ".join(
            " ".join(str(value) for value in item.values())
            for item in self.spec.market_anchors
        )
        for value in (
            "5,100–9,700 EUR/m²",
            "3,800–7,500 EUR/m²",
            "2,400–4,800 EUR/m²",
        ):
            self.assertIn(value, evidence)
        for term in ("2025 H2", "OMI", "normal-condition apartments", "gross area"):
            self.assertIn(term, evidence)

    def test_atlas_reads_are_concise_and_local(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(
                    atlas_read,
                    r"Dolomites|South Tyrol|Ortisei|Selva|Corvara|Brunico|Valdaora|San Candido|Pusteria",
                )


class DolomitesListingAndDataTests(unittest.TestCase):
    def test_three_current_direct_euro_observations_are_reconciled(self):
        rows = [
            row
            for row in json.loads((ROOT / "data/listings.json").read_text())
            if row["destination_id"] == DESTINATION_ID
        ]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Ortisei Via Minert three-room apartment",
                "Selva Strada da Nives tourist apartment",
                "Valdaora Residence Plunger second-home apartment",
            },
            {row["listing_name"] for row in rows},
        )
        self.assertEqual(
            {
                "https://www.immobiliare.it/annunci/123436481/",
                "https://www.immobiliare.it/annunci/126489173/",
                "https://www.immobiliare.it/annunci/128498934/",
            },
            {row["source_url"] for row in rows},
        )
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("Immobiliare.it", row["source_name"])
            self.assertEqual("2026-08-23", row["captured_date"])
            self.assertIn("1 EUR = 1.1699 USD", row["fx_basis"])
            self.assertIn("portal-stated", row["area_basis"].lower())
            self.assertRegex(row["area_basis"].lower(), r"commercial|surface|superficie")
            self.assertIn(row["confidence"], {"Medium-low", "Medium"})
            self.assertAlmostEqual(row["local_price"] * EUR_USD, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        self.assertEqual({115, 110, 50}, {row["size_m2"] for row in rows})
        selva = next(row for row in rows if row["listing_name"].startswith("Selva"))
        self.assertIn("Surface (Superficie) of 110 m²", selva["area_basis"])
        self.assertNotIn("commercial", selva["area_basis"].lower())
        ledger = (ROOT / "docs/research/dolomites-south-tyrol-evidence-ledger.md").read_text()
        self.assertNotIn("commercial surface 110 m²", ledger.lower())
        self.assertIn("Updated 2026-08-22; captured 2026-08-23", ledger)

    def test_shared_score_and_price_basis_are_reconciled(self):
        from src.build_unified_app import consolidate_destination

        destination = next(
            row
            for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        self.assertEqual(3.62, destination["overall_score"])
        self.assertEqual(9800.0, destination["usd_per_m2"])
        self.assertIn("median of three", destination["price_basis"].lower())
        self.assertIn("asking", destination["price_basis"].lower())
        enriched = consolidate_destination(destination)
        self.assertEqual(3.62, enriched["decision_score"])
        weighted = sum(
            item["score"] * item["weight"]
            for item in enriched["decision_dimensions"]
        )
        self.assertAlmostEqual(3.6215, weighted, places=4)


class DolomitesRenderingAndHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from src.build_unified_app import build_destination_page, consolidate_destination

        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        listings = json.loads((ROOT / "data/listings.json").read_text())
        enriched = [consolidate_destination(row) for row in destinations]
        destination = next(row for row in enriched if row["id"] == DESTINATION_ID)
        cls.html = build_destination_page(destination, listings, enriched, [])

    def test_page_uses_premium_sequence_and_responsive_records(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [
            self.html.index(f'id="{section_id}"')
            for section_id in (
                "verdict",
                "lenses",
                "scores",
                "listings",
                "locations",
                "checklist",
                "sources",
            )
        ]
        self.assertEqual(sorted(positions), positions)
        self.assertIn("Dolomites / South Tyrol through five destination lenses", self.html)
        self.assertEqual(
            3,
            self.html.count('<div class="premium-table-wrap premium-card-table-wrap">'),
        )
        self.assertIn(
            'class="premium-listing-table premium-card-table premium-desktop-record-table"',
            self.html,
        )
        self.assertEqual(27, self.html.count('class="premium-cell-value'))
        self.assertIn(".premium-desktop-record-table tbody tr", self.html)
        self.assertIn("/countries/italy-property/", self.html)

    def test_images_tables_anchors_and_orientation_are_complete(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/dolomites-south-tyrol-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            path = ROOT / "src/site_assets" / Path(image.src).name
            self.assertTrue(path.exists())
        self.assertEqual(10, self.html.count('class="premium-score-row"'))
        self.assertEqual(3, self.html.count('class="premium-listing-row"'))
        self.assertEqual(3, self.html.count('class="premium-market-anchor"'))
        self.assertEqual(2, self.html.count('class="premium-orientation-group"'))
        self.assertIn("OMI 2025 H2 zone ranges", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)

    def test_italy_hub_is_substantive_and_bidirectional(self):
        from src.build_unified_app import COUNTRY_HUBS, SEO_PAGES, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["country"] == "Italy")
        self.assertGreaterEqual(len(hub["country_rules"]), 3)
        urls = " ".join(item["url"] for item in hub["primary_sources"])
        self.assertIn("esteri.it", urls)
        self.assertIn("agenziaentrate.gov.it", urls)
        self.assertIn("elective-residence", urls)
        country_html = build_country_hub_page(
            hub,
            json.loads((ROOT / "data/destinations.json").read_text()),
            SEO_PAGES,
        )
        self.assertIn("/destinations/dolomites-south-tyrol/", country_html)
        self.assertIn("/destinations/lake-como/", country_html)

    def test_quality_review_uses_canonical_100_point_scorecard(self):
        review = (ROOT / "docs/research/dolomites-south-tyrol-quality-review.md").read_text()
        for field in (
            "Reviewer:",
            "Approval date:",
            "Decision usefulness",
            "Evidence and accuracy",
            "Atlas model integrity",
            "Property and location evidence",
            "Editorial quality",
            "Design, mobile, and accessibility",
            "SEO and trust",
            "Build and maintenance",
            "Console warnings:",
            "100/100",
        ):
            self.assertIn(field, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet approved")


if __name__ == "__main__":
    unittest.main()
