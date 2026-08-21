import unittest

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


if __name__ == "__main__":
    unittest.main()
