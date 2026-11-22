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
      lesson(data, url);
    });
  },
  toggleLesson(url) {
    update(data => {
      const entry = lesson(data, url);
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

window.addEventListener("storage", event => {
  if (event.key === key || event.key === null) {
    fallback = blank();
    window.dispatchEvent(new Event("yaoguai-progress"));
  }
});
