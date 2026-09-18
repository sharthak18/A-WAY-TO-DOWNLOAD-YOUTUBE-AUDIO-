# GrabBox — install & run, on everything

GrabBox is the "make it a software" answer to this repo. One small local server
plus a web UI, with three ways to reach it: a **browser window** (desktop),
a **browser extension** (the faded icon that lights up over downloadable
things, right-click "Grab with GrabBox", hover mini-button), and an **Android
app / Termux** install. It downloads anything a plain HTTP link can serve —
video, audio, images, installers, archives, documents — plus everything
yt-dlp already knows (YouTube, 1800+ sites, playlists).

Everything runs **on your device**. Nothing is uploaded anywhere.

---

## 1. The core (required, every platform)

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
* The popup lists every detected downloadable thing on the page.

Start the core app first (section 1); the extension just opens it with your
link. The icon "faded vs lit" behaviour is exactly what you asked for.

---

## 3. Desktop as one file (optional, no Python at all)

A GitHub Action builds a single-folder binary per OS on every push:

* `GrabBox-windows` (.exe), `GrabBox-ubuntu`, `GrabBox-macos`
* plus a `GrabBox-APK` for Android

See **Actions → build → Artifacts**. To build locally:

```bash
pip install pyinstaller yt-dlp
pyinstaller packaging/grabbox.spec --noconfirm     # -> dist/GrabBox/
```

---

## 4. Android

**Easiest (no APK):** install F-Droid → Termux (from F-Droid), then in Termux:

```bash
bash android/termux-install.sh
```

It installs python + ffmpeg + yt-dlp + deno, starts the server, and opens the
UI. Downloads go to `Download/GrabBox` on your internal storage.

**As a real app:** the CI workflow builds `app-debug.apk` (a WebView over the
same UI, with "Share → GrabBox" support). Install the APK, run the Termux
server, open the app. (The APK needs the Termux server because a phone app is
not allowed to run a background downloader the way a desktop service can.)

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
