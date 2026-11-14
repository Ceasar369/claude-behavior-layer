/* prototype.js — the Prototype page's own script, on the contract.

   1100 draws the page, tools/prototype-page.py's drawn(), beside every
   variation 1400 serves, and live.js puts each change in place and keeps
   my unsent feedback on this device. This script only moves about the
   page, picks, and sends: my pick, its looks and my feedback, typed into
   the session's pane. Nothing here decides whether that locks a variation
   in or opens a new generation.

   It reads the page's #proto data as 1100 last drew it: each variation's
   groups, route and direction, the first to show, and whether the session
   works now, which greys Send. My view, my pick and my looks are mine, so
   a change 1100 draws keeps them, until a newer generation than any this
   page has shown arrives: then the round starts again, on its first
   variation, as if loaded fresh. A send that landed empties the box. It
   touches the screen only from live.ready and live.drawn, and hears every
   click from the document. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const WORKING = 'Working. Send opens once its turn ends.';
  let D = {GROUPS: {}, ROUTES: {}, DIRECTIONS: {}, FIRST: '', BUSY: false, BASE: '/proto/'};
  /* cur is the view, pick the variation I chose, lk the look I chose in
     each group, as '1/v1|A': '1'. A group left out is open. */
  let cur = 'all', pick = '', lk = {}, sent = false;
  /* The newest generation this page has shown: FIRST's, as 3 for '3/v1'.
     Only one past it starts a new round, so a generation cut short, then
     mended, moves nothing. */
  const newest = () => parseInt(D.FIRST, 10) || 0;
  let high = 0;

  /* WebKit applies the page's zoom again inside a framed variation. Each
     frame undoes it, then a full variation zooms itself. Thumbnails keep
     their 1280 by 800 layout and scale with the page. */
  function zoomFrames() {
    const z = parseFloat(document.documentElement.style.zoom) || 1;
    document.querySelectorAll('#items iframe').forEach(f => {
      f.style.zoom = z === 1 ? '' : String(1 / z);
      if (f.closest('.thumb')) f.style.transform = `scale(${z / 4})`;
      else {
        try {
          const root = f.contentDocument && f.contentDocument.documentElement;
          if (root) root.style.zoom = z === 1 ? '' : String(z);
        } catch (e) {}
      }
    });
  }

  function show(k) {
    const item = $('t-' + k);
    if (!item) k = 'all';
    cur = k;
    tab(k);
    const f = $('f-' + k);
    if (f && !f.src) f.src = f.dataset.src;
    const from = ($('t-' + k) || {dataset: {}}).dataset.from;
    const bare = k === 'all' || k === 'pick';
    $('now').innerHTML = bare ? '' : 'G' + k.replace('/', ' · ')
      + `<span class="src">${from ? '  ←  ' + from : '  ·  fresh'}</span>`;
    $('all').disabled = k === 'all';
    $('alone').disabled = bare;
    if (k === 'pick') focusVar(pick || D.FIRST);
  }
  /* The frame beside the rows shows the variation I last clicked a row of.
     One whose file is gone shows its direction instead. */
  function focusVar(k) {
    if (!(k in D.ROUTES)) return;
    const f = $('pf'), st = $('ps');
    $('pc').textContent = 'G' + k.replace('/', ' · ');
    f.hidden = !D.ROUTES[k];
    st.hidden = !!D.ROUTES[k];
    if (D.ROUTES[k] && f.dataset.k !== k) { f.dataset.k = k; f.src = D.ROUTES[k]; }
    if (!D.ROUTES[k]) st.textContent = 'Reconstructed from the record — the file is gone. ' + D.DIRECTIONS[k];
  }
  function alone() {
    const f = $('f-' + cur);
    if (f) window.open(f.dataset.src, '_blank');
  }
  /* Every place a pick shows draws from pick and lk. */
  function paint() {
    document.querySelectorAll('.card, .item.v').forEach(el => el.classList.toggle('picked', el.dataset.k === pick));
    document.querySelectorAll('.opt.vo').forEach(el => el.classList.toggle('on', el.dataset.k === pick));
    document.querySelectorAll('.opt.lo').forEach(el =>
      el.classList.toggle('on', lk[el.dataset.k + '|' + el.dataset.g] === el.dataset.n));
    document.querySelectorAll('.ch.gr').forEach(el => el.classList.toggle('off', !!pick && el.dataset.k !== pick));
    sync();
  }
  function pickVar(k) { pick = pick === k ? '' : k; focusVar(k); paint(); }
  /* A look picked chooses its variation too. */
  function pickLook(k, g, n) {
    const id = k + '|' + g;
    lk[id] = lk[id] === n ? '' : n;
    if (lk[id]) pick = k;
    focusVar(k);
    paint();
  }
  const unpicked = () => (D.GROUPS[pick] || []).filter(g => !lk[pick + '|' + g]);
  const chosen = () => (D.GROUPS[pick] || []).map(g => g + ':' + (lk[pick + '|' + g] || '')).join(',');

  function fit() {
    const t = $('fb'), b = $('pbar');
    if (!t) return;
    const open = document.activeElement === t || !!t.value.trim();
    b.classList.toggle('open', open);
    t.style.height = 'auto';
    t.style.height = (open ? Math.max(t.scrollHeight + 4, 84) : 40) + 'px';
  }
  /* Send names what it types: a pick with every group picked, a pick with
     groups still open, or my words alone. Greyed while the session works.
     Once sent, it stays Sent until a new round. */
  function sync() {
    const t = $('fb'), b = $('send');
    if (!t || !b || sent) return;
    const note = t.value.trim(), left = unpicked().length, word = left ? left + ' open' : 'lock in';
    b.disabled = D.BUSY || (!pick && !note);
    if (D.BUSY) b.title = WORKING;
    else if (b.title === WORKING) b.removeAttribute('title');
    b.textContent = pick && note ? (left ? 'Send · ' + word + ', with feedback' : 'Send · with feedback')
      : pick ? 'Send · ' + word : note ? 'Send · feedback only' : 'Send';
  }
  async function send() {
    const b = $('send'), t = $('fb');
    b.classList.add('busy');
    b.disabled = true;
    // A press reaches 1100 with no query, so it names its session itself.
    const session = new URLSearchParams(location.search).get('session') || '';
    const got = await live.post({act: 'send', session, pick, looks: chosen(), feedback: t.value}, location.pathname);
    b.classList.remove('busy');
    if (got.ok) {
      sent = true;
      t.value = '';
      live.sent(t);
      fit();
      b.classList.add('sent');
      b.textContent = 'Sent';
      return;
    }
    b.classList.add('gone');
    b.title = got.said;
    b.textContent = 'Try again';
    b.disabled = false;
    live.said(got.said);
  }
  function read() { try { D = JSON.parse($('proto').textContent); } catch (e) {} }
  /* A new round: no pick, no looks, Send open again, the view on the
     newest generation's first variation. My unsent words stay. */
  function round() {
    pick = '';
    lk = {};
    sent = false;
    const b = $('send');
    if (b) { b.classList.remove('sent', 'gone'); b.removeAttribute('title'); }
    show(D.FIRST);
  }
  /* The hash names a variation, as 2/v3, or pick: the app door's show_page sets it. */
  const hashed = () => show(decodeURIComponent(location.hash.slice(1)) || 'all');

  document.addEventListener('click', e => {
    const t = e.target.closest('.pick, .thumb, .opt.vo, .opt.lo, nav.nums .tab[data-k], #all, #alone, #send, #back');
    if (!t) return;
    if (t.id === 'back') location.href = D.BASE;
    else if (!$('proto')) return;
    else if (t.id === 'all') show('all');
    else if (t.id === 'alone') alone();
    else if (t.id === 'send') send();
    else if (t.matches('.pick')) pickVar(t.closest('[data-k]').dataset.k);
    else if (t.matches('.thumb')) show(t.closest('.card').dataset.k);
    else if (t.matches('.opt.vo')) pickVar(t.dataset.k);
    else if (t.matches('.opt.lo')) pickLook(t.dataset.k, t.dataset.g, t.dataset.n);
    else show(t.dataset.k);
  });
  document.addEventListener('input', e => { if (e.target.id === 'fb') { fit(); sync(); } });
  document.addEventListener('focusin', e => { if (e.target.id === 'fb') fit(); });
  document.addEventListener('focusout', e => { if (e.target.id === 'fb') fit(); });
  document.addEventListener('load', e => { if (e.target.tagName === 'IFRAME') zoomFrames(); }, true);
  addEventListener('ws-zoom', zoomFrames);
  addEventListener('hashchange', hashed);

  live.ready(() => {
    read();
    high = newest();
    zoomFrames();
    if (!$('proto')) return;
    sync();
    fit();
    hashed();
  });
  /* 1100 drew the page again: its data is read again, and my view, my
     pick and my looks stand on it. A variation gone hands the view back to
     all. A newer generation starts a new round. */
  live.drawn(() => {
    read();
    zoomFrames();
    if (!$('proto')) return;
    if (newest() > high) { high = newest(); round(); }
    if (pick && !(pick in D.ROUTES)) pick = '';
    show(cur);
    paint();
    fit();
  });
})();
