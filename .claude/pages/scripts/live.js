/* live.js — what every page on the contract shares. .claude/lib/live.py's
   watch() loads it first in the page, before any script of the page's own.

   A page loads once. From then on 1100 says when its picture moved. The
   page fetches the new picture, off screen, and compares it with the last
   picture 1100 sent. Only what 1100 changed between the two is put in
   place. What I opened, typed or scrolled is not 1100's, so it stays.

   The last picture is kept off screen, and each of its nodes knows the
   node on screen that stands for it. So a page's own script may add to
   the screen freely, and a change still lands on the right node. It takes
   one rule: a page's script touches the screen only from live.ready(),
   never while the page loads. A block holding my words or my place
   carries an id, so it is found again wherever 1100 moves it.

   A box holding my cursor is never redrawn, nor one holding words 1100
   has not drawn yet: a field, or an element whose words I edit in place.
   Untouched under my cursor, it takes 1100's words once the cursor
   leaves. My unsent words wait on this device from the first
   keystroke, under their session's id, and come back after a reload, a
   restart of 1100 or a crash. A box that saves its own words tells
   live.sent() once they landed.

   A press carries an id of its own, so one sent again acts once.

   The page reloads in one case only: the picture's own code changed. It
   waits until I stop typing, and my words come back.

   A page 1100's home frames hands its watch up to home, which holds one
   request for every page it shows. Alone, a page holds its own, only
   while it shows. Unanswered for five seconds, it says so in one line.

   What it gives a page's own script, as window.live:
     ready(fn)            fn() once the page stands as 1100 drew it
     drawn(fn)            fn(nodes) after each change is put in place
     post(data, to)       one press: {ok, said}; ok is null when unanswered
     pressed(b, data, o)  a button's whole press, as the shell shows it
     said(line)           one sentence along the page's foot, or none
     now()                the page, brought in line with 1100 at once
     sent(box)            this box's words landed: nothing of it waits
     drawnAs(node)        the node of the last picture a node stands for
*/
(() => {
  'use strict';
  if (window.live) return;

  const nap = ms => new Promise(done => setTimeout(done, ms));
  const here = () => document.getElementById('watch');
  const address = () => location.pathname + location.search;
  const FIELD = 'input, textarea, select, [contenteditable]';
  const port = location.port || '1100';

  // ---- the last picture, and what stands for it on screen ------------------

  let last = null;
  const shown = new WeakMap(), pictured = new WeakMap();
  function pair(l, s) {
    shown.set(l, s);
    pictured.set(s, l);
    for (let a = l.firstChild, b = s.firstChild; a && b; a = a.nextSibling, b = b.nextSibling) pair(a, b);
  }
  // The node on screen that stands for a node of the picture. While words
  // I edit in place are brought up to date, the picture alone moves on,
  // and nothing on screen stands for it: quiet.
  let quiet = 0;
  const screen = x => quiet ? undefined : shown.get(x);

  // Whether a node on screen holds my cursor, in a box I type in.
  function holds(s) {
    const f = document.activeElement;
    return !!f && f !== document.body && s.nodeType === 1 && s.contains(f) && f.matches(FIELD);
  }

  // ---- a box, as the picture gives it and as it stands -----------------------

  // A box is a field, or an element whose own words I edit in place.
  const FIELDS = 'input, textarea, select', WORDS = '[contenteditable]:not([contenteditable="false"])';
  const words = f => !f.matches(FIELDS) && f.matches(WORDS);
  const boxed = f => f.type === 'checkbox' || f.type === 'radio';
  const picked = f => [...f.selectedOptions].map(o => o.value).join('\n');
  // A clone carries what was typed into it, so the picture's own value is
  // read from its attributes and text alone.
  const given = f => words(f) ? f.innerHTML : f.tagName === 'SELECT' ? picked(f) : boxed(f) ? String(f.defaultChecked) : f.defaultValue;
  const current = f => words(f) ? f.innerHTML : f.tagName === 'SELECT' ? picked(f) : boxed(f) ? String(f.checked) : f.value;
  // A box, put as the last picture gives it.
  function settle(s) {
    if (words(s)) { const l = pictured.get(s); s.innerHTML = l.innerHTML; pair(l, s); }
    else if (s.tagName === 'SELECT') for (const o of s.options) o.selected = o.defaultSelected;
    else if (boxed(s)) s.checked = s.defaultChecked;
    else s.value = s.defaultValue;
  }

  // What gives an input its words: left as it stands on screen while my
  // cursor is in it.
  const HELD = ['value', 'checked'];
  // A box 1100 changed under my cursor, brought in line once the cursor
  // left. `was` is what it stood as when 1100 first changed it, null when
  // it already held my own words. Untouched, it takes 1100's words.
  // Touched, a field keeps mine over what 1100 now draws beneath, and
  // words in place wait until 1100 draws them.
  function refit(box, was) {
    const l = pictured.get(box), mine = current(box), untouched = was !== null && mine === was;
    if (!l) return;
    if (words(box)) { if (untouched) settle(box); return; }
    if (box.tagName === 'INPUT') {
      for (const a of HELD) { if (l.hasAttribute(a)) box.setAttribute(a, l.getAttribute(a)); else box.removeAttribute(a); }
    } else { box.innerHTML = l.innerHTML; pair(l, box); }
    if (untouched) settle(box);
    else if (box.tagName === 'SELECT') { const kept = mine.split('\n'); for (const o of box.options) o.selected = kept.includes(o.value); }
    if (drafted(box)) keep(box);
  }
  // What left the picture while it held my cursor goes once the cursor
  // does, and each box 1100 changed under it is brought in line: `later`.
  const owed = new Set(), later = new Map();
  document.addEventListener('focusout', () => setTimeout(() => {
    for (const s of owed) if (!holds(s)) { s.remove(); owed.delete(s); }
    for (const [box, was] of later) {
      if (holds(box)) continue;
      later.delete(box);
      if (!box.isConnected) continue;
      refit(box, was);
      for (const fn of drawers) { try { fn([box]); } catch (e) { console.error(e); } }
    }
  }));

  // ---- putting a new picture in place ----------------------------------------

  const keyed = x => x.nodeType === 1 && !!x.id;
  const named = x => x.nodeName + '#' + x.id;
  const alike = (a, b) => a.nodeType === b.nodeType && a.nodeName === b.nodeName && (a.nodeType !== 1 || a.id === b.id);
  const tokens = v => new Set((v || '').split(/\s+/).filter(Boolean));
  // How far along its siblings an unchanged node is looked for.
  const NEAR = 16;

  // One attribute 1100 changed, on screen. A class changes word by word and
  // a style line by line, so what a script added there stays.
  function mirror(s, l, want, a, was) {
    if (a.namespaceURI === null && a.name === 'class') {
      const old = tokens(was), now = tokens(a.value);
      for (const t of now) if (!old.has(t)) s.classList.add(t);
      for (const t of old) if (!now.has(t)) s.classList.remove(t);
    } else if (a.namespaceURI === null && a.name === 'style' && s.style && l.style && want.style
               && (want.style.length || !a.value.trim())) {
      const old = l.style, now = want.style;
      for (const p of now) {
        if (old.getPropertyValue(p) !== now.getPropertyValue(p) || old.getPropertyPriority(p) !== now.getPropertyPriority(p)) {
          s.style.setProperty(p, now.getPropertyValue(p), now.getPropertyPriority(p));
        }
      }
      for (const p of [...old]) if (!now.getPropertyValue(p)) s.style.removeProperty(p);
    } else s.setAttributeNS(a.namespaceURI, a.name, a.value);
  }
  function unmirror(s, l, a) {
    if (a.namespaceURI === null && a.name === 'class') for (const t of tokens(a.value)) s.classList.remove(t);
    else if (a.namespaceURI === null && a.name === 'style' && s.style && l.style && l.style.length) {
      for (const p of [...l.style]) s.style.removeProperty(p);
    } else s.removeAttributeNS(a.namespaceURI, a.localName);
  }
  // The root's own attributes are the shell's scripts': its zoom, its frame.
  // `held`, an input my cursor is in: what gives it its words stays as it
  // stands on screen, and the picture alone takes the change.
  function attributes(l, want, s, held) {
    let touched = false;
    const mirrored = a => s && l !== last && !(held && a.namespaceURI === null && HELD.includes(a.name));
    for (const a of [...want.attributes]) {
      const was = l.getAttributeNS(a.namespaceURI, a.localName);
      if (was === a.value) continue;
      if (mirrored(a)) { mirror(s, l, want, a, was); touched = true; }
      l.setAttributeNS(a.namespaceURI, a.name, a.value);
    }
    for (const a of [...l.attributes]) {
      if (want.hasAttributeNS(a.namespaceURI, a.localName)) continue;
      if (mirrored(a)) { unmirror(s, l, a); touched = true; }
      l.removeAttributeNS(a.namespaceURI, a.localName);
    }
    return touched;
  }

  // The node on screen for x, put where x stands among l's children: before
  // the next one 1100 drew that still stands there, else after the one before.
  function place(l, x) {
    const p = screen(l), s = screen(x);
    if (!p || !s) return;
    for (let y = x.nextSibling; y; y = y.nextSibling) {
      const t = screen(y);
      if (t && t.parentNode === p) { if (s.nextSibling !== t) p.insertBefore(s, t); return; }
    }
    for (let y = x.previousSibling; y; y = y.previousSibling) {
      const t = screen(y);
      if (t && t.parentNode === p) { if (t.nextSibling !== s) p.insertBefore(s, t.nextSibling); return; }
    }
    p.appendChild(s);
  }
  function insert(l, want, before, out) {
    const x = document.importNode(want, true);
    l.insertBefore(x, before);
    if (!screen(l)) return;
    const s = x.cloneNode(true);
    pair(x, s);
    place(l, x);
    out.add(s);
  }
  function remove(x) {
    const s = screen(x);
    x.remove();
    if (s && s.parentNode) { if (holds(s)) owed.add(s); else s.remove(); }
  }
  // m, found further along, comes to stand before c. What holds my cursor
  // never moves: what stood before it steps behind it instead.
  function hoist(l, m, c) {
    const s = screen(m);
    if (s && holds(s)) {
      const after = m.nextSibling;
      for (let x = c; x !== m;) { const next = x.nextSibling; l.insertBefore(x, after); place(l, x); x = next; }
    } else { l.insertBefore(m, c); place(l, m); }
  }
  // The node of the last picture `want` takes the place of, from c on. A
  // node with an id is found wherever it stands. Any other is one standing
  // unchanged nearby, else the one at c, unless that one stands unchanged
  // further along the new picture: `want` is new then.
  function match(want, c, mine) {
    if (keyed(want)) return mine.get(named(want)) || null;
    let x = c;
    for (let i = 0; x && i < NEAR; x = x.nextSibling, i++) if (!keyed(x) && x.isEqualNode(want)) return x;
    if (!c || keyed(c) || !alike(c, want)) return null;
    let y = want.nextSibling;
    for (let i = 0; y && i < NEAR; y = y.nextSibling, i++) if (c.isEqualNode(y)) return null;
    return c;
  }
  function children(l, n, out) {
    const mine = new Map(), theirs = new Set();
    for (let x = l.firstChild; x; x = x.nextSibling) if (keyed(x)) mine.set(named(x), x);
    for (let x = n.firstChild; x; x = x.nextSibling) if (keyed(x)) theirs.add(named(x));
    let c = l.firstChild;
    for (let want = n.firstChild; want; want = want.nextSibling) {
      // A node with an id that the new picture no longer holds goes first.
      while (c && keyed(c) && !theirs.has(named(c))) { const gone = c; c = c.nextSibling; remove(gone); }
      const m = match(want, c, mine);
      if (!m) { insert(l, want, c, out); continue; }
      if (keyed(m)) mine.delete(named(m));
      if (m !== c) {
        // What stands between c and m goes, when the new picture holds
        // none of it further along. Otherwise m comes forward.
        let spare = true, x = c;
        for (; x && x !== m && spare; x = x.nextSibling) spare = keyed(x) ? !theirs.has(named(x)) : !further(want, x);
        if (spare && x === m) while (c !== m) { const gone = c; c = c.nextSibling; remove(gone); }
        else hoist(l, m, c);
      }
      if (m === c) c = c.nextSibling;
      sync(m, want, out);
    }
    while (c) { const gone = c; c = c.nextSibling; remove(gone); }
  }
  // Whether x, of the last picture, stands unchanged after `want` in the new one.
  function further(want, x) {
    for (let y = want.nextSibling; y; y = y.nextSibling) if (!keyed(y) && y.isEqualNode(x)) return true;
    return false;
  }
  // l, a node of the last picture, made the same as `want`, and each change
  // put on the node on screen that stands for l.
  function sync(l, want, out) {
    const s = screen(l);
    if (l.nodeType !== 1) {
      if (l.data === want.data) return;
      l.data = want.data;
      if (s) { s.data = want.data; if (s.parentElement) out.add(s.parentElement); }
      return;
    }
    if (l.isEqualNode(want)) return;
    const box = s && (s.matches(FIELDS) || words(s)) ? s : null;
    if (!box) {
      if (attributes(l, want, s)) out.add(s);
      return children(l, want, out);
    }
    // A box under my cursor is left alone, whatever it is, and so are words
    // in place that 1100 has not drawn: the picture alone moves on, and what
    // gives the box its words stays as it stands on screen.
    const before = given(l), stood = current(box), cursor = holds(box);
    const mine = cursor || (words(box) && stood !== before);
    if (attributes(l, want, s, mine && box.tagName === 'INPUT')) out.add(s);
    if (mine && box.tagName !== 'INPUT') {
      quiet++;
      try { children(l, want, out); } finally { quiet--; }
    } else children(l, want, out);
    if (given(l) === before) return;
    if (!mine) {
      // Out of my cursor, a field holding nothing 1100 had not drawn takes
      // 1100's words. Words in place just did, as any part does.
      if (!words(box) && stood === before) { settle(box); out.add(box); }
    } else if (words(box) && current(box) === given(l)) pair(l, box);
    else if (cursor && !later.has(box)) later.set(box, stood === before ? before : null);
    // Words 1100 now draws wait no more.
    if (drafted(box)) keep(box);
  }

  // My place: the node my cursor is in, else the first one showing in the
  // page's main, held where it stands while the page changes around it.
  function hold() {
    let a = document.activeElement;
    if (!a || a === document.body || !a.getClientRects().length) {
      const m = document.querySelector('main') || document.body, r = m.getBoundingClientRect();
      a = null;
      for (const dy of [8, 24, 48, 96]) {
        const e = document.elementFromPoint(r.left + r.width / 2, r.top + dy);
        if (e && e !== m && m.contains(e)) { a = e; break; }
      }
    }
    return a ? {a, top: a.getBoundingClientRect().top} : null;
  }
  function release(h) {
    if (!h || !h.a.isConnected) return;
    const off = () => h.a.getBoundingClientRect().top - h.top, d = off();
    if (Math.abs(d) < 0.5) return;
    for (let p = h.a.parentElement; p; p = p.parentElement) {
      if (p.scrollHeight <= p.clientHeight || !/auto|scroll/.test(getComputedStyle(p).overflowY)) continue;
      // A zoomed page measures and scrolls in two units: the first step
      // tells their ratio, the second lands.
      const was = p.scrollTop;
      p.scrollTop = was + d;
      const took = p.scrollTop - was, left = off();
      if (took && Math.abs(left) >= 0.5 && d !== left) p.scrollTop += left * took / (d - left);
      return;
    }
  }

  const drawers = [];
  function put(next) {
    const spot = hold(), out = new Set();
    sync(last, next.documentElement, out);
    if (!last.isEqualNode(next.documentElement)) throw new Error('the picture kept differs from the one put in place');
    release(spot);
    restore([...out]);
    for (const fn of drawers) { try { fn([...out]); } catch (e) { console.error(e); } }
  }

  // ---- my unsent words ---------------------------------------------------------

  const DRAFT = 'draft:', OLD = 30 * 86400 * 1000;
  const drafted = f => !!f.matches && f.matches('textarea, input:not([type]), input[type=text], input[type=search]')
    && !!(f.id || f.name) && f.dataset.draft !== 'no';
  const slot = f => DRAFT + ((here() && here().dataset.session) || 'page') + ':' + location.pathname + ':' + (f.id || f.name);
  function keep(f) {
    try {
      if (f.value === f.defaultValue) localStorage.removeItem(slot(f));
      else localStorage.setItem(slot(f), JSON.stringify({v: f.value, at: Date.now()}));
    } catch (e) {}
  }
  addEventListener('input', e => { if (drafted(e.target)) keep(e.target); }, true);
  // Each box under `roots` takes back the words that wait for it, and says
  // so as a keystroke would, so the page's own script sizes and saves it.
  function restore(roots) {
    for (const root of roots) {
      if (root.nodeType !== 1) continue;
      for (const f of [root, ...root.querySelectorAll('textarea, input')]) {
        if (!drafted(f)) continue;
        let d = null;
        try { d = JSON.parse(localStorage.getItem(slot(f)) || 'null'); } catch (e) {}
        if (!d || typeof d.v !== 'string') continue;
        if (d.v === f.defaultValue) { try { localStorage.removeItem(slot(f)); } catch (e) {} continue; }
        if (f.value !== d.v && f !== document.activeElement) {
          f.value = d.v;
          f.dispatchEvent(new Event('input', {bubbles: true}));
        }
      }
    }
  }
  function prune() {
    try {
      for (const k of Object.keys(localStorage)) {
        if (!k.startsWith(DRAFT)) continue;
        let d = null;
        try { d = JSON.parse(localStorage.getItem(k)); } catch (e) {}
        if (!d || !(Date.now() - d.at < OLD)) localStorage.removeItem(k);
      }
    } catch (e) {}
  }

  // ---- one sentence along the foot, and one line when 1100 is silent ----------

  let saidTimer = 0;
  function said(line) {
    let p = document.getElementById('refusal');
    if (!p && !line) return;
    if (!p) {
      p = document.createElement('p');
      p.id = 'refusal';
      p.className = 'refusal';
      p.setAttribute('role', 'status');
      document.body.appendChild(p);
    }
    clearTimeout(saidTimer);
    p.textContent = line;
    p.hidden = !line;
    if (line) saidTimer = setTimeout(() => { p.hidden = true; }, 8000);
  }
  // Behind since when, and why: 1100 silent, or a new picture that would
  // not come. Five seconds of either, and one line along the top says so.
  const since = {silent: 0, stuck: 0};
  function away(why, is) {
    since[why] = is ? since[why] || Date.now() : 0;
    let p = document.getElementById('away');
    const worst = ['silent', 'stuck'].find(k => since[k] && Date.now() - since[k] >= 5000);
    if (!worst) { if (p) p.hidden = true; return; }
    if (!p) {
      p = document.createElement('p');
      p.id = 'away';
      p.className = 'refusal';
      p.style.cssText = 'top:12px;bottom:auto';
      p.setAttribute('role', 'status');
      document.body.appendChild(p);
    }
    p.textContent = port + (worst === 'silent' ? ' is not answering.' : ' cannot draw this page now.') + ' What shows here may be old.';
    p.hidden = false;
  }

  // ---- the one reload ------------------------------------------------------------

  // Every script a picture runs: its address, or its own text. Data in a
  // JSON script is no code.
  const code = doc => [...doc.querySelectorAll('script')].filter(s => !/json/i.test(s.type))
    .map(s => s.getAttribute('src') || s.textContent).join('\u0000');
  let reloading = null;
  function reload() {
    return reloading = reloading || (async () => {
      while (Date.now() - (window.typedAt || 0) < 3000) await nap(500);
      const K = 'reloads:' + location.pathname;
      let at = [];
      try { at = JSON.parse(sessionStorage.getItem(K) || '[]').filter(t => Date.now() - t < 60000); } catch (e) {}
      const due = at.length ? at[at.length - 1] + Math.min(15000, 1000 * 2 ** (at.length - 1)) : 0;
      if (due > Date.now()) await nap(due - Date.now());
      try { sessionStorage.setItem(K, JSON.stringify([...at, Date.now()])); } catch (e) {}
      location.reload();
      await new Promise(() => {});
    })();
  }

  // ---- told it moved ------------------------------------------------------------

  // One new picture at a time, five a second at most. While one is fetched
  // the watch reads busy, so home asks about this page once a second, not
  // without pause. A picture that will not come is asked for ever slower.
  let moving = null, movedAt = 0, fails = 0, same = 0;
  function moved() {
    if (reloading) return reloading;
    return moving = moving || (async () => {
      const w = here();
      if (w) w.dataset.busy = '';
      let keepBusy = false;
      try {
        const wait = 200 - (Date.now() - movedAt);
        if (wait > 0) await nap(wait);
        movedAt = Date.now();
        const r = await fetch(address(), {cache: 'no-store'});
        if (!r.ok) { away('stuck', true); throw new Error('answered ' + r.status); }
        const next = new DOMParser().parseFromString(await r.text(), 'text/html');
        const mark = next.getElementById('watch');
        if (!mark || code(next) !== code(last)) { keepBusy = true; return await reload(); }
        // Told it moved, and nothing had: three times running, it waits.
        same = last.isEqualNode(next.documentElement) ? same + 1 : 0;
        if (same >= 3) await nap(15000);
        // The page is now about another session: my unsent words leave the
        // screen and wait under their own session, and this one's come back.
        const other = !!here() && mark.dataset.session !== here().dataset.session;
        if (other) for (const f of document.querySelectorAll('textarea, input')) if (drafted(f)) settle(f);
        try { put(next); } catch (e) { console.error(e); keepBusy = true; return await reload(); }
        if (other) restore([document.body]);
        if (here()) here().dataset.key = mark.dataset.key;
        fails = 0;
        away('stuck', false);
      } catch (e) {
        fails++;
        await nap(Math.min(15000, 1000 * 2 ** (fails - 1)));
      } finally {
        if (!keepBusy && here()) delete here().dataset.busy;
        moving = null;
      }
    })();
  }

  // Alone, a page holds its own watch, only while it shows. Shown again,
  // or back on the network, it asks at once.
  let ask = null;
  const again = () => { if (ask) ask.abort(); };
  async function watching() {
    for (;;) {
      const w = here();
      if (!w) return;
      if (document.hidden) {
        await new Promise(done => document.addEventListener('visibilitychange', done, {once: true}));
        continue;
      }
      ask = new AbortController();
      try {
        // After a silence, one quick ask says 1100 is back: a held watch
        // answers only once something moves.
        if (since.silent) { await fetch('/health', {signal: ask.signal, cache: 'no-store'}); away('silent', false); }
        const r = await fetch('/heard?key=' + encodeURIComponent(w.dataset.key) + '&path=' + encodeURIComponent(address()),
                              {signal: ask.signal, cache: 'no-store'});
        if (r.headers.get('X-Heard')) {
          away('silent', false);
          const now = (await r.text()).split('\n')[0];
          if (here() && now !== here().dataset.key) await moved(); else away('stuck', false);
          continue;
        }
        // Busy, or a server that cannot hold a watch: asked again in a moment.
        await nap(2000);
        continue;
      } catch (e) {
        if (ask.signal.aborted) continue;
      }
      away('silent', true);
      await nap(1000);
    }
  }
  document.addEventListener('visibilitychange', again);
  addEventListener('pageshow', again);
  addEventListener('online', again);

  // ---- a press --------------------------------------------------------------------

  const UNANSWERED = port + ' did not answer. Nothing was done.';
  // One press, sent with an id of its own: sent again after a silence, it
  // still acts once. Done, refused in a sentence, or unanswered.
  async function post(data, to) {
    const body = new URLSearchParams(data);
    body.set('press', crypto.randomUUID ? crypto.randomUUID() : Date.now() + '-' + Math.random().toString(36).slice(2));
    for (let tries = 0; tries < 3; tries++) {
      try {
        const r = await fetch(to || location.pathname, {method: 'POST', redirect: 'manual', body});
        if (r.type === 'opaqueredirect') return {ok: true, said: ''};
        if (r.ok) return {ok: true, said: await r.text()};
        if (r.status === 409) return {ok: false, said: await r.text()};
      } catch (e) {}
      await nap(1000);
    }
    return {ok: null, said: UNANSWERED};
  }
  // A button's whole press, as the shell shows it: greyed while it is
  // sent, green for a moment once done, and red with its sentence along the
  // foot until pressed again. `o.word` is what it reads while green, and
  // `o.not` while red.
  async function pressed(b, data, o = {}) {
    if ('was' in b.dataset) { b.innerHTML = b.dataset.was; b.title = b.dataset.tip; delete b.dataset.was; delete b.dataset.tip; }
    b.classList.remove('gone');
    said('');
    b.disabled = true;
    const got = await post(data, o.to);
    const l = pictured.get(b);
    b.disabled = !!l && l.hasAttribute('disabled');
    if (got.ok) {
      const was = b.innerHTML;
      if (o.word) b.textContent = o.word;
      b.classList.add('done');
      setTimeout(() => {
        if (o.word && b.textContent === o.word) b.innerHTML = was;
        b.classList.remove('done');
      }, 1500);
    } else {
      b.dataset.was = b.innerHTML;
      b.dataset.tip = b.title;
      b.textContent = o.not || 'Not done';
      b.title = got.said;
      b.classList.add('gone');
      said(got.said);
    }
    return got;
  }

  // ---- the page stands -------------------------------------------------------------

  const waiting = [];
  let standing = false;
  function run(fn) { try { fn(); } catch (e) { console.error(e); } }
  window.live = {
    ready: fn => { if (standing) run(fn); else waiting.push(fn); },
    drawn: fn => { drawers.push(fn); },
    post, pressed, said,
    now: async () => { if (moving) await moving; await moved(); },
    sent: box => { try { localStorage.removeItem(slot(box)); } catch (e) {} },
    drawnAs: node => pictured.get(node) || null,
  };
  function stand() {
    last = document.documentElement.cloneNode(true);
    pair(last, document.documentElement);
    prune();
    standing = true;
    for (const fn of waiting.splice(0)) run(fn);
    restore([document.body]);
    window.told = () => moved();
    let framed = false;
    try { framed = parent !== window && typeof parent.watchFor === 'function'; } catch (e) {}
    if (framed) parent.watchFor(window); else watching();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', stand, {once: true});
  else setTimeout(stand);
})();
