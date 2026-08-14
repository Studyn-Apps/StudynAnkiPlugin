from __future__ import annotations

from io import BytesIO
import platform
from typing import Any, Callable

from aqt import mw
from aqt.operations import QueryOp
from aqt.qt import QAction, QApplication, QTimer, qconnect
from aqt.utils import askUser, getText, openLink, showInfo, showWarning, tooltip

from .api import ApiClient, is_terminal_device_error
from .config import AddonConfig
from .diagnostics import build_diagnostic_report
from .i18n import Translator, normalize_configured_language
from .models import PairingSession, TokenResult
from .storage import LocalStorage
from .sync import SyncManager
from .updates import (
    ReleaseInfo,
    download_verified_package,
    fetch_latest_release,
    is_check_due,
    is_newer_version,
)
from .version import ADDON_VERSION


class AddonController:
    def __init__(
        self,
        config_provider: Callable[[], AddonConfig],
        api_base_url_writer: Callable[[str], None],
        language_writer: Callable[[str], None],
        automatic_updates_writer: Callable[[bool], None],
        storage: LocalStorage,
        sync_manager: SyncManager,
        profile_context: Callable[[], tuple[str, str]],
        anki_version: str,
    ) -> None:
        self._config_provider = config_provider
        self._api_base_url_writer = api_base_url_writer
        self._language_writer = language_writer
        self._automatic_updates_writer = automatic_updates_writer
        self._storage = storage
        self._sync_manager = sync_manager
        self._profile_context = profile_context
        self._anki_version = anki_version
        self._pairing_in_progress = False
        self._update_check_in_progress = False
        self._manual_update_check = False
        self._update_install_in_progress = False
        self._create_menu()

    def _create_menu(self) -> None:
        menu = mw.form.menuTools.addMenu("Studyn")
        self._add_action(menu, self._tr("menu.connect"), self.connect)
        self._add_action(menu, self._tr("menu.sync"), self.sync_now)
        self._add_action(menu, self._tr("menu.status"), self.show_status)
        self._add_action(menu, self._tr("menu.diagnostics"), self.copy_diagnostics)
        self._add_action(menu, self._tr("menu.configure"), self.configure_server)
        self._add_action(menu, self._tr("menu.language"), self.configure_language)
        self._add_action(menu, self._tr("menu.update_settings"), self.configure_updates)
        self._add_action(
            menu,
            self._tr("menu.check_updates"),
            lambda: self.check_for_updates(manual=True),
        )
        menu.addSeparator()
        self._add_action(menu, self._tr("menu.disconnect"), self.disconnect)

    def on_profile_open(self, *_args: Any) -> None:
        QTimer.singleShot(1500, self._maybe_offer_connection)
        if self._config_provider().check_for_updates:
            QTimer.singleShot(8000, self.check_for_updates)

    def _maybe_offer_connection(self) -> None:
        _, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        if profile.get("accessToken"):
            return

        invalidated_at = profile.get("connectionInvalidatedAt")
        reconnect = bool(
            invalidated_at
            and profile.get("reconnectPromptedFor") != invalidated_at
        )
        if not reconnect and profile.get("onboardingShownAt"):
            return

        self._storage.mark_connection_prompt(profile_key, reconnect=reconnect)
        message_key = "onboarding.reconnect" if reconnect else "onboarding.welcome"
        if askUser(self._tr(message_key), title=self._tr("pairing.title")):
            self.connect()

    def _tr(self, key: str, **values: object) -> str:
        config = self._config_provider()
        return Translator.create(config.language).t(key, **values)

    @staticmethod
    def _add_action(menu: Any, label: str, callback: Callable[[], None]) -> None:
        action = QAction(label, mw)
        qconnect(action.triggered, callback)
        menu.addAction(action)

    def connect(self) -> None:
        if self._pairing_in_progress:
            showInfo(
                self._tr("pairing.in_progress"),
                title=self._tr("app.title"),
            )
            return

        _, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        if profile.get("accessToken"):
            display_name = profile.get("displayName") or self._tr("account.fallback")
            showInfo(
                self._tr("pairing.already_connected", display_name=display_name),
                title=self._tr("app.title"),
            )
            return

        self._pairing_in_progress = True
        config = self._config_provider()
        try:
            client = ApiClient(
                config.api_base_url,
                config.request_timeout_seconds,
                config.language,
            )
        except (TypeError, ValueError) as error:
            self._pairing_in_progress = False
            showWarning(str(error), title=self._tr("app.title"))
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
            self._tr("pairing.browser_opened", code=session.user_code),
            title=self._tr("pairing.title"),
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
        tooltip(self._tr("pairing.connected"), parent=mw)
        self._sync_manager.request_sync(manual=True)

    def _on_pairing_error(self, error: Exception) -> None:
        self._pairing_in_progress = False
        server = self._config_provider().api_base_url
        detail = str(error)
        if getattr(error, "status", None) == 404:
            detail = self._tr("pairing.api_not_found", server=server)
        showWarning(
            self._tr("pairing.failed", detail=detail),
            title=self._tr("app.title"),
        )

    def configure_server(self) -> None:
        config = self._config_provider()
        value, accepted = getText(
            self._tr("config.prompt"),
            title=self._tr("config.title"),
            default=config.api_base_url,
        )
        if not accepted:
            return

        base_url = str(value).strip().rstrip("/")
        try:
            ApiClient(base_url, config.request_timeout_seconds, config.language)
        except (TypeError, ValueError) as error:
            showWarning(str(error), title=self._tr("config.title"))
            return

        self._api_base_url_writer(base_url)
        showInfo(
            self._tr("config.updated", base_url=base_url),
            title=self._tr("config.title"),
        )

    def configure_language(self) -> None:
        config = self._config_provider()
        value, accepted = getText(
            self._tr("language.prompt"),
            title=self._tr("language.title"),
            default=config.language,
        )
        if not accepted:
            return

        raw = str(value).strip().lower().replace("_", "-")
        language = normalize_configured_language(raw)
        if language == "auto" and raw not in {"auto", "system", "default"}:
            showWarning(
                self._tr("language.invalid"), title=self._tr("language.title")
            )
            return

        self._language_writer(language)
        showInfo(
            self._tr("language.updated", language=language),
            title=self._tr("language.title"),
        )

    def configure_updates(self) -> None:
        enabled = self._config_provider().automatic_updates
        message_key = "update.disable_prompt" if enabled else "update.enable_prompt"
        if not askUser(self._tr(message_key), title=self._tr("update.settings_title")):
            return
        self._automatic_updates_writer(not enabled)
        showInfo(
            self._tr("update.setting_enabled" if not enabled else "update.setting_disabled"),
            title=self._tr("update.settings_title"),
        )

    def sync_now(self) -> None:
        self._sync_manager.request_sync(manual=True)

    def show_status(self) -> None:
        profile_name, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        if not profile.get("accessToken"):
            status = self._tr("status.not_connected")
        else:
            display_name = profile.get("displayName") or self._tr("account.fallback")
            status = self._tr("status.connected", display_name=display_name)

        last_sync = profile.get("lastSyncAt") or self._tr("status.never")
        last_error = profile.get("lastError") or self._tr("status.none")
        activity = self._tr(
            "status.in_progress" if self._sync_manager.in_progress else "status.idle"
        )
        server = self._config_provider().api_base_url
        showInfo(
            self._tr(
                "status.body",
                profile_name=profile_name,
                status=status,
                server=server,
                activity=activity,
                last_sync=last_sync,
                last_error=last_error,
            ),
            title=self._tr("app.title"),
        )

    def copy_diagnostics(self) -> None:
        _, profile_key = self._profile_context()
        config = self._config_provider()
        translator = Translator.create(config.language)
        report = build_diagnostic_report(
            config=config,
            profile=self._storage.get_profile(profile_key),
            anki_version=self._anki_version,
            sync_in_progress=self._sync_manager.in_progress,
            translator=translator,
        )
        QApplication.clipboard().setText(report)
        tooltip(self._tr("diagnostics.copied"), parent=mw)

    def check_for_updates(self, manual: bool = False) -> None:
        config = self._config_provider()
        state = self._storage.get_update_state()
        if self._update_check_in_progress or self._update_install_in_progress:
            if manual:
                tooltip(self._tr("update.in_progress"), parent=mw)
            return
        if not manual and (
            not config.check_for_updates
            or not is_check_due(
                state.get("lastCheckedAt"), config.update_check_interval_hours
            )
        ):
            return

        self._update_check_in_progress = True
        self._manual_update_check = manual
        operation = QueryOp(
            parent=mw,
            op=lambda _col: fetch_latest_release(config.request_timeout_seconds),
            success=self._on_update_check_success,
        )
        operation.failure(self._on_update_check_failure).without_collection().run_in_background()

    def _on_update_check_success(self, release: ReleaseInfo) -> None:
        self._update_check_in_progress = False
        manual = self._manual_update_check
        self._manual_update_check = False
        state = self._storage.get_update_state()
        self._storage.record_update_check(release.version)
        if not is_newer_version(release.version, ADDON_VERSION):
            if manual:
                tooltip(self._tr("update.none"), parent=mw)
            return

        config = self._config_provider()
        if config.automatic_updates and release.can_install_automatically:
            if state.get("lastInstalledVersion") == release.version:
                if manual:
                    tooltip(self._tr("update.restart_pending"), parent=mw)
                return
            self._install_update(release)
            return

        if not manual and state.get("lastNotifiedVersion") == release.version:
            return

        self._storage.record_update_notification(release.version)
        if askUser(
            self._tr(
                "update.available",
                latest=release.version,
                current=ADDON_VERSION,
            ),
            title=self._tr("update.title"),
        ):
            openLink(release.url)

    def _on_update_check_failure(self, error: Exception) -> None:
        self._update_check_in_progress = False
        manual = self._manual_update_check
        self._manual_update_check = False
        self._storage.record_update_check()
        if manual:
            showWarning(
                self._tr("update.check_failed", error=error),
                title=self._tr("update.title"),
            )

    def _install_update(self, release: ReleaseInfo) -> None:
        self._update_install_in_progress = True
        config = self._config_provider()
        operation = QueryOp(
            parent=mw,
            op=lambda _col: download_verified_package(
                release, config.request_timeout_seconds
            ),
            success=lambda package: self._finish_update_install(release, package),
        )
        operation.failure(self._on_update_install_failure).without_collection().run_in_background()

    def _finish_update_install(self, release: ReleaseInfo, package: bytes) -> None:
        try:
            result = mw.addonManager.install(BytesIO(package))
        except Exception as error:
            self._on_update_install_failure(error)
            return

        self._update_install_in_progress = False
        error_message = getattr(result, "errmsg", None)
        if error_message:
            showWarning(
                self._tr("update.install_failed", error=error_message),
                title=self._tr("update.title"),
            )
            return
        self._storage.record_update_notification(release.version)
        self._storage.record_update_install(release.version)
        showInfo(
            self._tr("update.installed", version=release.version),
            title=self._tr("update.title"),
        )

    def _on_update_install_failure(self, error: Exception) -> None:
        self._update_install_in_progress = False
        showWarning(
            self._tr("update.install_failed", error=error),
            title=self._tr("update.title"),
        )

    def disconnect(self) -> None:
        _, profile_key = self._profile_context()
        profile = self._storage.get_profile(profile_key)
        token = profile.get("accessToken")
        device_id = profile.get("deviceId")
        if not token or not device_id:
            showInfo(self._tr("disconnect.not_connected"))
            return
        if not askUser(
            self._tr("disconnect.confirm"),
            title=self._tr("app.title"),
        ):
            return

        config = self._config_provider()
        try:
            client = ApiClient(
                config.api_base_url,
                config.request_timeout_seconds,
                config.language,
            )
        except (TypeError, ValueError) as error:
            showWarning(str(error), title=self._tr("app.title"))
            return
        operation = QueryOp(
            parent=mw,
            op=lambda _col: client.revoke_device(str(token), str(device_id)),
            success=lambda _result: self._finish_disconnect(profile_key),
        )
        operation.failure(
            lambda error: self._on_disconnect_error(profile_key, error)
        ).without_collection().run_in_background()

    def _on_disconnect_error(self, profile_key: str, error: Exception) -> None:
        if is_terminal_device_error(error):
            self._finish_disconnect(profile_key)
            return
        showWarning(
            self._tr("disconnect.failed", error=error),
            title=self._tr("app.title"),
        )

    def _finish_disconnect(self, profile_key: str) -> None:
        self._storage.disconnect(profile_key)
        tooltip(self._tr("disconnect.done"), parent=mw)
