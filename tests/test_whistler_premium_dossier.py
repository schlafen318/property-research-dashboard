import json
import csv
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
DESTINATION_ID = "whistler"
FX = 1.1699 / 1.6074


class WhistlerDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_complete_whistler_dossier(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 27)
        self.assertIsNotNone(self.spec)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual((3, 4, 3, 8), (
            len(self.spec.market_anchors),
            len(self.spec.micro_locations),
            len(self.spec.images),
            len(self.spec.checklist),
        ))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_local_decision_output_and_not_process_commentary(self):
        prose = " ".join([
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(p for lens in self.spec.lenses for p in lens.paragraphs),
            self.spec.micro_locations_intro,
        ])
        for term in (
            "Whistler Village", "Creekside", "Benchlands", "Nesters",
            "Highway 99", "Whistler Health Care Centre", "Phase 1",
        ):
            self.assertIn(term, prose)
        for pattern in (
            r"1 January 2027|January 1, 2027",
            r"census agglomeration|federal purchase",
            r"tourist accommodation|nightly rental",
            r"wildfire|flood",
            r"resale|exit",
        ):
            self.assertRegex(prose, pattern)
        self.assertNotRegex(prose, r"(?i)research read|comparative inputs|recorded dataset exchange basis")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_material_buyer_systems(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "AnnualStatutes/2024_17/page-15.html",
            "SOR-2022-250/section-3.html",
            "5931020",
            "property-transfer-tax",
            "tourist-accommodation-requirements",
            "principal-residence-requirement",
            "whistler-health-care-centre",
            "bctransit.com/whistler/schedules-and-maps",
            "drivebc.ca",
            "winter-tire-and-chain-up-routes",
            "engage.whistler.ca/add-your-voice-events",
            "bcassessment.ca/news/Pages/Lower-Mainland-2026",
        ):
            self.assertIn(fragment, urls)

    def test_official_market_anchors_are_asset_bounded(self):
        evidence = " ".join(" ".join(item.values()) for item in self.spec.market_anchors)
        for value in ("2,834,000 CAD", "1,328,000 CAD", "848,000 CAD"):
            self.assertIn(value, evidence)
        self.assertIn("July 1, 2025", evidence)
        self.assertRegex(evidence.lower(), r"assessed|median")
        self.assertRegex(evidence.lower(), r"not.*valuation|not.*candidate")

    def test_atlas_reads_are_plain_concise_and_local(self):
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for read in self.spec.score_reads.values():
            self.assertGreaterEqual(len(read.split()), 12)
            self.assertLessEqual(len(read.split()), 36)
            self.assertRegex(read, r"Whistler|Creekside|Village|Highway 99|Sea-to-Sky")

    def test_evidence_and_image_records_are_auditable(self):
        ledger = (ROOT / "docs/research/whistler-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 20)
        provenance = (ROOT / "docs/research/whistler-image-provenance.md").read_text()
        for filename in (
            "whistler-valley-hero.webp",
            "whistler-creekside-access.webp",
            "whistler-winter-diligence.webp",
        ):
            self.assertIn(filename, provenance)
        self.assertGreaterEqual(provenance.count("1672×941"), 3)
        self.assertNotRegex(provenance, r"(?i)pending|unknown")


class WhistlerDataTests(unittest.TestCase):
    def test_three_current_direct_cad_observations_reconcile(self):
        rows = [
            row for row in json.loads((ROOT / "data/listings.json").read_text())
            if row["destination_id"] == DESTINATION_ID
        ]
        self.assertEqual(3, len(rows))
        self.assertEqual({
            "Nicklaus North two-bedroom condo",
            "Nesters compact detached house",
            "Creekside Phase I three-bedroom condo",
        }, {row["listing_name"] for row in rows})
        self.assertEqual({1399000, 1899000, 3495000}, {row["local_price"] for row in rows})
        nicklaus = next(row for row in rows if row["listing_name"].startswith("Nicklaus North"))
        self.assertIn("seller-marketed flexible use", nicklaus["property_type"].lower())
        self.assertIn("independent zoning", nicklaus["note"].lower())
        self.assertEqual({
            "https://www.realtor.ca/real-estate/30103048/209-8080-nicklaus-north-boulevard-whistler",
            "https://www.realtor.ca/real-estate/30104636/7102-nesters-road-whistler",
            "https://www.realtor.ca/real-estate/30159689/416-2202-gondola-way-whistler",
        }, {row["source_url"] for row in rows})
        for row in rows:
            self.assertEqual("CAD", row["local_currency"])
            self.assertEqual("2026-08-24", row["captured_date"])
            self.assertIn("portal-stated square footage", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * FX, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)

    def test_shared_price_yield_and_calculator_are_reconciled(self):
        destination = next(
            row for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        self.assertEqual("available", destination["access_status"])
        self.assertEqual(3.55, destination["overall_score"])
        self.assertEqual(13200.0, destination["usd_per_m2"])
        self.assertNotRegex(json.dumps(destination), r"2[–-]4% est\. net")
        self.assertNotRegex(json.dumps(destination), r"(?i)high ADR|compressed yield")
        self.assertIn("no destination-wide net yield", destination["rental"]["net_yield"].lower())
        retirement = next(
            row for row in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
            if row["destination_id"] == DESTINATION_ID
        )
        self.assertAlmostEqual(FX, retirement["fx_to_usd"], places=12)
        self.assertEqual(1382133, retirement["property"]["representative_price_usd"])
        self.assertEqual(0.03, retirement["property"]["acquisition_cost_rate"])

        with (ROOT / "data/destinations_summary.csv").open(newline="") as handle:
            summary = next(row for row in csv.DictReader(handle) if row["name"] == "Whistler")
        self.assertEqual("3.55", summary["overall_score"])
        self.assertEqual("13200.0", summary["usd_per_m2"])
        self.assertEqual("Asset-specific; no destination-wide net yield", summary["net_yield_estimate"])

        with (ROOT / "data/listings.csv").open(newline="") as handle:
            csv_rows = [row for row in csv.DictReader(handle) if row["destination_name"] == "Whistler"]
        json_rows = [
            row for row in json.loads((ROOT / "data/listings.json").read_text())
            if row["destination_id"] == DESTINATION_ID
        ]
        self.assertEqual(3, len(csv_rows))
        self.assertEqual({row["source_url"] for row in json_rows}, {row["source_url"] for row in csv_rows})
        self.assertIn("property transfer tax", retirement["property"]["acquisition_cost_basis"].lower())


class WhistlerGeneratedPageTests(unittest.TestCase):
    def test_page_has_single_property_section_actions_and_distinct_images(self):
        html = (ROOT / "artifacts/destinations/whistler/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        for filename in (
            "whistler-valley-hero.webp",
            "whistler-creekside-access.webp",
            "whistler-winter-diligence.webp",
        ):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))
        self.assertIn("/countries/canada-property/", html)
        self.assertLess(html.index('id="sources"'), html.index("</article>"))

    def test_canada_hub_links_first_substantive_whistler_mention(self):
        html = (ROOT / "artifacts/countries/canada-property/index.html").read_text()
        href = '/destinations/whistler/'
        self.assertIn(href, html)
        self.assertGreaterEqual(html.count(href), 2)

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/whistler-quality-review.md").read_text()
        for text in (
            "Result: 100/100",
            "Approval date: 2026-08-24",
            "390×844",
            "1440×1000",
            "page-origin warnings/errors: 0",
        ):
            self.assertIn(text, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet")


if __name__ == "__main__":
    unittest.main()
