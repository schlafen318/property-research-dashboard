import unittest
import json
import re
from pathlib import Path

from src.premium_destination_dossiers import (
    PREMIUM_DESTINATION_DOSSIERS,
    get_premium_dossier,
    validate_premium_dossier,
)


class PremiumDossierContractTests(unittest.TestCase):
    def test_only_fukuoka_uses_the_premium_registry(self) -> None:
        self.assertEqual({"fukuoka-itoshima"}, set(PREMIUM_DESTINATION_DOSSIERS))
        self.assertIsNotNone(get_premium_dossier("fukuoka-itoshima"))
        self.assertIsNone(get_premium_dossier("valencia"))

    def test_fukuoka_spec_has_the_complete_bounded_contract(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        self.assertIsNotNone(spec)
        validate_premium_dossier(spec)
        self.assertEqual(5, len(spec.lenses))
        self.assertEqual(
            10,
            len({key for lens in spec.lenses for key in lens.dimension_keys}),
        )
        self.assertLessEqual(len(spec.nav_items), 7)
        self.assertEqual(3, len(spec.images))
        self.assertEqual("sources", spec.nav_items[-1][0])


class PremiumDossierContentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = get_premium_dossier("fukuoka-itoshima")
        self.assertIsNotNone(self.spec)

    def test_references_cover_the_high_stakes_source_categories(self) -> None:
        urls = " ".join(item["url"] for item in self.spec.references)
        required_fragments = (
            "mofa.go.jp",
            "mof.go.jp",
            "nta.go.jp",
            "mlit.go.jp",
            "city.fukuoka.lg.jp",
            "city.itoshima.lg.jp",
            "fukuoka-airport.jp",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, urls)

    def test_each_lens_is_destination_specific_and_editorial_length_is_bounded(self) -> None:
        for lens in self.spec.lenses:
            prose = " ".join(lens.paragraphs)
            self.assertRegex(prose, r"Fukuoka|Itoshima")
            self.assertGreaterEqual(len(lens.paragraphs), 3)

        prose_fields = [
            self.spec.lede,
            *self.spec.verdict_paragraphs,
            self.spec.lenses_intro,
            *(paragraph for lens in self.spec.lenses for paragraph in lens.paragraphs),
            self.spec.micro_locations_intro,
            self.spec.references_intro,
        ]
        words = re.findall(r"\b[\w’'-]+\b", " ".join(prose_fields))
        self.assertGreaterEqual(len(words), 1800)
        self.assertLessEqual(len(words), 2400)

    def test_micro_locations_and_checklist_are_complete(self) -> None:
        self.assertEqual(4, len(self.spec.micro_locations))
        for location in self.spec.micro_locations:
            self.assertTrue(location["name"].strip())
            for field in ("best_for", "daily_life", "diligence"):
                self.assertTrue(location[field].strip())
        self.assertEqual(8, len(self.spec.checklist))

    def test_score_audit_uses_the_model_derived_total(self) -> None:
        destinations = json.loads((Path(__file__).parents[1] / "data" / "destinations.json").read_text())
        fukuoka = next(row for row in destinations if row["id"] == "fukuoka-itoshima")
        from src.build_unified_app import consolidate_destination

        enriched = consolidate_destination(fukuoka)
        self.assertEqual(4.27, enriched["decision_score"])
        self.assertEqual(10, len(enriched["decision_dimensions"]))


if __name__ == "__main__":
    unittest.main()
