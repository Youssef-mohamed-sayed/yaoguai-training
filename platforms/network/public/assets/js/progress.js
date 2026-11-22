const key = "yaoguai:network:progress:v1";
const blank = () => ({ last: null, lessons: {} });
let fallback = blank();

function read() {
  try {
    const data = JSON.parse(sessionStorage.getItem(key));
    return data && data.lessons && typeof data.lessons === "object" ? data : fallback;
  } catch {
    return fallback;
  }
}

function update(change) {
  const data = read();
  change(data);
  fallback = data;
  try {
    sessionStorage.setItem(key, JSON.stringify(data));
  } catch {
    // Keep the current page usable if this browsing mode blocks storage.
  }
  window.dispatchEvent(new Event("yaoguai-progress"));
}

function lesson(data, url) {
  return data.lessons[url] ??= { done: false, exercises: {}, challenges: {} };
}

export const progress = {
  read,
  visit(url) {
    update(data => {
      data.last = url;
      lesson(data, url).started = true;
    });
  },
  toggleLesson(url) {
    update(data => {
      const entry = lesson(data, url);
      if (window.YaoguaiAccountUser && entry.done) return;
      entry.done = !entry.done;
    });
  },
  activity(url, id, kind, toggle = false) {
    update(data => {
      const entry = lesson(data, url);
      const activities = kind === "challenge" ? entry.challenges : entry.exercises;
      if (toggle && activities[id]) delete activities[id];
      else activities[id] = true;
    });
  },
};

window.addEventListener("yaoguai:central-progress", event => {
  if (!window.YaoguaiAccountUser) return;
  const activities = event.detail?.platforms?.find(platform => platform.id === "network")?.modules?.flatMap(module => module.activities || []) || [];
  update(data => {
    data.lessons = {};
    const last = event.detail?.last_activity?.id;
    if (last?.startsWith("network/")) data.last = "/network/" + last.replace(/^network\//, "").replace(/\/exercise\/[^/]+$/, "");
    for (const activity of activities) {
      if (activity.type === "exercise" || activity.type === "challenge" || activity.type === "quiz") {
        const match = activity.id.match(/^network\/(.+)\/exercise\/([^/]+)$/);
        if (match) lesson(data, "/network/" + match[1]).exercises[match[2]] = activity.completed;
      } else {
        const url = "/network/" + activity.id.replace(/^network\//, "");
        if (activity.completed || activity.started) {
          const entry = lesson(data, url);
          entry.done = Boolean(activity.completed);
          entry.started = Boolean(activity.started);
        }
      }
    }
  });
});

window.addEventListener("storage", event => {
  if (event.key === key || event.key === null) {
    fallback = blank();
    window.dispatchEvent(new Event("yaoguai-progress"));
  }
});
