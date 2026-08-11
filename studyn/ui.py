from __future__ import annotations

import platform
from typing import Any, Callable

from aqt import mw
from aqt.operations import QueryOp
from aqt.qt import QAction, qconnect
from aqt.utils import askUser, getText, openLink, showInfo, showWarning, tooltip

from .api import ApiClient
from .config import AddonConfig
from .models import PairingSession, TokenResult
from .storage import LocalStorage
from .sync import SyncManager


class AddonController:
    def __init__(
        self,
        config_provider: Callable[[], AddonConfig],
        api_base_url_writer: Callable[[str], None],
        storage: LocalStorage,
        sync_manager: SyncManager,
        profile_context: Callable[[], tuple[str, str]],
        anki_version: str,
    ) -> None:
        self._config_provider = config_provider
        self._api_base_url_writer = api_base_url_writer
        self._storage = storage
        self._sync_manager = sync_manager
        self._profile_context = profile_context
        self._anki_version = anki_version
        self._pairing_in_progress = False
        self._create_menu()

    def _create_menu(self) -> None:
        menu = mw.form.menuTools.addMenu("Studyn")
        self._add_action(menu, "Connect account", self.connect)
        self._add_action(menu, "Sync now", self.sync_now)
        self._add_action(menu, "View status", self.show_status)
        self._add_action(menu, "Configure server", self.configure_server)
        menu.addSeparator()
        self._add_action(menu, "Disconnect", self.disconnect)

    @staticmethod
    def _add_action(menu: Any, label: str, callback: Callable[[], None]) -> None:
        action = QAction(label, mw)
        qconnect(action.triggered, callback)
        menu.addAction(action)

    def connect(self) -> None:
        if self._pairing_in_progress:
            showInfo(
                "A connection is already waiting for authorization in your browser.",
                title="Studyn - Anki Sync",
            )
            return

        _, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        if profile.get("accessToken"):
            display_name = profile.get("displayName") or "Studyn account"
            showInfo(
                f"This profile is already connected to {display_name}.",
                title="Studyn - Anki Sync",
            )
            return

        self._pairing_in_progress = True
        config = self._config_provider()
        try:
            client = ApiClient(config.api_base_url, config.request_timeout_seconds)
        except (TypeError, ValueError) as error:
            self._pairing_in_progress = False
            showWarning(str(error), title="Studyn - Anki Sync")
            return
        device_name = platform.node().strip() or platform.system() or "Anki Desktop"
        operation = QueryOp(
            parent=mw,
            op=lambda _col: client.begin_pairing(device_name, self._anki_version),
            success=lambda session: self._on_pairing_started(
                client, profile_key, session
            ),
        )
        operation.failure(self._on_pairing_error).without_collection().run_in_background()

    def _on_pairing_started(
        self,
        client: ApiClient,
        profile_key: str,
        session: PairingSession,
    ) -> None:
        openLink(session.verification_uri_complete)
        showInfo(
            "Your browser was opened to connect your Studyn account.\n\n"
            f"Code: {session.user_code}\n\n"
            "After authorizing the device, return to Anki. You may close this window.",
            title="Connect to Studyn",
        )
        operation = QueryOp(
            parent=mw,
            op=lambda _col: client.poll_for_token(session),
            success=lambda result: self._on_pairing_complete(profile_key, result),
        )
        operation.failure(self._on_pairing_error).without_collection().run_in_background()

    def _on_pairing_complete(
        self, profile_key: str, result: TokenResult
    ) -> None:
        self._storage.save_token(
            profile_key,
            result.access_token,
            result.device_id,
            result.display_name,
        )
        self._pairing_in_progress = False
        tooltip("Studyn account connected successfully.", parent=mw)
        self._sync_manager.request_sync(manual=True)

    def _on_pairing_error(self, error: Exception) -> None:
        self._pairing_in_progress = False
        server = self._config_provider().api_base_url
        detail = str(error)
        if getattr(error, "status", None) == 404:
            detail = (
                "The Anki API was not found on this server.\n\n"
                f"Configured server: {server}\n\n"
                "If the site is running locally, open Tools > Studyn > "
                "Configure server and enter, for example:\n"
                "http://127.0.0.1/api/v1/anki"
            )
        showWarning(
            f"Could not connect to Studyn.\n\n{detail}",
            title="Studyn - Anki Sync",
        )

    def configure_server(self) -> None:
        config = self._config_provider()
        value, accepted = getText(
            "Studyn API base URL:\n\n"
            "Production: https://studyn.org/api/v1/anki\n"
            "Local site: http://127.0.0.1/api/v1/anki",
            title="Studyn - Configure server",
            default=config.api_base_url,
        )
        if not accepted:
            return

        base_url = str(value).strip().rstrip("/")
        try:
            ApiClient(base_url, config.request_timeout_seconds)
        except (TypeError, ValueError) as error:
            showWarning(str(error), title="Studyn - Configure server")
            return

        self._api_base_url_writer(base_url)
        showInfo(
            "Server updated successfully.\n\n"
            f"{base_url}\n\n"
            "Now open Tools > Studyn > Connect account.",
            title="Studyn - Configure server",
        )

    def sync_now(self) -> None:
        self._sync_manager.request_sync(manual=True)

    def show_status(self) -> None:
        profile_name, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        if not profile.get("accessToken"):
            status = "Not connected"
        else:
            status = f"Connected to {profile.get('displayName') or 'Studyn account'}"

        last_sync = profile.get("lastSyncAt") or "Never"
        last_error = profile.get("lastError") or "None"
        activity = "In progress" if self._sync_manager.in_progress else "Idle"
        server = self._config_provider().api_base_url
        showInfo(
            f"Anki profile: {profile_name}\n"
            f"Status: {status}\n"
            f"Server: {server}\n"
            f"Sync: {activity}\n"
            f"Last upload: {last_sync}\n"
            f"Last error: {last_error}",
            title="Studyn - Anki Sync",
        )

    def disconnect(self) -> None:
        _, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        token = profile.get("accessToken")
        device_id = profile.get("deviceId")
        if not token or not device_id:
            showInfo("This profile is not connected to Studyn.")
            return
        if not askUser(
            "Revoke this device and disconnect the Studyn account?",
            title="Studyn - Anki Sync",
        ):
            return

        config = self._config_provider()
        try:
            client = ApiClient(config.api_base_url, config.request_timeout_seconds)
        except (TypeError, ValueError) as error:
            showWarning(str(error), title="Studyn - Anki Sync")
            return
        operation = QueryOp(
            parent=mw,
            op=lambda _col: client.revoke_device(str(token), str(device_id)),
            success=lambda _result: self._finish_disconnect(profile_key),
        )
        operation.failure(
            lambda error: showWarning(
                "Could not revoke the device. The connection was kept."
                f"\n\n{error}",
                title="Studyn - Anki Sync",
            )
        ).without_collection().run_in_background()

    def _finish_disconnect(self, profile_key: str) -> None:
        self._storage.disconnect(profile_key)
        tooltip("Device disconnected from Studyn.", parent=mw)
