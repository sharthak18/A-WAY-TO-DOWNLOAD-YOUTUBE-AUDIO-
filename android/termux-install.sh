#!/data/data/com.termux/files/usr/bin/bash
# GrabBox on Android via Termux.
#   1. Install F-Droid, then Termux from F-Droid (Play Store copy is dead).
#   2. Paste this whole script into Termux, or run:  bash termux-install.sh
# It installs python + ffmpeg + yt-dlp, starts the GrabBox server and opens it.
set -e

echo "[*] Updating packages (first run is slow)…"
pkg update -y
pkg install -y python ffmpeg git termux-api

echo "[*] Installing yt-dlp…"
python -m pip install --upgrade pip
python -m pip install --upgrade yt-dlp

# deno gives yt-dlp full YouTube support on Android
if ! command -v deno >/dev/null 2>&1; then
  echo "[*] Installing deno (JS runtime for YouTube)…"
  curl -fsSL https://deno.land/install.sh | sh -s -- -y || true
  export PATH="$HOME/.deno/bin:$PATH"
fi

HERE="$(cd "$(dirname "$0")/.." && pwd)"
echo "[*] GrabBox folder: $HERE"

echo "[*] Starting GrabBox on http://127.0.0.1:8765 …"
echo "[*] Your downloads land in ~/storage/shared/Download/GrabBox (run termux-setup-storage once)."
termux-setup-storage || true

# Open the UI in the phone's browser.
( termux-open-url http://127.0.0.1:8765 ) || true

exec python "$HERE/launch.py" --host 127.0.0.1 --no-browser \
  --dir "$HOME/storage/shared/Download/GrabBox"
