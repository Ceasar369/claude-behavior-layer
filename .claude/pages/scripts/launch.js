/* launch.js — the launch page's own script, on the contract.

   1100 draws every row, tools/launch-page.py's drawn(), and live.js puts
   each change in place. This script draws what needs the browser's
   measure: the map, each row's lands line, and the row I picked, with
   its arrows. It keeps my changes as I make them, saves each one, and
   sends Launch.

   It reads the rows as 1100 last drew them from the page's #launch-data.
   A change of mine not saved yet wins: until it lands, the rows stay as I
   left them. It touches the screen only from live.ready and live.drawn,
   and hears every click, key and press from the document, so a row 1100
   draws later needs no wiring. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const H = 380;
  /* My phone, held sideways: the map fills the first screen, and the picked
     row's lands line and arrows sit beside it. */
  const SIDEWAYS = matchMedia('(hover:none) and (pointer:coarse) and (orientation:landscape)');
  const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  const copy = x => JSON.parse(JSON.stringify(x));

  /* What 1100 last drew, and the rows as I see them. */
  let D = null, LAYOUT = [], STARTER = '', ROWS = [], PLANNED = [], BUSY = false;
  const SEEN = new Set();
  let HOME = {win: 'N1', tab: 'N1', pane: ''}, FULL = [1600, 900];
  let active = 0;

  /* ---- the live layout ---------------------------------------------------- */

  /* A live window or tab is keyed L:<its iTerm id>. One a row opens is N1, N2… */
  const leaves = n => !n ? [] : n.split ? n.children.flatMap(leaves) : [n];
  const idOf = n => n.ghost != null ? 'r:' + n.ghost : 'p:' + n.pane;
  const liveWin = k => LAYOUT.find(w => 'L:' + w.window === k);
  const liveTab = (win, k) => { const w = liveWin(win); return w && w.tabs.find(t => 'L:' + t.tab === k); };

  /* A node's size, in iTerm's own pixels. A column split adds widths, a row split heights. */
  function size(n) {
    if (!n.split) return [n.w, n.h];
    const s = n.children.map(size);
    return n.split === 'columns' ? [s.reduce((a, c) => a + c[0], 0), Math.max(...s.map(c => c[1]))]
      : [Math.max(...s.map(c => c[0])), s.reduce((a, c) => a + c[1], 0)];
  }

  /* ---- rows --------------------------------------------------------------- */

  const web = r => r.kind === 'browser';
  /* ROWS is launch order, which moving a row changes. The cards stand in pos
     order instead, so a card never moves. */
  const shown = () => ROWS.map((r, i) => i).sort((a, b) => ROWS[a].pos - ROWS[b].pos);
  const tag = r => web(r) ? 'web ' + (r.site || '?') : r.n;
  const indexOf = card => card ? ROWS.findIndex(r => String(r.uid) === card.dataset.uid) : -1;

  const num = k => Number(k.slice(1));
  const news = keys => [...new Set(keys.filter(k => k && k[0] === 'N'))].sort((a, b) => num(a) - num(b));
  const next = keys => 'N' + (Math.max(0, ...keys.filter(k => k && k[0] === 'N').map(num)) + 1);

  function tabsOf(win) {
    const w = liveWin(win);
    const live = w ? w.tabs.map(t => 'L:' + t.tab) : [];
    return live.concat(news(ROWS.filter(r => r.win === win).map(r => r.tab)));
  }
  function winLabel(k) {
    const w = liveWin(k);
    return w ? 'window ' + (LAYOUT.indexOf(w) + 1)
      : 'window ' + (LAYOUT.length + news(ROWS.map(r => r.win)).indexOf(k) + 1) + ' · new';
  }
  function tabLabel(win, k) {
    const w = liveWin(win), t = liveTab(win, k);
    if (t) return 'tab ' + (w.tabs.indexOf(t) + 1);
    return 'tab ' + ((w ? w.tabs.length : 0) + news(ROWS.filter(r => r.win === win).map(r => r.tab)).indexOf(k) + 1) + ' · new';
  }

  /* ---- where a row lands -------------------------------------------------- */

  /* A node refitted to a new box. Its inner split keeps its proportions. */
  function fit(n, w, h) {
    if (!n.split) return {...n, w, h};
    const [ow, oh] = size(n), k = n.children.length;
    return {...n, children: n.children.map(c => {
      const [cw, ch] = size(c);
      return n.split === 'columns' ? fit(c, ow ? cw * w / ow : w / k, h) : fit(c, w, oh ? ch * h / oh : h / k);
    })};
  }

  /* A row lands as iTerm places it. Beside its anchor, inside the anchor's own
     split when that split runs the same way, and then every pane of that split
     takes an equal share. Otherwise the anchor splits in two, halves each. */
  function insert(tree, r, i) {
    const ghost = (w, h) => ({ghost: r.uid, idx: i, w, h});
    if (!tree) return ghost(FULL[0], FULL[1]);
    if (!r.at) return tree;
    const across = r.at.side === 'left' || r.at.side === 'right';
    const kind = across ? 'columns' : 'rows';
    const first = r.at.side === 'left' || r.at.side === 'up';
    const walk = n => {
      if (n.split) {
        const hit = n.split === kind ? n.children.findIndex(c => !c.split && idOf(c) === r.at.anchor) : -1;
        if (hit < 0) return {...n, children: n.children.map(walk)};
        const kids = n.children.slice();
        kids.splice(first ? hit : hit + 1, 0, ghost(0, 0));
        const [w, h] = size(n), k = kids.length;
        return {...n, children: kids.map(c => across ? fit(c, w / k, h) : fit(c, w, h / k))};
      }
      if (idOf(n) !== r.at.anchor) return n;
      const half = across ? [n.w / 2, n.h] : [n.w, n.h / 2];
      const a = {...n, w: half[0], h: half[1]}, g = ghost(half[0], half[1]);
      return {split: kind, children: first ? [g, a] : [a, g]};
    };
    return walk(tree);
  }

  /* The tab as it will stand once every row before `upto` has launched. */
  function treeFor(win, tab, upto) {
    const t = liveTab(win, tab);
    let tree = t ? copy(t.root) : null;
    if (BUSY) return tree;
    ROWS.slice(0, upto).forEach((r, i) => { if (r.win === win && r.tab === tab) tree = insert(tree, r, i); });
    if (upto === ROWS.length) PLANNED.filter(m => m.win === win && m.tab === tab).forEach(m => { tree = moved(tree, m); });
    return tree;
  }

  /* Remove one leaf, closing its empty split and fitting the remaining panes. */
  function without(n, id) {
    if (!n) return [null, null];
    if (!n.split) return idOf(n) === id ? [null, n] : [n, null];
    const [w, h] = size(n); let found = null;
    const kids = n.children.map(c => {
      const [rest, hit] = without(c, id);
      if (hit) found = hit;
      return rest;
    }).filter(Boolean);
    if (!found) return [n, null];
    if (!kids.length) return [null, found];
    const flat = kids.flatMap(c => c.split === n.split ? c.children : [c]);
    const rest = flat.length === 1 ? flat[0] : {...n, children: flat};
    return [fit(rest, w, h), found];
  }

  /* Replay a planned move on the preview; the real move waits for Launch. */
  function moved(tree, m) {
    const [rest, leaf] = without(tree, m.source);
    if (!rest || !leaf || !leaves(rest).some(n => idOf(n) === m.anchor)) return tree;
    const marker = '__planned_move__';
    const next = insert(rest, {uid: marker, at: {anchor: m.anchor, side: m.side}}, -1);
    const put = n => n.split ? {...n, children: n.children.map(put)}
      : n.ghost === marker ? fit(leaf, n.w, n.h) : n;
    return put(next);
  }

  function nameOf(id) {
    if (id[0] === 'r') { const r = ROWS.find(r => 'r:' + r.uid === id); return r ? tag(r) : '?'; }
    const p = LAYOUT.flatMap(w => w.tabs.flatMap(t => leaves(t.root))).find(p => 'p:' + p.pane === id);
    return p ? (p.number || p.label) : '?';
  }

  const SIDE = {right: 'right of', left: 'left of', down: 'below', up: 'above'};
  const OPPOSITE = {right: 'left', left: 'right', down: 'up', up: 'down'};

  /* Right of 07 and left of 08 are one place when they are neighbours. Such a
     place reads as between them, the left or upper one first. */
  function where(i) {
    const r = ROWS[i];
    const head = winLabel(r.win) + ' · ' + tabLabel(r.win, r.tab) + ' · ';
    if (PLANNED.some(m => m.win === r.win && m.tab === r.tab)) return head + 'as shown in the preview';
    if (!r.at) return head + 'fills the tab';
    const spot = BUSY ? null : spots(i).find(s => s.ways.some(o => o.anchor === r.at.anchor && o.side === r.at.side));
    const pair = spot && spot.ways.find(o => o.side === OPPOSITE[r.at.side] && o.anchor !== r.at.anchor);
    if (!pair) return head + SIDE[r.at.side] + ' ' + nameOf(r.at.anchor);
    const [a, b] = r.at.side === 'right' || r.at.side === 'down' ? [r.at.anchor, pair.anchor] : [pair.anchor, r.at.anchor];
    return head + 'between ' + nameOf(a) + ' and ' + nameOf(b);
  }

  /* ---- the arrows --------------------------------------------------------- */

  function rects(n, x, y, w, h, out) {
    if (!n.split) { out[idOf(n)] = {x, y, w, h}; return out; }
    const axis = n.split === 'columns' ? 0 : 1;
    const total = n.children.reduce((a, c) => a + size(c)[axis], 0);
    let at = axis ? y : x;
    n.children.forEach(c => {
      const part = (axis ? h : w) * size(c)[axis] / total;
      axis ? rects(c, x, at, w, part, out) : rects(c, at, y, part, h, out);
      at += part;
    });
    return out;
  }

  /* A tab's shape, sizes aside. Two spots giving one shape are one place. */
  const shape = n => n.split ? n.split[0] + '(' + n.children.map(shape).join(',') + ')' : idOf(n);

  /* Every distinct place a row can land, with every way of saying it. Each one
     sits where the row itself would be drawn, so an arrow measures what I see. */
  function spots(i) {
    const r = ROWS[i];
    const tree = treeFor(r.win, r.tab, i);
    if (!tree) return [];
    const places = new Map();
    leaves(tree).map(idOf).forEach(anchor => Object.keys(SIDE).forEach(side => {
      const t = insert(tree, {...r, at: {anchor, side}}, i), key = shape(t);
      if (places.has(key)) { places.get(key).ways.push({anchor, side}); return; }
      const [w, h] = size(t), g = rects(t, 0, 0, w, h, {})['r:' + r.uid];
      places.set(key, {anchor, side, cx: g.x + g.w / 2, cy: g.y + g.h / 2, ways: [{anchor, side}]});
    }));
    return [...places.values()];
  }

  /* The moving row launches last. A row anchored to it takes its old place. */
  function moveLast() {
    const r = ROWS[active];
    if (active !== ROWS.length - 1) {
      const id = 'r:' + r.uid, kids = ROWS.filter(s => s !== r && s.at && s.at.anchor === id);
      if (kids.length) {
        kids.slice(1).forEach(s => { s.at = {anchor: 'r:' + kids[0].uid, side: s.at.side}; });
        kids[0].at = r.at ? {...r.at} : null;
      }
      ROWS.splice(active, 1);
      ROWS.push(r);
      active = ROWS.length - 1;
    }
  }

  /* An arrow moves the row to the nearest place that way, measured where the
     row would be drawn. Drifting sideways costs four times going straight. */
  function move(dir) {
    const r = ROWS[active];
    if (BUSY || !r || !r.at) return;
    if (PLANNED.some(m => m.win === r.win && m.tab === r.tab)) return plannedArrow(dir);
    moveLast();
    const all = spots(active);
    const here = all.find(s => s.ways.some(o => o.anchor === r.at.anchor && o.side === r.at.side));
    if (!here) { changed(); return; }
    const [dx, dy] = {right: [1, 0], left: [-1, 0], down: [0, 1], up: [0, -1]}[dir];
    let best = null, score = Infinity;
    for (const s of all) {
      const along = (s.cx - here.cx) * dx + (s.cy - here.cy) * dy;
      if (s === here || along <= 0.5) continue;
      const sc = along + 4 * (Math.abs((s.cx - here.cx) * dy) + Math.abs((s.cy - here.cy) * dx));
      if (sc < score) { score = sc; best = s; }
    }
    if (best) r.at = {anchor: best.anchor, side: best.side};
    changed();
  }

  function plannedArrow(dir) {
    const r = ROWS[active], source = 'r:' + r.uid, tree = treeFor(r.win, r.tab, ROWS.length);
    const [w, h] = size(tree), current = rects(tree, 0, 0, w, h, {})[source];
    const [base] = without(tree, source);
    if (!current || !base) return;
    const x = current.x + current.w / 2, y = current.y + current.h / 2;
    const [dx, dy] = {right: [1, 0], left: [-1, 0], down: [0, 1], up: [0, -1]}[dir];
    let best = null, score = Infinity;
    for (const n of leaves(base)) for (const side of Object.keys(SIDE)) {
      const candidate = {win: r.win, tab: r.tab, source, anchor: idOf(n), side};
      const t = moved(tree, candidate), [tw, th] = size(t), p = rects(t, 0, 0, tw, th, {})[source];
      const px = p.x + p.w / 2 - x, py = p.y + p.h / 2 - y;
      const along = px * dx + py * dy;
      const sc = along + 4 * Math.abs(px * dy + py * dx);
      if (along > 0.5 && sc < score) { best = candidate; score = sc; }
    }
    if (best) { PLANNED.push(best); changed(); }
  }

  /* Drag within this tab. Removing the row first lets every remaining pane
     offer its four sides. A cancelled drag restores the original launch order. */
  let drag = null, suppressClick = false;
  function capture(e) {
    // The map survives redraws; capture before its touched child is removed.
    try { $('map').setPointerCapture(e.pointerId); } catch (err) {}
  }
  function dragStart(e, i) {
    if (BUSY || e.button !== 0 || drag) return;
    const r = ROWS[i];
    drag = {id: e.pointerId, x: e.clientX, y: e.clientY, i, source: 'r:' + r.uid,
      planned: PLANNED.some(m => m.win === r.win && m.tab === r.tab), rows: copy(ROWS), active, moving: false, target: null};
    capture(e);
  }
  function dragLive(e, source) {
    if (BUSY || e.button !== 0 || drag || !ROWS[active]) return;
    drag = {id: e.pointerId, x: e.clientX, y: e.clientY, source, planned: true,
      rows: copy(ROWS), active, moving: false, target: null};
    capture(e);
  }
  function dragMove(e) {
    if (!drag || e.pointerId !== drag.id) return;
    if (!drag.moving) {
      if (Math.hypot(e.clientX - drag.x, e.clientY - drag.y) < 6) return;
      drag.moving = true;
      if (drag.i != null) active = drag.i;
      if (!drag.planned) moveLast();
      drawMap();
    }
    e.preventDefault();
    document.querySelectorAll('#map .pane.drop').forEach(el => el.classList.remove('drop', 'left', 'right', 'up', 'down'));
    const el = document.elementFromPoint(e.clientX, e.clientY)?.closest('#map .pane[data-anchor]');
    drag.target = null;
    if (!el) return;
    const box = el.getBoundingClientRect(), x = (e.clientX - box.left) / box.width, y = (e.clientY - box.top) / box.height;
    const side = [['left', x], ['right', 1 - x], ['up', y], ['down', 1 - y]].sort((a, b) => a[1] - b[1])[0][0];
    el.classList.add('drop', side);
    drag.target = {anchor: el.dataset.anchor, side};
  }
  function dragEnd(e) {
    if (!drag || e.pointerId !== drag.id) return;
    const d = drag;
    drag = null;
    if (!d.moving) {
      if (e.type === 'pointerup' && d.i != null) pick(d.i);
      return;
    }
    suppressClick = true;
    setTimeout(() => { suppressClick = false; }, 0);
    if (e.type === 'pointercancel' || !d.target) {
      ROWS = d.rows; active = d.active; paint(); return;
    }
    if (d.planned) PLANNED.push({win: ROWS[active].win, tab: ROWS[active].tab,
      source: d.source, anchor: d.target.anchor, side: d.target.side});
    else ROWS[active].at = d.target;
    changed();
  }

  /* ---- saving ------------------------------------------------------------- */

  /* Every change is saved, so a reload keeps it. A save sends every row, and
     each row the page has seen: a row the session wrote since is kept. */
  let timer = null, seq = 0, dirty = false, writing = Promise.resolve();
  function plannedLayouts() {
    const places = new Map(PLANNED.map(m => [m.win + '\n' + m.tab, {win: m.win, tab: m.tab}]));
    const shape = n => !n ? null : n.split ? {split: n.split, children: n.children.map(shape)} : {ref: idOf(n)};
    return [...places.values()].map(p => ({...p, root: shape(treeFor(p.win, p.tab, ROWS.length))}));
  }
  const form = act => ({act, rows: JSON.stringify(ROWS), moves: JSON.stringify(PLANNED),
    layouts: JSON.stringify(plannedLayouts()), seen: JSON.stringify([...SEEN])});
  function save() {
    ++seq; dirty = true; clearTimeout(timer);
    timer = setTimeout(() => persist(false), 300);
  }
  /* A change of place saves at once, and the page then stands as 1100
     placed the rows. The picked row stays picked. Only the last change draws.
     A box whose words landed waits on this device no more. */
  async function persist(redraw) {
    const me = seq, sent = form('save'), rows = copy(ROWS);
    clearTimeout(timer);
    writing = writing.catch(() => null).then(() => live.post(sent));
    const got = await writing;
    if (me !== seq) { dirty = true; return false; }
    const error = $('save-error');
    if (got.ok !== true) { dirty = true; if (error) error.hidden = false; return false; }
    dirty = false;
    if (error) error.hidden = true;
    for (const box of document.querySelectorAll('#rows [data-f]')) {
      const r = rows.find(r => String(r.uid) === box.closest('.row').dataset.uid);
      if (r && String(r[box.dataset.f] ?? '') === box.value) live.sent(box);
    }
    if (redraw) await live.now();
    return true;
  }
  function changed() {
    ++seq; dirty = true; paint();
    return persist(true);
  }

  /* A scheduled page launches nothing: its fire does, once its stage closes.
     A refused launch shows its banner, as 1100 draws it. */
  async function launch() {
    if (BUSY || !ROWS.length || D.after) return;
    clearTimeout(timer);
    if (dirty && !await persist(false)) return;
    const got = await live.post(form('launch'));
    if (got.ok === null) {
      $('launch-error').hidden = false;
      $('launch').disabled = true;
      return;
    }
    await live.now();
  }

  /* ---- drawing ------------------------------------------------------------ */

  function node(n, grow) {
    if (n.split) {
      const axis = n.split === 'columns' ? 0 : 1;
      return `<div class="split ${axis ? 'rows' : 'cols'}" style="flex:${grow} 1 0">`
        + n.children.map(c => node(c, size(c)[axis])).join('') + '</div>';
    }
    if (n.ghost != null) {
      const r = ROWS[n.idx];
      return `<div class="pane ghost${n.idx === active ? ' active' : ''}" data-anchor="${esc(idOf(n))}" style="flex:${grow} 1 0"
        data-idx="${n.idx}" title="${esc(tag(r))} ${esc(r.name)}"><div class="pl">${esc(tag(r))}</div>
        <div class="pm">${esc(web(r) ? (r.name || 'browser') : r.name)}</div></div>`;
    }
    const me = n.pane === STARTER;
    return `<div class="pane live" data-anchor="${esc(idOf(n))}" style="flex:${grow} 1 0; --c:var(--${me ? 'green' : n.number ? 'grey' : 'line'})">
      <div class="pl">${esc(n.number)} ${esc(n.label)}</div>
      <div class="pm">${me ? 'starter' : ''}</div></div>`;
  }

  function drawMap() {
    const r = ROWS[active];
    const el = $('map');
    const win = r ? r.win : HOME.win, tab = r ? r.tab : HOME.tab;
    let tree = treeFor(win, tab, drag && drag.moving && !drag.planned ? ROWS.length - 1 : ROWS.length);
    if (tree && drag && drag.moving && drag.planned) tree = without(tree, drag.source)[0];
    if (!tree) { el.innerHTML = drag && drag.moving ? '<div class="note">No other pane in this tab.</div>'
      : '<div class="note">iTerm did not answer. The layout is missing.</div>'; return; }
    const [w, h] = size(tree);
    const sideways = SIDEWAYS.matches;
    const strip = tabsOf(win).map(t => `<span class="${t === tab ? 'on' : ''}">${esc(tabLabel(win, t))}</span>`).join('');
    const who = BUSY ? 'launching · new panes appear as they open'
      : r ? `row ${shown().indexOf(active) + 1} · ${esc(tag(r))} ${esc(web(r) ? (r.name || 'browser') : r.name)}` : 'no row';
    el.innerHTML = `<div class="mhead"><span class="who">${who}</span>
        <span class="lbl">${esc(winLabel(win))}</span><span class="strip">${strip}</span>
        <span class="lbl">${BUSY ? '' : `drag any pane · moves apply on Launch`}</span>
        ${PLANNED.length && !BUSY ? `<button type="button" id="undo">Undo move</button>` : ''}</div>
      <div class="tabmap" style="--h:${H}px; --ar:${w / h}">${node(tree, 1)}</div>${sideways ? bigPad(r) : ''}`;
    if (!sideways) return;
    /* The map stands as tall as the first screen has room for, under its head. */
    const main = document.querySelector('main'), map = el.querySelector('.tabmap');
    const top = map.getBoundingClientRect().top - main.getBoundingClientRect().top + main.scrollTop;
    map.style.setProperty('--h', Math.max(160, main.clientHeight - top - 8) + 'px');
  }

  /* The picked row's lands line and its four arrows, made for a finger. */
  function bigPad(r) {
    const still = BUSY || !r || !r.at ? ' disabled' : '';
    return `<div class="side"><span class="lbl place">lands</span>
      <div class="spot">${r && !BUSY ? esc(where(active)) : ''}</div><div class="pad big">`
      + [['up', '↑'], ['left', '←'], ['right', '→'], ['down', '↓']].map(([d, a]) =>
        `<button data-d="${d}"${still}>${a}</button>`).join('') + '</div></div>';
  }

  /* Which pill of a group shows picked: what its row holds, a family,
     sonnet, as its newest model's pill. A row holding none yet shows what
     its first save takes: the order's next turn, or System's. */
  function turn(i) {
    const k = ROWS.slice(0, i).filter(r => !web(r) && !r.account).length, o = D.order.order;
    return o.length ? o[(D.order.next + k) % o.length] : D.fallback;
  }
  function picked(i, key) {
    const r = ROWS[i], set = r[key];
    const now = key === 'account' ? turn(i) : D.system[key];
    const held = set == null || set === '' ? now : String(set);
    return key === 'model' && Object.hasOwn(D.families, held) ? D.families[held] : held;
  }

  /* The page as my rows stand: the map, then on each row 1100 drew, its
     lands line, whether it is the one I picked, its arrows and its pills.
     Then the buttons along the top. */
  function paint() {
    drawMap();
    for (const card of document.querySelectorAll('#rows .row[data-uid]')) {
      const i = indexOf(card);
      if (i < 0) continue;
      const r = ROWS[i];
      card.classList.toggle('active', i === active && !BUSY);
      const lands = card.querySelector('.lands'), text = where(i);
      if (lands && lands.textContent !== text) lands.textContent = text;
      for (const b of card.querySelectorAll('.pad button')) b.disabled = BUSY || i !== active || !r.at;
      for (const b of card.querySelectorAll('[data-pill]')) {
        b.classList.toggle('on', b.dataset.pill === 'drive' ? !!r.drive : picked(i, b.dataset.pill) === b.dataset.v);
      }
      for (const b of card.querySelectorAll('[data-win]:not(.new)')) b.classList.toggle('on', r.win === b.dataset.win);
      for (const b of card.querySelectorAll('[data-tab]:not(.new)')) b.classList.toggle('on', r.tab === b.dataset.tab);
    }
    document.body.classList.toggle('none', !ROWS.length);
    const go = $('launch');
    const count = (k, word) => k ? `${k} ${word}${k === 1 ? '' : 's'}` : '';
    const sessions = ROWS.filter(r => !web(r)).length, browsers = ROWS.length - sessions;
    // A scheduled page's press launches nothing, so its button never looks pressable.
    if (!$('launch-error').hidden) go.disabled = true;
    else go.disabled = BUSY || !ROWS.length || !!D.after;
    const words = BUSY ? 'Launching…' : `${D.after ? 'Schedule' : 'Launch'} · ${ROWS.length}`;
    if (go.textContent !== words) go.textContent = words;
    go.title = D.after ? `Launches once stage ${D.after} closes`
      : [count(sessions, 'session'), count(browsers, 'browser')].filter(Boolean).join(', ');
    $('add').disabled = BUSY;
    $('addweb').disabled = BUSY;
  }

  function pick(i) { if (!BUSY && i !== active) { active = i; paint(); } }
  function undoMove() { if (!BUSY && PLANNED.length) { PLANNED.pop(); changed(); } }

  function forgetRow(r) {
    const id = 'r:' + r.uid;
    PLANNED = PLANNED.filter(m => m.source !== id && m.anchor !== id);
  }

  /* A new window opens with its own first tab. A new tab starts empty. */
  function setWin(i, k) {
    const r = ROWS[i];
    if (k === r.win) return;
    forgetRow(r);
    active = i;
    if (k === null) { r.win = next(ROWS.map(s => s.win)); r.tab = 'N1'; }
    else { r.win = k; r.tab = tabsOf(k)[0]; }
    r.at = null;
    changed();
  }

  function setTab(i, k) {
    const r = ROWS[i];
    if (k === r.tab) return;
    forgetRow(r);
    active = i;
    r.tab = k === null ? next(ROWS.filter(s => s.win === r.win).map(s => s.tab)) : k;
    r.at = null;
    changed();
  }

  function drop(i) {
    forgetRow(ROWS[i]);
    ROWS.splice(i, 1);
    active = Math.max(0, Math.min(active, ROWS.length - 1));
    changed();
  }

  function add(browser) {
    if (BUSY) return;
    const last = ROWS[ROWS.length - 1];
    const uid = Date.now();
    SEEN.add(uid);
    const place = {win: last ? last.win : HOME.win, tab: last ? last.tab : HOME.tab, at: null};
    ROWS.push(browser ? {uid, kind: 'browser', site: '', ...place} : {uid, name: '', message: '', ...place});
    active = ROWS.length - 1;
    changed();
  }

  /* ---- what 1100 drew --------------------------------------------------------- */

  /* 1100's picture read again: the layout always, the rows unless a change
     of mine has not landed yet. */
  function read() {
    try { D = JSON.parse($('launch-data').textContent); } catch (e) { return; }
    LAYOUT = D.layout;
    STARTER = D.starter;
    HOME = LAYOUT.length ? {win: 'L:' + LAYOUT[0].window, tab: 'L:' + LAYOUT[0].tabs[0].tab, pane: ''}
      : {win: 'N1', tab: 'N1', pane: ''};
    LAYOUT.forEach(w => w.tabs.forEach(t => leaves(t.root).forEach(p => {
      if (p.pane === STARTER) HOME = {win: 'L:' + w.window, tab: 'L:' + t.tab, pane: p.pane};
    })));
    FULL = liveTab(HOME.win, HOME.tab) ? size(liveTab(HOME.win, HOME.tab).root) : [1600, 900];
    if (dirty || drag) return;
    const uid = ROWS[active] && ROWS[active].uid, first = !ROWS.length && !SEEN.size;
    ROWS = copy(D.rows);
    PLANNED = copy(D.moves || []);
    ROWS.forEach(r => SEEN.add(r.uid));
    BUSY = ROWS.some(r => r.status === 'booting');
    const kept = ROWS.findIndex(r => r.uid === uid);
    active = !first && kept >= 0 ? kept : first ? shown().find(i => ROWS[i].status !== 'booting') ?? 0
      : Math.max(0, Math.min(active, ROWS.length - 1));
  }

  document.addEventListener('click', e => {
    const t = e.target;
    if (!D) return;
    if (t.closest('#add')) return add(false);
    if (t.closest('#addweb')) return add(true);
    if (t.closest('#launch')) return launch();
    if (t.closest('#retry')) return persist(true);
    if (t.closest('#undo')) return undoMove();
    const arrow = t.closest('#map .pad [data-d]');
    if (arrow) return move(arrow.dataset.d);
    const ghost = t.closest('#map .pane.ghost');
    if (ghost) { if (!suppressClick) pick(Number(ghost.dataset.idx)); return; }
    const card = t.closest('#rows .row[data-uid]'), i = indexOf(card);
    if (i < 0 || t.closest('input, textarea')) return;
    const b = t.closest('button');
    if (!b) return pick(i);
    const r = ROWS[i];
    if (b.dataset.pill === 'drive') { r.drive = !r.drive; changed(); }
    else if (b.dataset.pill) { r[b.dataset.pill] = b.dataset.v; changed(); }
    else if ('win' in b.dataset) setWin(i, b.dataset.win || null);
    else if ('tab' in b.dataset) setTab(i, b.dataset.tab || null);
    else if (b.dataset.d) move(b.dataset.d);
    else if ('drop' in b.dataset) drop(i);
  });
  /* Typing a number or a name redraws the map and every lands line, never
     the box being typed in. */
  document.addEventListener('input', e => {
    const f = e.target.closest('#rows [data-f]'), i = indexOf(f && f.closest('.row[data-uid]'));
    if (i < 0) return;
    ROWS[i][f.dataset.f] = f.value;
    if (f.dataset.f !== 'message') paint();
    save();
  });
  document.addEventListener('pointerdown', e => {
    const p = e.target.closest('#map .pane[data-anchor]');
    if (!p || !D) return;
    if (p.classList.contains('ghost')) dragStart(e, Number(p.dataset.idx));
    else if (p.classList.contains('live')) dragLive(e, p.dataset.anchor);
  });
  addEventListener('pointermove', dragMove, {passive: false});
  addEventListener('pointerup', dragEnd);
  addEventListener('pointercancel', dragEnd);
  document.addEventListener('lostpointercapture', e => {
    if (e.target.id === 'map') dragEnd({pointerId: e.pointerId, type: 'pointercancel'});
  });
  // A new primary press also releases a gesture whose end never arrived.
  addEventListener('pointerdown', e => {
    if (!drag || !e.isPrimary || e.button !== 0) return;
    dragEnd({pointerId: drag.id, type: 'pointercancel'});
    e.preventDefault();
    e.stopImmediatePropagation();
  }, true);
  document.addEventListener('keydown', e => {
    if (!D || ['INPUT', 'TEXTAREA'].includes(e.target.tagName)) return;
    const dir = {ArrowRight: 'right', ArrowLeft: 'left', ArrowDown: 'down', ArrowUp: 'up'}[e.key];
    if (dir) { e.preventDefault(); move(dir); }
  });
  /* Turning my phone draws the page anew. A screen changing size measures the map again. */
  SIDEWAYS.addEventListener('change', () => { if (D) paint(); });
  addEventListener('resize', () => { if (D && SIDEWAYS.matches) drawMap(); });
  addEventListener('beforeunload', () => { if (dirty) persist(false); });

  live.ready(() => { read(); if (D) paint(); });
  live.drawn(() => { read(); if (D) paint(); });
})();
