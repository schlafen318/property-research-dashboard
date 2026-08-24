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
DESTINATION_ID = "da-nang-hoi-an"


class DaNangHoiAnDossierContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_exposes_a_complete_premium_dossier(self) -> None:
        self.assertIn(DESTINATION_ID, PREMIUM_DESTINATION_DOSSIERS)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(
            DECISION_DIMENSION_KEYS,
            {key for lens in self.spec.lenses for key in lens.dimension_keys},
        )
        self.assertEqual(3, len(self.spec.market_anchors))
        self.assertEqual(3, len(self.spec.images))
        self.assertEqual(4, len(self.spec.micro_locations))
        self.assertEqual(8, len(self.spec.checklist))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_local_decision_output_not_process_commentary(self) -> None:
        prose = " ".join([
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
            self.spec.micro_locations_intro,
        ])
        for term in (
            "Da Nang", "Hoi An", "My Khe", "Son Tra", "Hoa Hai",
            "Ngu Hanh Son", "Han River",
        ):
            with self.subTest(term=term):
                self.assertIn(term, prose)
        lower = prose.lower()
        for pattern in (
            r"ownership.*does not.*residen|buying.*does not.*residen",
            r"30%|thirty per cent|thirty percent",
            r"50 year|50-year|fifty year",
            r"flood|storm surge",
            r"hospital|health",
            r"short-term|tourist accommodation",
            r"condominium|apartment",
        ):
            self.assertRegex(lower, pattern)
        self.assertNotRegex(
            lower,
            r"local asking price is primary|usd uses|captured 2026|medium confidence|research process|the prose explains",
        )
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_current_sources_cover_material_buyer_systems(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in (
            "vanban.chinhphu.vn", "evisa.gov.vn", "moc.gov.vn",
            "danangairport.vn", "acv.vn", "soyte.danang.gov.vn",
            "danang.gov.vn", "worldbank.org", "whc.unesco.org",
            "mof.gov.vn", "dotproperty.com.vn",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)
        self.assertEqual("2026-08-24", self.spec.date_reviewed)
        self.assertRegex(self.spec.references_intro, r"24 February 2027")
        self.assertRegex(self.spec.references_intro.lower(), r"lawyer|tax adviser|property adviser")

    def test_atlas_reads_are_plain_local_and_concise(self) -> None:
        self.assertEqual(DECISION_DIMENSION_KEYS, set(self.spec.score_reads))
        for atlas_read in self.spec.score_reads.values():
            self.assertGreaterEqual(len(atlas_read.split()), 12)
            self.assertLessEqual(len(atlas_read.split()), 38)
            self.assertRegex(atlas_read, r"Da Nang|Hoi An|Vietnam|My Khe|Son Tra|Hoa Xuan")
            self.assertNotRegex(atlas_read.lower(), r"comparative inputs|research judgment|model")

    def test_evidence_and_image_records_are_auditable(self) -> None:
        ledger = (ROOT / "docs/research/da-nang-hoi-an-evidence-ledger.md").read_text()
        for heading in (
            "Claim or topic", "Source owner", "Direct URL", "Source date / status",
            "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)",
        ):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 18)

        provenance = (ROOT / "docs/research/da-nang-hoi-an-image-provenance.md").read_text()
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


class DaNangHoiAnDataTests(unittest.TestCase):
    def test_three_direct_vnd_observations_use_comparable_usable_area(self) -> None:
        listings = json.loads((ROOT / "data/listings.json").read_text())
        rows = [row for row in listings if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("VND", row["local_currency"])
            self.assertEqual("2026-08-24", row["captured_date"])
            self.assertRegex(row["area_basis"], r"(?i)portal-stated usable area")
            self.assertAlmostEqual(row["local_price"] * row["fx_rate_to_usd"], row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
            self.assertIn("dotproperty.com.vn", row["source_url"])
            self.assertNotRegex(row["note"].lower(), r"guaranteed|verified foreign quota")
        self.assertGreater(min(row["local_price"] for row in rows), 2_000_000_000)

    def test_score_price_yield_and_calculator_reconcile(self) -> None:
        from src.build_unified_app import consolidate_destination

        destination = next(
            row for row in json.loads((ROOT / "data/destinations.json").read_text())
            if row["id"] == DESTINATION_ID
        )
        enriched = consolidate_destination(destination)
        self.assertEqual(destination["overall_score"], enriched["decision_score"])
        self.assertIn("three direct", destination["price_basis"].lower())
        self.assertIn("usable area", destination["price_basis"].lower())
        self.assertNotRegex(destination["net_yield_estimate"], r"\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?%")
        self.assertEqual(destination["net_yield_estimate"], destination["quick_metrics"]["net_yield"])
        self.assertEqual(destination["net_yield_estimate"], destination["rental"]["net_yield"])

        costs = json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"]
        cost = next(row for row in costs if row["destination_id"] == DESTINATION_ID)
        self.assertIn("three direct", cost["property"]["price_basis"].lower())
        self.assertIn("planning", cost["property"]["acquisition_cost_basis"].lower())


class DaNangHoiAnGeneratedPageTests(unittest.TestCase):
    def test_page_has_one_property_section_direct_actions_and_three_distinct_images(self) -> None:
        page = (ROOT / "artifacts/destinations/da-nang-hoi-an/index.html").read_text()
        visible = html_module.unescape(re.sub(r"<[^>]+>", " ", page))
        self.assertEqual(1, page.count('id="listings"'))
        self.assertEqual(3, page.count('class="premium-property-record"'))
        self.assertEqual(3, page.count("View current listing"))
        self.assertNotRegex(visible.lower(), r"captured 2026|medium confidence|local asking price is primary")
        for image_name in (
            "da-nang-hoi-an-han-river-hero.webp",
            "da-nang-hoi-an-residential-coast.webp",
            "da-nang-hoi-an-heritage-water.webp",
        ):
            self.assertEqual(1, page.count(f'src="/assets/{image_name}"'))
        self.assertIn('/countries/vietnam-property/', page)
        self.assertRegex(page, r'/destinations/(?:bali|phuket-koh-samui|fukuoka-itoshima)/')

    def test_vietnam_hub_is_substantive_and_links_first_briefing(self) -> None:
        page = (ROOT / "artifacts/countries/vietnam-property/index.html").read_text()
        href = '/destinations/da-nang-hoi-an/'
        self.assertRegex(
            page,
            rf"Top destination match[\s\S]{{0,400}}href=\"{re.escape(href)}\"[\s\S]{{0,200}}Da Nang / Hoi An",
        )
        visible = html_module.unescape(page)
        self.assertRegex(visible, r"30%|50 years")
        self.assertIn("vanban.chinhphu.vn", page)

    def test_quality_review_records_completed_hard_gates(self) -> None:
        review = (ROOT / "docs/research/da-nang-hoi-an-quality-review.md").read_text()
        self.assertIn("Result: 100/100", review)
        self.assertIn("Independent reviewer:", review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not performed")
        self.assertIn("390×844", review)
        self.assertIn("1440×1000", review)
        self.assertRegex(review, r"page-origin (?:warnings/errors|console messages): 0")


if __name__ == "__main__":
    unittest.main()
