/* Crypto uses the single Yaoguai Training account and session. */
(() => {
  const AuthUI = {
    isLoggedIn: () => Boolean(window.YaoguaiAccountUser),
    getUser: () => window.YaoguaiAccountUser || null,
    promptAuth: () => { window.location.assign('/?auth=login'); },
    init: async () => {
      try {
        const response = await fetch('/api/auth/me', { credentials: 'same-origin' });
        const body = await response.json();
        window.YaoguaiAccountUser = body.data?.user || null;
      } catch { window.YaoguaiAccountUser = null; }
      const nav = document.querySelector('.topbar-tools') || document.querySelector('.topbar-inner');
      if (nav && !nav.querySelector('.training-account-link')) {
        const link = document.createElement('a');
        link.className = 'training-account-link';
        link.href = window.YaoguaiAccountUser ? '/' : '/?auth=login';
        link.textContent = window.YaoguaiAccountUser ? `Training · ${window.YaoguaiAccountUser.username}` : 'Training account';
        nav.append(link);
      }
      if (window.Progress) window.Progress.loadFromServer();
    },
  };
  window.AuthUI = AuthUI;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', AuthUI.init, { once: true });
  else AuthUI.init();
})();
