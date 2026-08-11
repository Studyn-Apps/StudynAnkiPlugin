from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_CATALOG_PATH = Path(__file__).with_name("locales.json")


def _load_catalog() -> tuple[str, tuple[dict[str, str], ...]]:
    raw: Any = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("schemaVersion") != 1:
        raise ValueError("Unsupported @studyn/locales catalog schema")

    package_version = raw.get("packageVersion")
    definitions = raw.get("locales")
    if not isinstance(package_version, str) or not package_version:
        raise ValueError("Missing @studyn/locales package version")
    if not isinstance(definitions, list) or not definitions:
        raise ValueError("Missing @studyn/locales definitions")

    required = {"code", "baseLanguage", "nativeName", "shortLabel"}
    normalized: list[dict[str, str]] = []
    for definition in definitions:
        if not isinstance(definition, dict) or not required.issubset(definition):
            raise ValueError("Invalid @studyn/locales definition")
        if not all(isinstance(definition[key], str) and definition[key] for key in required):
            raise ValueError("Invalid @studyn/locales definition value")
        normalized.append({key: definition[key] for key in required})

    codes = [definition["code"] for definition in normalized]
    if len(codes) != len(set(codes)):
        raise ValueError("Duplicate @studyn/locales code")

    return package_version, tuple(normalized)


LOCALES_PACKAGE_VERSION, LOCALE_DEFINITIONS = _load_catalog()
SUPPORTED_LANGUAGES = tuple(definition["code"] for definition in LOCALE_DEFINITIONS)
_CANONICAL_BY_LOWER = {code.lower(): code for code in SUPPORTED_LANGUAGES}
_LOCALE_BY_BASE_LANGUAGE = {
    definition["baseLanguage"].lower(): definition["code"]
    for definition in LOCALE_DEFINITIONS
}


def match_studyn_locale(value: object) -> str | None:
    raw = str(value or "").strip().lower().replace("_", "-")
    if not raw:
        return None
    exact = _CANONICAL_BY_LOWER.get(raw)
    if exact:
        return exact
    return _LOCALE_BY_BASE_LANGUAGE.get(raw.split("-", 1)[0])
