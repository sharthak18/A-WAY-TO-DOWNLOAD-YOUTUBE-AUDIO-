"use strict";

const $ = (s) => document.querySelector(s);
const ICON = { video: "🎬", audio: "🎵", image: "🖼️", file: "⬇️" };

let server = "http://127.0.0.1:8765";

function openGrab(url) {
  chrome.runtime.sendMessage({ type: "grab", url });
  window.close();
}

function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function init() {
  const s = await chrome.runtime.sendMessage({ type: "get-server" });
  server = (s && s.server) || server;
  $("#server").value = server;

  const h = await chrome.runtime.sendMessage({ type: "health" });
  const pill = $("#health");
  if (h && h.ytdlp) {
    pill.textContent = "ready · yt-dlp " + h.ytdlp;
    pill.className = "pill ok";
  } else {
    pill.textContent = "app offline";
    pill.className = "pill bad";
  }

  // Detected downloadable items on the active tab.
  let tabId = null;
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tabs.length) tabId = tabs[0].id;
  let items = [];
  if (tabId != null) {
    try {
      const res = await chrome.tabs.sendMessage(tabId, { type: "list" });
      items = (res && res.items) || [];
    } catch (e) { /* no content script on this tab */ }
  }
  $("#none").style.display = items.length ? "none" : "block";
  $("#items").innerHTML = items.slice(0, 30).map((it) =>
    `<div class="item"><span class="k">${ICON[it.kind] || "⬇️"}</span>` +
    `<span class="t" title="${esc(it.url)}">${esc(it.label || it.url)}</span>` +
    `<button data-url="${esc(it.url)}">grab</button></div>`).join("");
  $("#items").querySelectorAll("button[data-url]").forEach((b) =>
    b.addEventListener("click", () => openGrab(b.dataset.url)));

  $("#grab").addEventListener("click", () => {
    const u = $("#url").value.trim();
    if (u) openGrab(u);
  });
  $("#url").addEventListener("keydown", (e) => {
    if (e.key === "Enter" && $("#url").value.trim()) openGrab($("#url").value.trim());
  });
  $("#open").addEventListener("click", () => {
    chrome.tabs.create({ url: server });
    window.close();
  });
  $("#server").addEventListener("change", () => {
    const v = $("#server").value.trim().replace(/\/$/, "");
    if (v) {
      chrome.runtime.sendMessage({ type: "set-server", server: v });
      server = v;
    }
  });
}

init();
