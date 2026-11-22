/* ============================================================
   progress.js — progress tracking with JWT authenticated sync.
   Stores state per lesson id in localStorage, and automatically
   syncs with the YAOGUAI backend database for logged-in users.
   ============================================================ */

const GUEST_PROGRESS_KEY = "yaoguai:crypto:guest:v1";
let progressRevision = 0;

function getStore() {
  try { return JSON.parse(sessionStorage.getItem(GUEST_PROGRESS_KEY)) || {}; }
  catch (e) { return {}; }
}

function setStore(obj) {
  progressRevision++;
  try { sessionStorage.setItem(GUEST_PROGRESS_KEY, JSON.stringify(obj)); } catch (_) {}
}

const Progress = {
  /** status: "locked" | "available" | "in_progress" | "done" */
  getLesson(id) {
    const store = getStore();
    return store[id] || { status: "available", sections: {}, challenge: false, pct: 0 };
  },
  setSectionSeen(id, sectionId) {
    const store = getStore();
    const entry = store[id] || { status: "available", sections: {}, challenge: false, pct: 0 };
    entry.sections = entry.sections || {};
    entry.sections[sectionId] = true;
    if (entry.status !== "done") entry.status = "in_progress";
    store[id] = entry;
    setStore(store);
  },
  setChallengeSolved(id) {
    const store = getStore();
    const entry = store[id] || { status: "in_progress", sections: {}, challenge: false, pct: 0 };
    entry.challenge = true;
    store[id] = entry;
    setStore(store);
  },
  markComplete(id, totalSections) {
    const store = getStore();
    const entry = store[id] || { status: "in_progress", sections: {}, challenge: false, pct: 0 };
    entry.status = "done";
    entry.pct = 100;
    store[id] = entry;
    setStore(store);
  },
  computePct(id, totalSections) {
    const entry = this.getLesson(id);
    if (entry.status === "done") return 100;
    const seen = Object.keys(entry.sections || {}).length;
    return totalSections ? Math.round((seen / totalSections) * 100) : 0;
  },
  overall(allIds) {
    const store = getStore();
    const done = allIds.filter((id) => (store[id] || {}).status === "done").length;
    return { done, total: allIds.length };
  },
  syncFromServer(serverProgress, userId) {
    if (!window.YaoguaiAccountUser || String(userId) !== String(window.YaoguaiAccountUser.id)) return;
    if (!serverProgress || typeof serverProgress !== "object" || Array.isArray(serverProgress)) return;
    // Replace, never merge account data with an unidentified browser cache.
    try { sessionStorage.setItem(GUEST_PROGRESS_KEY, JSON.stringify(serverProgress)); } catch (_) {}
    window.dispatchEvent(new CustomEvent("yaoguai:progress-synced"));
  },
  async loadFromServer() {
    try {
      if (!window.YaoguaiAccountUser) return;
      const response = await fetch('/api/progress', { credentials: 'same-origin' });
      const payload = await response.json();
      const activities = payload.data?.platforms?.find((platform) => platform.id === 'crypto')?.modules?.flatMap((module) => module.activities) || [];
      const state = {};
      for (const activity of activities) {
        const key = activity.id.replace(/^crypto\//, '');
        if (activity.completed) state[key] = { status: 'done', sections: {}, challenge: false, pct: 100 };
        else if (activity.started) state[key] = { status: 'in_progress', sections: {}, challenge: false, pct: 20 };
      }
      try { sessionStorage.setItem(GUEST_PROGRESS_KEY, JSON.stringify(state)); } catch (_) {}
      window.dispatchEvent(new CustomEvent('yaoguai:progress-synced'));
    } catch (_) {}
  },
  reset() {
    progressRevision++;
    try { sessionStorage.removeItem(GUEST_PROGRESS_KEY); } catch (_) {}
    window.dispatchEvent(new CustomEvent("yaoguai:progress-synced"));
  },
};

window.Progress = Progress;

window.addEventListener("yaoguai:central-progress", event => {
  if (!window.YaoguaiAccountUser) return;
  const activities = event.detail?.platforms?.find(platform => platform.id === "crypto")?.modules?.flatMap(module => module.activities || []) || [];
  const state = {};
  for (const activity of activities) {
    const key = activity.id.replace(/^crypto\//, "");
    if (activity.completed) state[key] = { status: "done", sections: {}, challenge: false, pct: 100 };
    else if (activity.started) state[key] = { status: "in_progress", sections: {}, challenge: false, pct: 20 };
  }
  try { sessionStorage.setItem(GUEST_PROGRESS_KEY, JSON.stringify(state)); } catch (_) {}
  window.dispatchEvent(new CustomEvent("yaoguai:progress-synced"));
});

// Auto-sync on page load if logged in
if (typeof document !== "undefined") {
  document.addEventListener("DOMContentLoaded", () => {
    Progress.loadFromServer();
  });
}
