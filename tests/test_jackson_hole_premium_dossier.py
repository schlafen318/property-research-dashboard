import csv
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
from src.build_unified_app import consolidate_destination


ROOT = Path(__file__).parents[1]
DESTINATION_ID = "jackson-hole"


class JacksonHoleDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_complete_dossier(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 30)
        self.assertIsNotNone(self.spec)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(DECISION_DIMENSION_KEYS, {key for lens in self.spec.lenses for key in lens.dimension_keys})
        self.assertEqual((3, 4, 3, 8), (len(self.spec.market_anchors), len(self.spec.micro_locations), len(self.spec.images), len(self.spec.checklist)))

    def test_copy_is_local_decision_output_and_bounded(self):
        prose = " ".join([self.spec.lede, *self.spec.verdict_paragraphs, self.spec.lenses_intro,
                          *(p for lens in self.spec.lenses for p in lens.paragraphs), self.spec.micro_locations_intro])
        for term in ("Jackson", "Teton Village", "Wilson", "Hoback", "St. John’s Health", "Teton Pass"):
            self.assertIn(term, prose)
        for pattern in (r"visitor|residence", r"fewer than 30 consecutive days", r"60 rental nights", r"wildfire|snow", r"health", r"resale|exit"):
            self.assertRegex(prose, pattern)
        self.assertNotRegex(prose, r"(?i)research read|comparative inputs|recorded dataset exchange basis|most investable|1\.8[–-]3% est\. net")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_sources_cover_material_buyer_systems(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in ("Short-Term-Rentals", "Planning-FAQs", "HSP-2025", "Assessor", "SessionLaws",
                         "firpta-withholding", "tourism-visit", "healthcare.gov", "stjohns.health",
                         "jacksonholeairport", "Maps-Schedules", "214/Location", "Hazard-Mitigation"):
            self.assertIn(fragment.lower(), urls.lower())

    def test_evidence_and_image_records_are_auditable(self):
        ledger = (ROOT / "docs/research/jackson-hole-evidence-ledger.md").read_text()
        for heading in ("Claim or topic", "Source owner", "Direct URL", "Source date / status", "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)"):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        provenance = (ROOT / "docs/research/jackson-hole-image-provenance.md").read_text()
        for filename in ("jackson-hole-valley-hero.webp", "jackson-hole-town-access.webp", "jackson-hole-winter-diligence.webp"):
            self.assertIn(filename, provenance)


class JacksonHoleDataTests(unittest.TestCase):
    def test_three_current_direct_usd_observations_reconcile(self):
        rows = [row for row in json.loads((ROOT / "data/listings.json").read_text()) if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("USD", row["local_currency"])
            self.assertEqual("2026-08-27", row["captured_date"])
            self.assertIn("living area", row["area_basis"].lower())
            self.assertEqual(row["local_price"], row["usd_price"])
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        with (ROOT / "data/listings.csv").open(newline="") as handle:
            csv_rows = [row for row in csv.DictReader(handle) if row["destination_name"] == "Jackson Hole"]
        self.assertEqual(3, len(csv_rows))
        self.assertEqual({row["listing_name"] for row in rows}, {row["listing_name"] for row in csv_rows})

    def test_shared_price_yield_score_and_calculator_are_reconciled(self):
        destination = next(row for row in json.loads((ROOT / "data/destinations.json").read_text()) if row["id"] == DESTINATION_ID)
        self.assertAlmostEqual(destination["overall_score"], consolidate_destination(destination)["decision_score"], places=2)
        self.assertNotRegex(json.dumps(destination), r"1\.8[–-]3% est\. net|very limited private land supply|clean US freehold")
        self.assertIn("no destination-wide net yield", destination["rental"]["net_yield"].lower())
        self.assertEqual(13400, destination["usd_per_m2"])
        retirement = next(row for row in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"] if row["destination_id"] == DESTINATION_ID)
        self.assertEqual(1, retirement["fx_to_usd"])
        self.assertEqual(1350000, retirement["property"]["representative_price_usd"])
        self.assertIn("illustrative planning allowance", retirement["property"]["price_basis"])
        with (ROOT / "data/destinations_summary.csv").open(newline="") as handle:
            summary = next(row for row in csv.DictReader(handle) if row["name"] == "Jackson Hole")
        self.assertEqual("Asset-specific; no destination-wide net yield", summary["net_yield_estimate"])


class JacksonHoleGeneratedPageTests(unittest.TestCase):
    def test_page_has_single_property_section_and_distinct_images(self):
        html = (ROOT / "artifacts/destinations/jackson-hole/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        self.assertNotIn("<dt>USD comparison</dt>", html)
        self.assertEqual(3, html.count("<dt>Price / m²</dt>"))
        for filename in ("jackson-hole-valley-hero.webp", "jackson-hole-town-access.webp", "jackson-hole-winter-diligence.webp"):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))
        self.assertIn("/countries/united-states-property/", html)
        country = (ROOT / "artifacts/countries/united-states-property/index.html").read_text()
        self.assertGreaterEqual(country.count("/destinations/jackson-hole/"), 2)
        self.assertIn("critical-infrastructure", country)

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/jackson-hole-quality-review.md").read_text()
        for text in ("Result: 100/100", "Approval date: 2026-08-27", "390×844", "1440×1000", "page-origin warnings/errors: 0"):
            self.assertIn(text, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet")


if __name__ == "__main__":
    unittest.main()
