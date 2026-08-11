import unittest

from studyn.locales import (
    LOCALE_DEFINITIONS,
    LOCALES_PACKAGE_VERSION,
    SUPPORTED_LANGUAGES,
    match_studyn_locale,
)


class LocaleContractTests(unittest.TestCase):
    def test_vendored_catalog_version_and_codes(self) -> None:
        self.assertEqual(LOCALES_PACKAGE_VERSION, "0.1.0")
        self.assertEqual(SUPPORTED_LANGUAGES, ("pt-BR", "en-US", "es-419"))
        self.assertEqual(
            tuple(definition["code"] for definition in LOCALE_DEFINITIONS),
            SUPPORTED_LANGUAGES,
        )

    def test_matches_platform_locale_variants(self) -> None:
        self.assertEqual(match_studyn_locale("pt_BR"), "pt-BR")
        self.assertEqual(match_studyn_locale("pt-PT"), "pt-BR")
        self.assertEqual(match_studyn_locale("en"), "en-US")
        self.assertEqual(match_studyn_locale("en-GB"), "en-US")
        self.assertEqual(match_studyn_locale("es-MX"), "es-419")
        self.assertIsNone(match_studyn_locale("fr-FR"))


if __name__ == "__main__":
    unittest.main()
