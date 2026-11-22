export function bindActivities(page, progress) {
  for (const button of document.querySelectorAll("[data-review]")) {
    button.hidden = false;
    button.addEventListener("click", () => progress.activity(page, button.dataset.review, "exercise", true));
  }
  for (const form of document.querySelectorAll("[data-grade]")) {
    form.hidden = false;
    form.addEventListener("submit", async event => {
      event.preventDefault();
      const activity = form.dataset.grade;
      const isFlag = form.dataset.kind === "challenge";
      const button = form.querySelector("button");
      const feedback = form.querySelector("[role=status]");
      const fields = [...new FormData(form)];
      button.disabled = true;
      feedback.className = "task-fb show";
      feedback.textContent = "Checking…";
      for (const control of form.querySelectorAll("[aria-invalid]")) control.removeAttribute("aria-invalid");
      try {
        const csrfResponse = await fetch("/api/auth/csrf", { credentials: "same-origin" });
        const csrfBody = await csrfResponse.json();
        const response = await fetch("/network/check", {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json", ...(csrfBody.data?.csrf_token ? { "X-CSRFToken": csrfBody.data.csrf_token } : {}) },
          body: JSON.stringify({ page, activity, answers: fields.map(([, value]) => value) }),
        });
        const result = await response.json();
        if (!response.ok) {
          feedback.textContent = result.error || "This answer could not be checked.";
          feedback.classList.add("bad");
          return;
        }
        if (result.correct) {
          window.dispatchEvent(new Event("yaoguai:network-check-complete"));
          if (isFlag) {
            feedback.textContent = "Flag accepted. Challenge solved.";
          } else {
            feedback.textContent = "Correct. Open Check Your Answer for the explanation.";
          }
          progress.activity(page, activity, form.dataset.kind);
        } else {
          feedback.textContent = isFlag ? "Flag not accepted. Check the format and try again."
            : `${result.fields.filter(Boolean).length}/${fields.length} correct. Review the highlighted answers and try again.`;
          result.fields.forEach((correct, index) => {
            if (!correct) {
              for (const control of form.querySelectorAll("input")) {
                if (control.name === fields[index][0]) control.setAttribute("aria-invalid", "true");
              }
            }
          });
        }
        feedback.classList.add(result.correct ? "ok" : "bad");
      } catch {
        feedback.textContent = "The answer check is unavailable. Try again in a moment.";
        feedback.classList.add("bad");
      } finally {
        button.disabled = false;
      }
    });
  }
}
