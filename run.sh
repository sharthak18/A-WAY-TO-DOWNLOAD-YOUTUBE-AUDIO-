#!/bin/sh
# ytgrab launcher for Linux / macOS.
#   chmod +x run.sh && ./run.sh
# Needs Python 3 and yt-dlp:  python3 -m pip install -U yt-dlp
DIR="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    PY=python
fi
exec "$PY" "$DIR/ytgrab.py" "$@"
