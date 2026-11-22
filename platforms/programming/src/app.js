import MarkdownIt from 'markdown-it';
import DOMPurify from 'dompurify';
import hljs from 'highlight.js/lib/core';
import python from 'highlight.js/lib/languages/python';
import bash from 'highlight.js/lib/languages/bash';
import json from 'highlight.js/lib/languages/json';
import javascript from 'highlight.js/lib/languages/javascript';
import xml from 'highlight.js/lib/languages/xml';
import plaintext from 'highlight.js/lib/languages/plaintext';

for (const [name, language] of Object.entries({ python, py: python, bash, sh: bash, shell: bash, powershell: bash, json, javascript, js: javascript, html: xml, xml, text: plaintext, plaintext })) hljs.registerLanguage(name, language);

const STORAGE_KEY = 'yaoguai:programming-progress:v1';
const BASE_PATH = '/programming';
const app = document.querySelector('#app');
const md = new MarkdownIt({ html: true, linkify: true, typographer: false, highlight(code, language) {
  const normalized = (language || '').toLowerCase();
  if (normalized && hljs.getLanguage(normalized)) return hljs.highlight(code, { language: normalized }).value;
  return hljs.highlightAuto(code).value;
} });
DOMPurify.addHook('afterSanitizeAttributes', node => {
  if (node.nodeName === 'A' && node.getAttribute('target') === '_blank') node.setAttribute('rel', 'noopener noreferrer');
});
let course;
let searchFocusIndex = -1;
let searchResults = [];
let pendingQuery = '';
let centralProgress = null;
window.addEventListener('yaoguai:central-progress', (event) => {
  centralProgress = event.detail;
  const last = centralProgress?.last_activity?.id;
  if (window.YaoguaiAccountUser && last?.startsWith('programming/')) {
    const current = readProgress();
    current.lastLesson = last.replace(/^programming\//, '').replace(/\/exercise\/[^/]+$/, '');
    writeProgress(current);
  }
  if (course) renderRoute();
});

function readProgress() {
  try {
    const stored = JSON.parse(sessionStorage.getItem(STORAGE_KEY) || '{}');
    return { completedLessons: Array.isArray(stored.completedLessons) ? stored.completedLessons : [], lastLesson: typeof stored.lastLesson === 'string' ? stored.lastLesson : '', lastModule: typeof stored.lastModule === 'string' ? stored.lastModule : '' };
  } catch { return { completedLessons: [], lastLesson: '', lastModule: '' }; }
}
function writeProgress(next) {
  try { sessionStorage.setItem(STORAGE_KEY, JSON.stringify(next)); } catch { /* Browser storage can be disabled. */ }
  updateProgressChip();
  window.dispatchEvent(new CustomEvent('yaoguai:progress-changed'));
}
function flatLessons() { return course.modules.flatMap(module => module.lessons.map(lesson => ({ ...lesson, moduleId: module.id, moduleTitle: module.title }))); }
function stats() {
  const completed = new Set(readProgress().completedLessons);
  const done = flatLessons().filter(lesson => completed.has(lesson.id)).length;
  return { done, total: course.totalLessons, percent: course.totalLessons ? Math.round(done / course.totalLessons * 100) : 0 };
}
function updateProgressChip() {
  if (!course) return;
  const { done, total } = stats();
  const chip = document.querySelector('#progress-chip');
  if (!chip) return;
  chip.textContent = matchMedia('(max-width: 430px)').matches ? `${done}/${total} done` : `${done}/${total} lessons complete`;
  chip.title = `${done} of ${total} lessons complete`;
}
function isComplete(id) {
  if (window.YaoguaiAccountUser && centralProgress) {
    return Boolean(centralProgress.platforms?.find(p => p.id === 'programming')?.modules
      .flatMap(module => module.activities || []).find(activity => activity.id === `programming/${id}`)?.completed);
  }
  return readProgress().completedLessons.includes(id);
}
function encodeRoute(route) { return route.split('/').map(encodeURIComponent).join('/'); }
function appPath(path) { return path === BASE_PATH || path.startsWith(`${BASE_PATH}/`) ? path : `${BASE_PATH}${path.startsWith('/') ? path : `/${path}`}`; }
function go(path, { replace = false } = {}) {
  path = appPath(path);
  if (replace) history.replaceState({}, '', path); else history.pushState({}, '', path);
  closeDrawer();
  renderRoute();
  if (location.hash) requestAnimationFrame(() => document.getElementById(decodeURIComponent(location.hash.slice(1)))?.scrollIntoView({ behavior: 'smooth' }));
  else window.scrollTo({ top: 0, behavior: 'instant' });
}
function lessonUrl(id) { return `${BASE_PATH}/lesson/${encodeRoute(id)}`; }
function moduleUrl(id) { return `${BASE_PATH}/module/${encodeURIComponent(id)}`; }
function activeRoute() {
  const pathname = decodeURI(location.pathname).replace(/^\/programming(?=\/|$)/, '') || '/';
  if (pathname.startsWith('/lesson/')) return { type: 'lesson', id: pathname.slice('/lesson/'.length).replace(/\/$/, '') };
  if (pathname.startsWith('/module/')) return { type: 'module', id: decodeURIComponent(pathname.slice('/module/'.length).replace(/\/$/, '')) };
  if (pathname.startsWith('/resources')) return { type: 'resources' };
  if (pathname.startsWith('/search')) return { type: 'search', query: new URLSearchParams(location.search).get('q') || pendingQuery };
  return { type: 'home' };
}
function slug(text) { return text.toLocaleLowerCase().replace(/[`*_~]/g, '').normalize('NFKD').replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '') || 'section'; }
function sourcePathFor(page) { return page.sourcePath || 'README.md'; }
function resolveLocalTarget(target, sourceFile) {
  const trimmed = target.trim();
  if (!trimmed || /^(?:[a-z]+:|\/\/|#|mailto:|tel:)/i.test(trimmed)) return trimmed;
  const [rawPath, ...hashParts] = trimmed.split('#');
  const hash = hashParts.length ? `#${hashParts.join('#')}` : '';
  if (!rawPath) return hash;
  const normalized = pathResolve(sourceFile, rawPath).toLowerCase();
  if (/\.md$/i.test(rawPath)) {
    const lessonId = course.lessonBySourcePath[normalized];
    if (lessonId) return `${lessonUrl(lessonId)}${hash}`;
    const moduleId = course.moduleByReadmePath[normalized];
    if (moduleId) return `${moduleUrl(moduleId)}${hash}`;
    if (normalized === 'readme.md') return `${BASE_PATH}/${hash}`;
    if (course.documents[normalized]) return `${BASE_PATH}/resources?doc=${encodeURIComponent(normalized)}${hash}`;
  }
  const asset = course.assets[normalized];
  if (asset) return `${BASE_PATH}${asset}${hash}`;
  return trimmed;
}
function pathResolve(base, rel) {
  const stack = base.split('/').slice(0, -1);
  for (const part of rel.replace(/\\/g, '/').split('/')) {
    if (!part || part === '.') continue;
    if (part === '..') stack.pop(); else stack.push(part);
  }
  return stack.join('/');
}
function renderMarkdown(raw, sourceFile = 'README.md') {
  const oldLink = md.renderer.rules.link_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
  const oldImage = md.renderer.rules.image || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
  const oldHeading = md.renderer.rules.heading_open || ((tokens, idx, options, env, self) => self.renderToken(tokens, idx, options));
  md.renderer.rules.link_open = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    const href = token.attrGet('href');
    if (href) token.attrSet('href', resolveLocalTarget(href, sourceFile));
    const resolved = token.attrGet('href') || '';
    if (/^https?:\/\//i.test(resolved)) { token.attrSet('target', '_blank'); token.attrSet('rel', 'noopener noreferrer'); token.attrSet('class', `${token.attrGet('class') || ''} external-link`.trim()); }
    if (resolved.startsWith(`${BASE_PATH}/lesson/`) || resolved.startsWith(`${BASE_PATH}/module/`) || resolved.startsWith(`${BASE_PATH}/`)) token.attrSet('data-app-link', 'true');
    return oldLink(tokens, idx, options, env, self);
  };
  md.renderer.rules.image = (tokens, idx, options, env, self) => {
    const token = tokens[idx];
    const src = token.attrGet('src');
    if (src) token.attrSet('src', resolveLocalTarget(src, sourceFile));
    if (!token.attrGet('alt')) token.attrSet('alt', 'Course illustration');
    return oldImage(tokens, idx, options, env, self);
  };
  md.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
    const inline = tokens[idx + 1];
    tokens[idx].attrSet('id', slug(inline?.content || 'section'));
    tokens[idx].attrSet('tabindex', '-1');
    return oldHeading(tokens, idx, options, env, self);
  };
  md.renderer.rules.fence = (tokens, idx) => {
    const token = tokens[idx];
    const lang = (token.info || '').trim().split(/\s+/)[0] || 'text';
    const code = token.content;
    const language = lang.toLowerCase();
    const highlighted = token.info && hljs.getLanguage(language) ? hljs.highlight(code, { language }).value : escapeHtml(code).replace(/\n$/, '');
    return `<div class="code-panel"><div class="code-toolbar"><span class="code-language">${escapeHtml(lang)}</span><button class="copy-button" type="button" data-copy="${encodeURIComponent(code)}" aria-label="Copy ${escapeHtml(lang)} example">Copy</button></div><pre><code class="hljs language-${escapeHtml(lang)}">${highlighted}</code></pre></div>`;
  };
  md.core.ruler.push('course_heading_ids', state => {
    for (const token of state.tokens) {
      if (token.type !== 'heading_open') continue;
      const inline = state.tokens[state.tokens.indexOf(token) + 1];
      const label = inline?.content || 'section';
      token.attrSet('id', slug(label));
      token.attrSet('tabindex', '-1');
    }
  });
  const rendered = md.render(raw);
  md.renderer.rules.link_open = oldLink;
  md.renderer.rules.image = oldImage;
  md.renderer.rules.heading_open = oldHeading;
  md.renderer.rules.fence = undefined;
  return DOMPurify.sanitize(rendered, { ADD_ATTR: ['target', 'rel', 'data-app-link', 'tabindex', 'id', 'class'], ADD_TAGS: ['details', 'summary', 'input'] });
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]); }
function routeLink(label, href, className = '') { return `<a class="${className}" href="${href.startsWith('#') ? href : appPath(href)}" data-app-link="true">${label}</a>`; }
function progressBar(value, label) { return `<div class="progress-track" role="progressbar" aria-label="${escapeHtml(label)}" aria-valuenow="${value}" aria-valuemin="0" aria-valuemax="100"><span style="width:${value}%"></span></div>`; }
function courseSidebar(activeLesson = '', activeModule = '') {
  return `<aside class="course-sidebar" id="course-sidebar"><div class="sidebar-label">YOUR LEARNING PATH</div>${course.modules.map(module => {
    const finished = module.lessons.filter(lesson => isComplete(lesson.id)).length;
    return `<section class="sidebar-module ${activeModule === module.id ? 'expanded' : ''}"><a class="sidebar-module-link ${activeModule === module.id ? 'active' : ''}" href="${moduleUrl(module.id)}" data-app-link="true"><span class="module-index">${String(module.order).padStart(2, '0')}</span><span class="sidebar-module-name">${escapeHtml(module.title)}</span><span class="sidebar-count">${finished}/${module.lessons.length}</span></a>${activeModule === module.id || activeLesson ? `<div class="sidebar-lessons">${module.lessons.map(lesson => `<a class="sidebar-lesson ${activeLesson === lesson.id ? 'active' : ''} ${isComplete(lesson.id) ? 'is-done' : ''}" href="${lessonUrl(lesson.id)}" data-app-link="true"><span class="lesson-state" aria-label="${isComplete(lesson.id) ? 'Completed' : 'Not completed'}">${isComplete(lesson.id) ? '✓' : '·'}</span>${escapeHtml(lesson.title)}</a>`).join('')}</div>` : ''}</section>`;
  }).join('')}<button class="text-button reset-button" id="reset-progress">Reset local progress</button></aside>`;
}
function bindCommon() {
  document.querySelectorAll('.prose img').forEach(image => image.addEventListener('error', () => {
    const fallback = document.createElement('div');
    fallback.className = 'missing-asset';
    fallback.textContent = `Image unavailable: ${image.alt || 'course image'}`;
    image.replaceWith(fallback);
  }, { once: true }));
  document.querySelectorAll('[data-app-link="true"]').forEach(anchor => anchor.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const url = new URL(anchor.href, location.href);
    if (url.origin !== location.origin) return;
    event.preventDefault();
    go(`${url.pathname}${url.search}${url.hash}`);
  }));
  document.querySelector('#reset-progress')?.addEventListener('click', () => {
    if (!confirm('Reset lesson progress for this browser session? This cannot be undone.')) return;
    writeProgress({ completedLessons: [], lastLesson: '', lastModule: '' });
    renderRoute();
  });
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const code = decodeURIComponent(button.dataset.copy);
    try { await navigator.clipboard.writeText(code); button.textContent = 'Copied'; }
    catch { button.textContent = 'Select code'; }
    setTimeout(() => { button.textContent = 'Copy'; }, 1400);
  }));
}
function homePage() {
  const { done, total, percent } = stats();
  const progress = readProgress();
  const lessons = flatLessons();
  let continueLesson = lessons.find(lesson => lesson.id === progress.lastLesson && !isComplete(lesson.id));
  if (!continueLesson) continueLesson = lessons.find(lesson => !isComplete(lesson.id));
  if (!continueLesson) continueLesson = lessons[0];
  const firstModule = course.modules[0];
  app.innerHTML = `<main><section class="hero"><div class="hero-lines" aria-hidden="true"></div><div class="hero-content wrap"><div class="eyebrow"><span class="eyebrow-rule"></span> YAOGUAI LEARNING / PYTHON 3</div><h1>Turn curiosity<br>into <em>working code.</em></h1><p class="hero-lede">A practical path from your first Python statement to useful scripts for files, networks, and security analysis.</p><div class="hero-actions">${routeLink(done ? 'Continue learning <span aria-hidden="true">→</span>' : 'Begin the course <span aria-hidden="true">→</span>', lessonUrl(continueLesson.id), 'button button-primary')}${routeLink('Explore course path', '#course-path', 'button button-outline')}</div><div class="hero-footnote"><span class="status-pip"></span> NO ACCOUNT REQUIRED <span class="foot-separator">/</span> PROGRESS SAVED FOR THIS SESSION</div><div class="hero-sigil" aria-hidden="true">Y</div></div></section><section class="wrap dashboard"><div class="overview-grid"><div><div class="section-kicker">THE TRAINING GROUND</div><h2>Python, from first principles.</h2><p class="body-copy">${escapeHtml(course.modules.length)} modules. ${escapeHtml(total)} lessons. One clear progression into practical programming, debugging, and safe cybersecurity automation.</p><div class="learning-outcomes">${routeLink('Read the course overview', '/resources#course-overview', 'inline-link')}<span class="muted">·</span>${routeLink('Browse learning resources', '/resources', 'inline-link')}</div></div><div class="progress-card"><div class="card-label">YOUR COURSE PROGRESS</div><div class="progress-number">${percent}<span>%</span></div>${progressBar(percent, 'Overall course progress')}<div class="progress-caption"><span>${done} of ${total} lessons complete</span><span>${course.modules.length} modules</span></div>${done === total && total ? '<div class="completion-note">Course complete. Keep building.</div>' : ''}</div></div><div class="section-heading" id="course-path"><div><div class="section-kicker">THE LEARNING PATH</div><h2>Choose your next step.</h2></div><span class="section-count">${String(course.modules.length).padStart(2, '0')} MODULES</span></div><div class="module-grid">${course.modules.map(module => {
    const moduleDone = module.lessons.filter(lesson => isComplete(lesson.id)).length;
    const pct = module.lessons.length ? Math.round(moduleDone / module.lessons.length * 100) : 0;
    const next = module.lessons.find(lesson => !isComplete(lesson.id)) || module.lessons[0];
    return `<a class="module-card" href="${moduleUrl(module.id)}" data-app-link="true"><div class="module-card-top"><span class="module-index">${String(module.order).padStart(2, '0')}</span><span class="module-completion">${pct === 100 ? 'COMPLETE' : `${moduleDone}/${module.lessons.length} LESSONS`}</span></div><h3>${escapeHtml(module.title)}</h3><p>${escapeHtml(module.description.replace(/^\*\*[^*]+\*\*\s*/, '').split(/\n/)[0] || 'Explore the lessons in this module.')}</p>${progressBar(pct, `${module.title} progress`)}<div class="module-card-bottom"><span>${module.lessons.length} lessons</span><span>Open module <b aria-hidden="true">↗</b></span></div><span class="sr-only">Start with ${escapeHtml(next.title)}</span></a>`;
  }).join('')}</div></section></main>`;
  bindCommon();
}
function modulePage(module) {
  const done = module.lessons.filter(lesson => isComplete(lesson.id)).length;
  const pct = module.lessons.length ? Math.round(done / module.lessons.length * 100) : 0;
  const first = module.lessons.find(lesson => !isComplete(lesson.id)) || module.lessons[0];
  app.innerHTML = `<main class="wrap page-wrap"><div class="breadcrumb">${routeLink('Course', '/', '')}<span>/</span><span>${escapeHtml(module.title)}</span></div><div class="module-page-head"><div class="section-kicker">MODULE ${String(module.order).padStart(2, '0')} / ${String(course.modules.length).padStart(2, '0')}</div><h1>${escapeHtml(module.title)}</h1><div class="module-description prose">${renderMarkdown(module.description, module.sourcePath)}</div><div class="module-progress-row"><div>${progressBar(pct, `${module.title} progress`)}</div><span>${done} / ${module.lessons.length} complete</span></div>${routeLink(isComplete(first.id) ? 'Review first lesson →' : done ? 'Continue module →' : 'Start this module →', lessonUrl(first.id), 'button button-primary')}</div><div class="lesson-list">${module.lessons.map((lesson, index) => `<a class="lesson-list-item" href="${lessonUrl(lesson.id)}" data-app-link="true"><span class="lesson-list-number">${String(index + 1).padStart(2, '0')}</span><span class="lesson-list-title">${escapeHtml(lesson.title)}<small>${isComplete(lesson.id) ? 'Completed' : 'Lesson'}</small></span><span class="lesson-list-state ${isComplete(lesson.id) ? 'done' : ''}" aria-label="${isComplete(lesson.id) ? 'Completed' : 'Not completed'}">${isComplete(lesson.id) ? '✓' : '→'}</span></a>`).join('')}</div>${moduleNavigation(module)}</main>`;
  const guide = document.createElement('details');
  guide.className = 'module-guide';
  guide.innerHTML = `<summary>Module guide, objectives, and practice notes</summary><div class="prose">${renderMarkdown(module.readme, module.sourcePath)}</div>`;
  app.querySelector('.lesson-list').after(guide);
  bindCommon();
}
function moduleNavigation(module) {
  const index = course.modules.indexOf(module);
  const previous = course.modules[index - 1];
  const next = course.modules[index + 1];
  return `<div class="module-pagination">${previous ? routeLink(`← ${escapeHtml(previous.title)}`, moduleUrl(previous.id), 'inline-link') : '<span></span>'}${next ? routeLink(`${escapeHtml(next.title)} →`, moduleUrl(next.id), 'inline-link') : '<span></span>'}</div>`;
}
function lessonPage(lesson) {
  const all = flatLessons();
  const index = all.findIndex(item => item.id === lesson.id);
  const previous = all[index - 1];
  const next = all[index + 1];
  const module = course.modules.find(item => item.id === lesson.moduleId);
  const headings = course.headings[lesson.id] || [];
  const checked = isComplete(lesson.id);
  const progress = readProgress();
  progress.lastLesson = lesson.id;
  progress.lastModule = module.id;
  writeProgress(progress);
  app.innerHTML = `<main class="lesson-layout">${courseSidebar(lesson.id, module.id)}<article class="lesson-article"><div class="lesson-topline">${routeLink(`MODULE ${String(module.order).padStart(2, '0')}`, moduleUrl(module.id), 'lesson-module-link')}<span>/</span><span>${escapeHtml(module.title)}</span></div><header class="lesson-header"><div class="lesson-number">LESSON ${String(lesson.order).padStart(2, '0')} <span>·</span> ${module.lessons.length} IN MODULE</div><h1>${escapeHtml(lesson.title)}</h1><div class="lesson-meta"><span class="completion-pill ${checked ? 'completed' : ''}"><span class="completion-symbol">${checked ? '✓' : '○'}</span> ${checked ? 'COMPLETED' : 'IN YOUR LEARNING PATH'}</span><span>${escapeHtml(module.title)}</span></div></header><nav class="mobile-toc" aria-label="On this page"><label for="toc-select">ON THIS PAGE</label><select id="toc-select"><option value="">Jump to section…</option>${headings.map(heading => `<option value="${slug(heading.title)}">${escapeHtml(heading.title)}</option>`).join('')}</select></nav><div class="lesson-prose prose">${renderMarkdown(lesson.content, lesson.sourcePath)}</div><nav class="lesson-pagination" aria-label="Lesson navigation">${previous ? routeLink(`<span class="pagination-label">← PREVIOUS</span><strong>${escapeHtml(previous.title)}</strong>`, lessonUrl(previous.id), 'pagination-card') : '<div></div>'}${next ? routeLink(`<span class="pagination-label">NEXT LESSON →</span><strong>${escapeHtml(next.title)}</strong>`, lessonUrl(next.id), 'pagination-card next') : moduleNavigation(module)}</nav></article><aside class="lesson-toc"><div class="toc-title">ON THIS PAGE</div><nav>${headings.map(heading => `<a class="toc-link depth-${heading.level}" href="#${slug(heading.title)}">${escapeHtml(heading.title)}</a>`).join('')}</nav><div class="toc-module-progress"><span>MODULE PROGRESS</span><strong>${module.lessons.filter(item => isComplete(item.id)).length} / ${module.lessons.length}</strong>${progressBar(Math.round(module.lessons.filter(item => isComplete(item.id)).length / module.lessons.length * 100), `${module.title} progress`)}</div></aside></main>`;
  bindCommon();
  document.querySelector('#toc-select').addEventListener('change', event => {
    if (event.target.value) document.getElementById(event.target.value)?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  const sections = [...document.querySelectorAll('.lesson-prose h1,.lesson-prose h2,.lesson-prose h3,.lesson-prose h4')];
  const observer = new IntersectionObserver(entries => {
    const visible = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
    if (visible) document.querySelectorAll('.toc-link').forEach(link => link.classList.toggle('current', link.hash === `#${visible.target.id}`));
  }, { rootMargin: '-12% 0px -76% 0px' });
  sections.forEach(section => observer.observe(section));
}
function resourcesPage() {
  const requested = new URLSearchParams(location.search).get('doc')?.toLowerCase();
  const document = requested ? course.documents[requested] : null;
  if (document) {
    app.innerHTML = `<main class="wrap page-wrap"><div class="breadcrumb">${routeLink('Course', '/', '')}<span>/</span>${routeLink('Resources', '/resources', '')}<span>/</span><span>${escapeHtml(document.title)}</span></div><article class="document-page"><div class="section-kicker">COURSE DOCUMENT / ${escapeHtml(document.sourcePath)}</div><h1>${escapeHtml(document.title)}</h1><div class="prose">${renderMarkdown(document.content, document.sourcePath)}</div></article></main>`;
    bindCommon();
    return;
  }
  const rootResources = course.overview.match(/## Supplementary Resources\s*\r?\n([\s\S]*?)(?=\r?\n## |$)/i)?.[1] || '';
  const resourceLessons = course.modules.flatMap(module => module.lessons).filter(lesson => /resource/i.test(lesson.title));
  app.innerHTML = `<main class="wrap page-wrap"><div class="breadcrumb">${routeLink('Course', '/', '')}<span>/</span><span>Resources</span></div><div class="resources-head"><div class="section-kicker">REFERENCE DESK / PYTHON 3</div><h1>Keep exploring.</h1><p>Resources listed in the Python Programming Essentials course.</p></div><section class="resource-section" id="course-overview"><h2>Course overview</h2><div class="prose">${renderMarkdown(course.overview, 'README.md')}</div></section><section class="resource-section"><h2>Supplementary resources</h2><div class="prose">${renderMarkdown(rootResources, 'README.md')}</div></section>${resourceLessons.map(lesson => `<section class="resource-section"><h2>${escapeHtml(lesson.title)}</h2><div class="prose">${renderMarkdown(lesson.content, lesson.sourcePath)}</div></section>`).join('')}</main>`;
  bindCommon();
}
function tokenize(text) { return text.toLocaleLowerCase().normalize('NFKD').split(/[^\p{L}\p{N}_]+/u).filter(token => token.length > 1); }
function search(query) {
  const terms = tokenize(query);
  if (!terms.length) return [];
  return flatLessons().map(lesson => {
    const content = lesson.content.replace(/```[\s\S]*?```/g, ' ').replace(/[`*_>#\[\]()]/g, ' ').replace(/https?:\/\/\S+/g, ' ');
    const fields = [lesson.title, lesson.moduleTitle, ...(course.headings[lesson.id] || []).map(item => item.title), content];
    const normalized = fields.join(' ').toLocaleLowerCase();
    const score = terms.reduce((sum, term) => sum + (lesson.title.toLocaleLowerCase().includes(term) ? 8 : 0) + (lesson.moduleTitle.toLocaleLowerCase().includes(term) ? 3 : 0) + normalized.split(term).length - 1, 0);
    if (terms.some(term => !normalized.includes(term))) return null;
    const at = normalized.indexOf(terms[0]);
    const snippet = content.slice(Math.max(0, at - 90), at + 190).replace(/\s+/g, ' ').trim();
    return { ...lesson, score, snippet: `${at > 90 ? '…' : ''}${snippet}${at + 190 < content.length ? '…' : ''}` };
  }).filter(Boolean).sort((a, b) => b.score - a.score || a.moduleId.localeCompare(b.moduleId, undefined, { numeric: true }) || a.order - b.order);
}
function searchPage(query = '') {
  searchResults = query.trim() ? search(query) : [];
  searchFocusIndex = -1;
  app.innerHTML = `<main class="wrap page-wrap search-page"><div class="section-kicker">SEARCH THE COURSE</div><h1>Find your next answer.</h1><form class="search-form" id="search-form"><span aria-hidden="true">⌕</span><input id="search-input" type="search" autocomplete="off" placeholder="Try “lists”, “socket”, or “debugging”…" aria-label="Search Python course content" value="${escapeHtml(query)}"><button class="button button-primary" type="submit">Search</button></form><div class="search-hint">Searches titles, headings, and the complete lesson text.</div><div id="search-output" aria-live="polite">${renderSearchResults(query)}</div></main>`;
  bindCommon();
  const input = document.querySelector('#search-input');
  document.querySelector('#search-form').addEventListener('submit', event => { event.preventDefault(); pendingQuery = input.value.trim(); go(`/search${pendingQuery ? `?q=${encodeURIComponent(pendingQuery)}` : ''}`); });
  input.addEventListener('input', () => { searchResults = input.value.trim() ? search(input.value) : []; searchFocusIndex = -1; document.querySelector('#search-output').innerHTML = renderSearchResults(input.value); bindSearchResults(); });
  input.addEventListener('keydown', event => {
    if (!['ArrowDown', 'ArrowUp', 'Enter', 'Escape'].includes(event.key)) return;
    if (event.key === 'Escape') { input.blur(); return; }
    if (event.key === 'Enter' && searchFocusIndex >= 0) { event.preventDefault(); go(lessonUrl(searchResults[searchFocusIndex].id)); return; }
    if ((event.key === 'ArrowDown' || event.key === 'ArrowUp') && searchResults.length) { event.preventDefault(); searchFocusIndex = (searchFocusIndex + (event.key === 'ArrowDown' ? 1 : -1) + searchResults.length) % searchResults.length; document.querySelectorAll('.search-result').forEach((item, index) => item.classList.toggle('keyboard-active', index === searchFocusIndex)); }
  });
  bindSearchResults();
  if (!query) input.focus({ preventScroll: true });
}
function renderSearchResults(query) {
  if (!query.trim()) return '<div class="search-empty"><div class="empty-glyph">⌕</div><p>Search all lessons, modules, and headings.</p></div>';
  if (!searchResults.length) return `<div class="search-empty"><div class="empty-glyph">∅</div><p>No results for “${escapeHtml(query)}”. Try a broader term.</p></div>`;
  return `<div class="search-summary">${searchResults.length} ${searchResults.length === 1 ? 'RESULT' : 'RESULTS'} <span>FROM THE COURSE</span></div><div class="search-results">${searchResults.map(result => `<a class="search-result" href="${lessonUrl(result.id)}" data-app-link="true"><span class="search-result-module">${escapeHtml(result.moduleTitle)} · LESSON ${String(result.order).padStart(2, '0')}</span><strong>${escapeHtml(result.title)}</strong><p>${escapeHtml(result.snippet)}</p><span class="result-arrow" aria-hidden="true">↗</span></a>`).join('')}</div>`;
}
function bindSearchResults() {
  document.querySelectorAll('.search-result[data-app-link="true"]').forEach((anchor, index) => anchor.addEventListener('click', event => {
    event.preventDefault(); go(lessonUrl(searchResults[index].id));
  }));
}
function closeDrawer() {
  document.body.classList.remove('drawer-open');
  document.querySelector('.mobile-drawer-host')?.remove();
  const toggle = document.querySelector('#menu-toggle');
  toggle?.setAttribute('aria-expanded', 'false');
  toggle?.setAttribute('aria-label', 'Open course navigation');
  document.querySelector('#drawer-backdrop').hidden = true;
}
function setupDrawer() {
  const toggle = document.querySelector('#menu-toggle');
  toggle.addEventListener('click', () => {
    const open = !document.body.classList.contains('drawer-open');
    if (open && !document.querySelector('.course-sidebar')) {
      const host = document.createElement('div');
      host.className = 'mobile-drawer-host';
      host.innerHTML = courseSidebar();
      host.querySelector('.course-sidebar').classList.add('mobile-course-sidebar');
      document.body.append(host);
      bindCommon();
    }
    document.body.classList.toggle('drawer-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close course navigation' : 'Open course navigation');
    document.querySelector('#drawer-backdrop').hidden = !open;
  });
  document.querySelector('#drawer-backdrop').addEventListener('click', closeDrawer);
}
function renderRoute() {
  if (!course) return;
  updateProgressChip();
  const route = activeRoute();
  window.dispatchEvent(new CustomEvent('yaoguai:route', { detail: { activityId: route.type === 'lesson' ? `programming/${route.id}` : '' } }));
  if (route.type === 'lesson') {
    const lesson = flatLessons().find(item => item.id === route.id);
    if (lesson) { document.title = `${lesson.title} — Yaoguai Programming`; lessonPage(lesson); }
    else notFound();
  } else if (route.type === 'module') {
    const module = course.modules.find(item => item.id === route.id);
    if (module) { document.title = `${module.title} — Yaoguai Programming`; modulePage(module); }
    else notFound();
  } else if (route.type === 'resources') { document.title = 'Resources — Yaoguai Programming'; resourcesPage(); }
  else if (route.type === 'search') { document.title = 'Search — Yaoguai Programming'; searchPage(route.query); }
  else { document.title = 'Yaoguai Programming — Python Essentials'; homePage(); }
}
function notFound() {
  app.innerHTML = `<main class="wrap page-wrap not-found"><div class="section-kicker">404 / LESSON NOT FOUND</div><h1>This path is lost.</h1><p>The lesson may have moved when the course content changed.</p>${routeLink('Return to the course', '/', 'button button-primary')}</main>`;
  bindCommon();
}

window.addEventListener('popstate', renderRoute);
window.addEventListener('resize', updateProgressChip);
window.addEventListener('yaoguai:progress-changed', updateProgressChip);
setupDrawer();
try {
  const response = await fetch(`${BASE_PATH}/course-manifest.json`);
  if (!response.ok) throw new Error(`Course manifest request failed (${response.status})`);
  course = await response.json();
  renderRoute();
} catch (error) {
  app.innerHTML = `<main class="wrap page-wrap load-error"><div class="section-kicker">COURSE CONTENT UNAVAILABLE</div><h1>We could not load the course.</h1><p>${escapeHtml(error.message)}</p><p>Build the course index, then refresh this page.</p></main>`;
}
