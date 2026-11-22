const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function browser(data = new Map()) {
  const elements = new Map();
  const listeners = new Map();
  const navigations = [];
  const storage = {
    get length() { return data.size; },
    key(i) { return [...data.keys()][i] ?? null; },
    getItem(key) { return data.get(key) ?? null; },
    setItem(key, value) { data.set(key, String(value)); },
    removeItem(key) { data.delete(key); },
  };
  const get = id => {
    if (!elements.has(id)) elements.set(id, {
      id, value: '', style: {}, textContent: '', disabled: true,
      classList: { add() {}, remove() {} }, reset() { this.value = ''; }, focus() {},
    });
    return elements.get(id);
  };
  const context = vm.createContext({
    window: {
      location: { origin: 'http://localhost', replace(path) { navigations.push(path); }, reload() { navigations.push('reload'); } },
      addEventListener(name, handler) { listeners.set(name, handler); },
      dispatchEvent() {}, sessionStorage: storage,
    },
    document: { readyState: 'loading', body: { dataset: {} },
      addEventListener() {}, getElementById: get, querySelector() { return null; } },
    localStorage: storage, TextEncoder, AbortSignal, setTimeout() {},
    CustomEvent: class { constructor(type) { this.type = type; } },
    FormData: class { append() {} },
  });
  for (const path of ['api', 'progress', 'auth-ui']) {
    vm.runInContext(fs.readFileSync(`public/js/${path}.js`, 'utf8'), context);
  }
  const auth = context.window.CryptoAPI.auth;
  function session(id, progress = {}) {
    context.fetch = async () => response({ token: `token-${id}`, user: { id, username: `user${id}`, progress } });
    return auth.login(`user${id}`, 'password123');
  }
  return { context, auth, progress: context.window.Progress, ui: context.window.AuthUI,
    data, get, navigations, listeners, session };
}

function response(result) {
  return { ok: true, status: 200, headers: { get() { return null; } },
    json: async () => ({ success: true, result }) };
}

function deferred() {
  let resolve;
  const promise = new Promise(done => { resolve = done; });
  return { promise, resolve };
}

test('account switching replaces progress and never uploads another account cache', async () => {
  const b = browser(new Map([['yaoguai:progress:v1', '{"xor":{"status":"done"}}']]));
  assert.equal(b.data.has('yaoguai:progress:v1'), false);
  await b.session(1, { aes: { status: 'done' } });
  assert.equal(b.progress.overall(['aes', 'xor']).done, 1);
  await b.session(2);
  assert.equal(b.progress.overall(['aes', 'xor']).done, 0);
  const saves = [];
  b.context.fetch = async (url, options) => {
    saves.push({ url, token: options.headers.Authorization, body: JSON.parse(options.body) });
    return response({});
  };
  b.progress.markComplete('md5');
  await new Promise(setImmediate);
  assert.equal(saves.length, 1);
  assert.equal(saves[0].token, 'Bearer token-2');
  assert.deepEqual(Object.keys(saves[0].body.progress), ['md5']);
  await b.session(1, { aes: { status: 'done' } });
  assert.equal(b.progress.getLesson('md5').status, 'available');
  assert.equal(b.progress.getLesson('aes').status, 'done');
});

test('logout clears profile, token, caches and completion UI, then reloads the main page', async () => {
  const b = browser();
  await b.session(1, { aes: { status: 'done' } });
  b.data.set('yaoguai:tool:1:key', 'private');
  b.data.set('unrelated-setting', 'keep');
  b.get('profile-username-val').textContent = 'user1';
  b.get('profile-progress-stat').textContent = '1 modules completed';
  b.get('auth-form-login').value = 'old credentials';
  const revoke = deferred();
  b.context.fetch = (url, options) => {
    assert.match(url, /auth\/logout$/);
    assert.equal(options.headers.Authorization, 'Bearer token-1');
    return revoke.promise;
  };
  const logout = b.ui.handleLogout();
  assert.equal(b.auth.isLoggedIn(), false);
  assert.equal(b.auth.getUser(), null);
  assert.equal(b.progress.overall(['aes']).done, 0);
  assert.equal(b.data.has('yaoguai_user'), false);
  assert.equal(b.data.has('yaoguai:tool:1:key'), false);
  assert.equal(b.data.get('unrelated-setting'), 'keep');
  assert.equal(b.get('profile-username-val').textContent, '');
  assert.equal(b.get('profile-progress-stat').textContent, '');
  assert.equal(b.get('auth-form-login').value, '');
  assert.equal(b.get('complete-btn').disabled, false);
  revoke.resolve(response({ logged_out: true }));
  await logout;
  assert.deepEqual(b.navigations, ['/']);
  b.progress.markComplete('aes');
  assert.equal(b.progress.overall(['aes']).done, 0); // Guests cannot persist progress.
});

test('late profile and avatar responses cannot restore a logged-out or different account', async () => {
  const b = browser();
  await b.session(1);
  const profile = deferred();
  b.context.fetch = () => profile.promise;
  const pendingProfile = b.auth.me();
  const avatar = deferred();
  b.context.fetch = () => avatar.promise;
  const pendingAvatar = b.auth.updateAvatar({});
  await b.session(2);
  profile.resolve(response({ user: { id: 1, username: 'user1' } }));
  avatar.resolve(response({ avatar_url: 'account-1.png' }));
  await assert.rejects(pendingProfile, error => error.code === 'SESSION_CHANGED');
  await assert.rejects(pendingAvatar, error => error.code === 'SESSION_CHANGED');
  assert.equal(b.auth.getUser().id, 2);
  assert.equal(b.auth.getUser().avatar_url, undefined);
});

test('late login response after logout cannot recreate a session', async () => {
  const b = browser();
  const login = deferred();
  b.context.fetch = () => login.promise;
  const pending = b.auth.login('user1', 'password123');
  await b.auth.logout();
  login.resolve(response({ token: 'old-token', user: { id: 1, progress: {} } }));
  await assert.rejects(pending, error => error.code === 'SESSION_CHANGED');
  assert.equal(b.auth.isLoggedIn(), false);
  assert.equal(b.auth.getUser(), null);
});

test('late progress loads cannot mix accounts or overwrite newer completions', async () => {
  const b = browser();
  await b.session(1);
  const old = deferred();
  b.context.fetch = () => old.promise;
  const pending = b.progress.loadFromServer();
  await b.session(2);
  old.resolve(response({ progress: { aes: { status: 'done' } } }));
  await pending;
  assert.equal(b.progress.overall(['aes']).done, 0);
  const load = deferred();
  b.context.fetch = () => load.promise;
  const pendingLoad = b.progress.loadFromServer();
  b.context.fetch = async () => response({});
  b.progress.markComplete('md5');
  load.resolve(response({ progress: {} }));
  await pendingLoad;
  assert.equal(b.progress.getLesson('md5').status, 'done');
});

test('queued saves retain their original owner and skip requests after switching accounts', async () => {
  const b = browser();
  await b.session(1);
  const first = deferred();
  b.context.fetch = () => first.promise;
  const pending = b.auth.saveProgress({ aes: { status: 'done' } });
  await new Promise(setImmediate);
  const stale = b.auth.saveProgress({ xor: { status: 'done' } });
  const staleCheck = assert.rejects(stale, error => error.code === 'SESSION_CHANGED');
  await b.session(2);
  let called = false;
  b.context.fetch = async () => { called = true; return response({}); };
  first.resolve(response({}));
  await pending;
  await staleCheck;
  assert.equal(called, false);
});

test('a stale tab cannot write its old lesson data using another tab session', async () => {
  const b = browser();
  await b.session(1);
  b.data.set('yaoguai_jwt', 'token-2');
  b.data.set('yaoguai_user', JSON.stringify({ token: 'token-2', user: { id: 2 } }));
  b.progress.markComplete('aes'); // Before the storage event is delivered.
  assert.equal(b.auth.getToken(), '');
  assert.equal(b.data.has('yaoguai:progress:v2:2'), false);
  b.listeners.get('storage')({ key: 'yaoguai_jwt' });
  assert.deepEqual(b.navigations, ['/']);
  b.listeners.get('pageshow')({ persisted: true });
  assert.deepEqual(b.navigations, ['/', 'reload']);
});

test('offline logout still clears local data and returns to the main page', async () => {
  const b = browser();
  await b.session(1, { aes: { status: 'done' } });
  b.context.fetch = async () => { throw new TypeError('offline'); };
  await b.ui.handleLogout();
  assert.equal(b.auth.isLoggedIn(), false);
  assert.equal(b.progress.overall(['aes']).done, 0);
  assert.deepEqual(b.navigations, ['/']);
});
