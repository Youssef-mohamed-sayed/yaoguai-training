/* Crypto uses the single Yaoguai Training account and session. */
(() => {
  const AuthUI = {
    isLoggedIn: () => Boolean(window.YaoguaiAccountUser),
    getUser: () => window.YaoguaiAccountUser || null,
    promptAuth: () => { window.location.assign(`/login?next=${encodeURIComponent(location.pathname + location.search + location.hash)}`); },
    init: async () => {
      if (window.YaoguaiTraining?.ready) await window.YaoguaiTraining.ready;
      try {
        const response = await fetch('/api/auth/me', { credentials: 'same-origin' });
        const body = await response.json();
        const me = body.data?.user || null;
        window.YaoguaiAdminUser = me && me.is_admin ? me : null;
        window.YaoguaiAccountUser = me && !me.is_admin ? me : null;
      } catch { window.YaoguaiAccountUser = null; window.YaoguaiAdminUser = null; }
      const nav = document.querySelector('.topbar-tools') || document.querySelector('.topbar-inner');
      if (nav && !nav.querySelector('.training-account-link')) {
        const link = document.createElement('a');
        link.className = 'training-account-link';
        const admin = window.YaoguaiAdminUser;
        link.href = admin ? '/admin' : window.YaoguaiAccountUser ? '/profile' : `/login?next=${encodeURIComponent(location.pathname + location.search)}`;
        link.textContent = admin ? 'Administration' : window.YaoguaiAccountUser ? `Training · ${window.YaoguaiAccountUser.username}` : 'Training account';
        nav.append(link);
      }
      if (window.Progress) window.Progress.loadFromServer();
    },
  };
  window.AuthUI = AuthUI;
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', AuthUI.init, { once: true });
  else AuthUI.init();
})();
