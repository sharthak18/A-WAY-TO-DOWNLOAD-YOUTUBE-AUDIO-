#!/bin/sh
# GrabBox from source, for Linux:  ./scripts/grabbox.sh
# Needs python3 and yt-dlp:   python3 -m pip install -U yt-dlp   (+ ffmpeg from apt/dnf)
# (Prefer the AppImage? https://github.com/sharthak18/A-WAY-TO-DOWNLOAD-YOUTUBE-AUDIO-/releases/latest)
cd "$(dirname "$0")/.." || exit 1
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
exec "$PY" -m grabbox "$@"
