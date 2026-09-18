/* GrabBox web UI. No frameworks, no build step - just fetch() and the DOM. */
"use strict";

const $ = (sel) => document.querySelector(sel);
const api = {
  get: (p) => fetch(p).then((r) => r.json()),
  post: (p, body) =>
    fetch(p, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}),
    }).then((r) => r.json()),
};

const QUALITIES = {
  video: [
    ["best", "Best available"],
    ["2160", "2160p (4K)"],
    ["1440", "1440p"],
    ["1080", "1080p"],
    ["720", "720p"],
    ["480", "480p"],
    ["360", "360p (small file)"],
  ],
  audio: [
    ["m4a", "m4a — great quality, plays everywhere"],
    ["opus", "opus — best quality per MB"],
    ["mp3", "mp3 — maximum compatibility"],
    ["flac", "flac — lossless container (big, no extra detail)"],
    ["best", "original stream, no re-encode"],
  ],
  file: [["original", "original file, exactly as served"]],
};

const KIND_LABEL = {
  video: "🎬 Video", audio: "🎵 Audio", image: "🖼️ Image",
  app: "📦 Software", archive: "🗜️ Archive", document: "📄 Document",
  other: "⬇️ File",
};

let current = null;       // last probe result
let chosenKind = "file";
let health = null;

/* ------------------------------------------------------------- health */

async function loadHealth() {
  try {
    health = await api.get("/api/health");
  } catch (e) {
    $("#health").textContent = "server unreachable";
    $("#health").className = "pill bad";
    return;
  }
  const p = health.problems || [];
  const pill = $("#health");
  if (p.includes("ytdlp-missing")) {
    pill.textContent = "yt-dlp missing";
    pill.className = "pill bad";
  } else if (p.includes("ytdlp-stale")) {
    pill.textContent = `yt-dlp ${health.ytdlp} — update it`;
    pill.className = "pill warn";
  } else if (p.length) {
    pill.textContent = `yt-dlp ${health.ytdlp} — needs setup`;
    pill.className = "pill warn";
  } else {
    pill.textContent = `yt-dlp ${health.ytdlp} — ready`;
    pill.className = "pill ok";
  }
  pill.title = [
    `yt-dlp ${health.ytdlp || "?"} (${health.ytdlp_age ?? "?"} days old)`,
    `ffmpeg: ${health.ffmpeg || "MISSING"}`,
    `JS runtime: ${health.js_runtime || "MISSING"} ${health.js_path || ""}`.trim(),
    `Downloads: ${health.download_dir}`,
    health.update_hint,
  ].join("\n");
}

/* -------------------------------------------------------------- probe */

async function analyze(url) {
  url = (url || "").trim();
  if (!url) return toast("Paste a link first");
  $("#rTitle").textContent = "Analyzing…";
  $("#rSub").textContent = url;
  $("#rKinds").innerHTML = "";
  $("#rQuality").innerHTML = "";
  $("#result").classList.remove("hidden");
  $("#rThumb").removeAttribute("src");
  $("#rPlaylist").classList.add("hidden");
  $("#rWarn").classList.add("hidden");
  $("#rDownload").disabled = true;

  const res = await api.post("/api/probe", { url });
  current = res;

  if (!res.ok) {
    $("#rTitle").textContent = "Could not read that link";
    $("#rSub").textContent = res.error || "unknown error";
    $("#rKinds").innerHTML = res.hint
      ? `<span class="chip on">💡 ${res.hint}</span>` : "";
    return;
  }

  $("#rTitle").textContent = res.title || url;
  const bits = [];
  if (res.uploader) bits.push(res.uploader);
  if (res.duration) bits.push(fmtDuration(res.duration));
  if (res.direct) bits.push(`direct ${res.direct.kind} · ${fmtBytes(res.direct.size)}`);
  if (res.is_playlist) bits.push(`${(res.entries || []).length}+ items`);
  $("#rSub").textContent = bits.join("  ·  ") || url;
  if (res.thumb) $("#rThumb").src = res.thumb;

  const warn = $("#rWarn");
  if (res.note) { warn.textContent = "⚠️ " + res.note; warn.classList.remove("hidden"); }
  else warn.classList.add("hidden");

  const kinds = kindsFor(res);
  $("#rKinds").innerHTML = kinds
    .map((k) => `<button class="chip${k === res.kind ? " on" : ""}" data-kind="${k}">${KIND_LABEL[k] || k}</button>`)
    .join("");
  $("#rKinds").querySelectorAll(".chip").forEach((c) =>
    c.addEventListener("click", () => {
      $("#rKinds").querySelectorAll(".chip").forEach((x) => x.classList.remove("on"));
      c.classList.add("on");
      chosenKind = c.dataset.kind;
      fillQualities(chosenKind);
    })
  );

  chosenKind = res.kind;
  fillQualities(chosenKind);
  $("#rName").value = "";
  $("#rName").placeholder = cleanName(res.direct?.filename || res.title || "");
  $("#rDownload").disabled = false;

  if (res.is_playlist) {
    const list = (res.entries || []).slice(0, 25);
    $("#rPlaylist").innerHTML =
      `<b>Playlist</b> — every item will be downloaded and numbered in order.` +
      `<ul>` + list.map((e, i) =>
        `<li><span class="idx">${String(i + 1).padStart(2, "0")}</span><span>${escapeHtml(e.title || e.url || "")}</span></li>`
      ).join("") + `</ul>`;
    $("#rPlaylist").classList.remove("hidden");
  }
}

function kindsFor(res) {
  const set = new Set();
  set.add(res.kind || "file");
  const hasVideo = (res.formats || []).some((f) => f.kind === "video");
  const hasAudio = (res.formats || []).some((f) => f.kind === "audio");
  if (hasVideo) set.add("video");
  if (hasAudio) set.add("audio");
  if (res.direct) set.add(res.direct.kind);
  if (!set.size) set.add("file");
  return [...set];
}

function fillQualities(kind) {
  const opts = QUALITIES[kind] || QUALITIES.file;
  $("#rQuality").innerHTML = opts
    .map(([v, l]) => `<option value="${v}">${l}</option>`)
    .join("");
}

/* ------------------------------------------------------------ download */

async function startDownload() {
  if (!current || !current.url) return;
  const body = {
    url: current.url,
    kind: chosenKind,
    quality: $("#rQuality").value,
    playlist: !!current.is_playlist,
    filename: $("#rName").value.trim() || null,
  };
  const res = await api.post("/api/download", body);
  if (res.job) {
    toast(`Added: ${KIND_LABEL[chosenKind] || chosenKind}`);
    $("#result").classList.add("hidden");
    $("#url").value = "";
    refreshJobs();
  } else {
    toast(res.error || "could not start the download");
  }
}

/* ---------------------------------------------------------------- jobs */

let lastJobState = "";

async function refreshJobs() {
  let data;
  try {
    data = await api.get("/api/jobs");
  } catch (e) {
    return;
  }
  const jobs = (data.jobs || []).slice().reverse();
  const key = JSON.stringify(jobs.map((j) => [j.id, j.status, j.percent, j.filename]));
  if (key === lastJobState) return;
  const hadRunning = lastJobState.includes('"running"');
  lastJobState = key;

  const box = $("#jobs");
  if (!jobs.length) {
    box.innerHTML = `<p class="empty">Nothing downloading yet.</p>`;
  } else {
    box.innerHTML = jobs.map(jobCard).join("");
    box.querySelectorAll("[data-cancel]").forEach((b) =>
      b.addEventListener("click", () => api.post(`/api/jobs/${b.dataset.cancel}/cancel`)));
    box.querySelectorAll("[data-open]").forEach((b) =>
      b.addEventListener("click", () => api.post("/api/files/open", { path: b.dataset.open, action: "reveal" })));
  }
  if (hadRunning && !jobs.some((j) => j.status === "running")) loadFiles();
}

function jobCard(j) {
  const cls = j.status === "done" ? "done" : j.status === "error" ? "error" : "";
  const pct = j.percent ? `${j.percent.toFixed(0)}%` : "";
  const speed = j.speed ? `${fmtBytes(j.speed)}/s` : "";
  const eta = j.eta ? `· ${j.eta}s left` : "";
  const items = j.items_total ? ` · item ${j.items_done || 1}/${j.items_total}` : "";
  return `
  <div class="job ${cls}">
    <div class="job-top">
      <div class="job-title">${escapeHtml(j.filename || j.title || j.url)}</div>
      <div class="job-actions">
        ${j.status === "running" ? `<button data-cancel="${j.id}">stop</button>` : ""}
        ${j.status === "done" && j.path ? `<button data-open="${escapeAttr(j.path)}">show</button>` : ""}
      </div>
    </div>
    <div class="job-sub">${j.status}${pct ? " · " + pct : ""} ${speed} ${eta}${items}
      ${j.attempts_total > 1 ? ` · attempt ${j.attempt}/${j.attempts_total}` : ""}</div>
    <div class="bar"><i style="width:${j.percent || 0}%"></i></div>
    ${j.status === "error" ? `<div class="err">${escapeHtml(j.error || "failed")}</div>` : ""}
    ${j.hint ? `<div class="hint">💡 ${escapeHtml(j.hint)}</div>` : ""}
  </div>`;
}

/* --------------------------------------------------------------- files */

async function loadFiles() {
  let data;
  try {
    data = await api.get("/api/files");
  } catch (e) {
    return;
  }
  const box = $("#files");
  const list = data.files || [];
  if (!list.length) {
    box.innerHTML = `<p class="empty">Nothing here yet — folder: ${escapeHtml(data.dir || "")}</p>`;
    return;
  }
  box.innerHTML = list.map((f) => `
    <div class="file">
      <span class="ico">${f.icon}</span>
      <div class="meta">
        <div class="name">${escapeHtml(f.name)}</div>
        <div class="sub">${f.size_h} · ${new Date(f.mtime * 1000).toLocaleString()}</div>
      </div>
      <div class="acts">
        <button data-open="${escapeAttr(f.path)}">open</button>
        <button data-reveal="${escapeAttr(f.path)}">📂</button>
        <button data-del="${escapeAttr(f.path)}">🗑</button>
      </div>
    </div>`).join("");
  box.querySelectorAll("[data-open]").forEach((b) =>
    b.addEventListener("click", () => api.post("/api/files/open", { path: b.dataset.open, action: "open" })));
  box.querySelectorAll("[data-reveal]").forEach((b) =>
    b.addEventListener("click", () => api.post("/api/files/open", { path: b.dataset.reveal, action: "reveal" })));
  box.querySelectorAll("[data-del]").forEach((b) =>
    b.addEventListener("click", async () => {
      if (!confirm("Delete this file?")) return;
      await api.post("/api/files/open", { path: b.dataset.del, action: "delete" });
      loadFiles();
    }));
}

/* ------------------------------------------------------------ settings */

async function openSettings() {
  const cfg = await api.get("/api/config");
  $("#sDir").value = cfg.download_dir || "";
  $("#sConc").value = cfg.concurrency || 2;
  $("#sCookies").value = cfg.cookies_browser || "";
  $("#sClip").checked = !!cfg.watch_clipboard;
  const h = await api.get("/api/health");
  $("#sHealth").textContent = [
    `yt-dlp     ${h.ytdlp || "MISSING"}  (${h.ytdlp_age ?? "?"} days old)`,
    `ffmpeg     ${h.ffmpeg || "MISSING"}`,
    `JS runtime ${h.js_runtime || "MISSING"} ${h.js_path || ""}`.trim(),
    `folder     ${h.download_dir}`,
    "",
    `Update:    ${h.update_hint}`,
  ].join("\n");
  $("#settings").classList.remove("hidden");
}

async function saveSettings() {
  await api.post("/api/config", {
    download_dir: $("#sDir").value.trim(),
    concurrency: Math.max(1, parseInt($("#sConc").value || "2", 10)),
    cookies_browser: $("#sCookies").value,
    watch_clipboard: $("#sClip").checked,
  });
  $("#settings").classList.add("hidden");
  toast("Settings saved");
  loadHealth();
  loadFiles();
}

/* ------------------------------------------------------------ clipboard */

async function pollClipboard() {
  try {
    const d = await api.get("/api/clipboard");
    if (d.item && d.item.url) {
      $("#clipUrl").textContent = d.item.url.slice(0, 64) + (d.item.url.length > 64 ? "…" : "");
      $("#clipHint").classList.remove("hidden");
      $("#clipHint").dataset.url = d.item.url;
    }
  } catch (e) { /* server may be restarting */ }
}

/* ------------------------------------------------------------- helpers */

function fmtBytes(n) {
  if (!n) return "";
  const u = ["B", "KB", "MB", "GB", "TB"];
  let i = 0;
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
  return `${n.toFixed(i ? 1 : 0)} ${u[i]}`;
}
function fmtDuration(s) {
  s = Math.round(s);
  const m = Math.floor(s / 60);
  return `${m}:${String(s % 60).padStart(2, "0")}`;
}
function cleanName(s) {
  return (s || "").replace(/[\\/:*?"<>|]+/g, " ").replace(/\s+/g, " ").trim();
}
function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function escapeAttr(s) { return escapeHtml(s).replace(/`/g, "&#96;"); }

let toastTimer = null;
function toast(msg) {
  const el = $("#toast");
  el.textContent = msg;
  el.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add("hidden"), 2600);
}

/* ---------------------------------------------------------------- init */

document.addEventListener("DOMContentLoaded", () => {
  loadHealth();
  loadFiles();
  refreshJobs();
  setInterval(refreshJobs, 1000);
  setInterval(loadFiles, 5000);
  setInterval(pollClipboard, 1500);

  $("#go").addEventListener("click", () => analyze($("#url").value));
  $("#url").addEventListener("keydown", (e) => { if (e.key === "Enter") analyze($("#url").value); });
  $("#url").addEventListener("paste", () => setTimeout(() => analyze($("#url").value), 60));
  $("#rDownload").addEventListener("click", startDownload);
  $("#clearJobs").addEventListener("click", async () => { await api.post("/api/jobs/clear"); lastJobState = ""; refreshJobs(); });
  $("#openDir").addEventListener("click", () => api.post("/api/files/open", { action: "reveal" }));
  $("#settingsBtn").addEventListener("click", openSettings);
  $("#sSave").addEventListener("click", saveSettings);
  $("#sClose").addEventListener("click", () => $("#settings").classList.add("hidden"));
  $("#useClip").addEventListener("click", () => {
    const u = $("#clipHint").dataset.url;
    $("#clipHint").classList.add("hidden");
    $("#url").value = u;
    analyze(u);
  });

  // The browser extension just opens /?url=... — no CORS needed.
  const q = new URLSearchParams(location.search);
  const urlParam = q.get("url") || q.get("u");
  if (urlParam) {
    $("#url").value = urlParam;
    analyze(urlParam);
    history.replaceState({}, "", location.pathname);
  }
});
