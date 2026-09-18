"""
Recognise "anything downloadable" from a bare URL.

yt-dlp already knows ~1800 sites, but a plain link to a .zip, a .jpg or an
installer is just an HTTP file. This module asks the server what it is serving
(HEAD, falling back to a ranged GET) and classifies it, so the UI can offer
the right thing instead of guessing.
"""

import mimetypes
import os
import posixpath
import re
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

EXT_KIND = {
    # video
    "mp4": "video", "mkv": "video", "webm": "video", "mov": "video",
    "avi": "video", "m4v": "video", "flv": "video", "ts": "video",
    "mpg": "video", "mpeg": "video", "3gp": "video", "wmv": "video",
    # audio
    "mp3": "audio", "m4a": "audio", "aac": "audio", "opus": "audio",
    "ogg": "audio", "oga": "audio", "flac": "audio", "wav": "audio",
    "wma": "audio", "aiff": "audio",
    # images
    "jpg": "image", "jpeg": "image", "png": "image", "gif": "image",
    "webp": "image", "bmp": "image", "svg": "image", "avif": "image",
    "tif": "image", "tiff": "image", "ico": "image", "heic": "image",
    # software / installers
    "exe": "app", "msi": "app", "apk": "app", "dmg": "app", "pkg": "app",
    "deb": "app", "rpm": "app", "appimage": "app", "flatpakref": "app",
    "jar": "app", "ipa": "app", "snap": "app",
    # archives
    "zip": "archive", "rar": "archive", "7z": "archive", "tar": "archive",
    "gz": "archive", "tgz": "archive", "bz2": "archive", "xz": "archive",
    "zst": "archive", "iso": "archive", "img": "archive",
    # documents / other data
    "pdf": "document", "epub": "document", "mobi": "document",
    "txt": "document", "md": "document", "csv": "document",
    "json": "document", "xml": "document", "srt": "document",
    "vtt": "document", "torrent": "other",
}

TYPE_PREFIX_KIND = {
    "video": "video", "audio": "audio", "image": "image",
    "application/pdf": "document",
    "application/zip": "archive", "application/x-7z-compressed": "archive",
    "application/x-rar-compressed": "archive", "application/gzip": "archive",
    "application/x-tar": "archive", "application/x-iso9660-image": "archive",
    "application/vnd.android.package-archive": "app",
    "application/x-msdownload": "app", "application/x-apple-diskimage": "app",
    "application/java-archive": "app", "application/octet-stream": None,
    "text": "document",
}

KIND_ICON = {
    "video": "🎬", "audio": "🎵", "image": "🖼️", "app": "📦",
    "archive": "🗜️", "document": "📄", "other": "⬇️",
}


def ext_of(name):
    """Extension of a filename *or* a URL (query string and fragment ignored)."""
    name = (name or "").split("?", 1)[0].split("#", 1)[0]
    return os.path.splitext(name)[1].lstrip(".").lower()


def kind_of(filename=None, content_type=None):
    """Classify by extension first (it is more reliable than Content-Type)."""
    kind = EXT_KIND.get(ext_of(filename))
    if kind:
        return kind
    ct = (content_type or "").split(";")[0].strip().lower()
    if not ct:
        return "other"
    if ct in TYPE_PREFIX_KIND:
        return TYPE_PREFIX_KIND[ct] or "other"
    for prefix, kind in (("video/", "video"), ("audio/", "audio"),
                         ("image/", "image"), ("text/", "document")):
        if ct.startswith(prefix):
            return kind
    return "other"


def filename_from(url, content_disposition=None, content_type=None):
    """Best guess at a filename for a direct link."""
    if content_disposition:
        m = re.search(r"filename\*=(?:UTF-8'')?\"?([^\";]+)", content_disposition, re.I)
        if m:
            return urllib.parse.unquote(m.group(1).strip())
        m = re.search(r'filename="?([^";]+)"?', content_disposition, re.I)
        if m:
            return m.group(1).strip()
    path = urllib.parse.urlparse(url).path
    name = posixpath.basename(path)
    if name and ext_of(name):
        return urllib.parse.unquote(name)
    if name:
        guess = mimetypes.guess_extension((content_type or "").split(";")[0])
        return urllib.parse.unquote(name) + (guess or "")
    return "download"


def probe(url, timeout=15):
    """
    Ask the server about a direct link. Returns a dict; never raises.

    ``{'ok', 'url', 'final_url', 'status', 'kind', 'filename', 'size',
       'content_type'}``
    """
    out = {"ok": False, "url": url, "final_url": url, "status": None,
           "kind": "other", "filename": None, "size": None, "content_type": None,
           "error": None}
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            headers = resp.headers
            out.update(status=resp.status, final_url=resp.geturl())
    except urllib.error.HTTPError as exc:
        # Some servers refuse HEAD (405/403) but happily serve GET.
        headers = exc.headers
        out.update(status=exc.code, final_url=url)
        if exc.code not in (403, 405, 501):
            out["error"] = "HTTP %s" % exc.code
            return out
    except Exception as exc:
        out["error"] = str(exc)
        return out

    ctype = headers.get("Content-Type")
    cdisp = headers.get("Content-Disposition")
    length = headers.get("Content-Length")
    out["content_type"] = ctype
    out["filename"] = filename_from(out["final_url"], cdisp, ctype)
    out["kind"] = kind_of(out["filename"], ctype)
    try:
        out["size"] = int(length) if length else None
    except ValueError:
        out["size"] = None
    out["ok"] = out["status"] is not None and out["status"] < 400
    return out


def looks_like_page(url):
    """True when the URL is probably a web page rather than a file."""
    if re.search(r"\.(%s)(\?|#|$)" % "|".join(EXT_KIND), url, re.I):
        return False
    host = urllib.parse.urlparse(url).netloc.lower()
    return not host.startswith(("cdn.", "dl.", "download.", "files."))


def human_size(n):
    if not n:
        return ""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return ("%.1f %s" % (n, unit)) if unit != "B" else ("%d B" % n)
        n /= 1024.0
    return ""
