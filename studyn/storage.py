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

    def save_token(
        self,
        profile_key: str,
        access_token: str,
        device_id: str,
        display_name: Optional[str] = None,
    ) -> None:
        data = self._read()
        previous = data["profiles"].get(profile_key, {})
        data["profiles"][profile_key] = {
            **previous,
            "accessToken": access_token,
            "deviceId": device_id,
            "displayName": display_name,
            "connectedAt": datetime.now(timezone.utc).isoformat(),
            "lastError": None,
        }
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

    def disconnect(self, profile_key: str) -> None:
        data = self._read()
        data["profiles"].pop(profile_key, None)
        self._write(data)
