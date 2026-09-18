/*
 * GrabBox background service worker (Manifest V3).
 *
 * - Toolbar icon stays FADED until a content script reports downloadable media
 *   on a tab, then it lights up and shows a count badge.
 * - Right-click "Grab with GrabBox" on any link / video / audio / image.
 * - Grabbing just opens the local app with ?url=... so the user picks quality.
 */
"use strict";

const API = chrome.runtime;
let serverUrl = "http://127.0.0.1:8765";

chrome.storage.local.get({ server: serverUrl }, (s) => {
  serverUrl = s.server;
});

const ICONS_OFF = { 16: "icons/icon-faded-16.png", 32: "icons/icon-faded-32.png", 48: "icons/icon-faded-48.png", 128: "icons/icon-faded-128.png" };
const ICONS_ON = { 16: "icons/icon-16.png", 32: "icons/icon-32.png", 48: "icons/icon-48.png", 128: "icons/icon-128.png" };

/* ------------------------------------------------------------- context menu */
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "grab-link", title: "Grab this link with GrabBox",
      contexts: ["link"],
    });
    chrome.contextMenus.create({
      id: "grab-media", title: "Grab with GrabBox",
      contexts: ["video", "audio", "image"],
    });
    chrome.contextMenus.create({
      id: "grab-page", title: "Grab this page with GrabBox",
      contexts: ["page"],
    });
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  let url = null;
  if (info.menuItemId === "grab-link") url = info.linkUrl;
  else if (info.menuItemId === "grab-media") url = info.srcUrl;
  else if (info.menuItemId === "grab-page") url = info.pageUrl || (tab && tab.url);
  if (url) grab(url);
});

/* --------------------------------------------------------- content messages */
API.onMessage.addListener((msg, sender, sendResponse) => {
  const tabId = sender.tab && sender.tab.id;

  if (msg.type === "media-count" && tabId != null) {
    setTabState(tabId, msg.count | 0);
    sendResponse({ ok: true });
    return;
  }
  if (msg.type === "grab") {
    grab(msg.url);
    sendResponse({ ok: true });
    return;
  }
  if (msg.type === "health") {
    checkHealth().then((h) => sendResponse(h));
    return true; // async response
  }
  if (msg.type === "get-server") {
    sendResponse({ server: serverUrl });
    return;
  }
  if (msg.type === "set-server") {
    serverUrl = msg.server || serverUrl;
    chrome.storage.local.set({ server: serverUrl });
    sendResponse({ ok: true });
    return;
  }
});

function setTabState(tabId, count) {
  const on = count > 0;
  chrome.action.setIcon({ tabId, path: on ? ICONS_ON : ICONS_OFF }).catch(() => {});
  if (on) chrome.action.setBadgeText({ tabId, text: String(count) });
  else chrome.action.setBadgeText({ tabId, text: "" });
}

/* Reset the icon when a tab goes away. */
chrome.tabs.onRemoved.addListener((tabId) => setTabStateSilent(tabId));
chrome.tabs.onUpdated.addListener((tabId, change) => {
  if (change.status === "loading") setTabState(tabId, 0);
});
function setTabStateSilent(tabId) { /* icon state is per-tab; nothing stored */ }

/* ----------------------------------------------------------------- grabbing */
function grab(url) {
  if (!url) return;
  // Open the app with the link pre-analyzed; the user then chooses quality.
  chrome.tabs.create({ url: serverUrl.replace(/\/$/, "") + "/?url=" + encodeURIComponent(url) });
}

async function checkHealth() {
  try {
    const res = await fetch(serverUrl + "/api/health");
    return await res.json();
  } catch (e) {
    return { ok: false, error: "GrabBox app is not running on " + serverUrl };
  }
}
