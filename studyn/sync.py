from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from aqt import mw
from aqt.operations import QueryOp
from aqt.qt import QTimer, qconnect
from aqt.utils import showWarning, tooltip

from .api import ApiClient, is_terminal_device_error
from .config import AddonConfig
from .i18n import Translator
from .models import StatsSnapshot, SyncResult
from .stats import collect_snapshot
from .storage import LocalStorage


class SyncManager:
    def __init__(
        self,
        config_provider: Callable[[], AddonConfig],
        storage: LocalStorage,
        profile_context: Callable[[], tuple[str, str]],
        anki_version: str,
    ) -> None:
        self._config_provider = config_provider
        self._storage = storage
        self._profile_context = profile_context
        self._anki_version = anki_version
        self._in_progress = False
        self._pending = False
        self._review_count = 0
        self._manual_request = False
        self._debounce_timer = QTimer(mw)
        self._debounce_timer.setSingleShot(True)
        qconnect(self._debounce_timer.timeout, self._on_debounce_elapsed)

    @property
    def in_progress(self) -> bool:
        return self._in_progress

    def _tr(self, key: str, **values: object) -> str:
        config = self._config_provider()
        return Translator.create(config.language).t(key, **values)

    def on_profile_open(self, *_args: Any) -> None:
        config = self._config_provider()
        if not config.automatic_sync:
            return
        QTimer.singleShot(5000, lambda: self.request_sync(manual=False))

    def on_review_answered(self, *_args: Any) -> None:
        config = self._config_provider()
        if not config.automatic_sync:
            return
        _, profile_key = self._profile_context()
        if not self._storage.get_profile(profile_key).get("accessToken"):
            return

        self._review_count += 1
        if self._review_count >= config.sync_every_reviews:
            self._review_count = 0
            self._debounce_timer.stop()
            self.request_sync(manual=False)
            return
        self._debounce_timer.start(config.sync_debounce_seconds * 1000)

    def _on_debounce_elapsed(self) -> None:
        self._review_count = 0
        self.request_sync(manual=False)

    def request_sync(self, manual: bool = False) -> None:
        _, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        token = profile.get("accessToken")
        if not token:
            if manual:
                showWarning(
                    self._tr("sync.connect_first"),
                    title=self._tr("app.title"),
                )
            return

        if self._in_progress:
            self._pending = True
            self._manual_request = self._manual_request or manual
            return

        self._in_progress = True
        self._manual_request = manual
        config = self._config_provider()
        days = self._effective_sync_days(profile, config)

        operation = QueryOp(
            parent=mw,
            op=lambda col: collect_snapshot(
                col,
                days=days,
                day_starts_at_hour=config.day_starts_at_hour,
            ),
            success=lambda snapshot: self._upload(
                snapshot,
                profile_key=profile_key,
                token=str(token),
                config=config,
            ),
        )
        operation.failure(
            lambda error: self._finish_error(
                profile_key, error, "sync.collect_failed"
            )
        ).run_in_background()

    def _effective_sync_days(
        self, profile: dict[str, Any], config: AddonConfig
    ) -> int:
        last_sync = profile.get("lastSyncAt")
        if not last_sync:
            return config.initial_sync_days
        try:
            parsed = datetime.fromisoformat(str(last_sync).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            offline_days = max(0, (datetime.now(timezone.utc) - parsed).days + 2)
        except (TypeError, ValueError):
            offline_days = config.sync_days
        return min(config.max_sync_days, max(config.sync_days, offline_days))

    def _upload(
        self,
        snapshot: StatsSnapshot,
        profile_key: str,
        token: str,
        config: AddonConfig,
    ) -> None:
        try:
            client = ApiClient(
                config.api_base_url,
                config.request_timeout_seconds,
                config.language,
            )
        except (TypeError, ValueError) as error:
            self._finish_error(profile_key, error, "sync.prepare_failed")
            return
        sync_id = str(uuid.uuid4())
        operation = QueryOp(
            parent=mw,
            op=lambda _col: client.sync(
                access_token=token,
                snapshot=snapshot,
                sync_id=sync_id,
                day_starts_at_hour=config.day_starts_at_hour,
                anki_version=self._anki_version,
            ),
            success=lambda result: self._finish_success(profile_key, result),
        )
        operation.failure(
            lambda error: self._finish_error(profile_key, error, "sync.upload_failed")
        ).without_collection().run_in_background()

    def _finish_success(self, profile_key: str, result: SyncResult) -> None:
        self._storage.set_sync_success(profile_key, result.synced_at)
        if self._manual_request:
            tooltip(
                self._tr("sync.success", days=result.accepted_days),
                parent=mw,
            )
        self._finish()

    def _finish_error(
        self, profile_key: str, error: Exception, message_key: str
    ) -> None:
        message = str(error) or error.__class__.__name__
        connection_invalid = is_terminal_device_error(error)
        if connection_invalid:
            self._storage.invalidate_credentials(profile_key, message)
        else:
            self._storage.set_sync_error(profile_key, message)
        if connection_invalid:
            showWarning(
                self._tr("sync.reconnect_required"),
                title=self._tr("app.title"),
            )
        elif self._manual_request:
            showWarning(
                self._tr(message_key, message=message),
                title=self._tr("app.title"),
            )
        self._finish()

    def _finish(self) -> None:
        self._in_progress = False
        manual_pending = self._manual_request
        self._manual_request = False
        if self._pending:
            self._pending = False
            QTimer.singleShot(
                1000, lambda: self.request_sync(manual=manual_pending)
            )
