from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "studyn" / "locales.json"
REQUIRED_FIELDS = {"code", "baseLanguage", "nativeName", "shortLabel"}


def load_and_validate(path: Path) -> dict[str, Any]:
    data: Any = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schemaVersion") != 1:
        raise ValueError(f"Unsupported locale catalog schema: {path}")
    if not isinstance(data.get("packageVersion"), str) or not data["packageVersion"]:
        raise ValueError(f"Missing locale package version: {path}")
    locales = data.get("locales")
    if not isinstance(locales, list) or not locales:
        raise ValueError(f"Missing locale definitions: {path}")

    codes: list[str] = []
    for definition in locales:
        if not isinstance(definition, dict) or not REQUIRED_FIELDS.issubset(definition):
            raise ValueError(f"Invalid locale definition: {definition!r}")
        if not all(isinstance(definition[key], str) and definition[key] for key in REQUIRED_FIELDS):
            raise ValueError(f"Invalid locale definition value: {definition!r}")
        codes.append(definition["code"])
    if len(codes) != len(set(codes)):
        raise ValueError("Locale catalog contains duplicate codes")
    return data


def serialized(data: dict[str, Any]) -> str:
    return f"{json.dumps(data, ensure_ascii=False, indent=2)}\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vendor the language-neutral artifact emitted by @studyn/locales.",
    )
    parser.add_argument(
        "source",
        nargs="?",
        type=Path,
        default=TARGET,
        help="Path to @studyn/locales/dist/locales.json (defaults to the vendored copy).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate and fail instead of updating when the vendored copy differs.",
    )
    args = parser.parse_args()

    source = args.source.resolve()
    data = load_and_validate(source)
    expected = serialized(data)

    if args.check:
        current = TARGET.read_text(encoding="utf-8") if TARGET.is_file() else ""
        if current != expected:
            raise SystemExit(
                f"{TARGET} differs from {source}; run tools/sync_locales.py with that source"
            )
        print(f"Verified @studyn/locales {data['packageVersion']} in {TARGET}")
        return

    TARGET.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Vendored @studyn/locales {data['packageVersion']} in {TARGET}")


if __name__ == "__main__":
    main()
