/* Shared account and progress bridge for the four preserved course frontends. */
(() => {
  const prefix = '/api';
  let csrf = '';
  let signedIn = false;
  let activeId = '';

  function identify() {
    const path = decodeURI(location.pathname).replace(/\/$/, '');
    let match = path.match(/^\/linux\/lesson\/(.+)$/);
    if (match) return `linux/${match[1]}`;
    match = path.match(/^\/programming\/lesson\/(.+)$/);
    if (match) return `programming/${match[1]}`;
    match = path.match(/^\/network\/(.+)$/);
    if (match && !['course', 'search', 'challenges'].includes(match[1])) return `network/${match[1]}`;
    match = path.match(/^\/crypto\/lessons\/([^/]+)\.html$/);
    if (match) return `crypto/${match[1]}`;
    return '';
  }

  async function request(path, method = 'GET', body = undefined) {
    return fetch(`${prefix}${path}`, {
      method,
      credentials: 'same-origin',
      headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(method !== 'GET' && csrf ? { 'X-CSRFToken': csrf } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
  }

  async function markComplete(id) {
    if (!signedIn || !id) return;
    const safePath = id.split('/').map(encodeURIComponent).join('/');
    const response = await request(`/progress/activities/${safePath}/complete`, 'POST', {});
    if (!response.ok) {
      const message = await response.json().catch(() => ({}));
      window.dispatchEvent(new CustomEvent('yaoguai:central-progress-error', { detail: message.error?.message || 'Progress could not be saved.' }));
    }
  }

  async function init() {
    activeId = identify();
    try {
      const csrfResponse = await request('/auth/csrf');
      csrf = (await csrfResponse.json()).data?.csrf_token || '';
      const accountResponse = await request('/auth/me');
      window.YaoguaiAccountUser = (await accountResponse.json()).data?.user || null;
      signedIn = Boolean(window.YaoguaiAccountUser);
    } catch { return; }
    const homeLink = document.createElement('a');
    homeLink.className = 'training-account-link';
    homeLink.href = signedIn ? '/' : '/?auth=login';
    homeLink.textContent = signedIn ? `Training · ${window.YaoguaiAccountUser.username}` : 'Training account';
    homeLink.setAttribute('aria-label', signedIn ? 'Open Yaoguai Training dashboard' : 'Sign in to Yaoguai Training');
    document.querySelector('header nav, header .topnav, header .top-links, .topnav, .topbar-tools')?.append(homeLink);
    const style = document.createElement('style');
    style.textContent = '.training-account-link{margin-inline-start:12px;color:inherit;font-size:.84em;text-decoration:underline;text-underline-offset:4px}.training-account-link:focus-visible{outline:2px solid #c94b55;outline-offset:3px}';
    document.head.append(style);
    if (!signedIn) return;
    window.Progress?.loadFromServer?.();
    const progressResponse = await request('/progress');
    if (progressResponse.ok) {
      const progressData = (await progressResponse.json()).data;
      window.dispatchEvent(new CustomEvent('yaoguai:central-progress', { detail: progressData }));
    }
    if (!activeId) return;
    const visit = await request('/progress/visits', 'POST', { activity_id: activeId });
    if (!visit.ok) return;
    const safePath = activeId.split('/').map(encodeURIComponent).join('/');
    const heartbeat = () => {
      if (document.visibilityState === 'visible') request(`/progress/activities/${safePath}/heartbeat`, 'POST', {});
    };
    const timer = window.setInterval(heartbeat, 20000);
    window.addEventListener('pagehide', () => { clearInterval(timer); heartbeat(); }, { once: true });
    document.addEventListener('click', (event) => {
      if (event.target.closest('[data-complete], #complete-lesson, #complete-btn')) markComplete(activeId);
    }, true);
    if (window.Progress?.markComplete) {
      const original = window.Progress.markComplete.bind(window.Progress);
      window.Progress.markComplete = (...args) => { const value = original(...args); markComplete(activeId); return value; };
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
