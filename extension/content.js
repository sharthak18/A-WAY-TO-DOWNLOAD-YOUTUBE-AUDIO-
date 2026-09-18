/*
 * GrabBox content script.
 *
 * Two jobs:
 *  1. Count the things on this page that are actually downloadable and tell the
 *     background, so the toolbar icon lights up (it is faded by default).
 *  2. Put a small faded button on any hovered media / image / file link; a click
 *     hands that link straight to the app.
 */
"use strict";

(() => {
  const FILE_EXT = /\.(mp4|mkv|webm|mov|avi|m4v|flv|mp3|m4a|aac|opus|ogg|flac|wav|jpg|jpeg|png|gif|webp|bmp|svg|avif|exe|msi|apk|dmg|pkg|deb|rpm|appimage|zip|rar|7z|tar|gz|tgz|bz2|xz|iso|pdf|epub|torrent)(\?|#|$)/i;

  function collect() {
    const items = [];
    const push = (url, kind, label) => {
      if (url && url.startsWith("http") && !items.some((i) => i.url === url))
        items.push({ url, kind, label });
    };
    document.querySelectorAll("video[src], video source[src]").forEach((el) =>
      push(el.src || el.getAttribute("src"), "video", el.currentSrc || "video"));
    document.querySelectorAll("audio[src], audio source[src]").forEach((el) =>
      push(el.src || el.getAttribute("src"), "audio", el.currentSrc || "audio"));
    document.querySelectorAll("img[src]").forEach((el) =>
      push(el.src, "image", el.alt || "image"));
    document.querySelectorAll("a[href]").forEach((a) => {
      if (FILE_EXT.test(a.href)) push(a.href, "file", a.textContent.trim() || a.href);
    });
    return items.slice(0, 200);
  }

  function report() {
    const count = collect().length;
    chrome.runtime.sendMessage({ type: "media-count", count }).catch(() => {});
    return count;
  }

  /* ------------------------------------------- faded hover button */
  let btn = null;
  let btnTarget = null;

  function makeButton() {
    btn = document.createElement("div");
    btn.className = "grabbox-btn";
    btn.title = "Grab with GrabBox";
    btn.innerHTML = "&#8681;"; // ↓
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (btnTarget) {
        chrome.runtime.sendMessage({ type: "grab", url: btnTarget }).catch(() => {});
      }
      hideButton();
    });
    document.documentElement.appendChild(btn);
  }

  function positionFor(el) {
    const r = el.getBoundingClientRect();
    btn.style.top = r.top + window.scrollY + 8 + "px";
    btn.style.left = Math.max(4, r.left + window.scrollX + 8) + "px";
    btn.classList.add("show");
  }
  function hideButton() {
    if (btn) btn.classList.remove("show");
    btnTarget = null;
  }

  function targetOf(el) {
    if (!el || !el.closest) return null;
    const media = el.closest("video, audio, img");
    if (media && (media.src || media.currentSrc)) return media.src || media.currentSrc;
    const a = el.closest("a[href]");
    if (a && FILE_EXT.test(a.href)) return a.href;
    return null;
  }

  document.addEventListener("mouseover", (e) => {
    const url = targetOf(e.target);
    if (!url) return hideButton();
    if (!btn) makeButton();
    if (btnTarget !== url) {
      btnTarget = url;
      positionFor(e.target);
    }
  });
  document.addEventListener("scroll", hideButton, { passive: true });

  /* The popup asks for the current list of detected items. */
  chrome.runtime.onMessage.addListener((msg, sender, send) => {
    if (msg && msg.type === "list") send({ items: collect() });
    return false;
  });

  /* ------------------------------------------------- initial + live report */
  report();
  const mo = new MutationObserver(() => {
    clearTimeout(mo._t);
    mo._t = setTimeout(report, 1200);
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();
