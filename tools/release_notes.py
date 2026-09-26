#!/usr/bin/env python3
"""Print the Markdown body for a GitHub Release.

    python3 tools/release_notes.py 0.2.0 2026.09.05

Arguments: the version being released and the yt-dlp version that got bundled.
Used by .github/workflows/release.yml; harmless to run by hand.
"""
from __future__ import annotations

import sys

REPO = "sharthak18/A-WAY-TO-DOWNLOAD-YOUTUBE-AUDIO-"


def main() -> int:
    version = (sys.argv[1] if len(sys.argv) > 1 else "0.0.0").lstrip("v")
    engine = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    base = f"https://github.com/{REPO}/releases/download/v{version}"

    def link(name: str) -> str:
        return f"[`{name}`]({base}/{name})"

    print(f"""## GrabBox {version}

Paste a link, pick a quality, download. Everything (yt-dlp, ffmpeg, a JS
runtime) is bundled inside — nothing else to install.

### Download

| Your device | Get this file |
|---|---|
| **Windows** 10 / 11 | {link("GrabBox-Windows-Setup.exe")} — or {link("GrabBox-Windows.msi")} |
| **Mac** with Apple Silicon (M1, M2, M3, M4…) | {link("GrabBox-macOS-AppleSilicon.dmg")} |
| **Mac** with Intel chip (2020 and older) | {link("GrabBox-macOS-Intel.dmg")} |
| **Linux** | {link("GrabBox-Linux.AppImage")} — or {link("GrabBox-Linux.deb")} (Ubuntu / Debian / Mint) |
| **Android** 7.0+ | {link("GrabBox-Android.apk")} — very old 32-bit phones: {link("GrabBox-Android-32bit.apk")} |

Not sure which Mac you have? Apple menu → **About This Mac** → look at *Chip*.

### First launch

The app is not code-signed yet, so each OS shows a one-time warning:

* **Windows** SmartScreen: click *More info* → *Run anyway*.
* **macOS**: right-click GrabBox → *Open* → *Open* (or System Settings →
  Privacy & Security → *Open Anyway*).
* **Android**: allow *Install unknown apps* for your browser when asked.
* **Linux** AppImage: `chmod +x GrabBox-Linux.AppImage`, then double-click it.

### What's inside

* Bundled engine: **yt-dlp {engine}**. If YouTube changes something later,
  Settings → *Update yt-dlp* refreshes it in place — no reinstall.
* Checksums: `SHA256SUMS.txt`.

Problems? Read [TROUBLESHOOTING.md](https://github.com/{REPO}/blob/main/docs/TROUBLESHOOTING.md)
or email **feedit18@gmail.com**.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
