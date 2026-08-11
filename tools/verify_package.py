from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from studyn.version import ADDON_VERSION  # noqa: E402
from tools.build import OUTPUT, package_files  # noqa: E402


def verify(package: Path = OUTPUT) -> None:
    if not package.is_file():
        raise FileNotFoundError(package)

    expected = {path.relative_to(ROOT).as_posix() for path in package_files()}
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        actual = set(names)
        if len(actual) != len(names):
            raise ValueError("Package contains duplicate paths")
        if actual != expected:
            missing = sorted(expected - actual)
            unexpected = sorted(actual - expected)
            raise ValueError(
                f"Package contents differ (missing={missing}, unexpected={unexpected})"
            )
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"Unsafe package path: {name}")
            lowered = name.lower()
            if "credentials.json" in lowered or "__pycache__" in lowered:
                raise ValueError(f"Private or generated file in package: {name}")

        for source in package_files():
            name = source.relative_to(ROOT).as_posix()
            if archive.read(name) != source.read_bytes():
                raise ValueError(f"Packaged file does not match source: {name}")

        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        if str(manifest.get("version")) != ADDON_VERSION:
            raise ValueError(
                f"manifest version {manifest.get('version')} != {ADDON_VERSION}"
            )


if __name__ == "__main__":
    verify()
    print(f"Verified {OUTPUT}")
