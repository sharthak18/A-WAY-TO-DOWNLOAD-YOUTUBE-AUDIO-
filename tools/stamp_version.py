#!/usr/bin/env python3
"""Write one version number into every place that ships it.

    python3 tools/stamp_version.py 0.2.0

Touches:
  desktop/src-tauri/tauri.conf.json   "version"
  desktop/src-tauri/Cargo.toml        version = "..."
  android/app/build.gradle.kts        versionName / versionCode
  grabbox/__init__.py                 __version__

The release workflow runs this before building so the installers inside a
release really are the version the tag says. Safe to run locally too.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    version = sys.argv[1].lstrip("v")
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        print(f"version must look like 1.2.3, got {version!r}", file=sys.stderr)
        return 2
    major, minor, patch = (int(x) for x in m.groups())
    # Android needs a monotonically increasing integer: 0.2.0 -> 200, 1.0.3 -> 10003.
    version_code = major * 10000 + minor * 100 + patch

    # Tauri config (JSON).
    conf = ROOT / "desktop/src-tauri/tauri.conf.json"
    data = json.loads(conf.read_text(encoding="utf-8"))
    data["version"] = version
    conf.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Cargo.toml: only the [package] version (first match).
    cargo = ROOT / "desktop/src-tauri/Cargo.toml"
    cargo.write_text(
        re.sub(r'^version = "[^"]*"', f'version = "{version}"',
               cargo.read_text(encoding="utf-8"), count=1, flags=re.M),
        encoding="utf-8",
    )

    # Android.
    gradle = ROOT / "android/app/build.gradle.kts"
    text = gradle.read_text(encoding="utf-8")
    text = re.sub(r"versionCode = \d+", f"versionCode = {version_code}", text, count=1)
    text = re.sub(r'versionName = "[^"]*"', f'versionName = "{version}"', text, count=1)
    gradle.write_text(text, encoding="utf-8")

    # Python package.
    init = ROOT / "grabbox/__init__.py"
    init.write_text(
        re.sub(r'^__version__ = "[^"]*"', f'__version__ = "{version}"',
               init.read_text(encoding="utf-8"), count=1, flags=re.M),
        encoding="utf-8",
    )

    print(f"stamped {version} (android versionCode {version_code})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
