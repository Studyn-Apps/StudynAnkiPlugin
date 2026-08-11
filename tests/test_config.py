import unittest

from studyn.config import AddonConfig


class ConfigTests(unittest.TestCase):
    def test_defaults_and_bounds(self) -> None:
        config = AddonConfig.from_dict(
            {
                "day_starts_at_hour": 99,
                "sync_days": 0,
                "initial_sync_days": 2,
                "max_sync_days": 3,
            }
        )
        self.assertEqual(config.day_starts_at_hour, 23)
        self.assertEqual(config.sync_days, 1)
        self.assertGreaterEqual(config.initial_sync_days, config.sync_days)
        self.assertGreaterEqual(config.max_sync_days, config.initial_sync_days)
        self.assertEqual(config.language, "auto")
        self.assertTrue(config.check_for_updates)
        self.assertEqual(config.update_check_interval_hours, 24)

    def test_update_check_interval_is_bounded(self) -> None:
        self.assertEqual(
            AddonConfig.from_dict({"update_check_interval_hours": 0}).update_check_interval_hours,
            1,
        )
        self.assertEqual(
            AddonConfig.from_dict({"update_check_interval_hours": 999}).update_check_interval_hours,
            168,
        )

    def test_language_override_is_normalized(self) -> None:
        self.assertEqual(AddonConfig.from_dict({"language": "pt_BR"}).language, "pt-BR")
        self.assertEqual(AddonConfig.from_dict({"language": "es-MX"}).language, "es-419")
        self.assertEqual(AddonConfig.from_dict({"language": "unknown"}).language, "auto")


if __name__ == "__main__":
    unittest.main()
