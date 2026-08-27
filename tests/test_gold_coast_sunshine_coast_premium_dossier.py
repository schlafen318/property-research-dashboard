import json
import unittest
from pathlib import Path

from src.premium_destination_dossiers import DECISION_DIMENSION_KEYS, get_premium_dossier


ROOT = Path(__file__).resolve().parents[1]
DESTINATION_ID = "gold-coast-sunshine-coast"


class GoldCoastSunshineCoastSourceTests(unittest.TestCase):
    def test_dossier_has_complete_reader_facing_contract(self):
        spec = get_premium_dossier(DESTINATION_ID)
        self.assertIsNotNone(spec)
        self.assertEqual(5, len(spec.lenses))
        self.assertEqual(DECISION_DIMENSION_KEYS, set(spec.score_reads))
        self.assertEqual(3, len(spec.images))
        self.assertEqual(3, len(spec.market_anchors))
        self.assertEqual((0, 1, 2), spec.property_anchor_indexes)
        self.assertGreaterEqual(len(spec.micro_locations), 4)
        self.assertGreaterEqual(len(spec.checklist), 6)
        self.assertEqual("sources", spec.nav_items[-1][0])
        self.assertNotIn("research read", " ".join(spec.score_reads.values()).lower())

    def test_data_removes_unsupported_yield_and_uses_three_current_direct_observations(self):
        destinations = json.loads((ROOT / "data/destinations.json").read_text())
        destination = next(item for item in destinations if item["id"] == DESTINATION_ID)
        self.assertIn("no destination-wide net yield", destination["net_yield_estimate"].lower())
        listings = [
            item
            for item in json.loads((ROOT / "data/listings.json").read_text())
            if item.get("destination_id") == DESTINATION_ID
        ]
        self.assertEqual(3, len(listings))
        for listing in listings:
            self.assertEqual("2026-08-27", listing["captured_date"])
            self.assertTrue(listing["source_url"].startswith("https://"))
            self.assertNotIn("new-apartments/gold-coast", listing["source_url"])
            self.assertNotIn("estimate", listing["area_basis"].lower())
            self.assertGreater(listing["size_m2"], 20)
            self.assertGreater(listing["local_price"], 0)

    def test_evidence_and_image_provenance_are_recorded(self):
        ledger = (ROOT / "docs/research/gold-coast-sunshine-coast-evidence-ledger.md").read_text()
        provenance = (ROOT / "docs/research/gold-coast-sunshine-coast-image-provenance.md").read_text()
        self.assertIn("Foreign Investment", ledger)
        self.assertIn("Queensland Revenue Office", ledger)
        self.assertIn("Valuer-General", ledger)
        for filename in (
            "gold-coast-sunshine-coast-hero.webp",
            "gold-coast-sunshine-coast-daily-life.webp",
            "gold-coast-sunshine-coast-building-diligence.webp",
        ):
            self.assertIn(filename, provenance)
            self.assertTrue((ROOT / "src/site_assets" / filename).exists())


class GoldCoastSunshineCoastGeneratedPageTests(unittest.TestCase):
    def test_page_has_one_property_section_and_reader_facing_labels(self):
        html = (ROOT / "artifacts/destinations/gold-coast-sunshine-coast/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        self.assertEqual(3, html.count("Local comparison — why it matters"))
        self.assertIn("Atlas read", html)
        self.assertNotIn("Research read", html)
        self.assertNotIn("Medium confidence", html)
        self.assertIn("/countries/australia-property/", html)
        for filename in (
            "gold-coast-sunshine-coast-hero.webp",
            "gold-coast-sunshine-coast-daily-life.webp",
            "gold-coast-sunshine-coast-building-diligence.webp",
        ):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/gold-coast-sunshine-coast-quality-review.md").read_text()
        for text in (
            "Result: 100/100",
            "Approval date: 2026-08-27",
            "390×844",
            "1440×1000",
            "page-origin warnings/errors: 0",
        ):
            self.assertIn(text, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet")


if __name__ == "__main__":
    unittest.main()
