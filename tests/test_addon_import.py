import importlib.util
import sys
import types
import unittest
from pathlib import Path


class Signal:
    def __init__(self):
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)


class Timer:
    def __init__(self, *_args):
        self.timeout = Signal()

    def setSingleShot(self, _value):
        pass

    def start(self, _milliseconds):
        pass

    def stop(self):
        pass

    @staticmethod
    def singleShot(_milliseconds, _callback):
        pass


class Action:
    def __init__(self, _label, _parent):
        self.triggered = Signal()


class Clipboard:
    def __init__(self):
        self.text = ""

    def setText(self, value):
        self.text = value


class Application:
    clipboard_instance = Clipboard()

    @staticmethod
    def clipboard():
        return Application.clipboard_instance


class Menu:
    def __init__(self):
        self.actions = []

    def addAction(self, action):
        self.actions.append(action)

    def addSeparator(self):
        pass


class MenuTools:
    def __init__(self):
        self.menus = []

    def addMenu(self, _label):
        menu = Menu()
        self.menus.append(menu)
        return menu


class AddonManager:
    def __init__(self):
        self.config_actions = {}
        self.config = {}

    def getConfig(self, _module):
        return self.config

    def writeConfig(self, _module, config):
        self.config = config

    def setConfigAction(self, module, callback):
        self.config_actions[module] = callback


class QueryOp:
    def __init__(self, **_kwargs):
        pass

    def failure(self, _callback):
        return self

    def without_collection(self):
        return self

    def run_in_background(self):
        return self


class AddonImportTests(unittest.TestCase):
    def test_package_bootstraps_with_current_anki_surfaces(self):
        root = Path(__file__).resolve().parents[1]
        hooks = types.SimpleNamespace(
            profile_did_open=[], reviewer_did_answer_card=[]
        )
        addon_manager = AddonManager()
        menu_tools = MenuTools()
        mw = types.SimpleNamespace(
            addonManager=addon_manager,
            form=types.SimpleNamespace(menuTools=menu_tools),
            pm=types.SimpleNamespace(name="Test"),
        )

        aqt = types.ModuleType("aqt")
        aqt.mw = mw
        aqt.gui_hooks = hooks
        aqt.appVersion = "test"

        operations = types.ModuleType("aqt.operations")
        operations.QueryOp = QueryOp
        qt = types.ModuleType("aqt.qt")
        qt.QAction = Action
        qt.QApplication = Application
        qt.QTimer = Timer
        qt.qconnect = lambda signal, callback: signal.connect(callback)
        utils = types.ModuleType("aqt.utils")
        utils.askUser = lambda *_args, **_kwargs: True
        utils.getText = lambda *_args, **_kwargs: ("", False)
        utils.openLink = lambda *_args, **_kwargs: None
        utils.showInfo = lambda *_args, **_kwargs: None
        utils.showWarning = lambda *_args, **_kwargs: None
        utils.tooltip = lambda *_args, **_kwargs: None
        anki = types.ModuleType("anki")
        anki.version = "test"

        previous = {
            name: sys.modules.get(name)
            for name in ("aqt", "aqt.operations", "aqt.qt", "aqt.utils", "anki")
        }
        sys.modules.update(
            {
                "aqt": aqt,
                "aqt.operations": operations,
                "aqt.qt": qt,
                "aqt.utils": utils,
                "anki": anki,
            }
        )
        try:
            spec = importlib.util.spec_from_file_location(
                "studyn_anki_sync",
                root / "__init__.py",
                submodule_search_locations=[str(root)],
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules["studyn_anki_sync"] = module
            assert spec.loader is not None
            spec.loader.exec_module(module)

            self.assertEqual(len(menu_tools.menus), 1)
            self.assertEqual(len(menu_tools.menus[0].actions), 7)
            self.assertEqual(len(hooks.profile_did_open), 2)
            self.assertEqual(len(hooks.reviewer_did_answer_card), 1)
            self.assertIn("studyn_anki_sync", addon_manager.config_actions)
        finally:
            for name, old_module in previous.items():
                if old_module is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = old_module
            for name in list(sys.modules):
                if name == "studyn_anki_sync" or name.startswith("studyn_anki_sync."):
                    sys.modules.pop(name, None)


if __name__ == "__main__":
    unittest.main()
