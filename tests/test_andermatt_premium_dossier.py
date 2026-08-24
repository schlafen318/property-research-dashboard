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


ROOT = Path(__file__).parents[1]
DESTINATION_ID = "andermatt"
FX = 1.1664 / 0.9362


class AndermattDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_complete_andermatt_dossier(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 28)
        self.assertIsNotNone(self.spec)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(DECISION_DIMENSION_KEYS, {key for lens in self.spec.lenses for key in lens.dimension_keys})
        self.assertEqual((3, 4, 3, 8), (len(self.spec.market_anchors), len(self.spec.micro_locations), len(self.spec.images), len(self.spec.checklist)))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_local_decision_output_and_bounded(self):
        prose = " ".join([self.spec.lede, *self.spec.verdict_paragraphs, self.spec.lenses_intro,
                          *(p for lens in self.spec.lenses for p in lens.paragraphs), self.spec.micro_locations_intro])
        for term in ("Andermatt Reuss", "old village", "Göschenen", "Altdorf", "Ursern Valley", "Lex Koller"):
            self.assertIn(term, prose)
        for pattern in (r"2040", r"residence permit", r"rental|holiday letting", r"avalanche|flood|rockfall", r"resale|exit"):
            self.assertRegex(prose, pattern)
        self.assertNotRegex(prose, r"(?i)research read|comparative inputs|recorded dataset exchange basis|most investable")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_sources_cover_material_buyer_systems(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in ("grundstueckerwerb-durch-personen-im-ausland", "wirtschaft/6658", "online-schalter/2127",
                         "_doc/406051", "naturgefahren-karten", "sem.admin.ch", "bahnhof.5165.andermatt",
                         "ksuri.ch", "Zweitwohnungen", "ecb.europa.eu"):
            self.assertIn(fragment, urls)

    def test_official_market_anchors_are_tax_parameters_not_market_claims(self):
        evidence = " ".join(" ".join(item.values()) for item in self.spec.market_anchors)
        for value in ("500 CHF/m²", "300 CHF/m²", "40 CHF/m²"):
            self.assertIn(value, evidence)
        self.assertIn("11 January 2025", evidence)
        self.assertRegex(evidence.lower(), r"tax|assessment")
        self.assertRegex(evidence.lower(), r"not.*market|not.*candidate")
        self.assertEqual((None, None, None), self.spec.property_anchor_indexes)

    def test_evidence_and_image_records_are_auditable(self):
        ledger = (ROOT / "docs/research/andermatt-evidence-ledger.md").read_text()
        for heading in ("Claim or topic", "Source owner", "Direct URL", "Source date / status", "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)"):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        provenance = (ROOT / "docs/research/andermatt-image-provenance.md").read_text()
        for filename in ("andermatt-valley-hero.webp", "andermatt-village-access.webp", "andermatt-winter-diligence.webp"):
            self.assertIn(filename, provenance)
        self.assertGreaterEqual(provenance.count("1672×941"), 3)


class AndermattDataTests(unittest.TestCase):
    def test_three_current_direct_chf_observations_reconcile(self):
        rows = [row for row in json.loads((ROOT / "data/listings.json").read_text()) if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("CHF", row["local_currency"])
            self.assertEqual("2026-08-24", row["captured_date"])
            self.assertRegex(row["area_basis"].lower(), r"seller-stated|portal-stated")
            self.assertAlmostEqual(row["local_price"] * FX, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        grand_parc = next(row for row in rows if row["listing_name"] == "Grand Parc penthouse maisonette")
        self.assertEqual(3_135_000, grand_parc["local_price"])
        self.assertIn("mandatory", grand_parc["note"].lower())

    def test_shared_price_yield_and_calculator_are_reconciled(self):
        destination = next(row for row in json.loads((ROOT / "data/destinations.json").read_text()) if row["id"] == DESTINATION_ID)
        self.assertEqual(3.55, destination["overall_score"])
        self.assertNotRegex(json.dumps(destination), r"2[–-]3\.5% est\. net|high ADR|low net yield")
        self.assertIn("no destination-wide net yield", destination["rental"]["net_yield"].lower())
        retirement = next(row for row in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"] if row["destination_id"] == DESTINATION_ID)
        self.assertAlmostEqual(FX, retirement["fx_to_usd"], places=8)
        self.assertAlmostEqual(3_135_000 * FX, retirement["property"]["representative_price_usd"], places=2)
        self.assertIn("land-register fee", retirement["property"]["acquisition_cost_basis"].lower())
        with (ROOT / "data/destinations_summary.csv").open(newline="") as handle:
            summary = next(row for row in csv.DictReader(handle) if row["name"] == "Andermatt")
        self.assertEqual("Asset-specific; no destination-wide net yield", summary["net_yield_estimate"])


class AndermattGeneratedPageTests(unittest.TestCase):
    def test_page_has_single_property_section_and_distinct_images(self):
        html = (ROOT / "artifacts/destinations/andermatt/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        self.assertNotIn("Each property record is paired", html)
        self.assertIn("unmatched background context", html)
        for filename in ("andermatt-valley-hero.webp", "andermatt-village-access.webp", "andermatt-winter-diligence.webp"):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))
        self.assertIn("/countries/switzerland-property/", html)

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/andermatt-quality-review.md").read_text()
        for text in ("Result: 100/100", "Approval date: 2026-08-25", "390×844", "1440×1000", "page-origin warnings/errors: 0"):
            self.assertIn(text, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet")


if __name__ == "__main__":
    unittest.main()
