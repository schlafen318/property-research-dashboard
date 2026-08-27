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
DESTINATION_ID = "ticino-lake-lugano"


class TicinoLakeLuganoDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_complete_ticino_dossier(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 31)
        self.assertIsNotNone(self.spec)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(DECISION_DIMENSION_KEYS, {key for lens in self.spec.lenses for key in lens.dimension_keys})
        self.assertEqual((3, 4, 3, 8), (len(self.spec.market_anchors), len(self.spec.micro_locations), len(self.spec.images), len(self.spec.checklist)))
        self.assertEqual((0, 1, 2), self.spec.property_anchor_indexes)

    def test_copy_is_local_decision_output_and_bounded(self):
        prose = " ".join([self.spec.lede, *self.spec.verdict_paragraphs, self.spec.lenses_intro,
                          *(p for lens in self.spec.lenses for p in lens.paragraphs), self.spec.micro_locations_intro])
        for term in ("Lugano", "Lex Koller", "Paradiso", "Castagnola", "Morcote", "Ospedale Civico"):
            self.assertIn(term, prose)
        for pattern in (r"residence permit", r"holiday home", r"second home", r"landslide|flood", r"health", r"resale|exit"):
            self.assertRegex(prose, pattern)
        self.assertNotRegex(prose, r"(?i)research read|comparative inputs|recorded dataset exchange basis|1\.5[–-]3% est\. net|swiss safety and italian flavour")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_sources_cover_material_buyer_systems(self):
        urls = " ".join(item["url"] for item in self.spec.references).lower()
        for fragment in ("questions-and-answers", "/lafe/", "raccolta-leggi", "zweitwohnungen",
                         "health-insurance", "eoc.ch", "carte-del-pericolo", "258243ns_2026-08.pdf", "lugano.ch"):
            self.assertIn(fragment, urls)

    def test_evidence_and_image_records_are_auditable(self):
        ledger = (ROOT / "docs/research/ticino-lake-lugano-evidence-ledger.md").read_text()
        for heading in ("Claim or topic", "Source owner", "Direct URL", "Source date / status", "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)"):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 16)
        provenance = (ROOT / "docs/research/ticino-lake-lugano-image-provenance.md").read_text()
        for filename in ("ticino-lugano-lake-hero.webp", "ticino-lugano-city-access.webp", "ticino-lugano-hillside-diligence.webp"):
            self.assertIn(filename, provenance)
        for phrase in ("1672×941", "OpenAI ImageGen", "may publish", "Approved 2026-08-27", "/Users/steph-tmp/.codex/generated_images/"):
            self.assertIn(phrase, provenance)


class TicinoLakeLuganoDataTests(unittest.TestCase):
    def test_three_current_direct_chf_observations_reconcile(self):
        rows = [row for row in json.loads((ROOT / "data/listings.json").read_text()) if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("CHF", row["local_currency"])
            self.assertEqual("2026-08-27", row["captured_date"])
            self.assertIn("living area", row["area_basis"].lower())
            self.assertAlmostEqual(row["local_price"] * row["fx_to_usd"], row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        with (ROOT / "data/listings.csv").open(newline="") as handle:
            csv_rows = [row for row in csv.DictReader(handle) if row["destination_name"] == "Ticino / Lake Lugano"]
        self.assertEqual(3, len(csv_rows))
        self.assertEqual({row["listing_name"] for row in rows}, {row["listing_name"] for row in csv_rows})

    def test_shared_price_yield_score_and_calculator_are_reconciled(self):
        destination = next(row for row in json.loads((ROOT / "data/destinations.json").read_text()) if row["id"] == DESTINATION_ID)
        self.assertAlmostEqual(destination["overall_score"], consolidate_destination(destination)["decision_score"], places=2)
        self.assertNotRegex(json.dumps(destination), r"1\.5[–-]3% est\. net|Swiss safety and Italian flavour")
        self.assertIn("no destination-wide net yield", destination["rental"]["net_yield"].lower())
        self.assertNotRegex(json.dumps(destination), r"(?i)low yields|residential yields are low")
        self.assertEqual(8900, destination["usd_per_m2"])
        retirement = next(row for row in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"] if row["destination_id"] == DESTINATION_ID)
        self.assertAlmostEqual(1 / 0.81, retirement["fx_to_usd"], places=10)
        self.assertAlmostEqual(1450000 / 0.81, retirement["property"]["representative_price_usd"], places=2)
        self.assertEqual(0, retirement["property"]["acquisition_cost_rate"])
        self.assertIn("transaction costs are excluded", retirement["property"]["acquisition_cost_basis"].lower())
        self.assertIn("swiss national bank", retirement["property"]["price_basis"].lower())
        with (ROOT / "data/destinations_summary.csv").open(newline="") as handle:
            summary = next(row for row in csv.DictReader(handle) if row["name"] == "Ticino / Lake Lugano")
        self.assertEqual("Asset-specific; no destination-wide net yield", summary["net_yield_estimate"])


class TicinoLakeLuganoGeneratedPageTests(unittest.TestCase):
    def test_page_has_single_property_section_and_distinct_images(self):
        html = (ROOT / "artifacts/destinations/ticino-lake-lugano/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        self.assertEqual(3, html.count("<dt>USD comparison</dt>"))
        for filename in ("ticino-lugano-lake-hero.webp", "ticino-lugano-city-access.webp", "ticino-lugano-hillside-diligence.webp"):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))
        self.assertIn("/countries/switzerland-property/", html)
        calculator = (ROOT / "artifacts/retirement-abroad-calculator/index.html").read_text()
        self.assertIn('id="ret-acquisition-cost-guidance"', calculator)
        self.assertIn("Transaction costs are excluded because Ticino", calculator)
        self.assertIn("acquisitionCostBasis", calculator)
        country = (ROOT / "artifacts/countries/switzerland-property/index.html").read_text()
        self.assertGreaterEqual(country.count("/destinations/ticino-lake-lugano/"), 2)
        self.assertIn("questions-and-answers", country)

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/ticino-lake-lugano-quality-review.md").read_text()
        for text in ("Result: 100/100", "Approval date: 2026-08-27", "390×844", "1440×1000", "page-origin warnings/errors: 0"):
            self.assertIn(text, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet")


if __name__ == "__main__":
    unittest.main()
