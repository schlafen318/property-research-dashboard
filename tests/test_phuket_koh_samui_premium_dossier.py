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
DESTINATION_ID = "phuket-koh-samui"
FX = 1.1681 / 38.448


class PhuketKohSamuiDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_seventeen_reviewed_dossiers(self):
        self.assertEqual(17, len(PREMIUM_DESTINATION_DOSSIERS))
        self.assertIsNotNone(self.spec)

    def test_contract_passes_every_bounded_content_gate(self):
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(
            (3, 4, 3, 8, 2),
            (
                len(self.spec.market_anchors),
                len(self.spec.micro_locations),
                len(self.spec.images),
                len(self.spec.checklist),
                len(self.spec.orientation_groups),
            ),
        )
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_locally_specific_and_decision_grade(self):
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
            "Phuket Town",
            "Rawai",
            "Choeng Thale",
            "Si Sunthon",
            "Maenam",
            "Bo Phut",
            "Lamai",
            "Koh Samui",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        for pattern in (
            r"49%|foreign quota|land|lease",
            r"hotel|short.?stay|rental|licen",
            r"flood|landslide|tsunami|monsoon|drainage",
            r"hospital|health|emergency",
            r"resale|exit|buyer pool",
        ):
            self.assertRegex(prose.lower(), pattern)
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_high_stakes_and_local_categories(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "dol.go.th",
            "ltr.boi.go.th",
            "multi.dopa.go.th",
            "rd.go.th",
            "reic.or.th",
            "dmr.go.th",
            "tmd.go.th",
            "phuket.airportthai.co.th",
            "samuiairport.com",
            "bangkokhospital.com",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-22", self.spec.date_reviewed)

    def test_evidence_ledger_records_scope_limits_and_recheck_triggers(self):
        ledger = (ROOT / "docs/research/phuket-koh-samui-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic",
            "Source owner",
            "Direct URL",
            "Source date / status",
            "Reviewed",
            "Scope",
            "Limitation",
            "Recheck trigger",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("2026-08-22"), 14)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        for trigger in (
            "ownership",
            "visa",
            "tax",
            "lodging",
            "listing",
            "transport",
            "hazard",
            "market data",
        ):
            self.assertIn(trigger, ledger.lower())

    def test_three_market_anchors_are_current_and_officially_bounded(self):
        evidence = " ".join(" ".join(str(value) for value in item.values()) for item in self.spec.market_anchors)
        for value in ("1,190 units", "6,087 million THB", "8.3 million THB"):
            self.assertIn(value, evidence)
        self.assertRegex(evidence.lower(), r"transfer|asking inventory|province")
        self.assertIn("2025", evidence)
        self.assertIn("Q1 2026", evidence)

    def test_atlas_reads_are_concise_and_locally_specific(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for key, atlas_read in self.spec.score_reads.items():
            with self.subTest(key=key):
                self.assertGreaterEqual(len(atlas_read.split()), 12)
                self.assertLessEqual(len(atlas_read.split()), 36)
                self.assertRegex(
                    atlas_read,
                    r"Phuket|Koh Samui|Samui|Rawai|Choeng Thale|Si Sunthon|Maenam|Bo Phut|Lamai",
                )


class PhuketKohSamuiListingTests(unittest.TestCase):
    def test_three_current_direct_thb_observations_are_complete(self):
        rows = [
            item
            for item in json.loads((ROOT / "data/listings.json").read_text())
            if item["destination_id"] == DESTINATION_ID
        ]
        self.assertEqual(3, len(rows))
        self.assertEqual(
            {
                "Rawai foreign-quota resort condominium",
                "Si Sunthon company-structure pool villa",
                "Maenam company-sale pool villa",
            },
            {item["listing_name"] for item in rows},
        )
        self.assertEqual(
            {
                "https://www.fazwaz.com/property-sales/2-bedroom-condo-for-sale-at-selina-serenity-resort-residences-in-rawai-phuket-u1944488",
                "https://www.fazwaz.com/property-sales/4-bedroom-villa-for-sale-at-manor-phuket-in-si-sunthon-phuket-u6144306",
                "https://www.fazwaz.com/property-sales/3-bedroom-villa-for-sale-in-maenam-surat-thani-u6076824",
            },
            {item["source_url"] for item in rows},
        )
        for row in rows:
            self.assertEqual("THB", row["local_currency"])
            self.assertEqual("2026-08-22", row["captured_date"])
            self.assertIn("1 EUR = 1.1681 USD and 1 EUR = 38.448 THB", row["fx_basis"])
            self.assertIn("indoor area", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * FX, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        self.assertEqual({134, 220, 534}, {row["size_m2"] for row in rows})
        si_sunthon = next(row for row in rows if row["listing_name"].startswith("Si Sunthon"))
        self.assertEqual(30900000, si_sunthon["local_price"])
        maenam = next(row for row in rows if row["listing_name"].startswith("Maenam"))
        self.assertIn("Sale with Company", maenam["note"])

    def test_shared_price_basis_and_calculator_are_reconciled(self):
        destination = next(
            item
            for item in json.loads((ROOT / "data/destinations.json").read_text())
            if item["id"] == DESTINATION_ID
        )
        self.assertEqual(1800.0, destination["usd_per_m2"])
        self.assertEqual("$1,800", destination["quick_metrics"]["usd_m"])
        for text in ("three direct asking observations", "mixed-asset", "0.0303813"):
            self.assertIn(text, destination["price_basis"])
        retirement = next(
            item
            for item in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
            if item["destination_id"] == DESTINATION_ID
        )
        self.assertAlmostEqual(FX, retirement["fx_to_usd"], places=12)
        self.assertEqual(425338, retirement["property"]["representative_price_usd"])
        self.assertIn("median of three current direct asking observations", retirement["property"]["price_basis"].lower())
        self.assertEqual(0.025, retirement["property"]["acquisition_cost_rate"])
        self.assertIn("2% registration fee", retirement["property"]["acquisition_cost_basis"])
        source_urls = {source["url"] for source in retirement["sources"]}
        self.assertIn("https://www.dol.go.th/en/dol-services/public-service-manual/land-registration/fees-taxes-duties/", source_urls)
        self.assertIn("https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html", source_urls)


class PhuketKohSamuiRenderingTests(unittest.TestCase):
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

    def test_page_uses_premium_sequence_and_thailand_handoff(self):
        self.assertIn('<body class="premium-dossier">', self.html)
        positions = [
            self.html.index(f'id="{anchor}"')
            for anchor in ("verdict", "lenses", "scores", "listings", "locations", "checklist", "sources")
        ]
        self.assertEqual(sorted(positions), positions)
        for text in (
            "Phuket / Koh Samui through five destination lenses",
            "Here’s how Phuket / Koh Samui scores",
            "Compare Phuket / Koh Samui with the full Atlas.",
            "/countries/thailand-property/",
            "/retirement-abroad-calculator/",
        ):
            self.assertIn(text, self.html)

    def test_country_handoff_is_bidirectional_and_decision_useful(self):
        from src.build_unified_app import COUNTRY_HUBS, build_country_hub_page

        hub = next(item for item in COUNTRY_HUBS if item["slug"] == "thailand-property")
        self.assertEqual("Thailand", hub["country"])
        self.assertIn(DESTINATION_ID, hub["destination_ids"])
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        html = build_country_hub_page(hub, destinations, [])
        self.assertIn("Thailand Property Guide for Foreign Buyers", html)
        self.assertIn(f'/destinations/{DESTINATION_ID}/', html)
        for text in (
            "Foreign land ownership",
            "Foreign-quota condominium",
            "Residence is separate",
            "Short stays are an accommodation business",
            "https://www.dol.go.th/Documents/manual/2566/Info_Eng/ENG-No.42.pdf",
            "https://ltr.boi.go.th/",
            "https://multi.dopa.go.th/legal/assets/modules/news/uploads/a8fec27695d5ecdb26fe0de8f70040fc5c00b4c6870cd0192022484170852251.pdf",
        ):
            self.assertIn(text, html)

    def test_images_tables_and_orientation_are_complete(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertEqual(3, self.html.count('src="/assets/phuket-koh-samui-'))
        for image in spec.images:
            self.assertEqual(1, self.html.count(f'src="{image.src}"'))
            self.assertIn(f'alt="{image.alt}"', self.html)
            self.assertTrue((ROOT / "src/site_assets" / Path(image.src).name).exists())
        for count, marker in (
            (10, 'class="premium-score-row"'),
            (3, 'class="premium-listing-row"'),
            (3, 'class="premium-market-anchor"'),
            (2, 'class="premium-orientation-group"'),
        ):
            self.assertEqual(count, self.html.count(marker))
        self.assertIn("asking evidence—not valuations", self.html)
        self.assertIn("<th>Atlas read</th>", self.html)
        self.assertIn("<th>Area / basis</th>", self.html)

    def test_quality_review_uses_canonical_scorecard_fields(self):
        review = (ROOT / "docs/research/phuket-koh-samui-quality-review.md").read_text()
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


if __name__ == "__main__":
    unittest.main()
