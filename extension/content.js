/*
 * GrabBox content script.
 *
 *  1. Count downloadable things and tell the background (toolbar icon lights up).
 *  2. Faded hover button on media / file links.
 *  3. The Grab Dialog — an IDM-style in-page card: right-click or hover-↓ opens
 *     it, it probes the link via the local app, you pick quality right there
 *     and hit Download. Shadow DOM keeps page CSS from touching it.
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
    chrome.runtime.sendMessage({ type: "media-count", count: collect().length }).catch(() => {});
  }

  /* ============================================================== dialog == */

  const DIALOG_CSS = `
    :host { all: initial; }
    * { box-sizing: border-box; font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
    .card {
      position: fixed; top: 64px; left: 50%; transform: translateX(-50%);
      width: 350px; max-width: calc(100vw - 32px); z-index: 2147483647;
      background: #171a21; color: #e7ecf3;
      border: 1px solid #2b3342; border-radius: 18px;
      box-shadow: 0 18px 60px rgba(0,0,0,.55), 0 4px 16px rgba(0,0,0,.4);
      overflow: hidden; animation: pop .18s ease;
    }
    @keyframes pop { from { opacity: 0; transform: translateX(-50%) translateY(-8px) scale(.98); } }
    .head {
      display: flex; align-items: center; gap: 8px; padding: 12px 14px;
      border-bottom: 1px solid #232a36; background: #1b2029;
    }
    .head b { font-size: 13.5px; font-weight: 650; flex: 1; letter-spacing: .2px; }
    .x {
      width: 26px; height: 26px; border: 0; border-radius: 50%; cursor: pointer;
      background: transparent; color: #8d99ab; font-size: 13px;
    }
    .x:hover { background: #2a3240; color: #fff; }
    .body { padding: 14px; display: grid; gap: 10px; }
    .status { font-size: 13px; color: #8d99ab; padding: 18px 4px; text-align: center; }
    .meta { display: flex; gap: 11px; align-items: center; min-height: 0; }
    .thumb { width: 104px; aspect-ratio: 16/9; object-fit: cover; border-radius: 9px; background: #0f131a; flex: none; }
    .thumb.broken { display: none; }
    .tblock { min-width: 0; }
    .title { font-size: 13px; font-weight: 600; line-height: 1.35;
      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; overflow-wrap: anywhere; }
    .sub { font-size: 11.5px; color: #8d99ab; margin-top: 4px; }
    select, input {
      width: 100%; background: #0f131a; color: #e7ecf3;
      border: 1px solid #2b3342; border-radius: 10px;
      padding: 9px 11px; font-size: 13px; outline: none;
    }
    select:focus, input:focus { border-color: #4f8cff; }
    .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
    label { font-size: 10.5px; color: #8d99ab; text-transform: uppercase; letter-spacing: .7px;
      display: block; margin: 0 0 4px 2px; font-weight: 600; }
    .dl {
      border: 0; border-radius: 11px; cursor: pointer; padding: 11px;
      background: linear-gradient(140deg, #4f8cff, #8b5cf6);
      color: #fff; font-size: 14px; font-weight: 650;
    }
    .dl:hover { filter: brightness(1.1); }
    .dl:disabled { opacity: .45; cursor: default; }
    .foot { display: flex; justify-content: space-between; align-items: center; font-size: 11.5px; }
    .link { color: #4f8cff; cursor: pointer; text-decoration: none; }
    .link:hover { text-decoration: underline; }
    .err { font-size: 12.5px; color: #ff9aa4; background: #2a171c; border: 1px solid #4d2229;
      border-radius: 10px; padding: 9px 11px; overflow-wrap: anywhere; }
    .hint { font-size: 12px; color: #f6c453; }
    .ok { font-size: 13px; color: #7bd88f; text-align: center; padding: 10px 0 2px; }
    .hidden { display: none !important; }
  `;

  const QUALITIES = {
    video: [["best", "Best available"], ["2160", "2160p (4K)"], ["1440", "1440p"],
            ["1080", "1080p"], ["720", "720p"], ["480", "480p"], ["360", "360p (small)"]],
    audio: [["m4a", "m4a — plays everywhere"], ["mp3", "mp3 — max compatibility"],
            ["opus", "opus — best size/quality"], ["flac", "flac — lossless, big"],
            ["best", "original stream, no re-encode"]],
    file: [["original", "original file, as served"]],
  };
  let server = "http://127.0.0.1:8765";

  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function fmtBytes(n) {
    if (!n) return "";
    const u = ["B", "KB", "MB", "GB", "TB"];
    let i = 0;
    while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
    return `${n.toFixed(i ? 1 : 0)} ${u[i]}`;
  }
  function fmtDur(s) {
    s = Math.round(s);
    const m = Math.floor(s / 60);
    return `${m}:${String(s % 60).padStart(2, "0")}`;
  }

  const rpc = (msg) => new Promise((resolve) => {
    try {
      chrome.runtime.sendMessage(msg, (res) => {
        if (chrome.runtime.lastError) resolve(null);
        else resolve(res);
      });
    } catch (e) { resolve(null); }
  });

  let host = null, cardEl = null, dialogEls = null, currentProbe = null, chosenKind = "file";

  function closeDialog() {
    if (host) { host.remove(); host = null; cardEl = null; dialogEls = null; currentProbe = null; }
    window.removeEventListener("keydown", onEsc, true);
    window.removeEventListener("mousedown", onOutside, true);
  }
  function onEsc(e) { if (e.key === "Escape") { e.stopPropagation(); closeDialog(); } }
  function onOutside(e) {
    if (host && cardEl && !e.composedPath().includes(cardEl)) closeDialog();
  }

  function openDialog(url) {
    closeDialog();
    host = document.createElement("div");
    const root = host.attachShadow({ mode: "closed" });
    const style = document.createElement("style");
    style.textContent = DIALOG_CSS;
    const card = el("div", "card");
    cardEl = card;

    const head = el("div", "head");
    head.appendChild(el("b", null, "Grab with GrabBox"));
    const x = el("button", "x", "✕");
    x.addEventListener("click", closeDialog);
    head.appendChild(x);

    const body = el("div", "body");
    const status = el("div", "status", "Reading link…");
    const result = el("div", "hidden");
    const errorBox = el("div", "err hidden");
    const okBox = el("div", "ok hidden");

    body.append(status, result, errorBox, okBox);
    card.append(head, body);
    root.append(style, card);
    document.documentElement.appendChild(host);

    window.addEventListener("keydown", onEsc, true);
    setTimeout(() => window.addEventListener("mousedown", onOutside, true), 50);

    dialogEls = { status, result, errorBox, okBox };
    probeInto(url, dialogEls);
  }

  async function probeInto(url, els) {
    const res = await rpc({ type: "probe", url });
    if (!dialogEls) return; // closed while probing

    if (!res) {
      els.status.textContent = "";
      els.errorBox.classList.remove("hidden");
      els.errorBox.textContent = "The GrabBox app isn't running. Start it, then try again — the app does the actual downloading.";
      addOpenAppRow(els);
      const retry = el("button", "dl", "Retry");
      retry.addEventListener("click", () => openDialog(url));
      els.status.replaceWith(retry);
      return;
    }
    if (!res.ok) {
      els.status.classList.add("hidden");
      els.errorBox.classList.remove("hidden");
      els.errorBox.textContent = res.error || "Could not read that link.";
      if (res.hint) {
        const hint = el("div", "hint", "💡 " + res.hint);
        els.errorBox.appendChild(hint);
      }
      addOpenAppRow(els);
      return;
    }

    currentProbe = res;
    els.status.classList.add("hidden");
    buildResult(res, els, url);
  }

  function addOpenAppRow(els) {
    const foot = el("div", "foot");
    const link = el("a", "link", "Open the GrabBox app →");
    link.addEventListener("click", () => rpc({ type: "open-app" }));
    foot.append(link, el("span", null, ""));
    els.result.parentElement.appendChild(foot);
  }

  function buildResult(res, els, url) {
    const r = els.result;
    r.classList.remove("hidden");
    r.className = "result";
    r.style.display = "grid";
    r.style.gap = "10px";

    // meta row
    const meta = el("div", "meta");
    const img = document.createElement("img");
    img.className = "thumb broken";
    img.alt = "";
    img.addEventListener("error", () => img.classList.add("broken"));
    if (res.thumb) { img.src = res.thumb; img.classList.remove("broken"); }
    const tblock = el("div", "tblock");
    tblock.appendChild(el("div", "title", res.title || url));
    const bits = [];
    if (res.uploader) bits.push(res.uploader);
    if (res.duration) bits.push(fmtDur(res.duration));
    if (res.direct && res.direct.size) bits.push(fmtBytes(res.direct.size));
    if (res.is_playlist) bits.push("playlist");
    tblock.appendChild(el("div", "sub", bits.join("  ·  ") || KIND_NAME(res.kind)));
    meta.append(img, tblock);
    r.appendChild(meta);

    // kind + quality
    const kinds = kindsFor(res);
    chosenKind = kinds.includes(res.kind) ? res.kind : kinds[0];
    const kindSel = document.createElement("select");
    KIND_NAMES().forEach(([k, label]) => {
      if (!kinds.includes(k)) return;
      const o = document.createElement("option");
      o.value = k; o.textContent = label;
      kindSel.appendChild(o);
    });
    kindSel.value = chosenKind;

    const qSel = document.createElement("select");
    const fillQ = () => {
      const group = chosenKind === "video" || chosenKind === "audio" ? chosenKind : "file";
      let opts = QUALITIES[group];
      if (group === "video") {
        const hs = (res.formats || []).filter((f) => f.kind === "video" && f.height).map((f) => f.height);
        if (hs.length) {
          const maxH = Math.max(...hs);
          opts = opts.filter(([v]) => v === "best" || parseInt(v, 10) <= maxH * 1.02);
        }
      }
      qSel.innerHTML = "";
      opts.forEach(([v, label]) => {
        const o = document.createElement("option");
        o.value = v; o.textContent = label;
        qSel.appendChild(o);
      });
    };
    fillQ();
    kindSel.addEventListener("change", () => { chosenKind = kindSel.value; fillQ(); });

    const row = el("div", "row2");
    const kwrap = el("div"); kwrap.append(el("label", null, "Grab as"), kindSel);
    const qwrap = el("div"); qwrap.append(el("label", null, "Quality"), qSel);
    row.append(kwrap, qwrap);
    r.appendChild(row);

    // name (optional)
    const nameWrap = el("div");
    nameWrap.appendChild(el("label", null, "Rename (optional)"));
    const nameInput = document.createElement("input");
    nameInput.placeholder = cleanName((res.direct && res.direct.filename) || res.title || "");
    nameWrap.appendChild(nameInput);
    r.appendChild(nameWrap);

    // go
    const dl = el("button", "dl", "Download");
    dl.addEventListener("click", async () => {
      dl.disabled = true;
      dl.textContent = "Adding…";
      const out = await rpc({
        type: "download",
        body: {
          url,
          kind: chosenKind,
          quality: qSel.value,
          playlist: !!res.is_playlist,
          filename: nameInput.value.trim() || null,
        },
      });
      if (out && out.job) {
        els.result.classList.add("hidden");
        els.okBox.classList.remove("hidden");
        els.okBox.textContent = "✓ Queued — the GrabBox app is on it.";
        setTimeout(closeDialog, 2200);
      } else {
        dl.disabled = false;
        dl.textContent = "Download";
        els.errorBox.classList.remove("hidden");
        els.errorBox.textContent = (out && out.error) || "Could not start the download — is the app running?";
      }
    });
    r.appendChild(dl);

    const foot = el("div", "foot");
    const link = el("a", "link", "open full app");
    link.addEventListener("click", () => rpc({ type: "open-app" }));
    foot.append(link);
    const sizeNote = el("span", null, res.direct && res.direct.size ? "~" + fmtBytes(res.direct.size) : "");
    foot.append(sizeNote);
    r.appendChild(foot);
  }

  function KIND_NAMES() {
    return [["video", "Video"], ["audio", "Audio only"], ["image", "Image"], ["app", "File"], ["archive", "Archive"], ["file", "File"]];
  }
  function KIND_NAME(k) { return { video: "Video", audio: "Audio", image: "Image", app: "Software", archive: "Archive", document: "Document", other: "File" }[k] || "File"; }

  function kindsFor(res) {
    const set = new Set();
    if (res.kind) set.add(res.kind === "other" ? "file" : res.kind);
    const fmts = res.formats || [];
    if (fmts.some((f) => f.kind === "video")) set.add("video");
    if (fmts.some((f) => f.kind === "audio")) set.add("audio");
    if (res.direct) set.add(res.direct.kind === "other" ? "file" : res.direct.kind);
    if (!set.size) set.add("file");
    return [...set];
  }

  function cleanName(s) {
    return (s || "").replace(/[\\/:*?"<>|]+/g, " ").replace(/\s+/g, " ").trim();
  }

  /* ============================================== hover button + triggers = */

  let btn = null, btnTarget = null;

  function makeButton() {
    btn = document.createElement("div");
    btn.className = "grabbox-btn";
    btn.title = "Grab with GrabBox";
    btn.innerHTML = "&#8681;";
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      if (btnTarget) openDialog(btnTarget);
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
  function hideButton() { if (btn) btn.classList.remove("show"); btnTarget = null; }

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
    if (btnTarget !== url) { btnTarget = url; positionFor(e.target); }
  });
  document.addEventListener("scroll", hideButton, { passive: true });

  /* background / popup -> open the dialog for a URL */
  chrome.runtime.onMessage.addListener((msg, sender, send) => {
    if (!msg || !msg.type) return false;
    if (msg.type === "open-dialog" && msg.url) { openDialog(msg.url); send({ ok: true }); return false; }
    if (msg.type === "list") { send({ items: collect() }); return false; }
    return false;
  });

  rpc({ type: "get-server" }).then((s) => { if (s && s.server) server = s.server; });

  report();
  const mo = new MutationObserver(() => {
    clearTimeout(mo._t);
    mo._t = setTimeout(report, 1200);
  });
  mo.observe(document.documentElement, { childList: true, subtree: true });
})();
