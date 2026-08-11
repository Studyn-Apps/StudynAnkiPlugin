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


if __name__ == "__main__":
    unittest.main()
