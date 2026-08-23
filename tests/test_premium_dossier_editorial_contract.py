import unittest
from pathlib import Path

from src.premium_destination_dossiers import get_premium_dossier


ROOT = Path(__file__).parents[1]


class PremiumDossierEditorialContractTests(unittest.TestCase):
    def test_rulebook_requires_one_output_led_property_section(self) -> None:
        rulebook = (ROOT / "docs" / "PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md").read_text()
        self.assertIn("What homes cost", rulebook)
        self.assertIn("Local comparison", rulebook)
        self.assertIn("one property-evidence section", rulebook)
        self.assertIn("process commentary", rulebook)
        self.assertIn("internal audit data", rulebook)
        self.assertIn("view current listing", rulebook.lower())

    def test_rulebook_requires_distinct_image_roles_and_motif_review(self) -> None:
        rulebook = (ROOT / "docs" / "PREMIUM_DESTINATION_DOSSIER_RULEBOOK.md").read_text()
        for phrase in (
            "defining place",
            "built environment and access",
            "decision texture",
            "two images without a prominent person",
            "older people walking",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rulebook.lower())

    def test_fukuoka_uses_the_new_reader_facing_contract(self) -> None:
        spec = get_premium_dossier("fukuoka-itoshima")
        reader_copy = " ".join((
            spec.listings_intro,
            spec.market_anchors_intro,
            *(paragraph for lens in spec.lenses for paragraph in lens.paragraphs),
        )).lower()
        for phrase in (
            "representative property evidence",
            "official market anchors",
            "local asking price is primary",
            "recorded dataset exchange basis",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, reader_copy)

    def test_every_country_hub_links_its_first_substantive_destination_mention(self) -> None:
        from src.build_unified_app import COUNTRY_HUBS

        for hub in COUNTRY_HUBS:
            with self.subTest(country=hub["country"]):
                artifact = (
                    ROOT / "artifacts" / "countries" / hub["slug"] / "index.html"
                ).read_text()
                briefing = artifact.split('aria-label="Country briefing"', 1)[1].split(
                    "</section>", 1
                )[0]
                self.assertIn(
                    f'href="/destinations/{hub["destination_ids"][0]}/"',
                    briefing,
                )


if __name__ == "__main__":
    unittest.main()
