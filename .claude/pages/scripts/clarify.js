/* clarify.js — the clarify page's own script, on the contract.

   1100 draws every item, tools/clarify-page.py's drawn(), and live.js puts
   each change in place. This script only moves about the page, saves my
   words as I type them, sends each press, and draws what the browser alone
   can: the charts, charts.js's, and each box's size.

   It reads my answers as 1100 last drew them from the page's #wave data.
   What I did since, and 1100 has not drawn yet, wins: a box's own words,
   and an Agree just pressed. It touches the screen only from live.ready
   and live.drawn, and hears every click and key from the document, so an
   item 1100 draws later needs no wiring. */
(() => {
  'use strict';
  const PHONE = matchMedia('(hover: none) and (pointer: coarse)').matches;
  const NOT_TYPED = 'Not typed';
  const HINT = ': type or paste anywhere. Return moves on, and sends once all are answered. Shift+Return makes a new line.';
  const $ = id => document.getElementById(id);
  const main = () => document.querySelector('main');
  const boxOf = n => $('fb-' + n);

  /* The wave's answers as 1100 last drew them, and each Agree pressed
     that 1100 has not drawn yet. */
  let D = {wave: 0, sent: '', key: '', items: []};
  const agreeing = {};
  const find = n => D.items.find(it => it.n === String(n));
  const locked = it => it.status === 'agreed';
  const words = it => { const t = boxOf(it.n); return t ? t.value : it.feedback || ''; };
  const agreed = it => locked(it) || (it.n in agreeing ? agreeing[it.n] : it.agree) === 'yes';
  /* This page's own colours, per wave. Red: feedback given, and it always
     wins. Green: agreed. Grey: unanswered. */
  const colour = it => words(it) ? 'red' : agreed(it) ? 'green' : 'grey';
  const answered = it => colour(it) !== 'grey';
  function parts(it) {
    const [verdict, ...rest] = String(it.proposed || '').split('\n');
    return {v: verdict.trim().toLowerCase(),
            words: rest.filter(l => l.startsWith('>')).map(l => l.replace(/^>\s?/, '')).join('\n')};
  }
  /* An assistant's proposal outlines a number still grey: green for agree, red for feedback. */
  const hint = it => !it.proposed || answered(it) ? '' : parts(it).v === 'agree' ? 'green' : 'red';

  /* cur is the item at the top, and part how far into it main shows, as a
     share of its height: what a zoom from home keeps. typing is the item
     whose box holds my cursor. Agree acts on it, else on the item at the top. */
  let cur = null, part = 0, typing = null;
  const at = () => typing || cur;

  /* An item's top, under its rectangle, in main's scroll pixels. The visible
     rectangles agree across browsers; main's scale converts them to scroll
     pixels when home's zoom changes. */
  function placeOf(el) {
    const m = main(), mr = m.getBoundingClientRect(), er = el.getBoundingClientRect();
    const scale = mr.height / m.offsetHeight || 1;
    return m.scrollTop + (er.top - mr.top) / scale + el.clientTop - m.clientTop;
  }
  /* A number brings its item's top, under its rectangle, to the top of main.
     The room after the last item is sized first, for main as it stands. */
  function go(k, focus) {
    flush();
    cur = String(k);
    part = 0;
    room();
    const el = $('t-' + cur);
    if (el) main().scrollTop = placeOf(el);
    if (focus && boxOf(cur)) boxOf(cur).focus({preventScroll: true});
    outline();
  }
  /* The item at the top follows the scroll: the last whose top sits within
     80px of main's top. */
  function spy() {
    const now = main().scrollTop;
    let to = (D.items[0] || {}).n;
    for (const it of D.items) {
      const el = $('t-' + it.n);
      if (el && placeOf(el) - now <= 80) to = it.n;
    }
    const el = to && $('t-' + to);
    part = el && el.offsetHeight ? (now - placeOf(el)) / el.offsetHeight : 0;
    if (to && to !== cur) { cur = to; outline(); }
  }
  /* Room after the last item, so a number brings even its top to the top. */
  function room() {
    const items = document.querySelectorAll('#items .item'), last = items[items.length - 1];
    if (!last) return;
    items.forEach(e => { if (e !== last) e.style.minHeight = ''; });
    const pad = parseFloat(getComputedStyle($('items')).paddingBottom) || 0;
    last.style.minHeight = (main().clientHeight + last.clientTop - pad) + 'px';
  }
  function outline() {
    if (at()) tab(at());
    tools();
  }
  function tools() {
    const it = find(at()), a = $('agree');
    if (!a) return;
    a.className = 'agree' + (it && agreed(it) ? ' on' : '') + (it && locked(it) ? ' locked' : '');
    a.disabled = !it || !!D.sent || locked(it);
    a.textContent = !it ? 'Agree' : locked(it) ? 'Agreed before' : agreed(it) ? '✓ Agreed' : 'Agree';
  }

  /* A box is one line at rest. It opens while I type in it, or while it
     holds my answer, and grows with the text. */
  function fit(t) {
    const open = document.activeElement === t || !!t.value.trim();
    t.parentNode.classList.toggle('open', open);
    t.style.height = 'auto';
    t.style.height = (open ? Math.max(t.scrollHeight + 4, 84) : 40) + 'px';
  }
  function status(it, text) {
    const st = document.querySelector(`#t-${CSS.escape(it.n)} .fbx .st`);
    if (st) st.textContent = D.sent ? 'This wave is sent.' : text
      || (words(it) ? 'Saved. It counts as your answer.' : 'Anything you type counts as your answer.');
  }
  /* Paints what one answer changes, and leaves its box alone. */
  function paint(it) {
    const c = colour(it), rail = $('r-' + it.n), sec = $('t-' + it.n);
    if (rail) {
      rail.style.setProperty('--c', `var(--${c})`);
      rail.classList.toggle('g', c === 'grey');
      rail.classList.toggle('hint', !!hint(it));
      rail.style.setProperty('--h', `var(--${hint(it) || c})`);
    }
    if (sec) {
      sec.style.setProperty('--c', `var(--${c})`);
      sec.querySelector('h1.q .chip').classList.toggle('g', c === 'grey');
    }
    sendButton();
  }

  /* Send reads Sent, what is left, or Not typed when the last press typed
     nothing, its reason on hover. It spins while its line types. */
  let sending = false, gone = '';
  function sendButton() {
    const button = $('send');
    if (!button) return;
    const left = D.items.filter(it => !answered(it)).length, lost = !D.sent && !left && gone;
    button.disabled = !!D.sent || left > 0 || sending;
    button.classList.toggle('sent', !!D.sent);
    button.classList.toggle('gone', !!lost);
    button.classList.toggle('busy', sending);
    button.title = lost || '';
    button.textContent = D.sent ? 'Sent' : left ? 'Send · ' + left + ' left' : lost ? NOT_TYPED : 'Send';
  }

  /* Every keystroke is the answer. It is posted half a second after the
     last one, and at once when I leave the box or press Send. Each save
     waits for the one before, so they land in the order I typed them. */
  let pending = null, timer = 0, saving = Promise.resolve();
  function typed(it) {
    if (D.sent) return;
    pending = it;
    paint(it);
    status(it, 'Saving…');
    clearTimeout(timer);
    timer = setTimeout(flush, 500);
  }
  /* A save that never landed says so, and is tried again with the next
     keystroke or the next flush. Words that landed wait no more. */
  function flush() {
    clearTimeout(timer);
    if (!pending) return saving;
    const it = pending, t = boxOf(it.n), text = t ? t.value : '';
    pending = null;
    return saving = saving.then(() => live.post({act: 'feedback', n: it.n, text})).then(got => {
      if (got.ok) {
        if (t && t.value === text) live.sent(t);
        return status(it);
      }
      if (!pending) pending = it;
      status(it, got.ok === false ? 'Not saved: ' + got.said : 'Not saved: 1100 did not answer. It saves again as you type.');
    });
  }
  function next(n) {
    const open = D.items.filter(it => !answered(it)).map(it => it.n);
    return open.find(k => Number(k) > Number(n)) || open[0] || n;
  }
  /* An Agree, pressed: it shows at once, and is 1100's once 1100 draws it.
     Refused, it goes back, and the page says why. */
  function agreeTo(it, on) {
    agreeing[it.n] = on;
    paint(it);
    saving = saving.then(() => live.post({act: 'agree', n: it.n, on})).then(got => {
      if (got.ok) return;
      delete agreeing[it.n];
      paint(it);
      tools();
      live.said(got.said);
    });
  }
  /* A second click cancels this wave's Agree. An agree moves on to the next
     open item, and a box holding the cursor hands it to that item's box. */
  function agree() {
    const it = find(at());
    if (!it || D.sent || locked(it)) return;
    const on = agreed(it) ? '' : 'yes';
    agreeTo(it, on);
    const n = next(it.n);
    if (on && !words(it) && n !== it.n) go(n, !!typing);
    else tools();
  }
  /* Take it presses Agree, or writes the proposal's words as my feedback,
     still mine to edit. Either moves on to the next open item. */
  function takeIt(n) {
    const it = find(n), t = it && boxOf(it.n);
    if (!it || D.sent) return;
    const p = parts(it);
    if (p.v === 'agree') {
      if (!agreed(it)) agreeTo(it, 'yes');
      if (!words(it)) go(next(it.n));
      return;
    }
    if (!t) return;
    t.value = p.words;
    t.dispatchEvent(new Event('input', {bubbles: true}));
    flush();
    go(next(it.n));
  }
  /* Send waits for the last keystroke to land, then for the page to stand
     as the wave's file does, so the session reads what I see. Only a line
     that typed reads Sent. Anything else says why. */
  function send() {
    if (D.sent || sending || !D.items.every(answered)) return;
    sending = true;
    gone = '';
    live.said('');
    sendButton();
    flush().then(() => live.now()).then(() => live.post({act: 'send', worn: D.key})).then(got => {
      sending = false;
      if (got.ok) D.sent = 'yes';
      else live.said(gone = got.said);
      stand();
    });
  }

  /* The page, brought in line with the answers as they stand: each item's
     colours, its box and its line, then the tools. */
  function stand() {
    for (const it of D.items) {
      const t = boxOf(it.n);
      if (t) { if (!PHONE && !t.placeholder.endsWith(HINT)) t.placeholder = t.placeholder.replace(/\.$/, '') + HINT; fit(t); }
      paint(it);
      status(it, pending && pending.n === it.n ? 'Saving…' : '');
    }
    sendButton();
    tools();
    room();
  }
  /* 1100's answers, read again. An Agree it now draws is its own. */
  function read() {
    try { D = JSON.parse($('wave').textContent); } catch (e) {}
    for (const n of Object.keys(agreeing)) { const it = find(n); if (!it || it.agree === agreeing[n]) delete agreeing[n]; }
  }

  document.addEventListener('click', e => {
    const to = e.target.closest('[data-go], #index .tab[data-k], [data-take], #agree, #send');
    if (!to) return;
    if (to.id === 'agree') agree();
    else if (to.id === 'send') send();
    else if ('take' in to.dataset) takeIt(to.dataset.take);
    else go(to.dataset.go || to.dataset.k);
  });
  /* A press on Agree leaves the cursor in its box, so Agree acts on that box's item. */
  document.addEventListener('mousedown', e => { if (e.target.closest('#agree')) e.preventDefault(); });
  document.addEventListener('input', e => {
    const t = e.target.closest('.fbx textarea'), it = t && find(t.dataset.n);
    if (it) { typed(it); fit(t); }
  });
  /* On my Mac, Return in a box moves on to the next open item, the cursor
     in its box. With none left open, it sends. Shift+Return makes a new
     line. My phone's Return makes a new line. */
  document.addEventListener('keydown', e => {
    const t = e.target.closest('.fbx textarea'), it = t && find(t.dataset.n);
    if (!it || PHONE || e.isComposing || e.key !== 'Enter' || e.shiftKey || e.altKey || e.ctrlKey || e.metaKey) return;
    e.preventDefault();
    const n = next(it.n);
    if (n === it.n && D.items.every(answered)) send();
    else go(n, true);
  });
  document.addEventListener('focusin', e => {
    const t = e.target.closest('.fbx textarea');
    if (t) { typing = t.dataset.n; fit(t); outline(); }
  });
  document.addEventListener('focusout', e => {
    const t = e.target.closest('.fbx textarea');
    if (!t) return;
    if (typing === t.dataset.n) typing = null;
    fit(t);
    flush();
    outline();
  });
  /* Home's zoom reflows the page under the same scrollTop, and the scroll it
     causes would move the item at the top. So, after the reflow, each chart
     fits again, and the item I was reading comes back as far into it as I was,
     still the one Agree and my typing go to. */
  addEventListener('ws-zoom', () => {
    const n = cur, into = part;
    requestAnimationFrame(() => {
      fitAll();
      room();
      const el = $('t-' + n);
      if (el) main().scrollTop = placeOf(el) + into * el.offsetHeight;
      cur = n;
      part = into;
      outline();
    });
  });
  /* Home shows an item, as the app chat asks: its number as the address's
     #, or told when the address already holds it. It lands once the frame
     has its size, at the zoom and width it has then. */
  function shown(want) {
    if (!find(want)) return;
    requestAnimationFrame(() => requestAnimationFrame(() => go(want)));
  }
  addEventListener('hashchange', () => shown(decodeURIComponent(location.hash.slice(1))));
  addEventListener('message', e => {
    if (e.source === parent && e.data && e.data.ws && typeof e.data.place === 'string') shown(e.data.place.replace(/^#/, ''));
  });
  addEventListener('beforeunload', flush);

  live.ready(() => {
    read();
    if (!$('wave')) return;
    stand();
    /* On my Mac, a letter or a paste anywhere on the page lands in the box of
       the item at the top, with no click. Home hands it one landing on home
       itself, through typeIn. */
    anywhere(text => {
      const it = find(at()), t = it && boxOf(it.n);
      if (!t || t.disabled) return false;
      t.focus();
      t.setRangeText(text, t.value.length, t.value.length, 'end');
      t.dispatchEvent(new Event('input', {bubbles: true}));
      return true;
    });
    main().addEventListener('scroll', spy, {passive: true});
    /* Main's own size is watched, so the room after the last item follows the
       glass, home's rail and home's zoom alike. */
    new ResizeObserver(room).observe(main());
    const want = decodeURIComponent(location.hash.slice(1));
    const landed = find(want) ? want : (D.items.find(it => !answered(it)) || D.items[0] || {}).n || '';
    if (landed) go(landed);
    /* A chart drawn above the item pushes it down. Unless I moved, it goes
       back to the top. */
    charts().then(() => { if (landed && cur === landed && !typing) go(landed); });
  });
  /* 1100 changed the page: its answers are read again, and the page stands
     by them. An item gone from under me hands over to the first one open. */
  live.drawn(() => {
    read();
    stand();
    if (D.items.length && !find(cur)) go((D.items.find(it => !answered(it)) || D.items[0]).n);
    else outline();
    charts();
  });
})();
