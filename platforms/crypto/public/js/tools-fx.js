/* Crypto tools page: small visual helpers. They only add classes, they never touch the tool logic. */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };

  // 1. stagger the sidebar items and mark the API chip state
  function stagger() {
    var items = document.querySelectorAll('#tools-list > *');
    for (var i = 0; i < items.length; i++) items[i].style.animationDelay = (0.25 + i * 0.035) + 's';
  }
  function chip() {
    var c = $('api-status'); if (!c) return;
    var t = (c.textContent || '').toLowerCase();
    c.setAttribute('data-state', /offline|fail|error|down/.test(t) ? 'bad' : /check|\.\.\.|…/.test(t) ? 'wait' : 'ok');
  }
  var list = $('tools-list');
  if (list) new MutationObserver(stagger).observe(list, { childList: true });
  stagger();
  var cs = $('api-status');
  if (cs) { new MutationObserver(chip).observe(cs, { childList: true, characterData: true, subtree: true }); chip(); }

  // 2. replay the entrance animation whenever the tool changes
  var title = $('tool-title'), main = document.querySelector('.tools-main'), last = title && title.textContent;
  function swap() {
    if (!main || !title || title.textContent === last) return;
    last = title.textContent;
    main.classList.remove('fx-swap'); void main.offsetWidth; main.classList.add('fx-swap');
  }
  if (title) new MutationObserver(swap).observe(title, { childList: true, characterData: true, subtree: true });

  // 3. flash the output box when a result lands, show a loading bar on the Run button
  var out = $('output'), msg = $('msg'), run = $('run-btn');
  function flash() { if (!out) return; out.classList.remove('fx-result'); void out.offsetWidth; out.classList.add('fx-result'); }
  if (out) {
    var d = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value');
    if (d && d.set) Object.defineProperty(out, 'value', {
      configurable: true,
      get: function () { return d.get.call(this); },
      set: function (v) { var old = d.get.call(this); d.set.call(this, v); if (v && v !== old) flash(); }
    });
  }
  if (run) {
    run.addEventListener('click', function () {
      run.classList.add('fx-busy');
      setTimeout(function () { run.classList.remove('fx-busy'); }, 900);
    });
  }
  if (msg && run) new MutationObserver(function () { run.classList.remove('fx-busy'); }).observe(msg, { childList: true, characterData: true, subtree: true });
})();
