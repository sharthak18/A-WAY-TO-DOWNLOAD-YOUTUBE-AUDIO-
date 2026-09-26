#!/bin/sh
# GrabBox from source, for macOS - double-click me.
# Needs python3 and yt-dlp:   brew install python yt-dlp ffmpeg deno
# (Prefer the .dmg? https://github.com/sharthak18/A-WAY-TO-DOWNLOAD-YOUTUBE-AUDIO-/releases/latest)
cd "$(dirname "$0")/.." || exit 1
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
exec "$PY" -m grabbox "$@"
