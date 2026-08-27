import json
import unittest
from pathlib import Path

from src.premium_destination_dossiers import DECISION_DIMENSION_KEYS, get_premium_dossier


ROOT = Path(__file__).resolve().parents[1]
DESTINATION_ID = "vancouver"


class VancouverSourceTests(unittest.TestCase):
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
            self.assertNotIn("estimate", listing["area_basis"].lower())
            self.assertGreater(listing["size_m2"], 20)
            self.assertGreater(listing["local_price"], 0)

    def test_evidence_and_image_provenance_are_recorded(self):
        ledger = (ROOT / "docs/research/vancouver-evidence-ledger.md").read_text()
        provenance = (ROOT / "docs/research/vancouver-image-provenance.md").read_text()
        self.assertIn("Department of Finance Canada", ledger)
        self.assertIn("Speculation and Vacancy Tax", ledger)
        self.assertIn("Greater Vancouver REALTORS", ledger)
        for filename in (
            "vancouver-hero.webp",
            "vancouver-daily-life.webp",
            "vancouver-risk-texture.webp",
        ):
            self.assertIn(filename, provenance)
            self.assertTrue((ROOT / "src/site_assets" / filename).exists())


class VancouverGeneratedPageTests(unittest.TestCase):
    def test_canada_hub_includes_vancouver_and_current_uht_position(self):
        html = (ROOT / "artifacts/countries/canada-property/index.html").read_text()
        self.assertIn('href="/destinations/vancouver/"', html)
        self.assertIn("Vancouver", html)
        self.assertIn("2025 and later calendar years", html)

    def test_page_has_one_property_section_and_reader_facing_labels(self):
        html = (ROOT / "artifacts/destinations/vancouver/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        self.assertEqual(3, html.count("Local comparison — why it matters"))
        self.assertIn("Atlas read", html)
        self.assertNotIn("Research read", html)
        self.assertNotIn("Medium confidence", html)
        self.assertIn("/countries/canada-property/", html)
        for filename in (
            "vancouver-hero.webp",
            "vancouver-daily-life.webp",
            "vancouver-risk-texture.webp",
        ):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/vancouver-quality-review.md").read_text()
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
