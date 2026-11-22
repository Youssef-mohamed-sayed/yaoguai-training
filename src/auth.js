let csrfToken = '';
let currentUser = null;
let mode = 'login';

const dialog = document.querySelector('#auth-dialog');
const form = document.querySelector('#auth-form');
const message = document.querySelector('#auth-message');
const submit = document.querySelector('#auth-submit');
const usernameLabel = document.querySelector('#username-label');
const emailLabel = document.querySelector('#email-label');
const switchButton = document.querySelector('#auth-switch');
const resetButton = document.querySelector('#auth-reset-link');

export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    credentials: 'same-origin',
    ...options,
    headers: {
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...(options.method && options.method !== 'GET' ? { 'X-CSRFToken': csrfToken } : {}),
      ...options.headers,
    },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status === 400 && body?.error?.code === 'csrf_failed') await refreshCsrf();
    throw new Error(body?.error?.message || 'The request could not be completed');
  }
  return body.data;
}

async function refreshCsrf() {
  const result = await api('/auth/csrf', { method: 'GET' });
  csrfToken = result.csrf_token;
}

function setMessage(text, isError = false) {
  message.textContent = text;
  message.classList.toggle('is-error', isError);
}

function html(value = '') {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function activityUrl(id) {
  const [platform, ...parts] = String(id).split('/');
  const relative = parts.join('/');
  if (platform === 'network') return `/network/${relative.replace(/\/exercise\/[^/]+$/, '')}`;
  if (platform === 'linux') return `/linux/lesson/${relative}`;
  if (platform === 'programming') return `/programming/lesson/${relative}`;
  if (platform === 'crypto') return `/crypto/lessons/${relative}.html`;
  return '/';
}

async function refreshLearningSummary() {
  const root = document.querySelector('#account-summary');
  if (!root || location.pathname !== '/' || !currentUser || currentUser.must_change_password) return;
  try {
    const [progress, taskResult] = await Promise.all([
      api('/progress'), api('/assignments').catch(() => []),
    ]);
    const { overall, platforms, last_activity: last } = progress;
    const activityRows = platforms.flatMap((platform) => platform.modules.flatMap((module) => module.activities.map((activity) => ({ ...activity, platform: platform.name }))));
    const lastDone = last && activityRows.find((item) => item.id === last.id)?.completed;
    const next = last && !lastDone ? last : activityRows.find((item) => !item.completed);
    const tasks = taskResult.slice(0, 3);
    root.innerHTML = `<div class="account-summary-head"><div><p class="section-kicker">Your learning record</p><h2 id="account-summary-title">Welcome back, ${html(currentUser.username)}.</h2></div><div class="summary-total"><strong>${overall.completion_percent}%</strong><span>${overall.completed_activities} of ${overall.required_activities} required activities</span></div></div><div class="summary-progress" role="progressbar" aria-label="Overall learning progress" aria-valuenow="${overall.completion_percent}" aria-valuemin="0" aria-valuemax="100"><i style="width:${overall.completion_percent}%"></i></div><div class="summary-platforms">${platforms.map((platform) => `<a href="/${platform.id}"><span>${html(platform.name)}</span><b>${platform.completion_percent}%</b><small>${platform.completed_activities} / ${platform.required_activities} activities</small><i><em style="width:${platform.completion_percent}%"></em></i></a>`).join('')}</div><div class="summary-footer">${next ? `<a class="button button-primary" href="${activityUrl(next.id)}">Continue with ${html(next.title)} <span aria-hidden="true">→</span></a>` : '<span class="summary-complete">All required course activities are complete.</span>'}${tasks.length ? `<div class="summary-tasks"><strong>Assigned tasks</strong>${tasks.map((task) => `<span>${html(task.title)} · ${html(task.status)}${task.deadline_at ? ` · due ${new Date(task.deadline_at).toLocaleDateString()}` : ''}</span>`).join('')}</div>` : ''}${currentUser.is_admin ? '<a class="summary-admin-link" href="/admin">Administration</a>' : ''}</div>`;
    root.hidden = false;
  } catch {
    root.hidden = true;
  }
}

function setMode(nextMode) {
  mode = nextMode;
  const titles = {
    login: ['Sign in', 'Sign in', 'Create an account', true, false],
    register: ['Create account', 'Create account', 'Sign in instead', false, true],
    'request-reset': ['Reset password', 'Send reset link', 'Sign in', false, true],
    'reset-password': ['Choose a new password', 'Update password', 'Sign in', false, false],
    'change-password': ['Change your password', 'Update password', '', true, false],
  };
  const [title, button, switchText, showUsername, showEmail] = titles[nextMode];
  document.querySelector('#auth-title').textContent = title;
  submit.textContent = button;
  switchButton.textContent = switchText;
  switchButton.hidden = !switchText;
  resetButton.hidden = !['login', 'request-reset'].includes(nextMode);
  usernameLabel.hidden = !showUsername;
  emailLabel.hidden = !showEmail && nextMode !== 'request-reset';
  emailLabel.querySelector('input').required = showEmail || nextMode === 'request-reset';
  const password = form.elements.password;
  password.hidden = nextMode === 'request-reset';
  password.required = nextMode !== 'request-reset';
  password.autocomplete = nextMode === 'login' ? 'current-password' : 'new-password';
  password.minLength = nextMode === 'login' ? 1 : 10;
  let currentPassword = form.elements.current_password;
  if (!currentPassword) {
    const label = document.createElement('label');
    label.id = 'current-password-label';
    label.hidden = true;
    label.innerHTML = 'Current password<input name="current_password" type="password" autocomplete="current-password" />';
    form.insertBefore(label, emailLabel);
    currentPassword = label.querySelector('input');
  }
  document.querySelector('#current-password-label').hidden = nextMode !== 'change-password';
  currentPassword.required = nextMode === 'change-password';
  const newPasswordLabel = password.closest('label');
  newPasswordLabel.hidden = nextMode === 'request-reset';
  const resetToken = form.elements.reset_token;
  if (resetToken) resetToken.value = new URLSearchParams(location.search).get('token') || '';
  if (nextMode === 'reset-password' && !resetToken) {
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'reset_token';
    input.value = new URLSearchParams(location.search).get('token') || '';
    form.append(input);
  }
  setMessage('');
}

function showAuthenticated(user) {
  currentUser = user;
  const signIn = document.querySelector('[data-auth-open="login"]');
  const create = document.querySelector('[data-auth-open="register"]');
  const userMenu = document.querySelector('.user-menu');
  signIn.hidden = true;
  create.hidden = true;
  userMenu.hidden = false;
  userMenu.textContent = user.is_admin ? `${user.username} · Admin` : user.username;
  userMenu.setAttribute('aria-label', `Account for ${user.username}`);
  userMenu.onclick = async () => {
    if (user.is_admin && location.pathname !== '/admin') {
      location.href = '/admin';
      return;
    }
    try {
      await api('/auth/logout', { method: 'POST', body: JSON.stringify({}) });
      currentUser = null;
      location.href = '/';
    } catch (error) {
      setMessage(error.message, true);
    }
  };
  if (user.must_change_password) {
    setMode('change-password');
    dialog.showModal();
  }
  refreshLearningSummary();
}

function openAuth(nextMode) {
  setMode(nextMode);
  if (!dialog.open) dialog.showModal();
  const focus = nextMode === 'request-reset' ? emailLabel.querySelector('input') : form.elements.username;
  focus?.focus();
}

document.addEventListener('click', (event) => {
  const button = event.target.closest('[data-auth-open]');
  if (!button) return;
  event.preventDefault();
  openAuth(button.dataset.authOpen);
});

switchButton.addEventListener('click', () => setMode(mode === 'login' ? 'register' : 'login'));
resetButton.addEventListener('click', () => setMode('request-reset'));

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  submit.disabled = true;
  setMessage('');
  const values = new FormData(form);
  try {
    if (mode === 'login' || mode === 'register') {
      const payload = { username: values.get('username'), password: values.get('password') };
      if (mode === 'register') payload.email = values.get('email');
      const result = await api(`/auth/${mode}`, { method: 'POST', body: JSON.stringify(payload) });
      if (mode === 'login') await refreshCsrf();
      showAuthenticated(result.user);
      if (!result.user.must_change_password) dialog.close();
    } else if (mode === 'request-reset') {
      const result = await api('/auth/password-reset-requests', { method: 'POST', body: JSON.stringify({ email: values.get('email') }) });
      setMessage(result.message);
    } else if (mode === 'reset-password') {
      await api('/auth/password-resets', { method: 'POST', body: JSON.stringify({ token: values.get('reset_token'), password: values.get('password') }) });
      setMessage('Password updated. You can sign in now');
      setMode('login');
      setMessage('Password updated. You can sign in now');
    } else if (mode === 'change-password') {
      const result = await api('/auth/password', { method: 'POST', body: JSON.stringify({ current_password: values.get('current_password'), new_password: values.get('password') }) });
      currentUser = result.user;
      dialog.close();
      refreshLearningSummary();
    }
  } catch (error) {
    setMessage(error.message, true);
  } finally {
    submit.disabled = false;
  }
});

export async function initAuth() {
  try {
    await refreshCsrf();
    const result = await api('/auth/me');
    if (result.user) showAuthenticated(result.user);
  } catch {
    setMessage('Account services are temporarily unavailable');
  }
  if (location.pathname === '/reset-password') {
    document.querySelector('#portal-content').hidden = true;
    openAuth('reset-password');
  }
  if (new URLSearchParams(location.search).get('auth') === 'login' && !currentUser) openAuth('login');
  if (new URLSearchParams(location.search).get('auth') === 'login') openAuth('login');
  if (location.pathname === '/admin') {
    document.querySelector('#portal-content').hidden = true;
    const root = document.querySelector('#admin-root');
    root.hidden = false;
    const { mountAdmin } = await import('./admin.js');
    mountAdmin(root, () => currentUser, (nextMode) => openAuth(nextMode));
  }
}
