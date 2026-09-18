"""
Read the system clipboard, so "copy a link anywhere -> it shows up here" works
without a browser extension.

Platform native, no extra dependencies: PowerShell on Windows, pbpaste on
macOS, xclip/wl-paste on Linux (whichever is installed).
"""

import os
import re
import subprocess
import sys
import threading
import time

IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"

URL_RE = re.compile(r"\bhttps?://[^\s\"'<>]+", re.I)


def read_clipboard():
    """Current clipboard text, or None when it cannot be read."""
    cmds = []
    if IS_WINDOWS:
        cmds = [["powershell", "-NoProfile", "-Command", "Get-Clipboard"]]
    elif IS_MAC:
        cmds = [["pbpaste"]]
    else:
        cmds = [["wl-paste", "--no-newline"],
                ["xclip", "-selection", "clipboard", "-o"],
                ["xsel", "--clipboard", "--output"]]
    for cmd in cmds:
        try:
            out = subprocess.run(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.DEVNULL, timeout=3)
        except (OSError, subprocess.SubprocessError):
            continue
        if out.returncode == 0:
            try:
                return out.stdout.decode("utf-8", "replace")
            except Exception:
                return None
    return None


class Watcher(object):
    """Polls the clipboard in the background and remembers the newest URL."""

    def __init__(self, interval=1.0):
        self.interval = interval
        self.last_text = None
        self.pending = None
        self._stop = threading.Event()
        self._thread = None
        self.enabled = False

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self.enabled = True
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True,
                                        name="grabbox-clipboard")
        self._thread.start()

    def stop(self):
        self.enabled = False
        self._stop.set()

    def _loop(self):
        # wait() returns True when stop() was called
        while not self._stop.wait(self.interval):
            text = read_clipboard()
            if not text or text == self.last_text:
                continue
            self.last_text = text
            m = URL_RE.search(text)
            if m:
                self.pending = {"url": m.group(0), "at": time.time()}

    def take(self):
        """Return the newest clipboard URL once, then forget it."""
        item, self.pending = self.pending, None
        return item
