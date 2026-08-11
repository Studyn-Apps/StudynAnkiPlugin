import unittest

from studyn.i18n import Translator, resolve_language


class I18nTests(unittest.TestCase):
    def test_auto_detects_supported_system_locales(self) -> None:
        self.assertEqual(resolve_language("auto", "pt_BR"), "pt-BR")
        self.assertEqual(resolve_language("auto", "en_US"), "en-US")
        self.assertEqual(resolve_language("auto", "es_MX"), "es-419")
        self.assertEqual(resolve_language("auto", "Spanish_Argentina"), "es-419")

    def test_auto_falls_back_to_english(self) -> None:
        self.assertEqual(resolve_language("auto", "fr_FR"), "en-US")

    def test_manual_language_overrides_system_locale(self) -> None:
        self.assertEqual(resolve_language("pt-BR", "en_US"), "pt-BR")
        self.assertEqual(resolve_language("es-419", "en_US"), "es-419")

    def test_catalogs_translate_and_interpolate(self) -> None:
        expected = {
            "en-US": "Code: ABCD-EFGH",
            "pt-BR": "Código: ABCD-EFGH",
            "es-419": "Código: ABCD-EFGH",
        }
        for language, snippet in expected.items():
            message = Translator.create(language).t(
                "pairing.browser_opened", code="ABCD-EFGH"
            )
            self.assertIn(snippet, message)

    def test_every_catalog_has_the_same_keys(self) -> None:
        from studyn.i18n import TRANSLATIONS

        english_keys = set(TRANSLATIONS["en-US"])
        for language, catalog in TRANSLATIONS.items():
            self.assertEqual(set(catalog), english_keys, language)


if __name__ == "__main__":
    unittest.main()
