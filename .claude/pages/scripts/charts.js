/* charts.js — the charts the pages on the contract share. A page draws a
   ```mermaid fence as a pre.mmd inside #items, loads this file after
   page.py's ZOOM, and calls charts() from live.ready and live.drawn. The
   shell's #items .chart rules dress them. A page may add marks of its own
   to STD, WORD and HUE, and set READ. A page drawn with no server, as
   explanation-page.py check draws, puts this file inline.

   The chart standard. Colour says who acts, and grey says unchanged. Gold,
   dashed, says assumed, never ruled. A diamond is a condition, a cylinder
   a file. A solid arrow means then, a dashed one reads. The legend lists
   only what a chart uses. */
const STD = {
  you: 'fill:#3b2226,stroke:#f87171,stroke-width:2px,color:#e6e8ee',
  session: 'fill:#1e2b40,stroke:#60a5fa,stroke-width:2px,color:#e6e8ee',
  done: 'fill:#1b3326,stroke:#4ade80,stroke-width:2px,color:#e6e8ee',
  today: 'fill:#1a1d26,stroke:#4b5162,stroke-width:1px,color:#8b91a3',
  assumed: 'fill:#2a2414,stroke:#fbbf24,stroke-width:2px,stroke-dasharray:5 3,color:#e6e8ee'};
const WORD = {you: 'You act', session: 'A session or tool acts', done: 'Settled', today: 'Unchanged',
  assumed: 'Assumed'};
const HUE = {you: 'red', session: 'blue', done: 'green', today: 'grey', assumed: 'gold'};
const flow = src => /^\s*(flowchart|graph)\b/.test(src);
const standard = src => flow(src)
  ? src + '\n' + Object.entries(STD).map(([k, v]) => `classDef ${k} ${v}`).join('\n') : src;
/* A chart's line "%% green: Paid outcome" names what that mark means in
   it. A mark with no word, page's or chart's, stays out of its legend. A
   hue is a shell colour's name, or a colour itself. */
function legend(src) {
  if (!flow(src)) return '';
  const said = Object.fromEntries([...src.matchAll(/^\s*%%\s*(\w+):\s*(.+?)\s*$/gm)].map(m => [m[1], m[2]]));
  const used = Object.keys(STD).filter(k => new RegExp(`:::${k}\\b`).test(src) && (said[k] || WORD[k]))
    .map(k => `<span class="lg"><i class="sw${k === 'assumed' ? ' dash' : ''}" style="--c:${
      HUE[k].startsWith('#') ? HUE[k] : `var(--${HUE[k]})`}"></i>${
      (said[k] || WORD[k]).replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`);
  if (/\w\{/.test(src)) used.push('<span class="lg"><i class="sh dia"></i>A condition</span>');
  if (/\[\(/.test(src)) used.push('<span class="lg"><i class="sh cyl"></i>A file</span>');
  if (/-->/.test(src)) used.push('<span class="lg"><i class="ar"></i>Then</span>');
  if (/-\.->|-\.\s/.test(src)) used.push('<span class="lg"><i class="ar dash"></i>Reads</span>');
  return used.length ? `<div class="legend">${used.join('')}</div>` : '';
}

/* Mermaid loads only when a chart waits. Offline, a chart stays its source.
   Every chart draws left to right, whatever way it was written. Its strip
   flips it top to bottom, and back. The browser draws both ways, so a
   flip costs the session nothing. A label is SVG text, never HTML: WebKit
   measures HTML in a chart at the page's zoom, so zoomed in, a long label
   never wrapped, and its box cut it off. */
let M = null;
const mermaid = () => M = M || import('https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs')
  .then(x => { const m = x.default;
    m.initialize({ startOnLoad: false, htmlLabels: false, theme: 'dark', fontFamily: 'ui-monospace, Menlo, monospace',
      flowchart: { padding: 12 },
      themeVariables: { background: '#161922', primaryColor: '#1d212c', primaryBorderColor: '#8b91a3',
        primaryTextColor: '#e6e8ee', lineColor: '#8b91a3', fontSize: '13px' } });
    return m; });
/* A flowchart holding the line %% elk is placed by ELK, which keeps arrows
   from crossing. It loads only when such a chart waits. */
const ELK = /^\s*%%\s*elk\s*$/m;
let E = null;
const elk = m => E = E || import('https://cdn.jsdelivr.net/npm/@mermaid-js/layout-elk@0/dist/mermaid-layout-elk.esm.min.mjs')
  .then(x => { m.registerLayoutLoaders(x.default); return m; });
const orient = (src, dir) => { const ls = src.split('\n'), first = ls.findIndex(l => l.trim());
  return ls.map((l, i) => i === first
    ? l.replace(/^(\s*)(?:flowchart|graph)\b(?:\s+(?:TB|TD|BT|LR|RL)\b)?/, '$1flowchart ' + dir)
    : l.replace(/^(\s*)direction\s+(?:TB|TD|BT|LR|RL)\b/, '$1direction ' + dir)).join('\n'); };

/* Each chart draws once per direction, one render at a time. A flip is kept
   by its source, so a redraw of the page keeps it. */
const SVG = {}, DIR = {};
let queue = Promise.resolve(), ids = 0;
function svgOf(src, dir) {
  const key = dir + '\n' + src;
  const placed = ELK.test(src);
  if (!SVG[key]) SVG[key] = queue = queue.catch(() => {}).then(mermaid).then(m => placed ? elk(m) : m)
    .then(m => m.render('mmd' + ids++, (placed ? '---\nconfig:\n  layout: elk\n---\n' : '')
      + standard(orient(src, dir)))).then(r => r.svg);
  return SVG[key];
}
/* A page in a hidden frame has no width, so Mermaid measures nothing and
   fails. Its charts wait, and draw once the frame shows and resizes.

   1100 drew the source, a pre.mmd, and it stays where 1100 put it, hidden:
   its chart stands right after it. So a change to the source lands on the
   pre, and its chart is drawn again from it. A chart whose source left
   the page goes with it. A source Mermaid could not draw shows as text,
   and is tried again once it changes. */
const CHARTED = new WeakMap();
async function charts() {
  if (!innerWidth) return;
  for (const d of [...document.querySelectorAll('#items .chart')]) {
    const el = d.chart && d.chart.pre;
    if (!el || (el.isConnected && el.textContent === d.chart.src)) continue;
    d.remove();
    CHARTED.delete(el);
    el.hidden = false;
  }
  for (const el of document.querySelectorAll('#items pre.pre')) {
    if (CHARTED.has(el) && CHARTED.get(el) !== el.textContent) { CHARTED.delete(el); el.className = 'mmd'; }
  }
  for (const el of [...document.querySelectorAll('pre.mmd')]) {
    if (CHARTED.has(el)) continue;
    const src = el.textContent;
    CHARTED.set(el, src);
    let svg;
    try { svg = await svgOf(src, DIR[src] || 'LR'); } catch (e) { el.className = 'pre'; continue; }
    if (!el.isConnected || el.textContent !== src) { CHARTED.delete(el); continue; }
    const d = chart(src, svg);
    d.chart.pre = el;
    el.hidden = true;
    el.after(d);
    measure(d.chart);
  }
}

/* A chart is a frame: its strip, then a window it zooms and pans inside,
   then its legend. It keeps its natural size, and shrinks only when it is
   wider than the window, or taller than main. A page borrowing the charts
   may set READ: a chart shrinks to main's height only down to that size.
   Any smaller and it keeps its width's size, and the page scrolls past it.
   Narrower than the window, it sits in the middle. The window is as tall
   as the fitted chart, so the page never moves when the chart zooms.
   Its bottom edge drags down: the window grows, and the chart zooms with
   it, its top held still. Fit brings both back. */
const FIT = {k: 1, x: 0, y: 0}, MAX = 6;
let READ = 0;
const FLIP = {TB: ['LR', '↔ Horizontal'], LR: ['TB', '↕ Vertical']};
const atFit = v => v.k === 1 && v.x === 0 && v.y === 0;
const home = f => f ? Math.max(0, (f.vw - f.w) / 2) : 0;
/* The window's height: the fitted chart's, or more once its edge is dragged. */
const tall = c => Math.max(c.tall || 0, c.fit.h);
/* How many of the screen's pixels one of the window's own takes: home's
   zoom of the whole page. A pointer and a box's rectangle are the screen's;
   the chart's sizes and moves are the window's own, so each is divided. */
const scaleOf = c => { const p = c.el.querySelector('.cv');
  return p.offsetWidth ? p.getBoundingClientRect().width / p.offsetWidth : 1; };
function chart(src, svg) {
  const d = document.createElement('div');
  d.className = 'chart';
  d.innerHTML = '<div class="cf"><div class="strip">' + ZOOM_TOOLS
    + (flow(src) ? '<button class="flip" onmousedown="event.preventDefault()"></button>' : '')
    + '<span class="tip"></span></div><div class="cv"><div class="cz"></div>'
    + '<div class="sb x"><i></i></div><div class="sb y"><i></i></div></div>'
    + '<div class="grip" title="Drag down to make the chart bigger"></div></div>' + legend(src);
  const c = d.chart = {el: d, src, dir: DIR[src] || 'LR'};
  put(c, svg);
  wire(c);
  return d;
}
function put(c, svg) {
  const z = c.el.querySelector('.cz');
  z.innerHTML = svg;
  const box = z.querySelector('svg').viewBox.baseVal;
  c.nat = box && box.width ? {w: box.width, h: box.height} : {w: 400, h: 300};
  c.view = {...FIT};
  c.fit = null;
  c.tall = 0;
  measure(c);
}
/* A chart with no width yet measures nothing. It measures once it has one. */
function measure(c) {
  const p = c.el.querySelector('.cv');
  if (c.el.isConnected && p.clientWidth) {
    const main = c.el.closest('main');
    const area = main ? main.clientHeight : innerHeight;
    const extra = (c.el.getBoundingClientRect().height - p.getBoundingClientRect().height) / scaleOf(c) + 14;
    const vw = p.clientWidth, high = Math.max(120, area - extra) / c.nat.h;
    const s = Math.min(1, vw / c.nat.w, high >= READ ? high : 1);
    c.fit = {s, w: c.nat.w * s, h: c.nat.h * s, vw};
    c.view = clampView(c, c.view);
  }
  repaint(c);
}
function repaint(c) {
  const d = c.el, f = c.fit, v = c.view, away = !atFit(v), b = d.querySelector('.flip');
  if (b) b.textContent = FLIP[c.dir][1];
  if (!f) return;
  const p = d.querySelector('.cv'), z = d.querySelector('.cz');
  p.style.height = tall(c) + 'px';
  z.style.width = f.w + 'px';
  z.style.height = f.h + 'px';
  z.style.transform = `translate(${home(f) + v.x}px, ${v.y}px) scale(${v.k})`;
  p.classList.toggle('away', away);
  bars(c);
  if (c.paint) c.paint();
  d.querySelector('.tip').textContent = away ? 'drag or swipe to pan'
    : f.s < 0.995 ? 'shrunk to fit · pinch to read' : 'pinch to zoom';
}
/* A scroll bar shows on an edge of the window only while the chart runs
   past it that way: along the bottom when it is wider, down the right when
   it is taller. Its thumb's length is how much of the chart shows, and it
   sits where the window looks. */
function bars(c) {
  const f = c.fit, v = c.view, d = c.el;
  axis(d.querySelector('.sb.x'), f.vw, f.w * v.k, -(home(f) + v.x), true);
  axis(d.querySelector('.sb.y'), tall(c), f.h * v.k, -v.y, false);
}
function axis(bar, frame, content, at, wide) {
  const on = content > frame + 0.5;
  bar.classList.toggle('on', on);
  if (!on) return;
  const t = bar.firstChild, track = wide ? bar.clientWidth : bar.clientHeight;
  const len = Math.max(24, track * frame / content), spot = Math.min(1, Math.max(0, at / (content - frame)));
  t.style[wide ? 'width' : 'height'] = len + 'px';
  t.style[wide ? 'left' : 'top'] = spot * (track - len) + 'px';
}
/* Bigger than the window, no edge comes inside it. Smaller, half of it
   stays in view. x counts from the middle, where the chart sits at Fit. */
const keep = (pos, content, frame, from = 0) => { const [lo, hi] = content > frame
  ? [frame - content, 0] : [-content / 2, frame - content / 2];
  return Math.min(hi - from, Math.max(lo - from, pos)); };
/* The rows of the window I can see. The page may scroll its top above
   main, or its bottom below it. A chart pans between these, so its top
   and bottom always come into sight. */
function seen(c) {
  const k = scaleOf(c), r = c.el.querySelector('.cv').getBoundingClientRect(), main = c.el.closest('main');
  const m = main ? main.getBoundingClientRect() : {top: 0, bottom: innerHeight};
  const t = Math.max(0, (m.top - r.top) / k);
  const b = Math.min(tall(c), (m.bottom - r.top) / k);
  return b > t ? {t, b} : {t: 0, b: tall(c)};
}
const clampView = (c, v) => { if (!c.fit) return v; const s = seen(c);
  return {k: v.k, x: keep(v.x, c.fit.w * v.k, c.fit.vw, home(c.fit)), y: keep(v.y, c.fit.h * v.k, s.b - s.t, -s.t)}; };
function zoomTo(c, k, at) {
  const v = c.view, next = Math.min(MAX, Math.max(1, k));
  if (!c.fit || next === v.k) return;
  if (next <= 1) { c.view = {...FIT}; return repaint(c); }
  const r = next / v.k, ax = at.x - home(c.fit);
  c.view = clampView(c, {k: next, x: ax - (ax - v.x) * r, y: at.y - (at.y - v.y) * r});
  repaint(c);
}
/* + and − zoom around the middle of what shows. */
function centre(c) {
  const f = c.fit, v = c.view;
  if (!f) return {x: 0, y: 0};
  const left = home(f) + v.x, x0 = Math.max(0, left), x1 = Math.min(f.vw, left + f.w * v.k);
  const s = seen(c), y0 = Math.max(s.t, v.y), y1 = Math.min(s.b, v.y + f.h * v.k);
  return {x: x1 > x0 ? (x0 + x1) / 2 : f.vw / 2, y: y1 > y0 ? (y0 + y1) / 2 : (s.t + s.b) / 2};
}
async function flipIt(c) {
  const b = c.el.querySelector('.flip'), to = FLIP[c.dir][0];
  b.disabled = true;
  try { const svg = await svgOf(c.src, to); c.dir = DIR[c.src] = to; put(c, svg); } catch (e) {}
  b.disabled = false;
}
/* The strip's zoom tools, and a pinch, are page.py's: ZOOM. A chart's own
   zoom, k, counts from its fitted size, so its size is the fit's times k.
   A swipe scrolls the page at Fit, and pans the chart away from it. A
   drag pans too. */
function wire(c) {
  const d = c.el, p = d.querySelector('.cv'), b = d.querySelector('.flip');
  c.paint = zoomer(d.querySelector('.zt'), p, {
    scale: () => c.fit ? c.fit.s * c.view.k : 0,
    bounds: () => [c.fit.s, c.fit.s * MAX],
    to: (s, at) => zoomTo(c, s / c.fit.s, at ? {x: at.x / scaleOf(c), y: at.y / scaleOf(c)} : centre(c)),
    fit: () => { c.view = {...FIT}; c.tall = 0; repaint(c); },
    fitted: () => atFit(c.view) && tall(c) === c.fit.h});
  if (b) b.onclick = () => flipIt(c);
  scrub(c, d.querySelector('.sb.x'), true);
  scrub(c, d.querySelector('.sb.y'), false);
  /* The bottom edge, dragged, sets the window's height. The zoom grows in
     step with it, around the window's middle, its top held still. The edge
     stays under the pointer. Held past the bottom of main, the page
     scrolls on, and the window keeps growing. */
  const g = d.querySelector('.grip');
  const pull = () => { const q = c.pull, f = c.fit;
    if (!q || !f) return;
    const top = p.getBoundingClientRect().top;
    const h = Math.min(q.h * MAX / q.v.k, Math.max(f.h, (q.at - q.off - top) / scaleOf(c)));
    const k = Math.max(1, q.v.k * h / q.h), r = k / q.v.k, ax = f.vw / 2 - home(f);
    c.tall = h;
    c.view = clampView(c, {k, x: ax - (ax - q.v.x) * r, y: q.v.y * r});
    repaint(c); };
  const roll = () => { const q = c.pull;
    if (!q) return;
    const main = d.closest('main');
    const floor = main ? main.getBoundingClientRect().bottom : innerHeight;
    if (main && q.at > floor && tall(c) < q.h * MAX / q.v.k - 0.5) { main.scrollTop += Math.min(20, 1 + (q.at - floor) / 3); pull(); }
    requestAnimationFrame(roll); };
  g.addEventListener('pointerdown', e => {
    if (e.button !== 0 || !c.fit) return;
    e.preventDefault();
    c.pull = {id: e.pointerId, at: e.clientY, off: e.clientY - p.getBoundingClientRect().bottom, h: tall(c), v: {...c.view}};
    g.setPointerCapture(e.pointerId);
    g.classList.add('drag');
    requestAnimationFrame(roll);
  });
  g.addEventListener('pointermove', e => {
    if (c.pull && c.pull.id === e.pointerId) { c.pull.at = e.clientY; pull(); } });
  const release = e => { if (c.pull && c.pull.id === e.pointerId) { c.pull = null; g.classList.remove('drag'); } };
  g.addEventListener('pointerup', release);
  g.addEventListener('pointercancel', release);
  p.addEventListener('wheel', e => {
    if (!c.fit || e.ctrlKey) return;
    const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? p.clientHeight : 1 / scaleOf(c);
    const v = c.view;
    if (atFit(v)) return;
    const next = clampView(c, {k: v.k, x: v.x - e.deltaX * unit, y: v.y - e.deltaY * unit});
    if (next.x === v.x && next.y === v.y) return;
    e.preventDefault();
    c.view = next;
    repaint(c);
  }, {passive: false});
  p.addEventListener('pointerdown', e => {
    if (e.button !== 0 || atFit(c.view)) return;
    c.drag = {id: e.pointerId, x: e.clientX, y: e.clientY, vx: c.view.x, vy: c.view.y, k: scaleOf(c)};
    p.setPointerCapture(e.pointerId);
    p.classList.add('drag');
  });
  p.addEventListener('pointermove', e => { const g = c.drag;
    if (!g || g.id !== e.pointerId) return;
    c.view = clampView(c, {k: c.view.k, x: g.vx + (e.clientX - g.x) / g.k, y: g.vy + (e.clientY - g.y) / g.k});
    repaint(c); });
  const up = e => { if (c.drag && c.drag.id === e.pointerId) { c.drag = null; p.classList.remove('drag'); } };
  p.addEventListener('pointerup', up);
  p.addEventListener('pointercancel', up);
}
/* A scroll bar's thumb drags the chart along its edge. A press on the bar
   beside the thumb brings the thumb there first. The bar never pans the
   window under it. */
function scrub(c, bar, wide) {
  const t = bar.firstChild, along = e => wide ? e.clientX : e.clientY;
  bar.addEventListener('pointerdown', e => {
    if (e.button !== 0 || !c.fit) return;
    e.stopPropagation();
    e.preventDefault();
    const f = c.fit, v = c.view, r = bar.getBoundingClientRect(), k = scaleOf(c);
    const frame = wide ? f.vw : tall(c), content = (wide ? f.w : f.h) * v.k;
    const len = wide ? t.offsetWidth : t.offsetHeight, room = (wide ? r.width : r.height) / k - len;
    if (room <= 0) return;
    const per = (content - frame) / room, from = along(e);
    const at = e.target === t ? (wide ? -(home(f) + v.x) : -v.y) : ((from - (wide ? r.left : r.top)) / k - len / 2) * per;
    const go = m => { const to = at + (along(m) - from) / k * per;
      c.view = clampView(c, wide ? {...c.view, x: -to - home(f)} : {...c.view, y: -to});
      repaint(c); };
    go(e);
    bar.setPointerCapture(e.pointerId);
    bar.classList.add('drag');
    bar.onpointermove = go;
    bar.onpointerup = bar.onpointercancel = () => { bar.onpointermove = null; bar.classList.remove('drag'); };
  });
}
const fitAll = () => document.querySelectorAll('#items .chart').forEach(d => measure(d.chart));
addEventListener('resize', () => { charts(); fitAll(); });
