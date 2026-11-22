/* ============================================================
   interactions.js — small generic helpers the lesson HTML calls
   directly (onclick="...") so every lesson can define its own
   tasks without a heavy templating layer. Kept dependency-free.
   ============================================================ */

function _norm(s){ return (s || "").trim().toLowerCase().replace(/\s+/g, ""); }

async function _checkAuth(actionDesc) {
  if (window.YaoguaiTraining?.ready) await window.YaoguaiTraining.ready;
  if (window.AuthUI && !window.AuthUI.isLoggedIn()) {
    window.AuthUI.promptAuth(actionDesc || "Please log in or create an account to interact with lesson tasks and track progress.");
    return false;
  }
  return true;
}

/** Text / fill-blank / predict-output / decode tasks.
 *  btn: the Check button. expected: string or array of acceptable answers.
 *  inputSelector: CSS selector (relative to the task) for the input/textarea. */
async function checkTask(btn, expected, inputSelector){
  if (!await _checkAuth("Please log in or create an account to solve interactive tasks and record your course progress.")) {
    return;
  }

  const task = btn.closest(".task");
  const input = task.querySelector(inputSelector || "input, textarea");
  const fb = task.querySelector(".task-fb");
  const given = _norm(input.value);
  const list = Array.isArray(expected) ? expected.map(_norm) : [_norm(expected)];
  const correct = list.includes(given);
  fb.textContent = correct
    ? (fb.dataset.ok || "Correct — that's exactly right.")
    : (fb.dataset.bad || "Not quite. Check the example above and try again.");
  fb.classList.remove("ok","bad");
  fb.classList.add("show", correct ? "ok" : "bad");
  if (correct){
    const lessonId = document.body.dataset.lesson;
    const sectionId = task.closest(".lsec")?.id;
    if (lessonId && sectionId) Progress.setSectionSeen(lessonId, sectionId);
    updateProgressUI();
    await _completeIfTasksSolved();
  }
}

/** Multiple choice tasks. optEl: the clicked .mc-opt div. correctId: dataset id of right option. */
async function pickMC(optEl, correctId){
  if (!await _checkAuth("Please log in or create an account to answer multiple choice tasks and earn progress.")) {
    return;
  }

  const task = optEl.closest(".task");
  task.querySelectorAll(".mc-opt").forEach(o => o.classList.remove("picked"));
  optEl.classList.add("picked");
  const fb = task.querySelector(".task-fb");
  const correct = optEl.dataset.id === correctId;
  fb.textContent = correct
    ? (fb.dataset.ok || "Correct.")
    : (fb.dataset.bad || "Not this one — look again.");
  fb.classList.remove("ok","bad");
  fb.classList.add("show", correct ? "ok" : "bad");
  if (correct){
    const lessonId = document.body.dataset.lesson;
    const sectionId = task.closest(".lsec")?.id;
    if (lessonId && sectionId) Progress.setSectionSeen(lessonId, sectionId);
    updateProgressUI();
    await _completeIfTasksSolved();
  }
}

/** CTF flag submission. */
async function checkFlag(btn, expectedFlag){
  if (!await _checkAuth("Please log in or create an account to submit CTF challenge flags and earn completion.")) {
    return;
  }

  const card = btn.closest(".ctf");
  const input = card.querySelector(".ctf-flag input");
  const fb = card.querySelector(".task-fb") || card.querySelector(".ctf-fb");
  const given = input.value.trim();
  const correct = given === expectedFlag;
  if (fb){
    fb.textContent = correct ? "Flag accepted. Challenge solved." : "Wrong flag — check your working and try again.";
    fb.classList.remove("ok","bad");
    fb.classList.add("show", correct ? "ok" : "bad");
  }
  if (correct){
    const lessonId = document.body.dataset.lesson;
    if (lessonId) Progress.setChallengeSolved(lessonId);
    updateProgressUI();
    input.style.borderColor = "var(--ok)";
    await _completeIfTasksSolved();
  }
}

async function _completeIfTasksSolved(){
  const feedback = [...document.querySelectorAll(".task .task-fb, .ctf .task-fb, .ctf .ctf-fb")];
  if (!feedback.length || feedback.some(item => !item.classList.contains("ok"))) return;
  const lessonId = document.body.dataset.lesson;
  if (!lessonId) return;
  if (window.YaoguaiAccountUser && window.YaoguaiTraining) {
    const activityId = `crypto/${lessonId}`;
    if (!window.YaoguaiTraining.isComplete(activityId)) await window.YaoguaiTraining.complete(activityId);
  } else {
    Progress.markComplete(lessonId);
  }
  updateProgressUI();
}

function updateProgressUI(){
  const lessonId = document.body.dataset.lesson;
  if (!lessonId) return;
  const totalSections = document.querySelectorAll(".lsec").length;
  const pct = Progress.computePct(lessonId, totalSections);
  const chip = document.querySelector(".progress-chip");
  if (chip) chip.textContent = `progress: ${pct}%`;
}
