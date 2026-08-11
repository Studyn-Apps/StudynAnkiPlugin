import json
import unittest
from datetime import datetime, timedelta, timezone

from studyn.updates import (
    RELEASES_URL,
    fetch_latest_release,
    is_check_due,
    is_newer_version,
    parse_version,
)


class Response:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.body).encode("utf-8")


class UpdateTests(unittest.TestCase):
    def test_semantic_version_comparison(self) -> None:
        self.assertEqual(parse_version("v1.2.3"), (1, 2, 3))
        self.assertTrue(is_newer_version("0.4.0", "0.3.0"))
        self.assertFalse(is_newer_version("0.3.0", "0.3.0"))
        self.assertFalse(is_newer_version("unexpected", "0.3.0"))

    def test_check_interval(self) -> None:
        now = datetime(2026, 8, 11, 12, tzinfo=timezone.utc)
        self.assertTrue(is_check_due(None, 24, now))
        self.assertFalse(is_check_due((now - timedelta(hours=23)).isoformat(), 24, now))
        self.assertTrue(is_check_due((now - timedelta(hours=24)).isoformat(), 24, now))

    def test_fetches_latest_release_and_rejects_untrusted_download_url(self) -> None:
        seen = {}

        def opener(request, timeout):
            seen["url"] = request.full_url
            seen["timeout"] = timeout
            return Response(
                {
                    "tag_name": "v0.4.0",
                    "html_url": "https://attacker.example/download",
                }
            )

        release = fetch_latest_release(timeout=7, opener=opener)
        self.assertEqual(release.version, "0.4.0")
        self.assertEqual(release.url, RELEASES_URL)
        self.assertEqual(seen["timeout"], 7)
        self.assertIn("api.github.com", seen["url"])


if __name__ == "__main__":
    unittest.main()
