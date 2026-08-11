from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Callable
from urllib.request import Request, urlopen

from .version import ADDON_VERSION


RELEASES_API_URL = (
    "https://api.github.com/repos/Studyn-Apps/StudynAnkiPlugin/releases/latest"
)
RELEASES_URL = "https://github.com/Studyn-Apps/StudynAnkiPlugin/releases/latest"
_VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    url: str


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
    with open_url(request, timeout=max(1, int(timeout))) as response:
        raw = response.read()
    if len(raw) > 65536:
        raise ValueError("GitHub release response is too large")
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
    return ReleaseInfo(version=version, url=candidate_url)
