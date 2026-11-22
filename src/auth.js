let csrfToken = '';
let currentUser = null;

export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    credentials: 'same-origin', ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.method && options.method !== 'GET' ? { 'X-CSRFToken': csrfToken } : {}),
      ...options.headers,
    },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body?.error?.message || 'The request could not be completed');
  return body.data;
}

async function refreshCsrf() {
  csrfToken = (await api('/auth/csrf')).csrf_token;
}
const esc = (value = '') => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const portal = () => document.querySelector('#portal-content');
const path = () => location.pathname.replace(/\/$/, '') || '/';
const validNext = (value) => value?.startsWith('/') && !value.startsWith('//') ? value : '/';

function paintHeader() {
  document.querySelector('[data-sign-in]').hidden = Boolean(currentUser);
  document.querySelector('[data-register]').hidden = Boolean(currentUser);
  document.querySelector('[data-profile]').hidden = !currentUser;
  document.querySelector('[data-sign-out]').hidden = !currentUser;
  document.querySelector('[data-sign-out]').onclick = async () => {
    try { await api('/auth/logout', { method: 'POST', body: '{}' }); location.assign('/'); }
    catch (error) {
      let notice = document.querySelector('#account-notice');
      if (!notice) { notice = document.createElement('span'); notice.id = 'account-notice'; notice.setAttribute('role', 'status'); document.querySelector('.site-nav').append(notice); }
      notice.textContent = error.message;
    }
  };
}

function pageFrame(kicker, title, description, content) {
  portal().hidden = false;
  portal().innerHTML = `<section class="account-page"><div class="account-card"><p class="section-kicker">${kicker}</p><h1>${title}</h1><p class="account-description">${description}</p>${content}</div></section>`;
  document.querySelector('.site-footer').hidden = true;
}

function renderAuthPage(mode) {
  const register = mode === 'register';
  const forgot = mode === 'forgot-password';
  const reset = mode === 'reset-password';
  const next = validNext(new URLSearchParams(location.search).get('next'));
  const token = new URLSearchParams(location.search).get('token') || '';
  const title = register ? 'Create your account' : forgot ? 'Reset your password' : reset ? 'Choose a new password' : 'Sign in';
  const description = register ? 'Your learning record will follow you across all four courses.' : forgot ? 'Enter the email on your account. If it can be verified, reset instructions will be sent.' : reset ? 'Choose a new password for your Yaoguai Training account.' : 'Continue your courses and keep your progress in one place.';
  let fields = '';
  if (register) fields += '<label>Username<input name="username" autocomplete="username" minlength="3" maxlength="32" required></label><label>Email<input name="email" type="email" autocomplete="email" maxlength="254" required></label>';
  else if (!forgot && !reset) fields += '<label>Username or email<input name="username" autocomplete="username" required></label>';
  if (forgot) fields += '<label>Email<input name="email" type="email" autocomplete="email" required></label>';
  if (!forgot) fields += `<label>${reset ? 'New password' : 'Password'}<input name="password" type="password" autocomplete="${register || reset ? 'new-password' : 'current-password'}" minlength="${register || reset ? 10 : 1}" required></label>`;
  pageFrame('Yaoguai Training', title, description, `<form class="auth-form" id="auth-form">${fields}${reset ? `<input type="hidden" name="token" value="${esc(token)}">` : ''}<p class="form-message" id="auth-message" role="status"></p><button class="button button-primary" type="submit">${register ? 'Create account' : forgot ? 'Send reset instructions' : reset ? 'Update password' : 'Sign in'}</button></form><div class="account-links">${register ? '<a href="/login">Already have an account? Sign in</a>' : forgot || reset ? '<a href="/login">Back to sign in</a>' : `<a href="/register">Create an account</a><a href="/forgot-password">Forgot password?</a>`}</div>`);
  const form = document.querySelector('#auth-form');
  const message = document.querySelector('#auth-message');
  form.addEventListener('submit', async event => {
    event.preventDefault();
    const button = form.querySelector('button[type=submit]');
    button.disabled = true; message.textContent = '';
    const values = Object.fromEntries(new FormData(form));
    try {
      if (mode === 'login' || register) {
        const result = await api(`/auth/${register ? 'register' : 'login'}`, { method: 'POST', body: JSON.stringify(values) });
        currentUser = result.user;
        await refreshCsrf();
        const destination = !register && currentUser.is_admin && next === '/'
          ? '/admin'
          : validNext(next);
        if (currentUser.must_change_password) {
          location.assign(`/profile?required=1&next=${encodeURIComponent(destination)}`);
        } else {
          location.assign(destination);
        }
      } else if (forgot) {
        const result = await api('/auth/password-reset-requests', { method: 'POST', body: JSON.stringify({ email: values.email }) });
        message.textContent = result.message || 'If the account exists, reset instructions will be sent.';
      } else {
        await api('/auth/password-resets', { method: 'POST', body: JSON.stringify({ token: values.token, password: values.password }) });
        message.textContent = 'Password updated. You can sign in now.';
      }
    } catch (error) { message.textContent = error.message; message.classList.add('is-error'); }
    finally { button.disabled = false; }
  });
}

function renderProfile() {
  const forced = currentUser.must_change_password || new URLSearchParams(location.search).has('required');
  pageFrame('Your account', 'Profile settings', forced ? 'Set a new password to continue using your account.' : 'Update your sign-in password here.', `<dl class="profile-details"><div><dt>Username</dt><dd>${esc(currentUser.username)}</dd></div><div><dt>Email</dt><dd>${esc(currentUser.email)}</dd></div><div><dt>Account</dt><dd>${currentUser.is_admin ? 'Administrator' : 'Learner'}</dd></div></dl><h2>Password</h2><form class="auth-form" id="password-form"><label>Current password<input name="current_password" type="password" autocomplete="current-password" required></label><label>New password<input name="new_password" type="password" autocomplete="new-password" minlength="10" maxlength="128" required></label><label>Confirm new password<input name="confirm_password" type="password" autocomplete="new-password" minlength="10" maxlength="128" required></label><p class="form-message" id="profile-message" role="status"></p><button class="button button-primary" type="submit">Update password</button></form>${currentUser.is_admin ? '<p><a class="text-link" href="/admin">Open administration &rarr;</a></p>' : ''}<p><a class="text-link" href="/">Back to learning paths</a></p>`);
  document.querySelector('#password-form').addEventListener('submit', async event => {
    event.preventDefault();
    const form = event.currentTarget, values = Object.fromEntries(new FormData(form));
    const message = document.querySelector('#profile-message');
    if (values.new_password !== values.confirm_password) { message.textContent = 'The new passwords do not match.'; message.classList.add('is-error'); return; }
    const button = form.querySelector('button'); button.disabled = true; message.textContent = '';
    try {
      const result = await api('/auth/password', { method: 'POST', body: JSON.stringify({ current_password: values.current_password, new_password: values.new_password }) });
      currentUser = result.user; message.textContent = 'Password updated successfully.'; form.reset();
      if (forced) {
        const requested = validNext(new URLSearchParams(location.search).get('next'));
        const destination = requested === '/' && currentUser.is_admin ? '/admin' : requested;
        location.assign(destination);
      }
    } catch (error) { message.textContent = error.message; message.classList.add('is-error'); }
    finally { button.disabled = false; }
  });
}

function activityUrl(id) {
  const [platform, ...parts] = String(id).split('/'); const relative = parts.join('/');
  if (platform === 'network') return `/network/${relative.replace(/\/exercise\/[^/]+$/, '')}`;
  if (platform === 'linux') return `/linux/lesson/${relative}`;
  if (platform === 'programming') return `/programming/lesson/${relative}`;
  if (platform === 'crypto') return `/crypto/lessons/${relative}.html`;
  return '/';
}

async function refreshLearningSummary() {
  const root = document.querySelector('#account-summary');
  if (!root || path() !== '/' || !currentUser || currentUser.must_change_password) return;
  try {
    const progress = await api('/progress');
    const { overall, platforms, last_activity: last } = progress;
    const activities = platforms.flatMap(p => p.modules.flatMap(m => m.activities.map(a => ({ ...a, platform: p.name }))));
    const lastItem = last && activities.find(a => a.id === last.id);
    const next = lastItem && !lastItem.completed ? lastItem : activities.find(a => !a.completed);
    root.innerHTML = `<div class="account-summary-head"><div><p class="section-kicker">Your learning record</p><h2 id="account-summary-title">Learning progress</h2></div><div class="summary-total"><strong>${overall.completion_percent}%</strong><span>${overall.completed_activities} of ${overall.required_activities} required activities</span></div></div><div class="summary-progress" role="progressbar" aria-label="Overall learning progress" aria-valuenow="${overall.completion_percent}" aria-valuemin="0" aria-valuemax="100"><i style="width:${overall.completion_percent}%"></i></div><div class="summary-platforms">${platforms.map(p => `<a href="/${p.id}"><span>${esc(p.name)}</span><b>${p.completion_percent}%</b><small>${p.completed_activities} / ${p.required_activities} activities</small><i><em style="width:${p.completion_percent}%"></em></i></a>`).join('')}</div><div class="summary-footer">${next ? `<a class="button button-primary" href="${activityUrl(next.id)}">Continue with ${esc(next.title)} &rarr;</a>` : '<span class="summary-complete">All required course activities are complete.</span>'}${currentUser.is_admin ? '<a class="summary-admin-link" href="/admin">Administration</a>' : ''}</div>`;
    root.hidden = false;
  } catch { root.hidden = true; }
}

export async function initAuth() {
  try {
    await refreshCsrf();
    currentUser = (await api('/auth/me')).user || null;
  } catch { currentUser = null; }
  paintHeader();
  const route = path();
  if (route === '/login' || route === '/register' || route === '/forgot-password' || route === '/reset-password') {
    if (currentUser) {
      const requested = validNext(new URLSearchParams(location.search).get('next'));
      const destination = requested === '/' && currentUser.is_admin ? '/admin' : requested;
      location.replace(currentUser.must_change_password
        ? `/profile?required=1&next=${encodeURIComponent(destination)}`
        : destination);
      return;
    }
    renderAuthPage(route.slice(1));
  } else if (route === '/profile') {
    if (!currentUser) { location.replace(`/login?next=${encodeURIComponent('/profile')}`); return; }
    renderProfile();
  } else if (route === '/admin') {
    if (!currentUser) { location.replace(`/login?next=${encodeURIComponent('/admin')}`); return; }
    if (currentUser.must_change_password) { location.replace(`/profile?required=1&next=${encodeURIComponent('/admin')}`); return; }
    if (!currentUser.is_admin) { location.replace('/'); return; }
    portal().hidden = true;
    const root = document.querySelector('#admin-root'); root.hidden = false;
    const { mountAdmin } = await import('./admin.js');
    await mountAdmin(root, () => currentUser);
  } else if (currentUser?.must_change_password) {
    const destination = currentUser.is_admin ? '/admin' : '/';
    location.replace(`/profile?required=1&next=${encodeURIComponent(destination)}`); return;
  } else {
    refreshLearningSummary();
  }
}
