from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class LocalStorage:
    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path(__file__).resolve().parents[1] / "user_files"
        self.path = self.root / "credentials.json"

    @staticmethod
    def profile_key(profile_name: str) -> str:
        normalized = profile_name.strip().encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()

    def _read(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "profiles": {}}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {"version": 1, "profiles": {}}
        if not isinstance(data, dict) or not isinstance(data.get("profiles"), dict):
            return {"version": 1, "profiles": {}}
        return data

    def _write(self, data: Dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        handle, temp_name = tempfile.mkstemp(
            prefix="studyn-", suffix=".json.tmp", dir=str(self.root)
        )
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(data, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temp_name, self.path)
            try:
                os.chmod(self.path, 0o600)
            except OSError:
                pass
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    def get_profile(self, profile_key: str) -> Dict[str, Any]:
        data = self._read()
        profile = data["profiles"].get(profile_key, {})
        return dict(profile) if isinstance(profile, dict) else {}

    def get_update_state(self) -> Dict[str, Any]:
        data = self._read()
        state = data.get("updateState", {})
        return dict(state) if isinstance(state, dict) else {}

    def record_update_check(self, latest_version: Optional[str] = None) -> None:
        data = self._read()
        state = data.get("updateState")
        if not isinstance(state, dict):
            state = {}
            data["updateState"] = state
        state["lastCheckedAt"] = datetime.now(timezone.utc).isoformat()
        if latest_version:
            state["latestVersion"] = latest_version
        self._write(data)

    def record_update_notification(self, version: str) -> None:
        data = self._read()
        state = data.get("updateState")
        if not isinstance(state, dict):
            state = {}
            data["updateState"] = state
        state["lastNotifiedVersion"] = version
        self._write(data)

    def record_update_install(self, version: str) -> None:
        data = self._read()
        state = data.get("updateState")
        if not isinstance(state, dict):
            state = {}
            data["updateState"] = state
        state["lastInstalledVersion"] = version
        self._write(data)

    def save_token(
        self,
        profile_key: str,
        access_token: str,
        device_id: str,
        display_name: Optional[str] = None,
    ) -> None:
        data = self._read()
        previous = data["profiles"].get(profile_key, {})
        profile = {
            **previous,
            "accessToken": access_token,
            "deviceId": device_id,
            "displayName": display_name,
            "connectedAt": datetime.now(timezone.utc).isoformat(),
            "lastError": None,
        }
        profile.pop("connectionInvalidatedAt", None)
        profile.pop("reconnectPromptedFor", None)
        profile.pop("disconnectedAt", None)
        data["profiles"][profile_key] = profile
        self._write(data)

    def set_sync_success(self, profile_key: str, synced_at: str) -> None:
        data = self._read()
        profile = data["profiles"].setdefault(profile_key, {})
        profile["lastSyncAt"] = synced_at
        profile["lastError"] = None
        self._write(data)

    def set_sync_error(self, profile_key: str, message: str) -> None:
        data = self._read()
        profile = data["profiles"].setdefault(profile_key, {})
        profile["lastError"] = message[:500]
        profile["lastAttemptAt"] = datetime.now(timezone.utc).isoformat()
        self._write(data)

    def invalidate_credentials(self, profile_key: str, message: str) -> None:
        """Clear unusable credentials while retaining non-secret support history."""

        data = self._read()
        profile = data["profiles"].setdefault(profile_key, {})
        invalidated_at = datetime.now(timezone.utc).isoformat()
        profile.pop("accessToken", None)
        profile.pop("deviceId", None)
        profile["lastError"] = message[:500]
        profile["lastAttemptAt"] = invalidated_at
        profile["connectionInvalidatedAt"] = invalidated_at
        profile.pop("reconnectPromptedFor", None)
        self._write(data)

    def mark_connection_prompt(self, profile_key: str, reconnect: bool) -> None:
        data = self._read()
        profile = data["profiles"].setdefault(profile_key, {})
        now = datetime.now(timezone.utc).isoformat()
        if reconnect:
            profile["reconnectPromptedFor"] = profile.get("connectionInvalidatedAt")
        else:
            profile["onboardingShownAt"] = now
        self._write(data)

    def disconnect(self, profile_key: str) -> None:
        data = self._read()
        profile = data["profiles"].setdefault(profile_key, {})
        now = datetime.now(timezone.utc).isoformat()
        for key in (
            "accessToken",
            "deviceId",
            "displayName",
            "connectedAt",
            "connectionInvalidatedAt",
            "reconnectPromptedFor",
        ):
            profile.pop(key, None)
        profile["lastError"] = None
        profile["disconnectedAt"] = now
        profile.setdefault("onboardingShownAt", now)
        self._write(data)
