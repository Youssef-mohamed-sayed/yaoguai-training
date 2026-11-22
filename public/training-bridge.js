/* Shared account and durable progress bridge for the four course frontends. */
(() => {
  let csrf = '';
  let activeId = '';
  let snapshot = null;
  const account = () => window.YaoguaiAccountUser || null;

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

  async function request(path, method = 'GET', body) {
    return fetch(`/api${path}`, {
      method, credentials: 'same-origin',
      headers: { ...(body ? { 'Content-Type': 'application/json' } : {}), ...(method !== 'GET' && csrf ? { 'X-CSRFToken': csrf } : {}) },
      ...(body ? { body: JSON.stringify(body) } : {}),
    });
  }

  function publish() {
    window.dispatchEvent(new CustomEvent('yaoguai:central-progress', { detail: snapshot }));
  }

  async function refresh() {
    if (!account()) return null;
    const response = await request('/progress');
    if (!response.ok) return null;
    snapshot = (await response.json()).data;
    publish();
    return snapshot;
  }

  async function visit(id) {
    if (!account() || !id || id === activeId && window.__yaoguaiVisited === id) return;
    activeId = id;
    window.__yaoguaiVisited = id;
    const response = await request('/progress/visits', 'POST', { activity_id: id });
    if (!response.ok) return;
    await refresh();
    const safePath = id.split('/').map(encodeURIComponent).join('/');
    const heartbeat = () => {
      if (document.visibilityState === 'visible') request(`/progress/activities/${safePath}/heartbeat`, 'POST', {});
    };
    if (window.__yaoguaiHeartbeat) clearInterval(window.__yaoguaiHeartbeat);
    window.__yaoguaiHeartbeat = setInterval(heartbeat, 20000);
    window.addEventListener('pagehide', heartbeat, { once: true });
  }

  async function complete(id = activeId) {
    if (!account() || !id) return false;
    const safePath = id.split('/').map(encodeURIComponent).join('/');
    const response = await request(`/progress/activities/${safePath}/complete`, 'POST', {});
    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      window.dispatchEvent(new CustomEvent('yaoguai:central-progress-error', { detail: result.error?.message || 'Progress could not be saved.' }));
      return false;
    }
    await refresh();
    return true;
  }

  window.YaoguaiTraining = {
    get ready() { return ready; },
    get user() { return account(); },
    get snapshot() { return snapshot; },
    refresh,
    visit,
    complete,
    isComplete(id) {
      return Boolean(snapshot?.platforms?.flatMap(p => p.modules).flatMap(m => m.activities).find(a => a.id === id)?.completed);
    },
  };

  window.addEventListener('yaoguai:central-progress-error', event => {
    let notice = document.querySelector('.training-progress-notice');
    if (!notice) {
      notice = document.createElement('div');
      notice.className = 'training-progress-notice';
      notice.setAttribute('role', 'status');
      Object.assign(notice.style, { position: 'fixed', inset: 'auto 20px 20px auto', zIndex: '9999', maxWidth: 'min(420px, calc(100vw - 40px))', padding: '12px 16px', background: '#241719', color: '#f1e8e9', border: '1px solid #80424a', borderRadius: '6px', boxShadow: '0 8px 28px #0008', font: '14px/1.5 system-ui, sans-serif' });
      document.body.append(notice);
    }
    notice.textContent = event.detail || 'Progress could not be saved. Try again.';
    clearTimeout(notice._timer);
    notice._timer = setTimeout(() => notice.remove(), 8000);
  });

  const ready = (async () => {
    try {
      const csrfResponse = await request('/auth/csrf');
      csrf = (await csrfResponse.json()).data?.csrf_token || '';
      const accountResponse = await request('/auth/me');
      window.YaoguaiAccountUser = (await accountResponse.json()).data?.user || null;
    } catch { window.YaoguaiAccountUser = null; }

    const nav = document.querySelector('header nav, header .topnav, header .top-links, .topnav, .topbar-tools');
    if (nav && !nav.querySelector('.training-account-link')) {
      const link = document.createElement('a');
      link.className = 'training-account-link';
      const next = encodeURIComponent(location.pathname + location.search);
      link.href = account() ? '/profile' : `/login?next=${next}`;
      link.textContent = account() ? `Training · ${account().username}` : 'Training account';
      link.setAttribute('aria-label', account() ? 'Open profile settings' : 'Sign in to save learning progress');
      nav.append(link);
      const style = document.createElement('style');
      style.textContent = '.training-account-link{margin-inline-start:12px;color:inherit;font-size:.9em;text-decoration:underline;text-underline-offset:4px}.training-account-link:focus-visible{outline:2px solid #c94b55;outline-offset:3px}';
      document.head.append(style);
    }
    if (account()?.must_change_password) { location.assign('/profile?required=1'); return; }
    if (!account()) return;
    await refresh();
    activeId = identify();
    await visit(activeId);
    window.addEventListener('yaoguai:route', event => visit(event.detail?.activityId || identify()));
    window.addEventListener('yaoguai:network-check-complete', refresh);
  })();
})();
