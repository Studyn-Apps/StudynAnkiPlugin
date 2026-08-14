import hashlib
import json
from io import BytesIO
from zipfile import ZipFile
import unittest
from datetime import datetime, timedelta, timezone

from studyn.updates import (
    RELEASES_URL,
    ReleaseInfo,
    download_verified_package,
    fetch_latest_release,
    is_check_due,
    is_newer_version,
    parse_version,
)


class Response:
    def __init__(self, body, json_body=True):
        self.body = body
        self.json_body = json_body

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _size=-1):
        if self.json_body:
            return json.dumps(self.body).encode("utf-8")
        return self.body


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

    def test_downloads_release_package_only_after_checksum_verification(self) -> None:
        package_buffer = BytesIO()
        with ZipFile(package_buffer, "w") as archive:
            archive.writestr("__init__.py", "")
            archive.writestr(
                "manifest.json",
                json.dumps(
                    {
                        "package": "studyn_anki_sync",
                        "name": "Studyn - Anki Sync",
                        "version": "0.4.0",
                    }
                ),
            )
        package = package_buffer.getvalue()
        digest = hashlib.sha256(package).hexdigest()
        base = "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/download/v0.4.0/"

        def metadata_opener(_request, timeout):
            return Response(
                {
                    "tag_name": "v0.4.0",
                    "html_url": base,
                    "assets": [
                        {
                            "name": "studyn-anki-sync-0.4.0.ankiaddon",
                            "browser_download_url": base
                            + "studyn-anki-sync-0.4.0.ankiaddon",
                        },
                        {
                            "name": "SHA256SUMS.txt",
                            "browser_download_url": base + "SHA256SUMS.txt",
                        },
                    ],
                }
            )

        release = fetch_latest_release(opener=metadata_opener)
        self.assertTrue(release.can_install_automatically)

        def asset_opener(request, timeout):
            if request.full_url.endswith("SHA256SUMS.txt"):
                return Response(
                    f"{digest}  studyn-anki-sync-0.4.0.ankiaddon\n".encode(),
                    json_body=False,
                )
            return Response(package, json_body=False)

        self.assertEqual(
            download_verified_package(release, opener=asset_opener), package
        )

    def test_untrusted_release_assets_cannot_be_installed_automatically(self) -> None:
        def opener(_request, timeout):
            return Response(
                {
                    "tag_name": "v0.4.0",
                    "assets": [
                        {
                            "name": "studyn-anki-sync-0.4.0.ankiaddon",
                            "browser_download_url": "https://attacker.example/addon",
                        },
                        {
                            "name": "SHA256SUMS.txt",
                            "browser_download_url": "https://attacker.example/checksum",
                        },
                    ],
                }
            )

        self.assertFalse(fetch_latest_release(opener=opener).can_install_automatically)

    def test_rejects_package_with_mismatched_checksum(self) -> None:
        release = ReleaseInfo(
            version="0.4.0",
            url=RELEASES_URL,
            package_name="studyn-anki-sync-0.4.0.ankiaddon",
            package_url=(
                "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/download/"
                "v0.4.0/studyn-anki-sync-0.4.0.ankiaddon"
            ),
            checksum_url=(
                "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/download/"
                "v0.4.0/SHA256SUMS.txt"
            ),
        )

        def opener(request, timeout):
            if request.full_url.endswith("SHA256SUMS.txt"):
                return Response(
                    ("0" * 64 + "  studyn-anki-sync-0.4.0.ankiaddon\n").encode(),
                    json_body=False,
                )
            return Response(b"tampered", json_body=False)

        with self.assertRaisesRegex(ValueError, "SHA-256"):
            download_verified_package(release, opener=opener)

    def test_rejects_verified_archive_with_wrong_manifest_version(self) -> None:
        package_buffer = BytesIO()
        with ZipFile(package_buffer, "w") as archive:
            archive.writestr("__init__.py", "")
            archive.writestr(
                "manifest.json",
                json.dumps(
                    {
                        "package": "studyn_anki_sync",
                        "name": "Studyn - Anki Sync",
                        "version": "9.9.9",
                    }
                ),
            )
        package = package_buffer.getvalue()
        digest = hashlib.sha256(package).hexdigest()
        release = ReleaseInfo(
            version="0.4.0",
            url=RELEASES_URL,
            package_name="studyn-anki-sync-0.4.0.ankiaddon",
            package_url=(
                "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/download/"
                "v0.4.0/studyn-anki-sync-0.4.0.ankiaddon"
            ),
            checksum_url=(
                "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/download/"
                "v0.4.0/SHA256SUMS.txt"
            ),
        )

        def opener(request, timeout):
            if request.full_url.endswith("SHA256SUMS.txt"):
                return Response(
                    (f"{digest}  studyn-anki-sync-0.4.0.ankiaddon\n").encode(),
                    json_body=False,
                )
            return Response(package, json_body=False)

        with self.assertRaisesRegex(ValueError, "version"):
            download_verified_package(release, opener=opener)


if __name__ == "__main__":
    unittest.main()
