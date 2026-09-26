# GrabBox — visual & usability research (September 2026)

Research for turning GrabBox from "it works" into "it feels great", ahead of
shipping the desktop app (Win/mac/Linux), the browser extension flow, and a
self-contained Android APK.

> ## Decisions — locked 2026-09-25
>
> 1. **Desktop shell: Tauri v2.** Rust backend spawns **standalone
>    yt-dlp / ffmpeg / deno binaries as Tauri sidecars** (official yt-dlp
>    builds embed Python → still zero prerequisites for users). Native
>    installers (.msi/.dmg/.AppImage/.deb) built by GitHub Actions.
> 2. **Android: native Kotlin app**, Jetpack Compose + Material 3 dynamic
>    color, engine bundled via `youtubedl-android` (JunkFood02 fork), like
>    Seal / YTDLnis. minSdk 23 (Android 6+), per-ABI APKs, share-sheet target,
>    in-app yt-dlp update. Termux script stays as the "nerd path".
> 3. **Visuals: Material-adaptive.** One design language family-wide:
>    Material 3 tonal color generated from a user-picked accent seed
>    (blue default), dark default + light + auto. The **web UI is shared**
>    between the Tauri window and the Python server via a tiny driver layer
>    (`window.__TAURI__ ? invoke : fetch`) — one UI codebase, two transports.
> 4. **Python server stays** as the "nerd path" (LAN mode, extension backend
>    when the desktop app is closed, CLI companion).
>
> Build order: **P1** shared UI v2 → **P2** Tauri desktop + installer CI →
> **P3** extension in-page dialog → **P4** Android native → **P5** polish.

---

## 0. Where we are today

| Piece | State | Gap |
|---|---|---|
| Web UI (`grabbox/web/`) | Working dark UI: paste → analyze → quality → jobs/files | Feels like a tool, not a product; raw format dropdown; no drag-drop; no friendly quality names; settings bare |
| Desktop "app" | `python3 -m grabbox` opens a browser tab | Not an app: no window, no icon in dock/taskbar, no installer, requires Python+ytdlp+ffmpeg unless PyInstaller build |
| Extension (`extension/`) | Faded/lit icon, count badge, right-click grab, hover button, popup list | Sends link to the app page — no IDM-style "download popup with options" inside the browser |
| Android | Termux script + WebView APK *that needs the Termux server* | Two installs, terminal commands — fails the "smooth" test completely for normal users |
| Engine health | Doctor, retry ladder, plain-English 403 fixes | This is genuinely ahead of most competitors — keep it |

---

## 1. Benchmark apps — what the best actually do

### Seal (Android) — the mobile gold standard
<https://github.com/JunkFood02/Seal> · ~most-loved yt-dlp GUI on Android
- **Material You / Material Design 3**, dynamic color pulled from the wallpaper —
  the app feels like part of the OS.
- Flow: **share sheet → Seal → small config sheet (video quality / audio / path) → done.**
  Plus "**Quick Download**" = skip the sheet entirely, use saved defaults.
- Self-contained APK: built on `youtubedl-android` (Python runtime + yt-dlp + ffmpeg
  + aria2 **bundled inside the APK**). No Termux, no setup.
- yt-dlp is updatable **from inside the app** (stable/nightly channels) — critical,
  because YouTube breaks downloaders constantly.
- Extras: playlists in one tap, thumbnails/metadata embedded, subtitles, command templates.

### YTDLnis (Android) — the power-user sibling
<https://github.com/deniscerri/ytdlnis> — same youtubedl-android base, richer UI:
format cards, scheduling, batch. Proof the architecture scales to power features.

### Stacher (desktop, closed source) — most popular desktop wrapper
<https://stacher.io/> — Electron, "yt-dlp with checkboxes". Its killer feature is
boring but essential: **it keeps yt-dlp updated automatically**. Long tail of flags
exposed as UI. Lesson: format power belongs in an "Advanced" drawer, not the main flow.

### Parabolic (desktop, MIT) — the minimalist
<https://github.com/NickvisionApps/Parabolic> — one job: paste → pick quality →
download, nothing else on screen. Bundles yt-dlp + ffmpeg + deno. Lesson: restraint
reads as polish.

### VidBee (desktop, MIT) — modern Electron take
Queue, playlists, channels, history; ffmpeg bundled in the installer. Confirms the
"everything in one installer, zero terminal" expectation on desktop.

### IDM (Internet Download Manager) — the extension interaction model
The flow the user asked for, and the reference everyone knows: icon per-media state,
right-click "Download with…", and **a small native-feeling dialog appears with file
name + size + category + save path + start button**. The dialog is the whole trick —
the extension must not just hand off to the app, it must *feel* instant and in-page.

---

## 2. UX principles to build on (from all of the above)

1. **The 3-tap rule.** Paste → Analyze → Download. Everything else is optional,
   pre-set, or hidden in Advanced. Defaults must be good enough that "Analyze →
   Download" covers 90% of real use.
2. **Speak human, not ffmpeg.** Quality choices as friendly chips —
   `Best · 1080p · 720p · 480p` and `Audio: MP3 · M4A · Opus` — never raw
   `format_id` soup. (Keep format listing behind "Advanced".)
3. **Zero prerequisites.** The installer/APK ships the engine. If a user ever sees
   "install Python", we lost. yt-dlp updates itself from inside the app.
4. **Errors are moments of truth.** Our plain-English 403 explainer + retry ladder
   is a differentiator — surface it in-app, don't hide it in a log.
5. **Progress everywhere.** Live speed + ETA in the queue; OS notification when a
   download finishes; badge on extension.
6. **One brain, many faces.** Keep the Python server as the single place downloads
   happen (desktop window, extension, LAN devices, web UI all talk to it). New
   platforms = new thin clients, not new download logic.
7. **Respect the platform.** Desktop: native window, file dialogs, drag-drop, tray,
   notifications. Android: Material 3, share target, dynamic color. Don't fight the OS.

---

## 3. Desktop — options

Goal: repo → download installer → simple window → paste → choose → download;
folder picker; "Add extension" button that opens the browser to install it.

| Option | Size | Effort | Verdict |
|---|---|---|---|
| **pywebview** over our existing server (window instead of browser tab) + PyInstaller installers | ~30 MB | **Small** — backend unchanged, CI unchanged | **Recommended now** |
| Tauri v2 (Rust shell + Python sidecar) | ~10 MB | Large — Rust tooling, bridge rewrite, new CI | Revisit post-1.0 for beauty/size |
| Electron | 150 MB+ | Medium | No — absurd for a downloader |
| PySide6/Qt widgets | ~60 MB | Large — full UI rewrite | No — loses the shared web UI |

**Recommendation: pywebview + redesigned web UI.** The web UI stays the single
interface (desktop window, LAN, other devices), pywebview adds: real window with
icon/title, native file/folder pickers, drag-and-drop URLs, close-to-tray,
single-instance, OS notifications. Packaging (existing CI upgraded):

- **Windows:** single `.exe` + NSIS installer (Start menu, uninstall entry).
  Unsigned → SmartScreen note in README; winget package later.
- **macOS:** `.app` in `.dmg`, universal2. Unsigned → "right-click → Open" note;
  notarize later if the project takes off.
- **Linux:** AppImage + `.deb`. 
- All builds **bundle yt-dlp + ffmpeg + a JS runtime** and self-update yt-dlp
  (the doctor UI already does the explaining).

## 4. Extension — IDM-style upgrade

Current: right-click sends you to the app page. Target:

1. Right-click (or hover-↓) → **popup dialog in-page**: thumbnail/icon, detected
   name + size, friendly quality chips, save-name field, **Download** button.
   (Extension calls `/api/probe`, then `/api/download` — server API already has both.)
2. Icon states stay (faded = nothing, lit + badge count = grab-able).
3. "Add extension" button **in the desktop app** opens the browser directly at the
   load-unpacked page / store link with a 3-step guide.
4. Extension popup shows quick status: is the app running? Last 3 downloads.

## 5. Android — the real app (Android 6+ / API 23+)

Goal: install APK → open → same simple flow; share → GrabBox like Seal.

- **Stack:** Kotlin + Jetpack Compose + **Material 3 with dynamic color**
  (Seal's exact recipe; the pattern users already love).
- **Engine:** `youtubedl-android` (JunkFood02 fork — Python + yt-dlp + ffmpeg +
  aria2 bundled per-ABI). This is how Seal/YTDLnis ship self-contained APKs,
  and it supports **minSdk 21+** → Android 6 (API 23) is reachable.
- **Flows:** share-sheet target (Grab / Quick-Download), in-app paste box,
  quality sheet (video res chips / audio kbps), playlist picker, download path
  setting, history.
- **Permissions (keep it clean):** none at install worth mentioning; runtime
  notification permission on Android 13+; storage via SAF/app dir → no scary
  storage prompts on Android 10+; legacy storage only on old devices.
- **Delivery:** GitHub Releases APKs per ABI (arm64-v8a primary,
  armeabi-v7a + x86_64 as separate APKs to keep size sane), F-Droid later.
- Keep the Termux script as the "nerd path" — it costs nothing.

## 6. Roadmap

- [x] **P1 — Desktop UI redesign** (web UI v2: 3-step flow, friendly chips,
      drag-drop, notifications, settings incl. download folder, "Add extension")
- [x] **P2 — Desktop shell & installers** (**Tauri v2** window — chosen over
      pywebview for bundle size + native tray/notifications — plus tray,
      single-instance, URL forwarding into the running window, and
      Win/mac/Linux installer CI)
- [x] **P3 — Extension v2** (in-page download dialog with options)
- [x] **P4 — Android v1** (native Compose app with Material You dynamic
      colors, bundled yt-dlp + ffmpeg engine, share target, runtime
      permissions kept minimal, per-ABI APK CI)
- [ ] **P5 — Polish** (light theme, localization hooks, F-Droid, winget,
      Android release signing + Play/F-Droid listing)

---

*Sources: Seal & youtubedl-android repos, Stacher/Parabolic/VidBee docs and
2026 comparisons, Tauri/Electron/pywebview framework comparisons (June 2026).
Links inline above.*
