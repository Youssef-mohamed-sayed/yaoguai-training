/* ============================================================
   dashboard.js — renders the three category grids on index.html
   from the registry + localStorage progress.
   ============================================================ */

function diffClass(d){ return d.toLowerCase().replace(/\s+/g,"-"); }

function cardHTML(c, idx){
  const entry = Progress.getLesson(c.id);
  const pct = entry.status === "done" ? 100 : (entry.status === "in_progress" ? Math.max(entry.pct, 20) : 0);
  const statusDot = entry.status === "done" ? "done" : (entry.status === "in_progress" ? "active" : "");
  const statusLabel = entry.status === "done" ? "completed" : (entry.status === "in_progress" ? "in progress" : "not started");
  const href = c.implemented ? `lessons/${c.id}.html` : `lessons/stub.html?id=${c.id}`;
  const locked = !c.implemented ? "locked" : "";
  return `
  <a class="card ${locked}" href="${href}" style="display:block;">
    <div class="card-top">
      <span class="card-id">${String(c.order).padStart(2,"0")}</span>
      <span class="badge ${diffClass(c.difficulty)}">${c.difficulty}</span>
    </div>
    <h3>${c.title}</h3>
    <div class="cat">${c.native}${c.implemented ? "" : " · drafting"}</div>
    <p style="font-size:13.5px;color:var(--paper-dim);margin:0 0 6px;min-height:40px;">${c.summary}</p>
    <div class="bar"><i style="--p:${pct}%"></i></div>
    <div class="card-foot">
      <span class="card-status"><span class="dot ${statusDot}"></span>${statusLabel}</span>
      <span class="card-link">${c.implemented ? "Open →" : "Preview →"}</span>
    </div>
  </a>`;
}

function renderCategory(cat, mountId){
  const items = courseByCategory(cat);
  document.getElementById(mountId).innerHTML = items.map(cardHTML).join("");
}

function renderDashboard() {
  renderCategory("encoding", "grid-encoding");
  renderCategory("encryption", "grid-encryption");
  renderCategory("hashing", "grid-hashing");

  const implementedIds = courseOrdered().filter(c => c.implemented).map(c => c.id);
  const { done, total } = Progress.overall(implementedIds);
  const chip = document.querySelector(".progress-chip");
  if (chip) chip.textContent = `${done}/${total} modules complete`;

  const continueBtn = document.getElementById("continue-btn");
  if (continueBtn){
    const last = window.YaoguaiTraining?.snapshot?.last_activity?.id;
    const lastId = last?.startsWith("crypto/") ? last.replace(/^crypto\//, "").replace(/\/exercise\/[^/]+$/, "") : "";
    const resumed = courseById(lastId);
    const firstUnfinished = courseOrdered().find(c => c.implemented && Progress.getLesson(c.id).status !== "done");
    const target = (resumed?.implemented && Progress.getLesson(resumed.id).status !== "done" ? resumed : null) || firstUnfinished || courseOrdered().find(c => c.implemented);
    if (target) continueBtn.href = `lessons/${target.id}.html`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderDashboard();
  // Re-render cards & chip when progress syncs from server after login
  window.addEventListener("yaoguai:progress-synced", () => renderDashboard());
});
