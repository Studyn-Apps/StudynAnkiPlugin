from __future__ import annotations

import json
import platform
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from .i18n import Translator
from .models import PairingSession, StatsSnapshot, SyncResult, TokenResult
from .version import ADDON_VERSION, SCHEMA_VERSION


API_ERROR_KEYS = {
    "authorization_pending": "api.error.authorization_pending",
    "slow_down": "api.error.slow_down",
    "expired_token": "api.error.expired_token",
    "access_denied": "api.error.access_denied",
    "invalid_token": "api.error.invalid_token",
    "rate_limited": "api.error.rate_limited",
    "payload_too_large": "api.error.payload_too_large",
    "internal_server_error": "api.error.internal_server_error",
}
TERMINAL_DEVICE_ERROR_CODES = {"invalid_token", "device_not_found"}


class ApiError(RuntimeError):
    def __init__(
        self,
        message: str,
        status: Optional[int] = None,
        code: Optional[str] = None,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.retryable = retryable


def is_terminal_device_error(error: Exception) -> bool:
    """Return whether the server confirms that the local device cannot be used."""

    return isinstance(error, ApiError) and error.code in TERMINAL_DEVICE_ERROR_CODES


class ApiClient:
    def __init__(
        self, base_url: str, timeout: int = 15, language: str = "auto"
    ) -> None:
        self._translator = Translator.create(language)
        normalized = base_url.strip().rstrip("/") + "/"
        if not normalized.startswith("https://") and not normalized.startswith(
            ("http://localhost", "http://127.0.0.1")
        ):
            raise ValueError(self._tr("api.https_required"))
        self.base_url = normalized
        self.timeout = max(1, int(timeout))

    def _tr(self, key: str, **values: object) -> str:
        return self._translator.t(key, **values)

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        access_token: Optional[str] = None,
    ) -> Tuple[int, Dict[str, Any]]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"StudynAnkiSync/{ADDON_VERSION} ({platform.system()})",
        }
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            urljoin(self.base_url, path.lstrip("/")),
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
                return int(response.status), json.loads(raw) if raw else {}
        except HTTPError as error:
            try:
                raw = error.read().decode("utf-8")
                body = json.loads(raw) if raw else {}
            except (UnicodeDecodeError, ValueError):
                body = {}
            code = body.get("error") or body.get("code")
            error_key = API_ERROR_KEYS.get(str(code))
            message = (
                self._tr(error_key)
                if error_key
                else self._tr("api.error.default", status=error.code)
            )
            if error.code == 404 and not code:
                message = self._tr("api.endpoint_not_found", url=request.full_url)
            raise ApiError(
                message,
                status=int(error.code),
                code=str(code) if code else None,
                retryable=error.code == 429 or error.code >= 500,
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise ApiError(
                self._tr("api.connection_failed"),
                retryable=True,
            ) from error

    def begin_pairing(
        self, device_name: str, anki_version: str
    ) -> PairingSession:
        _, body = self._request(
            "POST",
            "device-authorizations",
            {
                "deviceName": device_name,
                "addonVersion": ADDON_VERSION,
                "ankiVersion": anki_version,
            },
        )
        required = ("deviceCode", "userCode", "verificationUri")
        if any(not body.get(key) for key in required):
            raise ApiError(self._tr("api.invalid_authorization"))
        return PairingSession(
            device_code=str(body["deviceCode"]),
            user_code=str(body["userCode"]),
            verification_uri=str(body["verificationUri"]),
            verification_uri_complete=str(
                body.get("verificationUriComplete") or body["verificationUri"]
            ),
            expires_in=max(30, int(body.get("expiresIn", 600))),
            interval=max(2, int(body.get("interval", 5))),
        )

    def poll_for_token(self, session: PairingSession) -> TokenResult:
        deadline = time.monotonic() + session.expires_in
        interval = session.interval
        while time.monotonic() < deadline:
            try:
                _, body = self._request(
                    "POST", "token", {"deviceCode": session.device_code}
                )
                token = body.get("accessToken")
                device_id = body.get("deviceId")
                if token and device_id:
                    return TokenResult(
                        access_token=str(token),
                        device_id=str(device_id),
                        display_name=(
                            str(body["displayName"])
                            if body.get("displayName")
                            else None
                        ),
                    )
                raise ApiError(self._tr("api.invalid_device_token"))
            except ApiError as error:
                if error.code == "authorization_pending":
                    time.sleep(interval)
                    continue
                if error.code == "slow_down":
                    interval += 2
                    time.sleep(interval)
                    continue
                if error.code in {"expired_token", "access_denied"}:
                    raise
                if error.retryable:
                    time.sleep(interval)
                    continue
                raise
        raise ApiError(self._tr("api.code_expired"), code="expired_token")

    def sync(
        self,
        access_token: str,
        snapshot: StatsSnapshot,
        sync_id: str,
        day_starts_at_hour: int,
        anki_version: str,
    ) -> SyncResult:
        payload = {
            "schemaVersion": SCHEMA_VERSION,
            "syncId": sync_id,
            "collectedAt": datetime.now(timezone.utc).isoformat(),
            "dayStartsAtHour": day_starts_at_hour,
            "addonVersion": ADDON_VERSION,
            "ankiVersion": anki_version,
            **snapshot.to_payload(),
        }
        _, body = self._request("POST", "sync", payload, access_token)
        return SyncResult(
            accepted_days=max(0, int(body.get("acceptedDays", len(snapshot.days)))),
            synced_at=str(
                body.get("syncedAt") or datetime.now(timezone.utc).isoformat()
            ),
        )

    def revoke_device(self, access_token: str, device_id: str) -> None:
        self._request(
            "DELETE",
            f"devices/{device_id}",
            access_token=access_token,
        )
