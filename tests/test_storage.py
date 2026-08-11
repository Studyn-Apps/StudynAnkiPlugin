import tempfile
import unittest
from pathlib import Path

from studyn.storage import LocalStorage


class StorageTests(unittest.TestCase):
    def test_credentials_are_isolated_by_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(Path(directory))
            first = storage.profile_key("Primeiro")
            second = storage.profile_key("Segundo")
            storage.save_token(first, "secret", "device-1", "Pessoa")

            self.assertEqual(storage.get_profile(first)["accessToken"], "secret")
            self.assertEqual(storage.get_profile(second), {})
            raw = storage.path.read_text(encoding="utf-8")
            self.assertNotIn("Primeiro", raw)

    def test_disconnect_removes_only_current_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            storage = LocalStorage(Path(directory))
            first = storage.profile_key("A")
            second = storage.profile_key("B")
            storage.save_token(first, "a", "one")
            storage.save_token(second, "b", "two")
            storage.disconnect(first)

            self.assertEqual(storage.get_profile(first), {})
            self.assertEqual(storage.get_profile(second)["accessToken"], "b")


if __name__ == "__main__":
    unittest.main()
