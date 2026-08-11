from __future__ import annotations

import platform
import re
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit

from .config import AddonConfig
from .i18n import Translator
from .version import ADDON_VERSION


_BEARER_PATTERN = re.compile(r"(?i)\bbearer\s+[a-z0-9._~+/=-]+")
_SECRET_FIELD_PATTERN = re.compile(
    r"(?i)(access[_-]?token|token|authorization|device[_-]?(?:id|code)|user[_-]?code)"
    r"\s*[:=]\s*['\"]?[^\s,;'\"]+"
)
_SECRET_QUERY_PATTERN = re.compile(
    r"(?i)([?&](?:access_?token|token|code|device_?id)=)[^&#\s]+"
)


def sanitize_url(value: object) -> str:
    """Return an API URL without credentials, query parameters, or fragments."""
    try:
        parsed = urlsplit(str(value or ""))
        hostname = parsed.hostname or ""
        if not parsed.scheme or not hostname:
            return "[invalid URL]"
        host = f"[{hostname}]" if ":" in hostname else hostname
        port = f":{parsed.port}" if parsed.port is not None else ""
        return urlunsplit((parsed.scheme, f"{host}{port}", parsed.path, "", ""))
    except (TypeError, ValueError):
        return "[invalid URL]"


def sanitize_text(value: object, secrets: Iterable[object] = ()) -> str:
    """Redact known credentials and credential-shaped values from diagnostic text."""
    text = str(value or "").replace("\r", " ").replace("\n", " ")
    for secret in sorted(
        {str(item) for item in secrets if item}, key=len, reverse=True
    ):
        text = text.replace(secret, "[REDACTED]")
    text = _BEARER_PATTERN.sub("Bearer [REDACTED]", text)
    text = _SECRET_FIELD_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", text)
    text = _SECRET_QUERY_PATTERN.sub(lambda match: f"{match.group(1)}[REDACTED]", text)
    return text[:500]


def build_diagnostic_report(
    config: AddonConfig,
    profile: dict[str, Any],
    anki_version: str,
    sync_in_progress: bool,
    translator: Translator,
    generated_at: datetime | None = None,
) -> str:
    """Build a support report that intentionally excludes user and card data."""
    generated = generated_at or datetime.now(timezone.utc)
    secrets = (profile.get("accessToken"), profile.get("deviceId"))
    last_error = sanitize_text(profile.get("lastError"), secrets)
    resolved_language = translator.language
    connected = bool(profile.get("accessToken"))

    fields = (
        ("diagnostics.addon_version", ADDON_VERSION),
        ("diagnostics.anki_version", sanitize_text(anki_version)),
        ("diagnostics.python_version", platform.python_version()),
        ("diagnostics.operating_system", sanitize_text(platform.platform())),
        ("diagnostics.language_setting", config.language),
        ("diagnostics.resolved_language", resolved_language),
        ("diagnostics.api_server", sanitize_url(config.api_base_url)),
        (
            "diagnostics.automatic_sync",
            translator.t("diagnostics.yes" if config.automatic_sync else "diagnostics.no"),
        ),
        (
            "diagnostics.update_checks",
            translator.t("diagnostics.yes" if config.check_for_updates else "diagnostics.no"),
        ),
        (
            "diagnostics.connected",
            translator.t("diagnostics.yes" if connected else "diagnostics.no"),
        ),
        (
            "diagnostics.sync_state",
            translator.t("status.in_progress" if sync_in_progress else "status.idle"),
        ),
        ("diagnostics.last_sync", sanitize_text(profile.get("lastSyncAt")) or translator.t("status.never")),
        ("diagnostics.last_attempt", sanitize_text(profile.get("lastAttemptAt")) or translator.t("status.never")),
        ("diagnostics.last_error", last_error or translator.t("status.none")),
    )

    lines = [
        translator.t("diagnostics.report_title"),
        f"{translator.t('diagnostics.generated')}: {generated.astimezone(timezone.utc).isoformat()}",
        "",
    ]
    lines.extend(f"{translator.t(key)}: {value}" for key, value in fields)
    return "\n".join(lines)
