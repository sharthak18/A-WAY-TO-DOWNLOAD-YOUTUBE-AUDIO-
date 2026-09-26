# GrabBox Desktop (Tauri v2)

The real desktop app: one native window, real installers, everything bundled.
Zero prerequisites — yt-dlp ships as a standalone sidecar that embeds Python.

```
┌─────────────────────────────────────────────────────────────┐
│ grabbox/web (the shared UI: HTML/CSS/JS, no framework)      │
│   └─ driver layer: window.__TAURI__ ? invoke : fetch        │
├──────────────────────────────┬──────────────────────────────┤
│ Tauri (Rust) — this folder   │ Python server (grabbox/)     │
│ spawns sidecar binaries:     │ HTTP /api/* — LAN mode,      │
│ yt-dlp · ffmpeg · deno       │ extension backend, CLI       │
└──────────────────────────────┴──────────────────────────────┘
```

Both engines share the same semantics on purpose: the YouTube client **retry
ladder**, the plain-English **diagnostics**, the HEAD **file sniffer**, and the
same `~/.grabbox/config.json` — switch transports without noticing.

## Build it

```bash
# 1. Rust toolchain: https://rustup.rs   (plus Tauri v2 prereqs for your OS —
#    Ubuntu: libwebkit2gtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev)
# 2. Tauri CLI:
cargo install tauri-cli --version "^2"

# 3. Stage the extension + the engine binaries sidecar-bundled per target:
mkdir -p desktop/src-tauri/extension && cp -r extension/* desktop/src-tauri/extension/
bash desktop/fetch-sidecars.sh --target x86_64-unknown-linux-gnu   # your triple

# 4. Develop (hot window) or build installers:
cd desktop/src-tauri
cargo tauri dev          # opens the app; no sidecars needed if system yt-dlp exists
cargo tauri build        # -> target/release/bundle/  {.msi,.dmg,.AppImage,.deb,...}
```

Developers' shortcut: with no `binaries/` staged, the app falls back to
whatever `yt-dlp` / `ffmpeg` / `deno` are on your PATH.

## What it adds over the Python server

* Real window with icon/title, native **folder picker**, **open/reveal/delete**
  via the OS, **clipboard** reading, and `~/.grabbox/config.json` shared config.
* Engine **self-update**: "Update yt-dlp" runs the sidecar's own `-U`.
* The **extension folder ships inside the bundle**, so Settings →
  "Add the browser extension" can open it straight on disk.

## CI

`.github/workflows/desktop.yml` compiles all four targets on every push (smoke
test). `.github/workflows/release.yml` — run it from the Actions tab with a
version number, or push a `v*` tag — stamps the version, builds the same four
targets plus Android, and publishes a GitHub Release with stable file names
(`GrabBox-Windows-Setup.exe`, `GrabBox-macOS-AppleSilicon.dmg`, …) that the
front-page download buttons link to.
