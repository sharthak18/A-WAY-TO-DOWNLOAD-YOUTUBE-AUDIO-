#!/bin/sh
# GrabBox for macOS - double-click me.
# Needs python3 and yt-dlp:   brew install python yt-dlp ffmpeg deno
DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
exec "$PY" "$DIR/launch.py" "$@"
