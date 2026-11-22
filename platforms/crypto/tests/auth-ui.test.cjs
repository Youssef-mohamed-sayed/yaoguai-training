const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function setup() {
  const elements = new Map();
  const context = vm.createContext({
    window: { location: { origin: 'http://localhost' } },
    document: {
      readyState: 'loading', addEventListener() {},
      getElementById(id) {
        if (!elements.has(id)) elements.set(id, { id, value: '', files: [], style: {} });
        return elements.get(id);
      },
    },
    localStorage: { getItem() { return null; }, setItem() {}, removeItem() {} },
    TextEncoder, AbortSignal, setTimeout() {},
  });
  for (const path of ['public/js/api.js', 'public/js/auth-ui.js']) {
    vm.runInContext(fs.readFileSync(path, 'utf8'), context);
  }
  return { context, ui: context.window.AuthUI, get: id => context.document.getElementById(id) };
}

test('all registration errors are visible and prevent requests', async () => {
  const { context, ui, get } = setup();
  let called = false;
  context.window.CryptoAPI.auth.register = async () => { called = true; };
  get('reg-username').value = 'bad name';
  get('reg-password').value = 'short';
  get('reg-msg').style.display = 'none';
  await ui.handleRegister({ preventDefault() {} });
  assert.equal(called, false);
  assert.equal(get('reg-msg').style.display, 'block');
  assert.match(get('reg-msg').textContent, /only contain/);
  assert.match(get('reg-msg').textContent, /at least 8/);
});

test('login server errors and success messages override previous hidden state', async () => {
  const { context, ui, get } = setup();
  get('login-username').value = 'test';
  get('login-password').value = '1234'; // Existing accounts can still sign in.
  context.window.CryptoAPI.auth.login = async () => { throw new Error('Invalid username or password.'); };
  await ui.handleLogin({ preventDefault() {} });
  assert.equal(get('login-msg').style.display, 'block');
  assert.match(get('login-msg').textContent, /Invalid username/);
  assert.equal(get('login-submit-btn').disabled, false);
  context.window.CryptoAPI.auth.login = async () => ({});
  await ui.handleLogin({ preventDefault() {} });
  assert.equal(get('login-msg').style.display, 'block');
  assert.match(get('login-msg').textContent, /successful/);
});

test('avatar validation errors remain visible after switching tabs', () => {
  const { ui, get } = setup();
  const input = { files: [{ name: 'bad.gif', size: 12 }], value: 'bad.gif' };
  get('reg-msg').style.display = 'none';
  ui.onAvatarSelect(input, 'preview', 'reg-msg');
  assert.equal(get('reg-msg').style.display, 'block');
  assert.match(get('reg-msg').textContent, /Invalid avatar/);
  assert.equal(input.value, '');
});

test('API errors preserve validation messages and HTTP status', async () => {
  const { context } = setup();
  context.fetch = async () => ({ ok: false, status: 400,
    json: async () => ({ errors: { username: 'Username is required.', password: 'Password must be at least 8 characters long.' } }) });
  await assert.rejects(context.window.CryptoAPI.auth.login('', ''), error => {
    assert.equal(error.status, 400);
    assert.match(error.message, /Username is required/);
    assert.match(error.message, /at least 8/);
    return true;
  });
});

test('network failures and non-JSON server failures have actionable messages', async () => {
  const { context } = setup();
  context.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(context.window.CryptoAPI.auth.login('test', 'password'), /Check your connection/);
  context.fetch = async () => ({ ok: false, status: 503, json: async () => { throw new Error('HTML'); } });
  await assert.rejects(context.window.CryptoAPI.auth.login('test', 'password'), /temporarily unavailable/);
});
