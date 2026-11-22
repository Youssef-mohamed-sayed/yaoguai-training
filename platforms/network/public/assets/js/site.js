import { progress } from "./progress.js";
import { bindActivities } from "./activities.js";

const current = document.body.dataset.current;
const catalog = document.getElementById("course-pages").content;
const pages = [...catalog.querySelectorAll("[data-url]")].map(node => node.dataset);
const menu = document.querySelector("[data-course-menu]");
const compact = matchMedia("(max-width: 920px)");

function setMenu(event) {
  if (menu) menu.open = !event.matches;
}

setMenu(compact);
compact.addEventListener("change", setMenu);

function update() {
  const state = progress.read();
  const done = pages.filter(page => state.lessons[page.url]?.done).length;
  document.querySelector("[data-progress-count]").textContent = `${done}/${pages.length} complete`;

  const resume = document.querySelector("[data-resume]");
  const last = pages.find(page => page.url === state.last);
  if (resume && last) {
    resume.href = last.url;
    resume.textContent = "Resume: " + last.title;
  }
  for (const card of document.querySelectorAll("[data-module-card]")) {
    const group = pages.filter(page => page.module === card.dataset.moduleCard);
    const completed = group.filter(page => state.lessons[page.url]?.done).length;
    card.querySelector("progress").value = completed;
    card.querySelector("[data-module-count]").textContent = `${completed}/${group.length} complete`;
    card.dataset.completed = String(Boolean(group.length && completed === group.length));
    card.dataset.started = String(group.some(page => state.lessons[page.url]) && card.dataset.completed !== "true");
  }
  for (const mark of document.querySelectorAll("[data-status-for]")) {
    const url = mark.dataset.statusFor;
    const entry = state.lessons[url];
    mark.dataset.done = String(Boolean(entry?.done));
    mark.textContent = url === current ? "→" : entry?.done ? "✓" : "○";
    const link = mark.closest("a");
    const oldStatus = link.querySelector(".sr-only");
    const status = oldStatus ?? document.createElement("span");
    status.className = "sr-only";
    status.textContent = entry?.done ? "Completed" : "Incomplete";
    if (!oldStatus) link.append(status);
  }
  if (!current) return;
  const lesson = state.lessons[current];
  const complete = document.querySelector("[data-complete]");
  complete.textContent = lesson?.done ? "✓ Complete · undo" : "Mark complete";
  complete.setAttribute("aria-pressed", String(Boolean(lesson?.done)));
  for (const button of document.querySelectorAll("[data-review]")) {
    button.dataset.label ??= button.textContent;
    const reviewed = Boolean(lesson?.exercises?.[button.dataset.review]);
    button.setAttribute("aria-pressed", String(reviewed));
    button.textContent = reviewed ? "✓ Practiced · undo" : button.dataset.label;
  }
  for (const form of document.querySelectorAll("[data-grade]")) {
    const isFlag = form.dataset.kind === "challenge";
    const saved = lesson?.[isFlag ? "challenges" : "exercises"]?.[form.dataset.grade];
    form.querySelector("button").textContent = saved
      ? (isFlag ? "✓ Flag solved · retry" : "✓ Answer checked · retry")
      : (isFlag ? "Submit flag" : "Check answer");
  }
}

for (const button of document.querySelectorAll("[data-copy]")) {
  button.hidden = false;
  let timeout;
  button.addEventListener("click", async () => {
    const code = button.closest(".terminal").querySelector("pre code");
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = "Copied";
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      button.textContent = "Selected · copy";
    }
    clearTimeout(timeout);
    timeout = setTimeout(() => { button.textContent = "Copy"; }, 1800);
  });
}

window.addEventListener("yaoguai-progress", update);
if (current) {
  bindActivities(current, progress);
  document.querySelector("[data-completion]").hidden = false;
  document.querySelector("[data-complete]").addEventListener("click", () => progress.toggleLesson(current));
  progress.visit(current);
} else {
  update();
}
