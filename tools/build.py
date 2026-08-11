from __future__ import annotations

import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from studyn.version import ADDON_VERSION  # noqa: E402


OUTPUT = ROOT / "dist" / f"studyn-anki-sync-{ADDON_VERSION}.ankiaddon"
ROOT_FILES = (
    "__init__.py",
    "manifest.json",
    "config.json",
    "config.md",
    "LICENSE",
    "README.md",
    "README.pt-BR.md",
    "README.es-419.md",
    "CHANGELOG.md",
    "SECURITY.md",
)


def package_files() -> list[Path]:
    files = [ROOT / name for name in ROOT_FILES]
    files.extend(sorted((ROOT / "studyn").glob("*.py")))
    files.append(ROOT / "docs" / "API_CONTRACT.md")
    files.append(ROOT / "static" / "logo.png")
    files.append(ROOT / "user_files" / "README.txt")
    return files


def build() -> Path:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in package_files():
            if not path.is_file():
                raise FileNotFoundError(path)
            archive.write(path, path.relative_to(ROOT).as_posix())
    return OUTPUT


if __name__ == "__main__":
    output = build()
    print(output)
