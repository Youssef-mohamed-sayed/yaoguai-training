/* ============================================================
   lesson-boot.js — wires a static lesson HTML page together:
   builds the left TOC from .lsec[data-title] elements, does
   scrollspy, fills prev/next from the registry, and restores
   the topbar progress chip. Runs after the lesson body is
   already in the DOM (lessons are plain static HTML per page).
   ============================================================ */

function buildTOC(){
  const secs = document.querySelectorAll(".lsec");
  const ol = document.querySelector(".lesson-toc ol");
  if (!ol) return;
  secs.forEach(sec => {
    const title = sec.dataset.title || sec.querySelector("h2")?.textContent || sec.id;
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "#" + sec.id;
    a.textContent = title;
    a.dataset.target = sec.id;
    li.appendChild(a);
    ol.appendChild(li);
  });
}

function scrollSpy(){
  const links = document.querySelectorAll(".lesson-toc a");
  const secs = document.querySelectorAll(".lsec");
  if (!secs.length) return;
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting){
        links.forEach(l => l.classList.remove("current"));
        const link = document.querySelector(`.lesson-toc a[data-target="${e.target.id}"]`);
        if (link) link.classList.add("current");
      }
    });
  }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });
  secs.forEach(s => io.observe(s));
}

function buildPrevNext(){
  const lessonId = document.body.dataset.lesson;
  if (!lessonId || typeof neighbours !== "function") return;
  const { prev, next } = neighbours(lessonId);
  const prevEl = document.getElementById("nav-prev");
  const nextEl = document.getElementById("nav-next");
  if (prev && prevEl){
    prevEl.href = prev.implemented ? `${prev.id}.html` : `../lessons/stub.html?id=${prev.id}`;
    prevEl.querySelector(".ttl").textContent = prev.title;
    prevEl.style.visibility = "visible";
  } else if (prevEl){ prevEl.style.visibility = "hidden"; }
  if (next && nextEl){
    nextEl.href = next.implemented ? `${next.id}.html` : `../lessons/stub.html?id=${next.id}`;
    nextEl.querySelector(".ttl").textContent = next.title;
    nextEl.style.visibility = "visible";
  } else if (nextEl){ nextEl.style.visibility = "hidden"; }
}

function bootTopbarChip(){
  const chip = document.querySelector(".progress-chip");
  if (!chip) return;
  if (document.body.dataset.lesson){
    updateProgressUI();
  } else {
    const all = courseOrdered().filter(c => c.implemented).map(c => c.id);
    const { done, total } = Progress.overall(all);
    chip.textContent = `${done}/${total} modules complete`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  buildTOC();
  scrollSpy();
  buildPrevNext();
  bootTopbarChip();
  // Re-run chip update after progress syncs from server
  window.addEventListener("yaoguai:progress-synced", () => {
    bootTopbarChip();
    if (typeof updateProgressUI === "function") updateProgressUI();
  });
});
