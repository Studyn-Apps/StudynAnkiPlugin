from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import PurePosixPath
from typing import Any, Callable
from urllib.request import Request, urlopen
from zipfile import BadZipFile, ZipFile

from .version import ADDON_VERSION


RELEASES_API_URL = (
    "https://api.github.com/repos/Studyn-Apps/StudynAnkiPlugin/releases/latest"
)
RELEASES_URL = "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/latest"
RELEASE_ASSET_PREFIX = (
    "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/download/"
)
_VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")
_CHECKSUM_PATTERN = re.compile(r"^([0-9a-fA-F]{64})\s+\*?(.+)$")
_MAX_RELEASE_RESPONSE_BYTES = 65536
_MAX_CHECKSUM_BYTES = 65536
_MAX_PACKAGE_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    url: str
    package_name: str | None = None
    package_url: str | None = None
    checksum_url: str | None = None

    @property
    def can_install_automatically(self) -> bool:
        return bool(self.package_name and self.package_url and self.checksum_url)


def parse_version(value: object) -> tuple[int, int, int] | None:
    match = _VERSION_PATTERN.fullmatch(str(value or "").strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


def is_newer_version(candidate: object, current: object = ADDON_VERSION) -> bool:
    candidate_parts = parse_version(candidate)
    current_parts = parse_version(current)
    return bool(candidate_parts and current_parts and candidate_parts > current_parts)


def is_check_due(
    last_checked_at: object,
    interval_hours: int,
    now: datetime | None = None,
) -> bool:
    if not last_checked_at:
        return True
    try:
        checked = datetime.fromisoformat(str(last_checked_at).replace("Z", "+00:00"))
        if checked.tzinfo is None:
            checked = checked.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return True
    reference = now or datetime.now(timezone.utc)
    return reference - checked >= timedelta(hours=max(1, interval_hours))


def fetch_latest_release(
    timeout: int = 10,
    opener: Callable[..., Any] | None = None,
) -> ReleaseInfo:
    request = Request(
        RELEASES_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"StudynAnkiSync/{ADDON_VERSION}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    open_url = opener or urlopen
    raw = _download_bytes(
        request,
        timeout=max(1, int(timeout)),
        opener=open_url,
        maximum_bytes=_MAX_RELEASE_RESPONSE_BYTES,
        description="GitHub release response",
    )
    body = json.loads(raw.decode("utf-8"))
    tag = str(body.get("tag_name") or "")
    parsed = parse_version(tag)
    if not parsed:
        raise ValueError("GitHub returned an invalid release version")
    version = ".".join(str(part) for part in parsed)
    candidate_url = str(body.get("html_url") or "")
    if not candidate_url.startswith(
        "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/"
    ):
        candidate_url = RELEASES_URL

    package_name = f"studyn-anki-sync-{version}.ankiaddon"
    package_url = _asset_url(body.get("assets"), package_name)
    checksum_url = _asset_url(body.get("assets"), "SHA256SUMS.txt")
    return ReleaseInfo(
        version=version,
        url=candidate_url,
        package_name=package_name if package_url and checksum_url else None,
        package_url=package_url,
        checksum_url=checksum_url,
    )


def download_verified_package(
    release: ReleaseInfo,
    timeout: int = 15,
    opener: Callable[..., Any] | None = None,
) -> bytes:
    if not release.can_install_automatically:
        raise ValueError("The release does not include a verifiable add-on package")

    open_url = opener or urlopen
    request_timeout = max(1, int(timeout))
    checksum_data = _download_bytes(
        Request(
            str(release.checksum_url),
            headers={"User-Agent": f"StudynAnkiSync/{ADDON_VERSION}"},
        ),
        timeout=request_timeout,
        opener=open_url,
        maximum_bytes=_MAX_CHECKSUM_BYTES,
        description="release checksum",
    )
    expected = _checksum_for_file(
        checksum_data.decode("utf-8"), str(release.package_name)
    )
    package = _download_bytes(
        Request(
            str(release.package_url),
            headers={"User-Agent": f"StudynAnkiSync/{ADDON_VERSION}"},
        ),
        timeout=request_timeout,
        opener=open_url,
        maximum_bytes=_MAX_PACKAGE_BYTES,
        description="add-on package",
    )
    actual = hashlib.sha256(package).hexdigest()
    if actual != expected:
        raise ValueError("The downloaded add-on failed SHA-256 verification")
    _validate_package_archive(package, release.version)
    return package


def _asset_url(assets: object, expected_name: str) -> str | None:
    if not isinstance(assets, list):
        return None
    for asset in assets:
        if not isinstance(asset, dict) or asset.get("name") != expected_name:
            continue
        candidate = str(asset.get("browser_download_url") or "")
        if candidate.startswith(RELEASE_ASSET_PREFIX) and candidate.endswith(
            f"/{expected_name}"
        ):
            return candidate
    return None


def _checksum_for_file(contents: str, filename: str) -> str:
    for line in contents.splitlines():
        match = _CHECKSUM_PATTERN.fullmatch(line.strip())
        if match and match.group(2) == filename:
            return match.group(1).lower()
    raise ValueError(f"SHA-256 checksum not found for {filename}")


def _validate_package_archive(package: bytes, expected_version: str) -> None:
    try:
        with ZipFile(BytesIO(package)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)) or len(names) > 500:
                raise ValueError("The add-on package has an invalid file list")
            if sum(item.file_size for item in archive.infolist()) > 20 * 1024 * 1024:
                raise ValueError("The add-on package expands beyond the safety limit")
            for name in names:
                path = PurePosixPath(name)
                if (
                    not name
                    or path.is_absolute()
                    or ".." in path.parts
                    or "\\" in name
                    or (path.parts and ":" in path.parts[0])
                ):
                    raise ValueError("The add-on package contains an unsafe path")
            if "__init__.py" not in names or "manifest.json" not in names:
                raise ValueError("The add-on package is missing required files")
            manifest_raw = archive.read("manifest.json")
    except BadZipFile as error:
        raise ValueError("The downloaded add-on is not a valid archive") from error

    if len(manifest_raw) > 65536:
        raise ValueError("The add-on manifest is too large")
    try:
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as error:
        raise ValueError("The add-on manifest is invalid") from error
    if not isinstance(manifest, dict):
        raise ValueError("The add-on manifest is invalid")
    if manifest.get("package") != "studyn_anki_sync":
        raise ValueError("The release contains an unexpected add-on package")
    if str(manifest.get("version")) != expected_version:
        raise ValueError("The release package version does not match its tag")


def _download_bytes(
    request: Request,
    *,
    timeout: int,
    opener: Callable[..., Any],
    maximum_bytes: int,
    description: str,
) -> bytes:
    with opener(request, timeout=timeout) as response:
        try:
            raw = response.read(maximum_bytes + 1)
        except TypeError:
            # Small test doubles and older compatible response wrappers may not
            # accept a size argument. The limit is still enforced below.
            raw = response.read()
    if len(raw) > maximum_bytes:
        raise ValueError(f"{description} is too large")
    return raw
