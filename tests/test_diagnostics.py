import unittest
from datetime import datetime, timezone

from studyn.config import AddonConfig
from studyn.diagnostics import build_diagnostic_report, sanitize_text, sanitize_url
from studyn.i18n import Translator


class DiagnosticsTests(unittest.TestCase):
    def test_url_removes_credentials_query_and_fragment(self) -> None:
        value = "https://person:password@example.com:8443/api/v1/anki?token=secret#part"
        self.assertEqual(sanitize_url(value), "https://example.com:8443/api/v1/anki")

    def test_text_redacts_known_secret_shapes(self) -> None:
        value = "Authorization: Bearer abc.def token=hidden deviceId=device-7"
        sanitized = sanitize_text(value, ("abc.def", "device-7"))
        self.assertNotIn("abc.def", sanitized)
        self.assertNotIn("hidden", sanitized)
        self.assertNotIn("device-7", sanitized)

    def test_report_excludes_tokens_and_profile_identity(self) -> None:
        config = AddonConfig.from_dict(
            {
                "api_base_url": "https://person:password@example.com/api/v1/anki?token=url-secret",
                "language": "en-US",
            }
        )
        profile = {
            "accessToken": "access-secret",
            "deviceId": "device-secret",
            "displayName": "Private Person",
            "lastError": "Bearer access-secret failed for device-secret",
        }
        report = build_diagnostic_report(
            config=config,
            profile=profile,
            anki_version="25.09",
            sync_in_progress=False,
            translator=Translator.create("en-US"),
            generated_at=datetime(2026, 8, 11, tzinfo=timezone.utc),
        )

        for private_value in (
            "access-secret",
            "device-secret",
            "Private Person",
            "password",
            "url-secret",
        ):
            self.assertNotIn(private_value, report)
        self.assertIn("https://example.com/api/v1/anki", report)
        self.assertIn("Connected: Yes", report)


if __name__ == "__main__":
    unittest.main()
