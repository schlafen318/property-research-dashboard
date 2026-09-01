import copy
import json
import unittest
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from src.fire_abroad import (
    ACTIVE_LIFE_WEIGHTS,
    DESTINATION_SCORE_KEYS,
    FIRE_WEIGHTS,
    LAUNCH_DESTINATION_IDS,
    load_fire_abroad,
    validate_fire_abroad_payload,
)


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_COUNTRIES = {
    "Portugal",
    "Indonesia",
    "Croatia",
    "Greece",
    "Vietnam",
    "Japan",
    "Thailand",
    "Spain",
}
EXPECTED_DESTINATION_COUNTRIES = {
    "algarve-cascais": "Portugal",
    "bali": "Indonesia",
    "croatia-istria-dalmatia": "Croatia",
    "crete": "Greece",
    "da-nang-hoi-an": "Vietnam",
    "fukuoka-itoshima": "Japan",
    "madeira": "Portugal",
    "malaga-costa-del-sol": "Spain",
    "phuket-koh-samui": "Thailand",
    "valencia": "Spain",
}
OFFICIAL_SOURCE_HOSTS = {
    "aade.gr",
    "administracion.gob.es",
    "atrbpn.go.id",
    "commission.europa.eu",
    "europa.eu",
    "exteriores.gob.es",
    "evisa.xuatnhapcanh.gov.vn",
    "fia.mof.gov.vn",
    "gov.hr",
    "gov.pt",
    "home-affairs.ec.europa.eu",
    "imigrasi.go.id",
    "info.portaldasfinancas.gov.pt",
    "mofa.go.jp",
    "narodne-novine.nn.hr",
    "nta.go.jp",
    "pajak.go.id",
    "rd.go.th",
    "sede.agenciatributaria.gob.es",
    "tax.metro.tokyo.lg.jp",
    "dol.go.th",
    "dla.go.th",
    "thaievisa.go.th",
    "vanban.chinhphu.vn",
}


class FireAbroadDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.destination_ids = {
            row["id"]
            for row in json.loads((ROOT / "data" / "destinations.json").read_text(encoding="utf-8"))
        }
        cls.retirement_ids = {
            row["destination_id"]
            for row in json.loads((ROOT / "data" / "retirement_costs.json").read_text(encoding="utf-8"))["destinations"]
        }

    def setUp(self):
        self.payload = load_fire_abroad()

    def validate(self, payload):
        return validate_fire_abroad_payload(
            payload,
            destination_ids=self.destination_ids,
            retirement_ids=self.retirement_ids,
            as_of=date(2026, 9, 1),
        )

    def test_launch_contract_is_structurally_valid(self):
        self.assertEqual(1.0, sum(FIRE_WEIGHTS.values()))
        self.assertEqual(1.0, sum(ACTIVE_LIFE_WEIGHTS.values()))
        self.assertEqual(set(LAUNCH_DESTINATION_IDS), set(self.payload["launch_destination_ids"]))
        self.assertEqual([], self.validate(self.payload))

    def test_missing_tax_source_is_rejected_for_complete_country(self):
        payload = copy.deepcopy(self.payload)
        payload["countries"]["Spain"]["tax_screen"]["source_ids"] = []
        errors = self.validate(payload)
        self.assertTrue(
            any("countries.Spain.tax_screen.source_ids" in error for error in errors),
            errors,
        )

    def test_unordered_tax_bands_are_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["countries"]["Spain"]["tax_screen"]["planning_bands"]["full_relocation"] = {
            "favorable_rate": 0.30,
            "central_rate": 0.20,
            "adverse_rate": 0.10,
        }
        errors = self.validate(payload)
        self.assertTrue(
            any("planning_bands.full_relocation" in error and "ordered" in error for error in errors),
            errors,
        )

    def test_missing_property_lifecycle_stage_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        del payload["countries"]["Spain"]["tax_screen"]["property_lifecycle"]["sale"]
        errors = self.validate(payload)
        self.assertTrue(
            any("property_lifecycle.sale" in error for error in errors),
            errors,
        )

    def test_pending_country_must_be_explicit_and_cannot_claim_tax_values(self):
        payload = copy.deepcopy(self.payload)
        pending = payload["countries"]["Portugal"]["tax_screen"]
        pending["status"] = "research_pending"
        pending["planning_bands"] = {
            "seasonal": {"favorable_rate": 0, "central_rate": 0, "adverse_rate": 0}
        }
        errors = self.validate(payload)
        self.assertTrue(
            any("countries.Portugal.tax_screen.planning_bands" in error for error in errors),
            errors,
        )

    def test_stale_review_date_is_rejected(self):
        payload = copy.deepcopy(self.payload)
        payload["countries"]["Spain"]["tax_screen"]["last_reviewed"] = "2024-01-01"
        errors = self.validate(payload)
        self.assertTrue(any("last_reviewed is stale" in error for error in errors), errors)

    def test_complete_country_requires_eligibility_evidence(self):
        payload = copy.deepcopy(self.payload)
        del payload["countries"]["Spain"]["eligibility"]
        errors = self.validate(payload)
        self.assertTrue(any("countries.Spain.eligibility" in error for error in errors), errors)

    def test_complete_destination_scores_must_be_bounded_and_complete(self):
        payload = copy.deepcopy(self.payload)
        del payload["destination_overrides"]["valencia"]["scores"]["active_life"]
        payload["destination_overrides"]["malaga-costa-del-sol"]["scores"]["global_access"] = 9
        errors = self.validate(payload)
        self.assertTrue(any("valencia.scores.active_life" in error for error in errors), errors)
        self.assertTrue(any("malaga-costa-del-sol.scores.global_access" in error for error in errors), errors)

    def test_every_launch_country_and_destination_is_complete(self):
        self.assertEqual(EXPECTED_COUNTRIES, set(self.payload["countries"]))
        self.assertEqual(EXPECTED_DESTINATION_COUNTRIES, {
            destination_id: override["country"]
            for destination_id, override in self.payload["destination_overrides"].items()
        })
        for country_name, country in self.payload["countries"].items():
            with self.subTest(country=country_name):
                self.assertEqual("complete", country["tax_screen"]["status"])
                self.assertEqual("complete", country["eligibility"]["status"])
        for destination_id, override in self.payload["destination_overrides"].items():
            with self.subTest(destination=destination_id):
                scores = override.get("scores", {})
                self.assertEqual(set(DESTINATION_SCORE_KEYS), set(scores))
                self.assertTrue(all(0 <= score <= 5 for score in scores.values()))

    def test_every_source_is_official_and_has_review_controls(self):
        source_ids = set()
        for source in self.payload["sources"]:
            with self.subTest(source=source.get("id")):
                self.assertTrue(source["id"])
                self.assertNotIn(source["id"], source_ids)
                source_ids.add(source["id"])
                self.assertTrue(source["publisher"])
                self.assertEqual("https", urlparse(source["url"]).scheme)
                host = urlparse(source["url"]).hostname
                self.assertTrue(
                    any(host == official or host.endswith(f".{official}") for official in OFFICIAL_SOURCE_HOSTS),
                    f"{source['id']} does not use an approved official host: {host}",
                )
                self.assertTrue(source.get("source_date"))
                self.assertEqual("2026-09-01", source.get("accessed_on"))
                self.assertTrue(source.get("metric_supported"))
                self.assertTrue(source.get("scope_limitation"))
                self.assertTrue(source.get("recheck_trigger"))

    def test_every_tax_claim_has_claim_level_official_sources(self):
        official_source_ids = {source["id"] for source in self.payload["sources"]}
        for country_name, country in self.payload["countries"].items():
            screen = country["tax_screen"]
            with self.subTest(country=country_name):
                screen_source_ids = set(screen.get("source_ids", []))
                self.assertTrue(screen_source_ids)
                self.assertLessEqual(screen_source_ids, official_source_ids)
                residence_source_ids = set(screen.get("residence", {}).get("source_ids", []))
                self.assertTrue(residence_source_ids)
                self.assertLessEqual(residence_source_ids, screen_source_ids)
                scope_source_ids = set(screen.get("scope_source_ids", []))
                self.assertTrue(scope_source_ids)
                self.assertLessEqual(scope_source_ids, screen_source_ids)

                funding_notes = screen.get("funding_source_notes", {})
                funding_sources = screen.get("funding_source_source_ids", {})
                self.assertTrue(funding_notes)
                self.assertEqual(set(funding_notes), set(funding_sources))
                for funding_source, summary in funding_notes.items():
                    self.assertTrue(summary, f"{country_name}.{funding_source} summary is empty")
                    claim_sources = set(funding_sources[funding_source])
                    self.assertTrue(claim_sources, f"{country_name}.{funding_source} has no sources")
                    self.assertLessEqual(claim_sources, screen_source_ids)

                method = screen.get("planning_band_method", "")
                self.assertIn("Product-defined", method)
                self.assertIn("not statutory tax rates", method)
                planning_sources = set(screen.get("planning_band_basis_source_ids", []))
                self.assertTrue(planning_sources)
                self.assertLessEqual(planning_sources, screen_source_ids)

                lifecycle = screen.get("property_lifecycle", {})
                self.assertTrue(lifecycle)
                for stage, claim in lifecycle.items():
                    if claim.get("summary"):
                        claim_sources = set(claim.get("source_ids", []))
                        self.assertTrue(claim_sources, f"{country_name}.{stage} has no sources")
                        self.assertLessEqual(claim_sources, screen_source_ids)


if __name__ == "__main__":
    unittest.main()
