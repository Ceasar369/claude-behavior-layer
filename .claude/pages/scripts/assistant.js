/* assistant.js — the assistant page's own script, on the contract.

   1100 draws the whole page, tools/assistant-page.py's drawn(), and live.js
   puts each change in place. This script keeps the view, the folds and the
   scroll I left, opens a stage once when words newly wait for my send, and
   sends each press.

   The page's buttons call it by name, as tab(), pressType() and unfold():
   lib/drive.py draws some of them too, for its own page as for this one.
   So each is set on the window, and a button 1100 draws later needs no
   wiring. It touches the screen only from live.ready, live.drawn and a
   press. */
(() => {
  'use strict';
  const items = () => document.getElementById('items');
  const main = () => document.querySelector('main');
  // The current stage, as 1100 last drew it: the team number and the Team
  // tab bring the page back to it.
  const opening = () => (items() && items().dataset.first) || 'all';

  // A fact shows once: while the active stage's own view shows, its heading
  // names the stage, and the team bar's name goes.
  const shown = window.tab;
  window.tab = k => {
    shown(k);
    const bar = document.querySelector('.tb-stage');
    if (bar) bar.classList.toggle('here', String(k) === bar.dataset.at);
  };

  // Auto-send's pills: the one pressed shows at once, and the switch is kept.
  window.autoSend = b => {
    document.querySelectorAll('#auto button').forEach(x => x.classList.toggle('on', x === b));
    live.post({act: 'auto', id: b.dataset.v}).then(got => { if (!got.ok) live.said(got.said); });
  };
  window.copy = b => {
    navigator.clipboard.writeText(b.previousElementSibling.textContent).then(() => {
      b.textContent = 'Copied'; b.classList.add('done');
      setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('done'); }, 1500);
    });
  };
  // A button that types. Never named typeIn: home hands my typing anywhere to
  // a page's window.typeIn, and this page takes none. Once Type typed a line,
  // the Send beside it presses Return alone, so the line goes with any words
  // I added, never typed twice.
  window.pressType = async (b, k, send, key, act) => {
    act = act || (key ? 'paste' : 'type');
    const pair = b.parentElement, mine = act + '|' + k + '|' + (key || '');
    const only = send && pair.dataset.typed === mine ? 'return' : '';
    const got = await live.pressed(b, {act, id: k, key: key || '', send: send ? 'yes' : '', only},
                                   {word: send ? '' : 'Typed', not: 'Not typed'});
    if (!got.ok) return;
    if (send) delete pair.dataset.typed;
    else pair.dataset.typed = mine;
  };
  // A folded line opens what it holds, and closes it again.
  window.unfold = b => {
    const open = b.getAttribute('aria-expanded') !== 'true';
    b.setAttribute('aria-expanded', open);
    b.nextElementSibling.classList.toggle('open', open);
  };
  // A session whose wave waits on me opens its Clarify tab, in 1100's home,
  // or its clarify page when this page stands alone.
  window.toClarify = nn => {
    if (parent !== window) parent.postMessage({ws: 1, open: 'clarify', nn}, '*');
    else location.href = '/p/clarify/' + nn;
  };
  // A chip opens its mission, and brings its item into view.
  window.jump = (k, n) => {
    tab(k);
    const h = document.querySelectorAll('#t-' + CSS.escape(k) + ' .ans h3')[n];
    if (!h) return;
    h.scrollIntoView({block: 'center'});
    h.classList.add('hit');
    setTimeout(() => h.classList.remove('hit'), 1600);
  };
  addEventListener('ws-home', () => tab(opening()));

  // The view stands: words newly waiting for my send open their stage once,
  // whatever view I left. Otherwise the view I picked stays, and a view the
  // plan no longer holds, as a mission gone with a new plan, opens the
  // current stage instead of a blank page.
  const DUE = 'due:' + location.pathname;
  function land() {
    if (!items()) return;
    const due = items().dataset.due;
    if (due && sessionStorage.getItem(DUE) !== due) {
      sessionStorage.setItem(DUE, due);
      return tab(opening());
    }
    const asked = decodeURIComponent(location.hash.slice(1));
    tab(asked && document.getElementById('t-' + asked) ? asked : opening());
  }

  // The one reload, on changed code, keeps my place while the view stays
  // the one I left: each fold I opened, and main's scroll. A hidden frame
  // has no scroll to keep, so it keeps the last, and takes it once it shows.
  const PLACE = 'place:' + location.pathname;
  addEventListener('beforeunload', () => {
    if (!innerWidth || !main()) return;
    sessionStorage.setItem(PLACE, JSON.stringify({view: location.hash, top: main().scrollTop,
      open: [...document.querySelectorAll('#items .item > .finl[aria-expanded="true"]')].map(b => b.parentNode.id),
      folds: [...document.querySelectorAll('#items h2.fold[aria-expanded="true"]')].map(h => h.id)}));
  });
  function back() {
    let was = null;
    try { was = JSON.parse(sessionStorage.getItem(PLACE) || 'null'); } catch (e) {}
    if (!was || was.view !== location.hash) return;
    (was.open || []).forEach(id => { const b = document.querySelector('#' + CSS.escape(id) + ' > .finl'); if (b) unfold(b); });
    (was.folds || []).forEach(id => { const h = document.getElementById(id); if (h) unfold(h); });
    const scroll = () => {
      if (!innerWidth) return;
      removeEventListener('resize', scroll);
      main().scrollTop = was.top;
    };
    addEventListener('resize', scroll);
    scroll();
  }

  live.ready(() => { land(); back(); });
  live.drawn(land);
})();
