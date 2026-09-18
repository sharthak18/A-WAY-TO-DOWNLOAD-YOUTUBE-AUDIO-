"""The downloaded-files view: list, reveal, open, delete."""

import os
import subprocess
import sys

from . import sniff

IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"


def list_files(directory, limit=200):
    """Newest-first listing of the download folder."""
    out = []
    try:
        names = os.listdir(directory)
    except OSError:
        return out
    for name in names:
        if name.startswith("."):
            continue
        path = os.path.join(directory, name)
        try:
            st = os.stat(path)
        except OSError:
            continue
        if not os.path.isfile(path):
            continue
        out.append({
            "name": name,
            "path": path,
            "size": st.st_size,
            "size_h": sniff.human_size(st.st_size),
            "mtime": st.st_mtime,
            "kind": sniff.kind_of(name),
            "icon": sniff.KIND_ICON.get(sniff.kind_of(name), "⬇️"),
        })
    out.sort(key=lambda f: f["mtime"], reverse=True)
    return out[:limit]


def open_in_file_manager(path):
    """Open the folder (or reveal the file) using the OS file manager."""
    target = path if os.path.isdir(path) else os.path.dirname(path)
    try:
        if IS_WINDOWS:
            if os.path.isfile(path):
                subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
            else:
                os.startfile(target)  # noqa: only exists on Windows
            return True
        if IS_MAC:
            args = ["open", "-R", path] if os.path.isfile(path) else ["open", target]
            subprocess.Popen(args)
            return True
        subprocess.Popen(["xdg-open", target])
        return True
    except OSError:
        return False


def open_file(path):
    """Hand the file to the OS default application."""
    try:
        if IS_WINDOWS:
            os.startfile(path)  # noqa: only exists on Windows
            return True
        opener = "open" if IS_MAC else "xdg-open"
        subprocess.Popen([opener, path])
        return True
    except OSError:
        return False


def delete(path, root):
    """Delete a file, but only inside the configured download folder."""
    real = os.path.realpath(path)
    if not real.startswith(os.path.realpath(root) + os.sep):
        return False
    try:
        os.remove(real)
        return True
    except OSError:
        return False
