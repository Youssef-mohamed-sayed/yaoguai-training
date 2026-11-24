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

    // 3. blood drips under the bar
    var drips = document.createElement('div');
    drips.className = 'yg-drips';
    var positions = [4, 11, 19, 27, 36, 44, 53, 61, 70, 78, 87, 95];
    var heights = [18, 30, 38, 24, 34, 20, 40, 26, 36, 18, 32, 24];
    positions.forEach(function (p, n) {
      var d = document.createElement('i');
      d.style.left = p + '%';
      d.style.height = heights[n] + 'px';
      d.style.animationDelay = (0.9 + n * 0.22) + 's';
      drips.appendChild(d);
    });
    bar.appendChild(drips);

    // 4. intro wipe, only the first page of a browser session
    try {
      if (!sessionStorage.getItem('yg-intro')) {
        sessionStorage.setItem('yg-intro', '1');
        var intro = document.createElement('div');
        intro.className = 'yg-intro';
        intro.innerHTML = '<img src="/brand/logo-mask.svg" alt="">';
        document.body.appendChild(intro);
        setTimeout(function () { intro.remove(); }, 1800);
      }
    } catch (e) { /* storage blocked: skip the intro */ }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();

// Keep the brand stylesheet last in <head> so it wins over styles that scripts add later.
window.addEventListener('load', function () {
  var link = document.querySelector('link[href="/brand/yaoguai-brand.css"]');
  if (link) document.head.appendChild(link);
});
