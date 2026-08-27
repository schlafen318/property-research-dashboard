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
DESTINATION_ID = "innsbruck-tyrol"
FX = 1.1664


class InnsbruckTyrolDossierContractTests(unittest.TestCase):
    def setUp(self):
        self.spec = get_premium_dossier(DESTINATION_ID)

    def test_registry_contains_complete_dossier(self):
        self.assertGreaterEqual(len(PREMIUM_DESTINATION_DOSSIERS), 29)
        self.assertIsNotNone(self.spec)
        validate_premium_dossier(self.spec)
        self.assertEqual(5, len(self.spec.lenses))
        self.assertEqual(DECISION_DIMENSION_KEYS, {key for lens in self.spec.lenses for key in lens.dimension_keys})
        self.assertEqual((3, 4, 3, 8), (len(self.spec.market_anchors), len(self.spec.micro_locations), len(self.spec.images), len(self.spec.checklist)))
        self.assertEqual("sources", self.spec.nav_items[-1][0])

    def test_copy_is_local_decision_output_and_bounded(self):
        prose = " ".join([self.spec.lede, *self.spec.verdict_paragraphs, self.spec.lenses_intro,
                          *(p for lens in self.spec.lenses for p in lens.paragraphs), self.spec.micro_locations_intro])
        for term in ("Innsbruck", "Hötting", "Igls", "Seefeld", "Freizeitwohnsitz", "Landeskrankenhaus"):
            self.assertIn(term, prose)
        for pattern in (r"third-country|EU|EEA", r"main residence|residence permit", r"holiday|tourist", r"flood|avalanche", r"resale|exit"):
            self.assertRegex(prose, pattern)
        self.assertNotRegex(prose, r"(?i)research read|comparative inputs|recorded dataset exchange basis|most investable|2[–-]3\.5% est\. net")
        words = re.findall(r"\b[\w’'-]+\b", prose)
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2500)

    def test_sources_cover_material_buyer_systems(self):
        urls = " ".join(item["url"] for item in self.spec.references)
        for fragment in ("grundstueckskauf", "grundverkehrsrecht", "freizeitwohnsitze", "grunderwerbsteuer/steuersatz.html",
                         "tiris-kartendienste-zu-fachthemen", "WT-TE-UK-PV",
                         "Seite.120217", "immobilien-durchschnittspreise", "vvt.at", "innsbruck-airport", "tirol-kliniken", "tiris"):
            self.assertIn(fragment.lower(), urls.lower())

    def test_evidence_and_image_records_are_auditable(self):
        ledger = (ROOT / "docs/research/innsbruck-tyrol-evidence-ledger.md").read_text()
        for heading in ("Claim or topic", "Source owner", "Direct URL", "Source date / status", "Reviewed", "Scope", "Limitation", "Recheck trigger", "Destination section(s)"):
            self.assertIn(heading, ledger)
        self.assertGreaterEqual(ledger.count("https://"), 18)
        provenance = (ROOT / "docs/research/innsbruck-tyrol-image-provenance.md").read_text()
        for filename in ("innsbruck-tyrol-city-hero.webp", "innsbruck-tyrol-access.webp", "innsbruck-tyrol-winter-diligence.webp"):
            self.assertIn(filename, provenance)
        self.assertGreaterEqual(provenance.count("1672×941"), 3)


class InnsbruckTyrolDataTests(unittest.TestCase):
    def test_three_current_direct_eur_observations_reconcile(self):
        rows = [row for row in json.loads((ROOT / "data/listings.json").read_text()) if row["destination_id"] == DESTINATION_ID]
        self.assertEqual(3, len(rows))
        self.assertEqual(3, len({row["source_url"] for row in rows}))
        for row in rows:
            self.assertEqual("EUR", row["local_currency"])
            self.assertEqual("2026-08-25", row["captured_date"])
            self.assertRegex(row["area_basis"].lower(), r"living|wohnfläche")
            self.assertAlmostEqual(row["local_price"] * FX, row["usd_price"], places=2)
            self.assertAlmostEqual(row["usd_price"] / row["size_m2"], row["usd_per_m2"], places=2)
        with (ROOT / "data/listings.csv").open(newline="") as handle:
            csv_rows = [row for row in csv.DictReader(handle) if row["destination_name"] == "Innsbruck / Tyrol"]
        self.assertEqual(3, len(csv_rows))
        self.assertEqual({row["listing_name"] for row in rows}, {row["listing_name"] for row in csv_rows})

    def test_shared_price_yield_score_and_calculator_are_reconciled(self):
        destination = next(row for row in json.loads((ROOT / "data/destinations.json").read_text()) if row["id"] == DESTINATION_ID)
        self.assertAlmostEqual(destination["overall_score"], consolidate_destination(destination)["decision_score"], places=2)
        self.assertNotRegex(json.dumps(destination), r"2[–-]3\.5% est\. net|high ADR|good year-round urban")
        self.assertIn("no destination-wide net yield", destination["rental"]["net_yield"].lower())
        retirement = next(row for row in json.loads((ROOT / "data/retirement_costs.json").read_text())["destinations"] if row["destination_id"] == DESTINATION_ID)
        self.assertAlmostEqual(FX, retirement["fx_to_usd"], places=8)
        with (ROOT / "data/destinations_summary.csv").open(newline="") as handle:
            summary = next(row for row in csv.DictReader(handle) if row["name"] == "Innsbruck / Tyrol")
        self.assertEqual("Asset-specific; no destination-wide net yield", summary["net_yield_estimate"])


class InnsbruckTyrolGeneratedPageTests(unittest.TestCase):
    def test_page_has_single_property_section_and_distinct_images(self):
        html = (ROOT / "artifacts/destinations/innsbruck-tyrol/index.html").read_text()
        self.assertEqual(1, html.count('id="listings"'))
        self.assertEqual(3, html.count("View current listing"))
        for filename in ("innsbruck-tyrol-city-hero.webp", "innsbruck-tyrol-access.webp", "innsbruck-tyrol-winter-diligence.webp"):
            self.assertEqual(1, html.count(f'<img src="/assets/{filename}"'))
        self.assertIn("/countries/austria-property/", html)

        country = (ROOT / "artifacts/countries/austria-property/index.html").read_text()
        self.assertIn("/destinations/innsbruck-tyrol/", country)
        self.assertIn("grundverkehrsrecht", country)
        self.assertIn("/countries/austria-property/", (ROOT / "artifacts/sitemap.xml").read_text())

    def test_quality_review_records_completed_hard_gates(self):
        review = (ROOT / "docs/research/innsbruck-tyrol-quality-review.md").read_text()
        for text in ("Result: 100/100", "Approval date: 2026-08-27", "390×844", "1440×1000", "page-origin warnings/errors: 0"):
            self.assertIn(text, review)
        self.assertNotRegex(review, r"(?i)pending|provisional|not yet")


if __name__ == "__main__":
    unittest.main()
