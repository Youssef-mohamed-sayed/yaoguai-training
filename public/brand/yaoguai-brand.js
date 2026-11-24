/* Yaoguai shared brand script: course bar, logo swap, drips, intro. Plain JavaScript, no libraries. */
(function () {
  var COURSES = [
    { href: '/', label: 'HOME', cn: '', match: /^\/$/ },
    { href: '/network', label: 'NETWORK', cn: '网络', match: /^\/network/ },
    { href: '/linux', label: 'LINUX', cn: '系统', match: /^\/linux/ },
    { href: '/programming', label: 'PYTHON', cn: '代码', match: /^\/programming/ },
    { href: '/crypto/', label: 'CRYPTO', cn: '密码', match: /^\/crypto/ },
  ];
  var path = location.pathname;

  function start() {
    // 1. sharp SVG logo instead of the 128px PNG
    var imgs = document.querySelectorAll('img[src*="logo-emblem"]');
    for (var i = 0; i < imgs.length; i++) imgs[i].src = '/brand/logo-mask.svg';

    // 2. one course bar on every page
    var bar = document.createElement('nav');
    bar.className = 'yg-bar';
    bar.setAttribute('aria-label', 'Yaoguai courses');
    var html = '<a class="yg-logo" href="/"><img src="/brand/logo-mask.svg" alt=""><span>YAOGUAI</span></a>';
    COURSES.forEach(function (c) {
      var on = c.match.test(path) ? ' on' : '';
      html += '<a class="yg-link' + on + '" href="' + c.href + '">' + (c.cn ? '<b>' + c.cn + '</b>' : '') + c.label + '</a>';
    });
    bar.innerHTML = html;
    document.body.insertBefore(bar, document.body.firstChild);

    // 3. oni masks: they drop in, wander, then settle in an even row under the bar
    var drips = document.createElement('div');
    drips.className = 'yg-drips';
    // masks sit inside the bar, in the free space to the right of the course links
    var last = bar.querySelector('.yg-link:last-of-type');
    var from = last ? last.getBoundingClientRect().right + 30 : 600;
    var room = window.innerWidth - from - 24;
    var count = Math.max(0, Math.min(14, Math.floor(room / 44)));
    drips.style.left = from + 'px';
    drips.style.right = '24px';
    for (var n = 0; n < count; n++) {
      var m = document.createElement('b');
      m.className = 'yg-oni';
      var slot = (n + 0.5) / count;
      m.style.left = (slot * 100) + '%';
      var seed = Math.sin(n * 12.9898) * 43758.5453;
      var r = seed - Math.floor(seed);
      m.style.setProperty('--dx', Math.round((r - 0.5) * 240) + 'px');
      m.style.setProperty('--dy', Math.round(-30 - r * 40) + 'px');
      m.style.setProperty('--rot', Math.round((r - 0.5) * 220) + 'deg');
      m.style.animationDelay = (0.5 + n * 0.12) + 's';
      m.innerHTML = '<img src="/brand/logo-oni.svg" alt="">';
      drips.appendChild(m);
    }
    bar.appendChild(drips);

    // 4. intro wipe with the course name, once per course per browser session
    try {
      var course = COURSES.filter(function (c) { return c.cn && c.match.test(path); })[0] || { cn: '妖怪', label: 'TRAINING' };
      var seen = 'yg-intro-' + course.label;
      if (!sessionStorage.getItem(seen)) {
        sessionStorage.setItem(seen, '1');
        var intro = document.createElement('div');
        intro.className = 'yg-intro';
        intro.innerHTML = '<img src="/brand/logo-oni.svg" alt=""><b class="k">' + course.cn + '</b><span class="t">YAOGUAI ' + course.label + '</span>';
        document.body.appendChild(intro);
        setTimeout(function () { intro.remove(); }, 1800);
      }
    } catch (e) { /* storage blocked: skip the intro */ }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();


// v5: motion layer shared by every course page (also runs on pages that render client-side)
(function () {
  var KANJI = ['妖怪', '网络', '系统', '代码', '密码', 'YAOGUAI'];
  var CARDS = '.module-card,.lesson-card,.card,.platform-card,.pathway-card,.stat-card,.progress-card';
  var io = null;
  if ('IntersectionObserver' in window) {
    io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.08 });
  }
  function ticker(hero) {
    if (document.querySelector('.ticker')) return; // the portal home already has its own ticker
    if (hero.nextElementSibling && hero.nextElementSibling.classList.contains('yg-ticker')) return;
    var one = '';
    KANJI.forEach(function (k, i) { one += '<span class="' + (i % 2 ? 'k' : '') + '">' + k + '</span>'; });
    var t = document.createElement('div');
    t.className = 'yg-ticker';
    t.setAttribute('aria-hidden', 'true');
    t.innerHTML = '<div>' + one + one + one + one + '</div>';
    hero.parentNode.insertBefore(t, hero.nextSibling);
  }
  function accent(hero) {
    if (hero.querySelector('.yg-accent')) return;
    var h = hero.querySelector('h1');
    if (!h) return;
    var em = h.querySelector('span,em');
    if (em) em.classList.add('yg-accent');
  }
  function scan() {
    var heroes = document.querySelectorAll('.hero,.dashboard-hero');
    for (var i = 0; i < heroes.length; i++) { ticker(heroes[i]); accent(heroes[i]); }
    var cs = document.querySelectorAll(CARDS);
    for (var j = 0; j < cs.length; j++) {
      var c = cs[j];
      if (c.dataset.ygRv || c.closest('#platforms')) continue;
      c.dataset.ygRv = '1';
      if (!io) continue;
      c.classList.add('yg-rv');
      c.style.transitionDelay = Math.min(j % 6, 5) * 70 + 'ms';
      io.observe(c);
    }
  }
  function dripFade() {
    var d = document.querySelector('.yg-drips');
    if (d) d.style.opacity = window.scrollY > 24 ? '0' : '1';
  }
  window.addEventListener('scroll', dripFade, { passive: true });
  var pending = false;
  function later() { if (pending) return; pending = true; setTimeout(function () { pending = false; scan(); }, 120); }
  function boot() {
    scan();
    new MutationObserver(later).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();

// Keep the brand stylesheet last in <head> so it wins over styles that scripts add later.
window.addEventListener('load', function () {
  var link = document.querySelector('link[href="/brand/yaoguai-brand.css"]');
  if (link) document.head.appendChild(link);
});
