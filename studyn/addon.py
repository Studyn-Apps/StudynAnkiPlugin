from __future__ import annotations

from typing import Optional, Tuple

import aqt
from aqt import gui_hooks, mw

from .config import AddonConfig, addon_module_name
from .storage import LocalStorage
from .sync import SyncManager
from .ui import AddonController


_controller: Optional[AddonController] = None


def _anki_version() -> str:
    try:
        from anki import version

        return str(version)
    except (ImportError, AttributeError):
        return str(getattr(aqt, "appVersion", "unknown"))


def _profile_context(storage: LocalStorage) -> Tuple[str, str]:
    profile_name = str(getattr(mw.pm, "name", "") or "default")
    return profile_name, storage.profile_key(profile_name)


def bootstrap() -> None:
    global _controller
    if _controller is not None:
        return

    addon_module = addon_module_name(__package__)
    storage = LocalStorage()

    def config_provider() -> AddonConfig:
        raw = mw.addonManager.getConfig(addon_module) or {}
        return AddonConfig.from_dict(raw)

    def api_base_url_writer(api_base_url: str) -> None:
        raw = dict(mw.addonManager.getConfig(addon_module) or {})
        raw["api_base_url"] = api_base_url
        mw.addonManager.writeConfig(addon_module, raw)

    def language_writer(language: str) -> None:
        raw = dict(mw.addonManager.getConfig(addon_module) or {})
        raw["language"] = language
        mw.addonManager.writeConfig(addon_module, raw)

    profile_provider = lambda: _profile_context(storage)
    anki_version = _anki_version()
    sync_manager = SyncManager(
        config_provider=config_provider,
        storage=storage,
        profile_context=profile_provider,
        anki_version=anki_version,
    )
    _controller = AddonController(
        config_provider=config_provider,
        api_base_url_writer=api_base_url_writer,
        language_writer=language_writer,
        storage=storage,
        sync_manager=sync_manager,
        profile_context=profile_provider,
        anki_version=anki_version,
    )

    gui_hooks.profile_did_open.append(sync_manager.on_profile_open)
    gui_hooks.profile_did_open.append(_controller.on_profile_open)
    gui_hooks.reviewer_did_answer_card.append(sync_manager.on_review_answered)
    mw.addonManager.setConfigAction(addon_module, _controller.configure_language)
