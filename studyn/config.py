from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .i18n import normalize_configured_language


def addon_module_name(package_name: str) -> str:
    return package_name.split(".", 1)[0]


def _bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return min(maximum, max(minimum, parsed))


@dataclass(frozen=True)
class AddonConfig:
    api_base_url: str
    language: str
    automatic_sync: bool
    check_for_updates: bool
    day_starts_at_hour: int
    initial_sync_days: int
    max_sync_days: int
    request_timeout_seconds: int
    sync_days: int
    sync_debounce_seconds: int
    sync_every_reviews: int
    update_check_interval_hours: int

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "AddonConfig":
        sync_days = _bounded_int(raw.get("sync_days"), 31, 1, 365)
        initial_days = _bounded_int(raw.get("initial_sync_days"), 365, sync_days, 3650)
        max_days = _bounded_int(raw.get("max_sync_days"), 730, initial_days, 3650)
        return cls(
            api_base_url=str(
                raw.get("api_base_url") or "https://studyn.org/api/v1/anki"
            ),
            language=normalize_configured_language(raw.get("language")),
            automatic_sync=bool(raw.get("automatic_sync", True)),
            check_for_updates=bool(raw.get("check_for_updates", True)),
            day_starts_at_hour=_bounded_int(
                raw.get("day_starts_at_hour"), 4, 0, 23
            ),
            initial_sync_days=initial_days,
            max_sync_days=max_days,
            request_timeout_seconds=_bounded_int(
                raw.get("request_timeout_seconds"), 15, 3, 60
            ),
            sync_days=sync_days,
            sync_debounce_seconds=_bounded_int(
                raw.get("sync_debounce_seconds"), 60, 10, 600
            ),
            sync_every_reviews=_bounded_int(
                raw.get("sync_every_reviews"), 25, 1, 1000
            ),
            update_check_interval_hours=_bounded_int(
                raw.get("update_check_interval_hours"), 24, 1, 168
            ),
        )
