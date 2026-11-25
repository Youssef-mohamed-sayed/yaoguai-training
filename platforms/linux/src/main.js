import { marked } from 'marked';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js/lib/common';
import './style.css';

const STORE_KEY = 'yaoguai-linux:progress:v1';
const BASE_PATH = '/linux';
const icons = {
  menu: '<path d="M4 7h16M4 12h16M4 17h16"/>', close: '<path d="m6 6 12 12M18 6 6 18"/>', search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
  arrow: '<path d="M5 12h14m-7-7 7 7-7 7"/>', check: '<path d="m5 12 4 4L19 6"/>', book: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 1 4 17.5zM4 5.5v12M8 7h8M8 11h8"/>',
  terminal: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m7 9 3 3-3 3m6 0h4"/>', chevron: '<path d="m9 18 6-6-6-6"/>', home: '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-6v-7h-4v7H4a1 1 0 0 1-1-1z"/>',
  reset: '<path d="M3 12a9 9 0 1 0 2.64-6.36L3 8m0-5v5h5"/>',
};
const icon = (name, size = 18) => `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">${icons[name]}</svg>`;
const app = document.querySelector('#app');
let course;
let lessonIndex = [];
let activeModule = null;
let searchItems = [];
let drawerOpen = false;
let searchSelection = -1;
let readingListener = null;
let headingObserver = null;
let centralProgressSnapshot = null;

const readProgress = () => {
  try { return JSON.parse(sessionStorage.getItem(STORE_KEY)) || { completed: [], lastLesson: null }; }
  catch { return { completed: [], lastLesson: null }; }
};
let progress = readProgress();
window.addEventListener('yaoguai:central-progress', (event) => {
  centralProgressSnapshot = event.detail;
  syncCentralProgress();
  if (course) render();
});

function syncCentralProgress() {
  if (!window.YaoguaiAccountUser || !centralProgressSnapshot || !course) return;
  const platform = centralProgressSnapshot.platforms?.find((item) => item.id === 'linux');
  if (!platform) return;
  progress.completed = platform.modules.flatMap((module) => module.activities || [])
    .filter((activity) => activity.completed && activity.type === 'lesson')
    .map((activity) => activity.id.replace(/^linux\//, ''));
  const last = centralProgressSnapshot.last_activity?.id;
  if (last?.startsWith('linux/')) progress.lastLesson = last.replace(/^linux\//, '').replace(/\/exercise\/[^/]+$/, '');
  saveProgress();
}
const saveProgress = () => {
  try { sessionStorage.setItem(STORE_KEY, JSON.stringify(progress)); } catch { /* Browser storage can be unavailable in private modes. */ }
};
const completeCount = (module) => (module?.lessons || lessonIndex).filter((lesson) => progress.completed.includes(lesson.slug)).length;
const percent = (done, total) => total ? Math.round(done / total * 100) : 0;
const esc = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const titleCase = (value = '') => value.replace(/^\d+-/, '').replaceAll('-', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
const route = () => decodeURI(location.pathname).replace(/^\/linux(?=\/|$)/, '').replace(/\/$/, '') || '/';
const appPath = (path) => path === BASE_PATH || path.startsWith(`${BASE_PATH}/`) ? path : `${BASE_PATH}${path.startsWith('/') ? path : `/${path}`}`;
const lessonPath = (lesson) => `${BASE_PATH}/lesson/${lesson.slug}`;
const modulePath = (module) => `${BASE_PATH}/module/${module.id}`;
const findLesson = (slug) => lessonIndex.find((lesson) => lesson.slug === slug);
const findModule = (id) => course.modules.find((module) => module.id === id);
const textOnly = (text) => text.replace(/```[\s\S]*?```/g, ' ').replace(/`([^`]+)`/g, '$1').replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1').replace(/<[^>]*>/g, ' ').replace(/[#>*_|~\-]+/g, ' ').replace(/\s+/g, ' ').trim();

marked.setOptions({ gfm: true, breaks: false });

function progressSummary(module) {
  const done = completeCount(module);
  const total = module ? module.lessons.length : lessonIndex.length;
  return { done, total, pct: percent(done, total) };
}

function renderSidebar(currentLesson) {
  return `<aside class="sidebar ${drawerOpen ? 'is-open' : ''}" id="course-nav" aria-label="Course navigation">
    <div class="side-top"><span class="eyebrow">YOUR LEARNING PATH</span><button class="icon-button side-close" aria-label="Close navigation">${icon('close')}</button></div>
    <a class="side-home ${route() === '/' ? 'current' : ''}" href="/" data-link>${icon('home')}<span>Course dashboard</span></a>
    <a class="side-home ${route() === '/course' ? 'current' : ''}" href="/course" data-link>${icon('book')}<span>All modules</span><span class="side-count">${course.modules.length}</span></a>
    <div class="side-progress"><div class="side-progress-label"><span>COURSE PROGRESS</span><b>${progressSummary().pct}%</b></div><div class="progress-track"><i style="width:${progressSummary().pct}%"></i></div><small>${progressSummary().done} of ${progressSummary().total} lessons complete</small></div>
    <nav class="module-nav">${course.modules.map((module, index) => `<section class="nav-module ${currentLesson?.moduleId === module.id || activeModule === module.id ? 'expanded' : ''}">
      <button class="module-toggle" data-module-toggle="${esc(module.id)}" aria-expanded="${currentLesson?.moduleId === module.id || activeModule === module.id}"><span class="module-number">${String(index + 1).padStart(2, '0')}</span><span class="module-nav-title">${esc(module.title)}</span><span class="module-done">${completeCount(module)}/${module.lessons.length}</span></button>
      <div class="module-lessons">${module.lessons.map((lesson) => `<a href="${lessonPath(lesson)}" data-link class="lesson-nav-link ${currentLesson?.slug === lesson.slug ? 'current' : ''}" aria-current="${currentLesson?.slug === lesson.slug ? 'page' : 'false'}"><span class="lesson-state ${progress.completed.includes(lesson.slug) ? 'done' : ''}" aria-label="${progress.completed.includes(lesson.slug) ? 'Completed' : 'Not completed'}">${progress.completed.includes(lesson.slug) ? icon('check', 12) : ''}</span><span>${esc(lesson.title)}</span></a>`).join('')}</div>
    </section>`).join('')}</nav>
    <button class="reset-link" data-reset>${icon('reset')} Reset local progress</button>
  </aside>`;
}

function renderFrame(content, currentLesson = null) {
  app.innerHTML = `<header class="topbar"><button class="icon-button menu-button" aria-label="Open course navigation" aria-expanded="${drawerOpen}">${icon('menu')}</button><a class="brand" href="/" data-link><img src="/linux/assets/images/logo-emblem.png" alt="" width="36" height="36"><span class="brand-copy"><b>YAOGUAI</b><small>LINUX LEARNING PATH</small></span></a><nav class="top-links" aria-label="Main navigation"><a href="/" data-link class="${route() === '/' ? 'active' : ''}">Learn</a><a href="/course" data-link class="${route() === '/course' ? 'active' : ''}">Curriculum</a></nav><div class="top-tools"><label class="search-field">${icon('search')}<input id="course-search" type="search" placeholder="Search lessons…" autocomplete="off" aria-label="Search lessons"><kbd>⌘ K</kbd><div class="search-results" id="search-results" role="listbox" aria-label="Search results"></div></label><span class="top-progress"><i></i>${progressSummary().pct}%</span></div></header>
    <div class="app-layout">${renderSidebar(currentLesson)}<main id="main-content" tabindex="-1">${content}</main></div><div class="drawer-scrim ${drawerOpen ? 'visible' : ''}"></div><footer class="site-footer"><div class="footer-brand"><img src="/linux/assets/images/logo-emblem.png" alt="" width="28" height="28"><span>YAOGUAI <b>LINUX</b></span></div><p>Built for curious minds and careful operators.</p><a href="/" data-link>Yaoguai Training ${icon("arrow", 14)}</a></footer>`;
  bindFrame();
}

function moduleCard(module, index) {
  const summary = progressSummary(module);
  const next = module.lessons.find((lesson) => !progress.completed.includes(lesson.slug)) || module.lessons[0];
  const description = textOnly(module.description).replace(/^.*?\s/, '');
  return `<a class="module-card" href="${modulePath(module)}" data-link><div class="module-card-top"><span class="module-index">MODULE ${String(index + 1).padStart(2, '0')}</span><span class="module-card-status">${summary.done === summary.total ? `<span class="status-complete">${icon('check', 13)} COMPLETE</span>` : `${summary.total} LESSON${summary.total === 1 ? '' : 'S'}`}</span></div><h3>${esc(module.title)}</h3><p>${esc(description || `${module.lessons.length} lessons to build practical Linux skills.`)}</p><div class="card-progress"><div class="progress-track"><i style="width:${summary.pct}%"></i></div><span>${summary.pct}%</span></div><div class="card-bottom"><span>${summary.done} / ${summary.total} lessons</span><span class="card-arrow">${icon('arrow', 16)}</span></div></a>`;
}

function renderDashboard() {
  const summary = progressSummary();
  const last = findLesson(progress.lastLesson);
  const next = last && !progress.completed.includes(last.slug) ? last : lessonIndex.find((lesson) => !progress.completed.includes(lesson.slug));
  const continueLesson = next || lessonIndex.at(-1);
  const resumeTitle = summary.done === summary.total ? 'Course complete' : last ? 'Pick up where you left off' : 'Begin your Linux journey';
  const resumeCopy = summary.done === summary.total ? 'You have completed every lesson. Revisit any topic or reset your local progress to start again.' : last ? `Continue with ${esc(continueLesson.title)}` : 'A practical path from your first terminal command to hands-on labs.';
  const intro = course.overviewSections || {};
  const introHtml = DOMPurify.sanitize(marked.parse(intro.audience || ''), { USE_PROFILES: { html: true } });
  const outcomesHtml = DOMPurify.sanitize(marked.parse(intro.outcomes || ''), { USE_PROFILES: { html: true } });
  const setupHtml = DOMPurify.sanitize(marked.parse(intro.setup || ''), { USE_PROFILES: { html: true } });
  const referencesHtml = DOMPurify.sanitize(marked.parse(course.references || ''), { USE_PROFILES: { html: true } });
  return `<section class="dashboard-hero"><div class="hero-grid"></div><div class="hero-content"><div class="eyebrow"><span class="live-dot"></span> LINUX ESSENTIALS <span class="eyebrow-sep">/</span> FIELD GUIDE 01</div><h1>Find your footing.<br><em>Own the command line.</em></h1><p class="hero-description">${esc(course.description)}</p><div class="hero-actions"><a class="button primary" href="${lessonPath(continueLesson)}" data-link>${summary.done === summary.total ? 'Review lessons' : last ? 'Continue learning' : 'Start learning'} ${icon('arrow', 16)}</a><a class="button quiet" href="/course" data-link>Explore curriculum</a></div><div class="hero-stats"><div><b>${course.modules.length.toString().padStart(2, '0')}</b><span>modules</span></div><div><b>${lessonIndex.length.toString().padStart(2, '0')}</b><span>lessons</span></div><div><b>${summary.pct}<small>%</small></b><span>complete</span></div></div></div><div class="hero-seal"><img src="/linux/assets/images/logo-emblem.png" alt="Yaoguai emblem"><span>Yaoguai</span><small>LEARN · PRACTICE · REPEAT</small></div><div class="hero-coordinate">Course · TERMINAL STUDIES · 01</div></section>
  <section class="resume-section"><div class="resume-mark">${icon('terminal', 22)}</div><div class="resume-copy"><span class="eyebrow">${summary.done === summary.total ? 'NICE WORK' : last ? 'YOUR NEXT STEP' : 'READY WHEN YOU ARE'}</span><h2>${resumeTitle}</h2><p>${resumeCopy}</p></div><a class="resume-link" href="${lessonPath(continueLesson)}" data-link aria-label="${summary.done === summary.total ? 'Review lessons' : 'Continue learning'}">${icon('arrow', 20)}</a><div class="resume-meter"><div class="progress-track"><i style="width:${summary.pct}%"></i></div><span>${summary.done} / ${summary.total}</span></div></section>
  <section class="intro-panel"><div class="intro-copy"><span class="eyebrow">COURSE INTRODUCTION</span><h2>Linux is best learned hands-on.</h2><div class="markdown-body">${introHtml}</div></div><div class="outcome-copy"><span class="eyebrow">WHAT YOU'LL LEARN</span><div class="markdown-body">${outcomesHtml}</div></div></section><section class="resource-panel"><div class="resource-heading"><span class="eyebrow">KEEP THESE CLOSE</span><h2>Learning resources</h2></div><div class="resource-content markdown-body">${referencesHtml}</div><div class="setup-note"><span class="eyebrow">PRACTICE SETUP</span><div class="markdown-body">${setupHtml}</div></div></section>
  <section class="curriculum-section"><div class="section-heading"><div><span class="eyebrow">THE LEARNING PATH</span><h2>Course modules <small>${String(course.modules.length).padStart(2, '0')}</small></h2></div><a class="text-link" href="/course" data-link>View full curriculum ${icon('arrow', 15)}</a></div><div class="module-grid">${course.modules.map(moduleCard).join('')}</div></section>
  <section class="course-note"><span class="note-symbol">!</span><div><span class="eyebrow">A NOTE BEFORE YOU BEGIN</span><p>Practice in a safe environment. Read each command before running it, and follow the course's guidance on permissions, destructive operations, and authorized security labs.</p></div><a href="/course" data-link>How the course works ${icon('chevron', 15)}</a></section>`;
}

function renderCourse() {
  const summary = progressSummary();
  return `<div class="page-wrap overview-page"><div class="breadcrumb"><a href="/" data-link>Home</a>${icon('chevron', 13)}<span>Curriculum</span></div><header class="page-heading"><span class="eyebrow">THE COMPLETE LEARNING PATH</span><h1>Linux, from the ground up.</h1><p>${esc(course.description)}</p><div class="overview-progress"><div class="progress-track"><i style="width:${summary.pct}%"></i></div><span><b>${summary.pct}%</b> · ${summary.done} of ${summary.total} lessons complete</span></div></header><div class="module-grid overview-grid">${course.modules.map(moduleCard).join('')}</div></div>`;
}

function renderModule(module) {
  if (!module) return renderNotFound();
  activeModule = module.id;
  const summary = progressSummary(module);
  const contentHtml = DOMPurify.sanitize(marked.parse(module.description), { USE_PROFILES: { html: true } });
  const moduleIndex = course.modules.indexOf(module);
  const previous = course.modules[moduleIndex - 1];
  const next = course.modules[moduleIndex + 1];
  return `<div class="page-wrap module-page"><div class="breadcrumb"><a href="/" data-link>Home</a>${icon('chevron', 13)}<a href="/course" data-link>Curriculum</a>${icon('chevron', 13)}<span>${esc(module.title)}</span></div><header class="module-page-head"><span class="eyebrow">MODULE ${String(moduleIndex + 1).padStart(2, '0')} <span class="eyebrow-sep">/</span> ${summary.done} OF ${summary.total} COMPLETE</span><h1>${esc(module.title)}</h1><div class="module-description markdown-body">${contentHtml}</div><div class="module-progress"><div class="progress-track"><i style="width:${summary.pct}%"></i></div><span>${summary.pct}% complete</span></div></header><section class="module-lesson-list"><h2>Lessons <small>${String(module.lessons.length).padStart(2, '0')}</small></h2>${module.lessons.map((lesson, index) => `<a class="lesson-row" href="${lessonPath(lesson)}" data-link><span class="row-number">${String(index + 1).padStart(2, '0')}</span><span class="row-title"><b>${esc(lesson.title)}</b><small>${esc(module.title)}</small></span><span class="row-status ${progress.completed.includes(lesson.slug) ? 'complete' : ''}">${progress.completed.includes(lesson.slug) ? icon('check', 15) : icon('chevron', 17)}<span>${progress.completed.includes(lesson.slug) ? 'Completed' : 'Open lesson'}</span></span></a>`).join('')}</section><nav class="module-pager">${previous ? `<a href="${modulePath(previous)}" data-link>← ${esc(previous.title)}</a>` : '<span></span>'}${next ? `<a href="${modulePath(next)}" data-link>${esc(next.title)} →</a>` : '<a href="/course" data-link>Back to curriculum →</a>'}</nav></div>`;
}

function getHeadings(source) {
  const counts = new Map();
  return marked.lexer(source).filter((token) => token.type === 'heading').map((token) => {
    const text = token.text.replace(/<[^>]*>/g, '');
    const base = text.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, '').trim().replace(/\s+/g, '-') || 'section';
    const count = counts.get(base) || 0;
    counts.set(base, count + 1);
    return { depth: token.depth, text, id: `${base}${count ? `-${count}` : ''}` };
  });
}

function markdownHtml(lesson) {
  const toc = getHeadings(lesson.markdown).filter((heading, index) => !(index === 0 && heading.depth === 1 && heading.text.trim().toLowerCase() === lesson.title.trim().toLowerCase()));
  const counts = new Map();
  let firstHeading = true;
  const renderer = new marked.Renderer();
  renderer.heading = ({ text, depth }) => {
    const plain = text.replace(/<[^>]*>/g, '');
    const base = plain.toLowerCase().replace(/[^\p{L}\p{N}\s-]/gu, '').trim().replace(/\s+/g, '-') || 'section';
    const number = counts.get(base) || 0;
    counts.set(base, number + 1);
    const isPageTitle = firstHeading && depth === 1 && plain.trim().toLowerCase() === lesson.title.trim().toLowerCase();
    firstHeading = false;
    return `<h${depth} id="${base}${number ? `-${number}` : ''}"${isPageTitle ? ' class="source-title"' : ''}>${text}</h${depth}>\n`;
  };
  renderer.code = ({ text, lang }) => {
    const language = lang?.split(/[\s,]/)[0]?.toLowerCase();
    const grammar = language && hljs.getLanguage(language);
    const rendered = grammar ? hljs.highlight(text, { language, ignoreIllegals: true }).value : esc(text);
    return `<pre class="code-block"><div class="code-head"><span><i></i><i></i><i></i> ${esc(language || 'TEXT')}</span><button class="copy-code" type="button" aria-label="Copy code">${icon('terminal', 14)} Copy</button></div><code class="hljs ${grammar ? `language-${esc(language)}` : ''}">${rendered}</code></pre>`;
  };
  const rendered = DOMPurify.sanitize(marked.parse(lesson.markdown, { renderer }), { USE_PROFILES: { html: true }, ADD_ATTR: ['id', 'class', 'target', 'rel'] });
  return { html: rendered, toc };
}

function renderLesson(lesson) {
  if (!lesson) return renderNotFound();
  progress.lastLesson = lesson.slug;
  saveProgress();
  activeModule = lesson.moduleId;
  const module = findModule(lesson.moduleId);
  const index = lessonIndex.indexOf(lesson);
  const previous = lessonIndex[index - 1];
  const next = lessonIndex[index + 1];
  const complete = progress.completed.includes(lesson.slug);
  const { html, toc } = markdownHtml(lesson);
  return `<div class="lesson-layout"><article class="lesson-article"><div class="breadcrumb"><a href="/" data-link>Home</a>${icon('chevron', 13)}<a href="${modulePath(module)}" data-link>${esc(module.title)}</a>${icon('chevron', 13)}<span>Lesson ${String(index + 1).padStart(2, '0')}</span></div><header class="lesson-heading"><span class="eyebrow">${esc(module.title)} <span class="eyebrow-sep">/</span> LESSON ${String(module.lessons.indexOf(lesson) + 1).padStart(2, '0')}</span><h1>${esc(lesson.title)}</h1><div class="lesson-meta"><span>${lesson.markdown.trim().split(/\s+/).length} words</span><span class="meta-dot"></span><span>${Math.max(1, Math.round(lesson.markdown.trim().split(/\s+/).length / 220))} min read</span><span class="meta-dot"></span><span class="lesson-state ${complete ? 'done' : ''}">${complete ? icon('check', 12) : ''}</span><span>${complete ? 'Completed' : 'In progress'}</span></div></header><div class="reading-progress"><i></i></div><div class="markdown-body lesson-content">${html}</div><div class="lesson-complete-box ${complete ? 'is-complete' : ''}"><span class="complete-icon">${icon('check', 16)}</span><div><b>${complete ? 'Lesson completed' : 'Finished reading?'}</b><p>${complete ? 'This lesson is marked complete in your learning path.' : 'Mark this lesson complete to track it in your course progress.'}</p></div><button class="button ${complete ? 'quiet' : 'primary'}" type="button" data-complete-lesson ${complete ? 'disabled' : ''}>${complete ? 'Completed' : 'Mark complete'}</button></div><nav class="lesson-pager">${previous ? `<a href="${lessonPath(previous)}" data-link><small>← PREVIOUS LESSON</small><span>${esc(previous.title)}</span></a>` : `<a href="${modulePath(module)}" data-link><small>← BACK TO MODULE</small><span>${esc(module.title)}</span></a>`}${next ? `<a class="next" href="${lessonPath(next)}" data-link><small>NEXT LESSON →</small><span>${esc(next.title)}</span></a>` : `<a class="next" href="${modulePath(module)}" data-link><small>MODULE COMPLETE →</small><span>Review ${esc(module.title)}</span></a>`}</nav></article><aside class="lesson-rail"><div class="rail-sticky"><div class="toc-title"><span class="eyebrow">IN THIS LESSON</span><button class="icon-button toc-toggle" aria-label="Toggle table of contents">${icon('menu', 16)}</button></div><nav class="toc-list" aria-label="Table of contents">${toc.map((heading) => `<a href="#${esc(heading.id)}" class="toc-link level-${heading.depth}">${esc(heading.text)}</a>`).join('')}</nav><a class="rail-module" href="${modulePath(module)}" data-link><span class="eyebrow">CURRENT MODULE</span><b>${esc(module.title)}</b><span>${completeCount(module)} / ${module.lessons.length} lessons complete</span><div class="progress-track"><i style="width:${progressSummary(module).pct}%"></i></div></a><span class="rail-index">${String(index + 1).padStart(2, '0')} <i>/</i> ${String(lessonIndex.length).padStart(2, '0')}</span></div></aside></div>`;
}

function renderNotFound() {
  return `<div class="page-wrap not-found"><span class="eyebrow">404 · PATH NOT FOUND</span><h1>This page isn't on the map.</h1><p>The course content may have moved, or the link may be out of date.</p><a class="button primary" href="/course" data-link>Browse the curriculum ${icon('arrow', 16)}</a></div>`;
}

function render() {
  if (readingListener) { window.removeEventListener('scroll', readingListener); readingListener = null; }
  if (headingObserver) { headingObserver.disconnect(); headingObserver = null; }
  const current = route();
  const lessonRoute = current.match(/^\/lesson\/(.+)$/);
  window.dispatchEvent(new CustomEvent('yaoguai:route', { detail: { activityId: lessonRoute ? `linux/${lessonRoute[1]}` : '' } }));
  const match = current.match(/^\/lesson\/(.+)$/);
  const moduleMatch = current.match(/^\/module\/(.+)$/);
  let content;
  let lesson = null;
  if (match) { lesson = findLesson(match[1]); content = renderLesson(lesson); }
  else if (moduleMatch) content = renderModule(findModule(moduleMatch[1]));
  else if (current === '/course') content = renderCourse();
  else if (current === '/') content = renderDashboard();
  else content = renderNotFound();
  renderFrame(content, lesson);
  if (match && lesson) setupLessonInteractions(lesson);
  window.scrollTo({ top: 0, behavior: 'instant' });
}

function navigate(href) {
  href = appPath(href);
  if (location.pathname !== href) history.pushState({}, '', href);
  drawerOpen = false;
  render();
}

function bindFrame() {
  app.querySelectorAll('[data-link]').forEach((anchor) => {
    const url = new URL(anchor.href, location.href);
    if (url.origin === location.origin && !url.pathname.startsWith(`${BASE_PATH}/`) && url.pathname !== BASE_PATH) {
      anchor.href = appPath(`${url.pathname}${url.search}${url.hash}`);
    }
  });
  app.querySelectorAll('[data-link]').forEach((anchor) => anchor.addEventListener('click', (event) => {
    const url = new URL(anchor.href, location.href);
    if (url.origin !== location.origin || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(url.pathname + url.search + url.hash);
  }));
  app.querySelector('.menu-button').addEventListener('click', () => { drawerOpen = !drawerOpen; render(); });
  app.querySelector('.side-close').addEventListener('click', () => { drawerOpen = false; render(); });
  app.querySelector('.drawer-scrim').addEventListener('click', () => { drawerOpen = false; render(); });
  app.querySelectorAll('[data-module-toggle]').forEach((button) => button.addEventListener('click', () => {
    activeModule = activeModule === button.dataset.moduleToggle ? null : button.dataset.moduleToggle;
    button.closest('.nav-module').classList.toggle('expanded');
    button.setAttribute('aria-expanded', String(button.closest('.nav-module').classList.contains('expanded')));
  }));
  const moduleMatch = route().match(/^\/module\/(.+)$/);
  if (moduleMatch) {
    const module = findModule(moduleMatch[1]);
    app.querySelectorAll('.module-description a').forEach((anchor) => resolveLessonLink(anchor, module.lessons[0]));
  }
  app.querySelectorAll('.markdown-body a').forEach((anchor) => {
    if (/^https?:/i.test(anchor.getAttribute('href') || '')) { anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; }
  });
  app.querySelector('[data-reset]').addEventListener('click', () => {
    if (!confirm('Reset lesson progress for this browser session? This cannot be undone.')) return;
    progress = { completed: [], lastLesson: null };
    saveProgress();
    render();
  });
  const input = app.querySelector('#course-search');
  input.addEventListener('input', () => showSearch(input.value));
  input.addEventListener('keydown', (event) => {
    const results = app.querySelectorAll('.search-result');
    if (event.key === 'ArrowDown') { event.preventDefault(); searchSelection = Math.min(searchSelection + 1, results.length - 1); focusSearchResult(results); }
    else if (event.key === 'ArrowUp') { event.preventDefault(); searchSelection = Math.max(searchSelection - 1, 0); focusSearchResult(results); }
    else if (event.key === 'Enter' && searchSelection >= 0 && results[searchSelection]) results[searchSelection].click();
    else if (event.key === 'Escape') { input.value = ''; showSearch(''); input.blur(); }
  });
  document.addEventListener('click', closeSearchOnOutside, { once: true });
}

function closeSearchOnOutside(event) {
  if (!event.target.closest('.search-field')) {
    const results = app.querySelector('#search-results');
    if (results) results.classList.remove('open');
  }
  document.addEventListener('click', closeSearchOnOutside, { once: true });
}

function focusSearchResult(results) {
  results.forEach((result, index) => result.classList.toggle('selected', index === searchSelection));
  results[searchSelection]?.scrollIntoView({ block: 'nearest' });
}

function showSearch(value) {
  const panel = app.querySelector('#search-results');
  const query = value.trim().toLowerCase();
  searchSelection = -1;
  if (!query) { panel.innerHTML = ''; panel.classList.remove('open'); return; }
  const terms = query.split(/\s+/).filter(Boolean);
  const found = searchItems.map((item) => {
    const heading = item.headings.find((candidate) => terms.some((term) => candidate.text.toLowerCase().includes(term)));
    return { ...item, heading: heading?.text, score: terms.reduce((score, term) => score + (item.title.toLowerCase().includes(term) ? 5 : 0) + (item.module.toLowerCase().includes(term) ? 3 : 0) + (item.headings.some((candidate) => candidate.text.toLowerCase().includes(term)) ? 2 : 0) + (item.content.toLowerCase().includes(term) ? 1 : 0), 0) };
  })
    .filter((item) => item.score && terms.every((term) => `${item.title} ${item.module} ${item.headings.map((heading) => heading.text).join(' ')} ${item.content}`.toLowerCase().includes(term)))
    .sort((a, b) => b.score - a.score).slice(0, 8);
  panel.innerHTML = found.length ? `<span class="search-label">${found.length} MATCH${found.length === 1 ? '' : 'ES'}</span>${found.map((item) => `<a class="search-result" role="option" href="${lessonPath(item.lesson)}" data-search-link><span class="search-result-icon">${icon('book', 16)}</span><span><b>${esc(item.lesson.title)}</b><small>${esc(item.module)} · ${esc(item.heading || 'Lesson content')}</small></span>${icon('arrow', 14)}</a>`).join('')}` : `<div class="search-empty"><b>No lessons found</b><span>Try a command, concept, or module name.</span></div>`;
  panel.classList.add('open');
  panel.querySelectorAll('[data-search-link]').forEach((link) => link.addEventListener('click', (event) => {
    event.preventDefault(); navigate(link.getAttribute('href'));
  }));
}

function setupLessonInteractions(lesson) {
  const completeButton = app.querySelector('[data-complete-lesson]');
  if (completeButton && !progress.completed.includes(lesson.slug)) {
    completeButton.addEventListener('click', async () => {
      completeButton.disabled = true;
      completeButton.textContent = 'Saving…';
      let saved = true;
      if (window.YaoguaiAccountUser && window.YaoguaiTraining) {
        saved = await window.YaoguaiTraining.complete(`linux/${lesson.slug}`).catch(() => false);
      }
      if (saved) {
        if (!progress.completed.includes(lesson.slug)) progress.completed.push(lesson.slug);
        saveProgress();
        render();
      } else {
        completeButton.disabled = false;
        completeButton.textContent = 'Mark complete';
      }
    });
  }
  const content = app.querySelector('.lesson-content');
  const tocLinks = [...app.querySelectorAll('.toc-link')];
  content.querySelectorAll('a').forEach((anchor) => resolveLessonLink(anchor, lesson));
  content.querySelectorAll('img').forEach((image) => resolveAsset(image, lesson));
  content.querySelectorAll('blockquote').forEach((quote) => {
    const first = quote.querySelector('p');
    const note = first?.textContent.match(/^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*/i);
    if (note) { quote.classList.add('callout', `callout-${note[1].toLowerCase()}`); first.textContent = first.textContent.replace(/^\[![^\]]+\]\s*/i, ''); }
  });
  content.querySelectorAll('pre.code-block').forEach((pre) => {
    const button = pre.querySelector('.copy-code');
    button.addEventListener('click', async () => {
      let copied = false;
      const code = pre.querySelector('code').textContent;
      try {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
        await navigator.clipboard.writeText(code);
        copied = true;
      } catch {
        const field = document.createElement('textarea');
        field.value = code;
        field.setAttribute('readonly', '');
        field.style.position = 'fixed';
        field.style.opacity = '0';
        document.body.append(field);
        field.select();
        try { copied = document.execCommand('copy'); } catch { copied = false; }
        field.remove();
      }
      button.textContent = copied ? 'Copied' : 'Copy unavailable';
      setTimeout(() => { button.innerHTML = `${icon('terminal', 14)} Copy`; }, 1400);
    });
  });
  content.querySelectorAll('table').forEach((table) => { const wrapper = document.createElement('div'); wrapper.className = 'table-scroll'; table.before(wrapper); wrapper.append(table); });
  content.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => { checkbox.disabled = true; });
  app.querySelector('.toc-toggle').addEventListener('click', () => app.querySelector('.toc-list').classList.toggle('toc-open'));
  tocLinks.forEach((link) => link.addEventListener('click', (event) => {
    event.preventDefault();
    const target = document.getElementById(decodeURIComponent(link.hash.slice(1)));
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.replaceState({}, '', `${location.pathname}${location.search}${link.hash}`);
  }));
  const observed = [...content.querySelectorAll('h1[id],h2[id],h3[id],h4[id]')];
  if ('IntersectionObserver' in window) {
    headingObserver = new IntersectionObserver((entries) => entries.forEach((entry) => {
      if (entry.isIntersecting) tocLinks.forEach((link) => link.classList.toggle('active', link.hash === `#${entry.target.id}`));
    }), { rootMargin: '-15% 0px -75% 0px' });
    observed.forEach((heading) => headingObserver.observe(heading));
  }
  const updateReading = () => {
    const bounds = content.getBoundingClientRect();
    const available = content.scrollHeight - window.innerHeight * .55;
    const read = Math.max(0, Math.min(100, (-bounds.top + window.innerHeight * .4) / Math.max(available, 1) * 100));
    app.querySelector('.reading-progress i').style.width = `${read}%`;
  };
  readingListener = updateReading;
  window.addEventListener('scroll', readingListener, { passive: true });
  updateReading();
  if (location.hash) setTimeout(() => document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView(), 50);
}

function resolveLessonLink(anchor, lesson) {
  const raw = anchor.getAttribute('href') || '';
  if (raw.startsWith('#')) return;
  if (/^(https?:|mailto:)/i.test(raw)) { anchor.target = '_blank'; anchor.rel = 'noopener noreferrer'; return; }
  if (/^(javascript|data|file):/i.test(raw) || raw.startsWith('//')) { anchor.removeAttribute('href'); return; }
  let resolved;
  try { resolved = new URL(raw, `https://course.local/${lesson.id}`); } catch { anchor.removeAttribute('href'); return; }
  let relative;
  try { relative = decodeURIComponent(resolved.pathname.replace(/^\//, '')); }
  catch { anchor.removeAttribute('href'); return; }
  const target = findLesson(relative.replace(/\.md$/i, '')) || findLesson(relative);
  const moduleId = relative.match(/^([^/]+)\/(?:README\.md)?$/i)?.[1];
  if (target) anchor.href = lessonPath(target);
  else if (moduleId && findModule(moduleId)) anchor.href = modulePath(findModule(moduleId));
  else if (course.assets.includes(relative)) { anchor.href = `${BASE_PATH}/course-assets/${relative}`; return; }
  else { anchor.href = '/course'; anchor.title = 'Browse the course curriculum'; }
  anchor.dataset.link = '';
  anchor.addEventListener('click', (event) => {
    if (anchor.hash || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    navigate(new URL(anchor.href, location.href).pathname);
  });
}

function resolveAsset(image, lesson) {
  const raw = image.getAttribute('src') || '';
  if (/^(https?:|data:image\/)/i.test(raw)) return;
  try {
    const path = decodeURIComponent(new URL(raw, `https://course.local/${lesson.id}`).pathname.replace(/^\//, ''));
    if (course.assets.includes(path)) image.src = `${BASE_PATH}/course-assets/${path}`;
    else image.remove();
  } catch { image.remove(); }
}

function initShortcuts() {
  document.addEventListener('keydown', (event) => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); app.querySelector('#course-search')?.focus(); }
    if (event.key === 'Escape' && drawerOpen) { drawerOpen = false; render(); }
  });
  window.addEventListener('popstate', () => { drawerOpen = false; render(); });
}

async function init() {
  try {
  const response = await fetch(`${BASE_PATH}/course-data.json`);
    if (!response.ok) throw new Error(`Course index returned ${response.status}`);
    course = await response.json();
    syncCentralProgress();
    lessonIndex = course.modules.flatMap((module) => module.lessons);
    searchItems = lessonIndex.map((lesson) => {
      const module = findModule(lesson.moduleId);
      const headings = getHeadings(lesson.markdown);
      return { lesson, module: module.title, headings, title: lesson.title, content: `${lesson.title} ${module.title} ${textOnly(lesson.markdown)}` };
    });
    render();
    initShortcuts();
  } catch (error) {
    console.error(error);
    app.innerHTML = `<main class="load-error"><img src="/brand/logo-oni-face.svg" alt="" width="84"><span class="eyebrow">COURSE CONTENT UNAVAILABLE</span><h1>We couldn't load the learning path.</h1><p>${esc(error.message)}. Rebuild the course index and refresh this page.</p></main>`;
  }
}

init();
