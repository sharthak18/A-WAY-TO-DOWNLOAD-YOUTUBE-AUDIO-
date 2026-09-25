#!/usr/bin/env bash
# Fetch the standalone engine binaries GrabBox bundles as Tauri sidecars.
#
#   bash desktop/fetch-sidecars.sh                 # every supported target
#   bash desktop/fetch-sidecars.sh --target aarch64-apple-darwin
#
# Output: desktop/src-tauri/binaries/<name>-<triple>[.exe]  (gitignored)
set -euo pipefail

BIN_DIR="$(cd "$(dirname "$0")" && pwd)/src-tauri/binaries"
mkdir -p "$BIN_DIR"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

TARGETS=(x86_64-pc-windows-msvc x86_64-apple-darwin aarch64-apple-darwin \
         x86_64-unknown-linux-gnu aarch64-unknown-linux-gnu)
if [[ "${1:-}" == "--target" && -n "${2:-}" ]]; then
  TARGETS=("$2")
fi

dl() {  # dl <url> <out>
  echo "  -> $2"
  curl -fL --retry 3 --connect-timeout 20 -o "$2" "$1"
}

for triple in "${TARGETS[@]}"; do
  echo "== $triple =="
  case "$triple" in
    x86_64-pc-windows-msvc)   os=windows; arch=amd64; suffix=.exe; ytdlp=yt-dlp.exe ;;
    x86_64-apple-darwin)      os=macos;   arch=amd64; suffix=;     ytdlp=yt-dlp_macos ;;
    aarch64-apple-darwin)     os=macos;   arch=arm64; suffix=;     ytdlp=yt-dlp_macos ;;
    x86_64-unknown-linux-gnu) os=linux;   arch=amd64; suffix=;     ytdlp=yt-dlp_linux ;;
    aarch64-unknown-linux-gnu) os=linux;  arch=arm64; suffix=;     ytdlp=yt-dlp_linux_aarch64 ;;
    *) echo "unknown target: $triple" >&2; exit 1 ;;
  esac

  # --- yt-dlp (official standalone builds; embed Python, nothing to install)
  dl "https://github.com/yt-dlp/yt-dlp/releases/latest/download/${ytdlp}" \
     "$BIN_DIR/yt-dlp-${triple}${suffix}"

  # --- ffmpeg (Martin Riedl static release builds, all OS/arch)
  dl "https://ffmpeg.martin-riedl.de/redirect/latest/${os}/${arch}/release/ffmpeg.zip" \
     "$WORK/ffmpeg-${triple}.zip"
  unzip -o -q "$WORK/ffmpeg-${triple}.zip" "ffmpeg${suffix}" -d "$WORK/$triple" \
    || unzip -o -q "$WORK/ffmpeg-${triple}.zip" -d "$WORK/$triple"
  ff="$(find "$WORK/$triple" -name "ffmpeg${suffix}" -type f | head -1)"
  cp "$ff" "$BIN_DIR/ffmpeg-${triple}${suffix}"

  # --- deno (JavaScript runtime yt-dlp uses for YouTube n-signatures)
  dl "https://github.com/denoland/deno/releases/latest/download/deno-${triple}.zip" \
     "$WORK/deno-${triple}.zip"
  unzip -o -q "$WORK/deno-${triple}.zip" "deno${suffix}" -d "$WORK/$triple-deno"
  cp "$WORK/$triple-deno/deno${suffix}" "$BIN_DIR/deno-${triple}${suffix}"

  chmod +x "$BIN_DIR/yt-dlp-${triple}${suffix}" \
            "$BIN_DIR/ffmpeg-${triple}${suffix}" \
            "$BIN_DIR/deno-${triple}${suffix}" 2>/dev/null || true
done

ls -lh "$BIN_DIR"
echo "Sidecars staged in $BIN_DIR"
