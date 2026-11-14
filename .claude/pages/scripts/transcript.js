/* transcript.js — the Transcript tab's own script, on the contract.

   1100 draws every turn, what still runs, what waits queued and the status
   line, tools/transcript-page.py's drawn(), and live.js puts each change in
   place. This script works the box I type into, unfolds a call, opens a
   picture, reads what only the pane shows, and sends each press. live.js
   keeps my unsent words, under the session's id.

   It reads its address, its icons and the / menu from the page's #tdata.
   It touches the screen only from live.ready and live.drawn, and hears
   every click and key from the document, so a turn 1100 draws later needs
   no wiring. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
  const nap = ms => new Promise(f => setTimeout(f, ms));
  const PHONE = matchMedia('(hover: none) and (pointer: coarse)').matches;
  let D = {base: location.pathname, icons: {}, skills: []};
  const read = () => { try { D = JSON.parse($('tdata').textContent); } catch (e) {} };
  const tx = () => $('tx'), scroll = () => $('scroll'), turns = () => $('turns');
  const words = () => $('words'), send = () => $('send');

  // It opens at its newest turn, and stays there while I read there.
  const pinned = () => { const s = scroll(); return s.scrollTop + s.clientHeight >= s.scrollHeight - 48; };
  const bottom = () => { const s = scroll(); s.scrollTop = s.scrollHeight; };
  let stuck = true, share = 0;
  // Home's zoom reflows the transcript under the same scrollTop, and the
  // scroll it causes would unpin it. Read at its newest turn, it stays
  // there; read anywhere else, it keeps its share of the way down.
  addEventListener('ws-zoom', () => {
    const was = stuck, at = share;
    requestAnimationFrame(() => {
      if (was) bottom();
      else scroll().scrollTop = at * scroll().scrollHeight;
      stuck = was;
    });
  });

  // A fence or a table wider than its card scrolls sideways, and fades where
  // more waits.
  const WIDE = '.fence pre, .fence .grid';
  const fade = p => p.parentNode.classList.toggle('more', p.scrollLeft + p.clientWidth < p.scrollWidth - 2);
  const fences = () => document.querySelectorAll(WIDE).forEach(fade);
  document.addEventListener('scroll', e => {
    const t = e.target;
    if (t === scroll()) {
      stuck = pinned();
      share = t.scrollTop / (t.scrollHeight || 1);
      jumps();
    } else if (t.matches && t.matches(WIDE)) fade(t);
  }, true);

  // What I unfolded, by id, so a turn drawn again keeps it open. A detail
  // is read from disk once, bar a call still running: data-live. An open
  // one is read again each time 1100 draws, until its call ends.
  const open = new Set(), got = {};
  async function unfold(b, on) {
    const id = b.dataset.id, next = b.nextElementSibling;
    const box = next && next.matches('.detail, .sub') ? next : null;
    b.setAttribute('aria-expanded', on);
    if (on) open.add(id); else open.delete(id);
    if (box) box.hidden = !on;
    if (!on || !box || !box.classList.contains('detail') || box.dataset.got) return;
    await load(id, box);
  }
  async function load(id, box) {
    box.dataset.got = '1';
    try {
      let html = got[id];
      if (html === undefined) {
        const r = await fetch(D.base + '/step/' + encodeURIComponent(id));
        if (!r.ok) throw r;
        html = await r.text();
      }
      box.innerHTML = html;
      if (!box.querySelector('[data-live]')) got[id] = html;
      fences();
    } catch (e) { delete box.dataset.got; }
  }
  const relive = () => turns().querySelectorAll('.detail:not([hidden])').forEach(box => {
    const b = box.previousElementSibling;
    if (b && box.querySelector('[data-live]')) load(b.dataset.id, box);
  });
  function reopen() {
    for (const id of open) {
      const b = turns().querySelector(`.row[data-id="${CSS.escape(id)}"]`);
      if (b && (b.getAttribute('aria-expanded') !== 'true' || b.nextElementSibling?.hidden)) unfold(b, true);
    }
  }

  // ---- the box I type into ----

  let held = [], busy = false;
  // While the session works, an empty box's Send reads Stop.
  const stopping = () => tx().dataset.claude === 'busy' && !words().value.trim() && !held.length;
  function ready() {
    const stop = stopping(), b = send();
    b.textContent = stop ? 'Stop' : 'Send';
    b.classList.toggle('stop', stop);
    b.classList.toggle('busy', busy);
    b.disabled = busy || !(stop || words().value.trim() || held.length);
    $('box').classList.toggle('typed', !!words().value);
  }
  const say = s => { const why = $('why'); why.textContent = s; why.hidden = !s; };
  // The box grows with its text, up to two fifths of the transcript's height.
  function grow() {
    const w = words();
    const cap = Math.max(parseFloat(getComputedStyle(w).minHeight) || 44, Math.round(tx().clientHeight * 0.4));
    w.style.height = 'auto';
    w.style.height = Math.min(w.scrollHeight + 4, cap) + 'px';
  }
  function chips() {
    const att = $('att');
    att.hidden = !held.length;
    att.innerHTML = held.map((h, i) => `<span class="chipf">${h.file.type.startsWith('image/')
      ? `<img src="${h.url}" alt="">` : `<span class="fi">${D.icons.file}</span>`}<span class="nm">${esc(h.file.name)}</span>`
      + `<button class="b0 x" data-i="${i}" aria-label="Remove ${esc(h.file.name)}">${D.icons.x}</button></span>`).join('');
  }
  // A / opening the box lists every skill, those starting with what I
  // typed first, then those holding it. Esc shuts the list until I type.
  let rows = [], at = 0, shut = false;
  function slash() {
    const m = /^\/([\w:-]*)$/.exec(words().value), q = m ? m[1].toLowerCase() : '';
    rows = !m || shut ? [] : D.skills.filter(s => s[0].startsWith(q))
      .concat(D.skills.filter(s => !s[0].startsWith(q) && s[0].includes(q)));
    at = 0;
    list();
  }
  function list() {
    const menu = $('menu');
    menu.hidden = !rows.length;
    menu.innerHTML = rows.map((s, i) => `<button class="b0 sk${i === at ? ' on' : ''}" data-i="${i}" tabindex="-1">`
      + `<b>/${esc(s[0])}</b><span>${esc(s[1])}</span></button>`).join('');
    menu.querySelector('.on')?.scrollIntoView({block: 'nearest'});
  }
  function fill(text) {
    const w = words();
    w.value = text;
    w.dispatchEvent(new Event('input', {bubbles: true}));
    rows = [];
    list();
    w.focus();
    w.setSelectionRange(text.length, text.length);
  }
  // The app chat's draft_reply, through home: its words fill the box, unsent.
  // Home keeps the draft until this page says it took it.
  addEventListener('ws-draft', e => {
    fill(e.detail);
    if (parent !== window) parent.postMessage({ws: 1, drafted: 1}, '*');
  });

  // On my Mac, the up arrow in an empty box brings back my last line, again
  // the one before; the down arrow returns. Only an untouched line moves on.
  let back = -1;
  const mine = () => [...turns().querySelectorAll('.turn.mine .said')].map(s => s.textContent.trim())
    .filter((s, i, all) => s && s !== all[i - 1]);
  function recall(up) {
    const lines = mine(), now = back < 0 ? '' : lines[lines.length - 1 - back];
    const next = back + (up ? 1 : -1);
    if (words().value !== now || next < -1 || next >= lines.length) return false;
    const was = next;
    fill(next < 0 ? '' : lines[lines.length - 1 - next]);
    back = was;
    shut = true;
    slash();
    return true;
  }

  document.addEventListener('input', e => {
    if (e.target.id !== 'words') return;
    back = -1;
    shut = false;
    slash();
    grow(); ready(); say(''); send().classList.remove('gone');
  });
  // On my Mac, Return sends, as Send does; Shift+Return adds a line. My
  // phone sends only from Send. Neither ever stops: only Stop, pressed, does.
  document.addEventListener('keydown', e => {
    if (e.target.id !== 'words' || e.isComposing) return;
    const plain = !(e.shiftKey || e.metaKey || e.altKey || e.ctrlKey);
    if (rows.length && plain && /^(ArrowUp|ArrowDown|Tab|Enter|Escape)$/.test(e.key)) {
      e.preventDefault();
      if (e.key === 'Escape') { shut = true; slash(); }
      else if (e.key.startsWith('Arrow')) { at = (at + (e.key === 'ArrowUp' ? -1 : 1) + rows.length) % rows.length; list(); }
      else fill('/' + rows[at][0] + ' ');
      return;
    }
    if (PHONE) return;
    const tip = $('offer').querySelector('.hint');
    if (tip && !words().value && plain && (e.key === 'Tab' || e.key === 'ArrowRight')) {
      e.preventDefault();
      fill(tip.dataset.text);
      return;
    }
    if (plain && (e.key === 'ArrowUp' || e.key === 'ArrowDown')) {
      if (recall(e.key === 'ArrowUp')) e.preventDefault();
      return;
    }
    if (e.key !== 'Enter' || e.shiftKey || e.altKey || e.ctrlKey) return;
    e.preventDefault();
    if (!stopping()) sendIt();
  });

  // What only the pane shows, read each time the session's state moves:
  // its mode, and a dialog while it waits, else the reply it suggests once
  // its turn ends. The suggestion lands a moment after the turn, so a miss
  // is read again, twice. A mode hidden under a dialog keeps the last. A
  // page in a hidden frame has no width, and reads nothing until it shows:
  // home opens every tab of a hub ahead, hidden.
  let reading = 0, unread = false;
  // A dialog waiting takes my words into its own field. On my phone, its hint is short.
  const asking = () => {
    const ask = !!$('offer').querySelector('.ask');
    words().placeholder = PHONE ? (ask ? 'Or answer' : 'Type') : ask ? 'Or answer in your own words' : 'Type or dictate';
  };
  async function looking() {
    if (!innerWidth) { unread = true; return; }
    const ticket = ++reading, now = tx().dataset.claude;
    if (!now) { $('offer').replaceChildren(); asking(); return; }
    for (const wait of now === 'idle' || now === 'waiting' ? [0, 1500, 4000] : [0]) {
      if (wait) await nap(wait);
      if (ticket !== reading) return;
      try {
        const r = await fetch(D.base + '/pane');
        if (!r.ok || ticket !== reading) return;
        const t = document.createElement('template');
        t.innerHTML = await r.text();
        $('offer').replaceChildren(...t.content.getElementById('offer').childNodes);
        const m = t.content.getElementById('mode');
        if (m) { $('modev').textContent = m.textContent; $('mode').hidden = false; }
        asking();
        // A panel's Close may show before its dialog draws: read again.
        if ($('offer').querySelector('.hint, .ch[data-n]')) return;
      } catch (e) { return; }
    }
  }
  async function moded(b) {
    b.disabled = true;
    const got = await live.post({act: 'mode'});
    if (got.ok === false) say(got.said);
    else if (got.ok === null) say('1100 did not answer.');
    else { await nap(500); await looking(); }
    b.disabled = false;
  }
  async function chose(ch) {
    ch.parentNode.querySelectorAll('.ch').forEach(b => { b.disabled = true; });
    const got = await live.post(ch.dataset.n ? {act: 'answer', n: ch.dataset.n} : {act: 'close'});
    if (got.ok === false) { say(got.said); looking(); }
    else if (got.ok === null) say('1100 did not answer.');
    else $('offer').replaceChildren();
  }

  // A picture pasted, on my Mac or my phone, is held as the paperclip holds it.
  addEventListener('paste', e => {
    const pics = [...(e.clipboardData?.files || [])].filter(f => f.type.startsWith('image/'));
    if (pics.length) { e.preventDefault(); hold(pics); }
  });

  // On my Mac, the box holds the cursor, so a dictation tool always finds a
  // field to paste into. It takes it when the page opens, and back half a
  // second after a click on the page, the Mac's double-click time, so a
  // double or triple click highlights first. Home hands it back, through
  // holdCursor, when the page comes on show and after a click on home
  // itself. Text left highlighted keeps it out, and so does another field
  // holding it, or another page beside it.
  const field = el => !!el && el.matches('input, textarea, select, [contenteditable]');
  function holdCursor() {
    if (!innerWidth || field(document.activeElement)) return document.activeElement === words();
    const s = getSelection();
    if (s && !s.isCollapsed) return false;
    try {
      const at = parent !== window && parent.document.activeElement;
      if (at && (field(at) || (at.tagName === 'IFRAME' && at !== frameElement))) return false;
      words().focus({preventScroll: true});
    } catch (e) { return false; }
    return true;
  }
  let settle = 0;
  addEventListener('click', () => {
    if (PHONE) return;
    clearTimeout(settle);
    settle = setTimeout(holdCursor, 500);
  });

  // The menu beside the text opens above the line, and shuts on a tap
  // anywhere else, on Esc, or once the paperclip is chosen. iOS's paperclip
  // menu comes from a file input with no accept: Photo Library, Take Photo
  // or Video, Choose Files.
  const popped = on => { $('pop').hidden = !on; $('more').setAttribute('aria-expanded', on); };
  document.addEventListener('pointerdown', e => {
    if (e.target.closest && e.target.closest('#menu')) e.preventDefault();
    const pop = $('pop');
    if (pop && !pop.hidden && !pop.contains(e.target) && !$('more').contains(e.target)) popped(false);
  });
  addEventListener('keydown', e => { if (e.key === 'Escape' && $('pop') && !$('pop').hidden) popped(false); });

  // Two arrows step through my turns, landing each at the top: up, the
  // nearest starting above the top edge; down, the nearest below it, and
  // past my last, the foot. With none that way, an arrow greys. A turn's
  // place is read from offsetTop, in scrollTop's own pixels: the zoom from
  // home's rail scales getBoundingClientRect, and never those two.
  function aims() {
    const s = scroll(), now = s.scrollTop, max = s.scrollHeight - s.clientHeight;
    const top = s.offsetTop + (parseFloat(getComputedStyle(s).paddingTop) || 0);
    const all = [...s.querySelectorAll('.turn.you')]
      .map(t => Math.min(max, Math.max(0, t.offsetTop - top))).concat(max);
    return [all.filter(a => a < now - 2).pop(), all.find(a => a > now + 2)];
  }
  function jumps() {
    if (!$('prev')) return;
    const [up, down] = aims();
    $('prev').disabled = up === undefined;
    $('next').disabled = down === undefined;
  }
  function hold(files) {
    for (const file of files) held.push({file, url: URL.createObjectURL(file)});
    chips();
    ready();
  }
  document.addEventListener('change', e => {
    if (e.target.id !== 'pick') return;
    hold([...e.target.files]);
    e.target.value = '';
  });
  const b64 = f => new Promise((ok, no) => {
    const r = new FileReader();
    r.onload = () => ok(String(r.result).split(',')[1] || '');
    r.onerror = no;
    r.readAsDataURL(f);
  });
  // It spins while it types, then flashes green. Refused, it turns red, and
  // the one sentence why shows above the line; my words stay. Sent, only
  // what went leaves the box: words typed and files added meanwhile stay,
  // and the draft holds only those.
  async function sendIt() {
    const b = send(), w = words();
    if (b.disabled) return;
    const stop = b.classList.contains('stop');
    const text = stop ? '' : w.value, went = stop ? [] : [...held];
    busy = true;
    ready();
    b.classList.remove('gone', 'done');
    say('');
    try {
      const data = new URLSearchParams(stop ? {act: 'stop'} : {act: 'send', text});
      for (const h of went) { data.append('name', h.file.name); data.append('data', await b64(h.file)); }
      const got = await live.post(data);
      if (got.ok === false) {
        say(got.said);
        b.classList.add('gone');
      } else if (got.ok === null) {
        say('1100 did not answer.');
      } else {
        if (w.value.startsWith(text)) w.value = w.value.slice(text.length).trimStart();
        if (w.value) w.dispatchEvent(new Event('input', {bubbles: true}));
        else live.sent(w);
        slash();
        went.forEach(h => URL.revokeObjectURL(h.url));
        held = held.filter(h => !went.includes(h));
        chips();
        grow();
        b.classList.add('done');
        setTimeout(() => b.classList.remove('done'), 1500);
      }
    } catch (e) { say('1100 did not answer.'); }
    busy = false;
    ready();
  }

  // A hand-off's button, pressed: Type leaves its words in its session's
  // prompt, and its Send then presses Return alone. Copy is the page's own
  // click, copied().
  async function handed(b) {
    const pair = b.parentElement, sent = !!b.dataset.send;
    const only = sent && pair.dataset.typed ? 'return' : '';
    const got = await live.pressed(b, {act: 'hand', key: pair.dataset.hand, send: sent ? 'yes' : '', only},
                                   {word: sent ? '' : 'Typed', not: 'Not typed'});
    if (!got.ok) return;
    if (sent) delete pair.dataset.typed;
    else pair.dataset.typed = '1';
  }

  document.addEventListener('click', e => {
    const t = e.target;
    if (!t.closest) return;
    // A picture opens over the page; a tap anywhere closes it.
    const viewer = t.closest('#viewer');
    if (viewer) { viewer.hidden = true; viewer.querySelector('img').removeAttribute('src'); return; }
    if (t.closest('#scroll')) {
      const p = t.closest('.pic'), c = t.closest('.cp'), r = t.closest('button.row');
      const h = t.closest('.group[data-hand] > button:not(.cp)');
      if (p) { const v = $('viewer'); v.querySelector('img').src = p.dataset.src; v.hidden = false; }
      else if (c) copied(c);
      else if (r) unfold(r, r.getAttribute('aria-expanded') !== 'true');
      if (h && !h.disabled) handed(h);
      return;
    }
    const b = t.closest('#more, #clip, #prev, #next, #mode, #send, #menu .sk, #att .x, #offer .hint, #offer .ch');
    if (!b) return;
    if (b.id === 'more') popped($('pop').hidden);
    else if (b.id === 'clip') { popped(false); $('pick').click(); }
    else if (b.id === 'prev' || b.id === 'next') {
      const a = aims()[b.id === 'prev' ? 0 : 1];
      if (a !== undefined) scroll().scrollTop = a;
    } else if (b.id === 'mode') moded(b);
    else if (b.id === 'send') sendIt();
    else if (b.matches('.sk')) fill('/' + rows[+b.dataset.i][0] + ' ');
    else if (b.matches('.x')) {
      URL.revokeObjectURL(held.splice(+b.dataset.i, 1)[0].url);
      chips();
      ready();
    } else if (b.matches('.hint')) fill(b.dataset.text);
    else if (!b.disabled) chose(b);
  });

  // iOS gives a framed page no home-bar band, so the home's own is measured.
  // It is the glass's pixels, and this page's own are home's zoom of them.
  function inset() {
    let band = 0;
    try {
      const doc = parent !== window ? parent.document : document, probe = doc.createElement('div');
      probe.style.cssText = 'position:fixed;left:0;bottom:0;width:0;visibility:hidden;'
        + 'height:env(safe-area-inset-bottom, 0px)';
      doc.body.appendChild(probe);
      band = probe.offsetHeight;
      probe.remove();
    } catch (e) {}
    const zoom = parseFloat(document.documentElement.style.zoom) || 1;
    document.documentElement.style.setProperty('--ib', band / zoom + 'px');
  }
  addEventListener('resize', inset);
  addEventListener('ws-zoom', inset);
  addEventListener('resize', () => { if (unread && innerWidth) { unread = false; looking(); } });
  addEventListener('orientationchange', inset);

  let claude = '';
  live.ready(() => {
    read();
    claude = tx().dataset.claude;
    new ResizeObserver(() => { if (stuck) bottom(); fences(); }).observe(scroll());
    const sized = new ResizeObserver(jumps);
    sized.observe(scroll());
    sized.observe(turns());
    // On my Mac, a letter or a paste anywhere on the page lands in the box,
    // with no click. Home hands it one landing on home itself, through
    // typeIn. Tab outside the box, or on home around it, fills the empty box
    // with the reply Claude Code suggests, as Tab in the box does.
    anywhere(text => {
      const w = words();
      w.focus();
      w.setRangeText(text, w.value.length, w.value.length, 'end');
      w.dispatchEvent(new Event('input', {bubbles: true}));
      return true;
    }, () => {
      const tip = $('offer').querySelector('.hint');
      if (!tip || words().value) return false;
      fill(tip.dataset.text);
      return true;
    });
    // It takes the cursor once live.js gave back my unsent words, a box
    // holding the cursor taking none, and before the page first paints.
    if (!PHONE) {
      window.holdCursor = holdCursor;
      queueMicrotask(holdCursor);
    }
    inset();
    requestAnimationFrame(() => { bottom(); fences(); });
    ready();
    asking();
    looking();
  });
  // 1100 drew the page again: the box reads the session's state, a call I
  // unfolded stays unfolded, and one still running is read again. At its
  // newest turn, it stays there. The pane is read again once the state moves.
  live.drawn(() => {
    read();
    relive();
    reopen();
    fences();
    if (stuck) bottom();
    jumps();
    ready();
    if (claude !== tx().dataset.claude || tx().dataset.claude === 'waiting') looking();
    claude = tx().dataset.claude;
  });
})();
