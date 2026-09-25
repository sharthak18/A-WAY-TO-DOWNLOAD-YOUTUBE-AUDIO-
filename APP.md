# GrabBox — install & run, on everything

GrabBox is the "make it a software" answer to this repo. It downloads anything
a plain HTTP link can serve — video, audio, images, installers, archives,
documents — plus everything yt-dlp already knows (YouTube, 1800+ sites,
playlists). There are four ways to use it:

1. **Desktop app** (Windows / macOS / Linux) — the flagship. One installer,
   everything bundled, no prerequisites. → section 1a
2. **Browser extension** — a faded toolbar icon that lights up over
   downloadable things, right-click "Grab with GrabBox", and an in-page
   download dialog with quality options. → section 2
3. **Android app** (Android 6+) — native app with the engine bundled;
   share any link straight into it. → section 4
4. **The core** (any platform) — the Python server + web UI underneath it
   all. This is what the desktop app and extension actually talk to.
   → section 1b

Everything runs **on your device**. Nothing is uploaded anywhere.

---

## 1a. Desktop app (recommended on computers)

Grab the installer for your OS from **Actions → desktop (Tauri) → Artifacts**
(`GrabBox-desktop-windows`, `GrabBox-desktop-macos`, `GrabBox-desktop-linux`),
or from Releases once a release is cut:

| OS | Install |
|---|---|
| Windows | run the `.msi` (or `.exe`) |
| macOS | open the `.dmg`, drag GrabBox to Applications |
| Linux | `.AppImage` (no install) or `.deb` |

yt-dlp, ffmpeg and a JS runtime are bundled **inside** the app — install and
open, nothing else to get. It sits in the system tray, single instance:
pasting a link while it's already running just focuses the window.

The flow: paste URL (or it arrives from the extension / share) → it reads the
link → you pick kind + quality (or rename it) → Download. Files land in a
folder you choose in Settings. The 💬 icon in the top bar and the Settings
footer open a feedback email to **feedit18@gmail.com**.

---

## 1b. The core (server + web UI)

This repo already ships a working `vendor/` folder (yt-dlp 2026.08.19, the
`bgutil` PO-token plugin, and a static ffmpeg) so it runs with **no system
install** — it is what the live preview uses. On your own machine you can
instead install normally:

You need **Python 3**, **yt-dlp**, and (for merging/converting) **ffmpeg**.

```bash
python3 -m pip install -U yt-dlp      # Windows:  py -m pip install -U yt-dlp
# ffmpeg:
#   Windows: winget install Gyan.FFmpeg
#   macOS:   brew install ffmpeg deno
#   Linux:   sudo apt install ffmpeg
#   Android: see section 4
```

Then start the app:

```bash
python3 -m grabbox            # or double-click the launcher below
```

A window opens at `http://127.0.0.1:8765`.

| Platform | Launcher |
|---|---|
| Windows | double-click `GrabBox.bat` |
| Linux | `./GrabBox.sh` |
| macOS | double-click `GrabBox.command` |
| Anywhere | `python3 -m grabbox` or `python3 launch.py` |

Useful flags: `--dir FOLDER`, `--port 8765`, `--host 0.0.0.0` (reach it from
other devices on your LAN), `--watch-clipboard` (auto-pick-up copied links).

Paste any link → it tells you what it is (video / audio / image / software /
archive) and the size → pick a quality → Download. The Queue shows live
progress; Downloads lists, opens, reveals and deletes files.

> If a download 403s, GrabBox already walks the retry ladder and tells you the
> next step. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

---

## 2. Browser extension (Chrome / Edge / Brave / Firefox)

1. Open `chrome://extensions` (or `brave://extensions`, `edge://extensions`).
   Firefox: `about:debugging#/runtime/this-firefox` → Load Temporary Add-on.
2. Enable **Developer mode**.
3. **Load unpacked** → select the `extension/` folder.

Now:
* The toolbar icon is **faded** on pages with nothing to grab, and lights up +
  shows a count where there is.
* **Right-click** any link / video / audio / image → "Grab with GrabBox".
* **Hover** a video, image or file link → a small faded ↓ button appears; click
  it to grab.
* Either way an **in-page dialog** pops up right there on the page: pick kind
  and quality, rename if you like, hit Download — you never leave the tab.
* The popup lists every detected downloadable thing on the page.

The extension needs the app running on the same machine — either the desktop
app (section 1a) or the core server (`python3 -m grabbox`, section 1b). It
talks to `http://127.0.0.1:8765`, nothing touches the internet but the
download itself.

---

## 3. The desktop installers are CI-built; one-file binaries too

The Tauri installers from section 1a build on every push (see **Actions →
desktop (Tauri) → Artifacts**): `.msi` + `.exe` on Windows, `.dmg` on macOS,
`.AppImage` + `.deb` on Linux.

A separate action also builds a single-folder PyInstaller binary per OS
(`GrabBox-windows`, `GrabBox-ubuntu`, `GrabBox-macos` under **Actions →
build**), handy for USB sticks. To build that one locally:

```bash
pip install pyinstaller yt-dlp
pyinstaller packaging/grabbox.spec --noconfirm     # -> dist/GrabBox/
```

---

## 4. Android

**The native app (recommended)** — a real Kotlin app with the yt-dlp engine
bundled inside, so there is no server, no Termux, no terminal anywhere.
Android 6.0 or newer.

1. Grab the APK for your phone from the CI artifacts / Releases:
   `app-arm64-v8a-debug.apk` (almost every phone from the last ~8 years),
   `app-armeabi-v7a-debug.apk` (very old 32-bit phones), or
   `app-x86_64-debug.apk` (emulators).
2. Install it. Android will warn about "unknown apps from this source" the
   first time — allow it for your browser/file manager. That's the only hoop;
   sideloading is normal for apps distributed outside the Play Store.
3. Open **GrabBox**. That's it — the engine unpacks itself on first launch.

Using it:

- **Share any link → GrabBox** — from YouTube, a browser, a chat — the app
  opens with the video already probed. Pick quality, tap Download.
- **Or paste a link** inside the app and tap **Grab**.
- Music saves as real audio files (m4a default, mp3/vorbis/opus available);
  videos merge to mp4 via the bundled ffmpeg.

Permissions, handled the first time they matter:

- **Notifications** (Android 13+) — so you can see download progress and tap
  the finished file. Grant once, never asked again.
- **All-files access** (Android 11+) — requested so files land in the familiar
  `Download/GrabBox` folder. If you'd rather skip it, Settings lets you switch
  to the app's own folder instead (no permission needed, still accessible via
  Files → GrabBox).
- Nothing else. No account, no data leaves the phone except the downloads.

Tips:

- **Settings → Update yt-dlp engine** refreshes the engine over the network.
  YouTube changes break downloaders every few months; this fixes it without
  waiting for a new APK.
- **Settings → Download folder** picks where files go.

<details>
<summary><b>Nerd path (Termux)</b></summary>

Prefer running the same server-based UI in Termux instead (e.g. so a tablet or
desktop on your Wi-Fi can reach it too)?

```bash
bash android/termux-install.sh
```

It installs python + ffmpeg + yt-dlp + deno, starts the server, and opens the
UI. Downloads go to `Download/GrabBox` on your internal storage.
</details>

---

## 5. Reach it from other devices

```bash
python3 -m grabbox --host 0.0.0.0
```

Then any phone/tablet on your Wi-Fi opens `http://<your-laptop-ip>:8765`.
Great for sending a desktop download to a big drive while browsing on a phone.

---

## Privacy & legality

* 100% local. The only network traffic is between your device and the sites you
  download from.
* Use it for your own uploads, Creative-Commons material, things you bought, or
  offline copies you are allowed to keep. Downloading other people's copyright
  material breaks YouTube's terms and, depending on where you live, the law.
