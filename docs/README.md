# Docs

| File | Read it when… |
|---|---|
| [APP.md](APP.md) | you want the full install / run guide for every platform: desktop app, browser extension, Android, the Python core, LAN mode. |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | a download fails. Every error explained in plain English, 403s first. |
| [MANUAL.md](MANUAL.md) | you prefer a terminal: the `ytgrab.py` menu and the original step-by-step raw `yt-dlp` guide. |
| [CHEATSHEET.md](CHEATSHEET.md) | you just want the copy-paste `yt-dlp` commands and the one-click `.bat` trick. |
| [RESEARCH.md](RESEARCH.md) | you are curious why the app is built the way it is. |

## Repo layout

```
.github/workflows/   CI: release.yml publishes installers to GitHub Releases;
                     desktop.yml / build.yml are per-push smoke builds
android/             native Android app (Kotlin + Compose, yt-dlp engine bundled)
desktop/             desktop app (Tauri v2 / Rust) - installers for Win / mac / Linux
extension/           browser extension (Chrome / Edge / Brave / Firefox)
grabbox/             the Python core: HTTP server + the shared web UI (grabbox/web)
scripts/             run-from-source entry points: grabbox.* launchers, ytgrab.py menu
packaging/           PyInstaller spec + its entry point (portable one-folder build)
tools/               developer scripts: icon generators, version stamping, release notes
docs/                this folder
```
