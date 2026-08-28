import html as html_module
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
DESTINATION_ID = "miami-fort-lauderdale"


class MiamiFortLauderdaleDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_exposes_a_complete_miami_dossier(self) -> None:
        self.assertIn(DESTINATION_ID, PREMIUM_DESTINATION_DOSSIERS)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(3, len(self.spec.market_anchors))
        self.assertEqual((0, 2, 1), self.spec.property_anchor_indexes)
        self.assertEqual(4, len(self.spec.micro_locations))
        self.assertEqual(3, len(self.spec.images))
        self.assertEqual(8, len(self.spec.checklist))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_reader_copy_is_local_decision_output_not_process_commentary(self) -> None:
        prose = " ".join([
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
            self.spec.micro_locations_intro,
        ])
        for term in (
            "Miami", "Fort Lauderdale", "Brickell", "Coral Gables",
            "Miami Beach", "Galt Ocean", "Broward",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        lower_prose = prose.lower()
        for pattern in (
            r"property ownership does not (?:create|provide).*immigration|buying.*does not create.*immigration",
            r"medicare|private health",
            r"milestone inspection|structural integrity reserve",
            r"flood|storm surge",
            r"insurance|wind coverage",
            r"firpta|foreign seller",
            r"short-term|vacation rental",
        ):
            self.assertRegex(lower_prose, pattern)
        self.assertNotRegex(
            prose.lower(),
            r"local asking price is primary|usd uses|appears once|the listings below|the prose explains",
        )
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_direct_sources_cover_each_material_buyer_system(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "leg.state.fl.us", "uscis.gov/eb-5", "medicare.gov",
            "condos.myfloridalicense.com", "miamidade.gov", "miamibeachfl.gov",
            "fortlauderdale.gov", "citizensfla.com", "floridarevenue.com",
            "irs.gov", "miami-airport.com", "broward.org/Airport",
            "jacksonhealth.org", "browardhealth.org", "miamirealtors.com",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-24", self.spec.date_reviewed)
        self.assertIn("24 February 2027", self.spec.references_intro)
        self.assertRegex(self.spec.references_intro.lower(), r"lawyer|tax adviser|insurance")

    def test_atlas_reads_are_plain_local_and_concise(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for atlas_read in self.spec.score_reads.values():
            self.assertGreaterEqual(len(atlas_read.split()), 12)
            self.assertLessEqual(len(atlas_read.split()), 36)
            self.assertRegex(atlas_read, r"Miami|Fort Lauderdale|Brickell|Broward|Florida|Galt")
            self.assertNotRegex(atlas_read.lower(), r"comparative inputs|research judgment|model")

    def test_evidence_and_image_records_are_auditable(self) -> None:
        ledger = (ROOT / "docs/research/miami-fort-lauderdale-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 20)
        self.assertGreaterEqual(ledger.count("2026-08-24"), 18)

        provenance = (ROOT / "docs/research/miami-fort-lauderdale-image-provenance.md").read_text()
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


class MiamiFortLauderdaleDataTests(unittest.TestCase):
    def test_three_live_usd_observations_use_living_area(self) -> None:
        listings = json.loads((ROOT / "data/listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("USD", row["local_currency"])
            self.assertEqual(1.0, row["fx_rate_to_usd"])
            self.assertEqual("2026-08-24", row["captured_date"])
            self.assertRegex(row["area_basis"], r"(?i)living")
            self.assertAlmostEqual(row["local_price"], row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)

        brickell = next(row for row in rows if "Brickell" in row["listing_name"])
        self.assertEqual(659999, brickell["local_price"])
        self.assertEqual(810, brickell["size_sqft"])
        self.assertIn("$1,319", brickell["note"])

        galt = next(row for row in rows if "Galt Ocean" in row["listing_name"])
        self.assertEqual(849000, galt["local_price"])
        self.assertEqual(1650, galt["size_sqft"])
        self.assertIn("$1,594", galt["note"])

        gables = next(row for row in rows if "Coral Gables" in row["listing_name"])
        self.assertEqual(1480000, gables["local_price"])
        self.assertEqual(1575, gables["size_sqft"])

    def test_shared_score_price_yield_and_calculator_reconcile(self) -> None:
        from src.build_unified_app import consolidate_destination

        destination = next(
            row for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        enriched = consolidate_destination(destination)
        self.assertEqual(3.9, destination["overall_score"])
        self.assertEqual(destination["overall_score"], enriched["decision_score"])
        self.assertEqual(8800, destination["usd_per_m2"])
        self.assertIn("three direct", destination["price_basis"])
        self.assertIn("living area", destination["price_basis"].lower())
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])

        costs = json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
        cost = next(row for row in costs if row["destination_id"] == DESTINATION_ID)
        self.assertEqual(849000, cost["property"]["representative_price_usd"])
        self.assertEqual(0.02, cost["property"]["acquisition_cost_rate"])
        self.assertIn("planning assumption", cost["property"]["acquisition_cost_basis"])


class MiamiFortLauderdaleGeneratedPageTests(unittest.TestCase):
    def test_generated_page_has_one_property_section_and_complete_reader_actions(self) -> None:
        page = (ROOT / "artifacts/destinations/miami-fort-lauderdale/index.html").read_text()
        visible = html_module.unescape(re.sub(r"<[^>]+>", " ", page))
        self.assertEqual(1, page.count('id="listings"'))
        self.assertEqual(3, page.count('class="premium-property-record"'))
        self.assertEqual(3, page.count("View current listing"))
        self.assertNotRegex(visible.lower(), r"captured 2026|medium confidence|local asking price is primary")
        for image_name in (
            "miami-fort-lauderdale-waterfront-hero.webp",
            "miami-fort-lauderdale-residential-life.webp",
            "miami-fort-lauderdale-coastal-diligence.webp",
        ):
            self.assertEqual(1, page.count(f'src="/assets/{image_name}"'))
        self.assertIn('/countries/united-states-property/', page)
        self.assertIn('/where-can-foreigners-buy-property/', page)
        self.assertRegex(page, r'/destinations/(?:lake-tahoe|park-city-deer-valley|fukuoka-itoshima)/')

    def test_united_states_hub_links_its_first_miami_briefing_to_the_dossier(self) -> None:
        page = (ROOT / "artifacts/countries/united-states-property/index.html").read_text()
        href = '/destinations/miami-fort-lauderdale/'
        comparison = page.split('<section id="destinations">', 1)[1].split('</section>', 1)[0]
        self.assertIn(f'href="{href}"', comparison)
        self.assertIn("Miami / Fort Lauderdale", comparison)
        self.assertIn("Florida condominium", html_module.unescape(page))

    def test_quality_review_records_completed_hard_gates(self) -> None:
        review = (ROOT / "docs/research/miami-fort-lauderdale-quality-review.md").read_text()
        self.assertIn("Result: 100/100", review)
        self.assertIn("Independent reviewer:", review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not performed")
        self.assertIn("390×844", review)
        self.assertIn("1440×1000", review)
        self.assertRegex(review, r"page-origin (?:warnings/errors|console messages): 0")


if __name__ == "__main__":
    unittest.main()
