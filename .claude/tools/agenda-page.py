#!/usr/bin/env python3
"""agenda-page.py — my agenda, drawn on 1100/agenda.

Its folder, .claude/state/agenda/, holds one file per item, each naming
its topics. This page draws them as one chart, read from left
to right: the topics' rectangles down the first column, in their
order, then the items waiting on nothing, each linked to the rectangle of
every topic it sits under, then what waits on them, each one column past
the furthest item it waits on. An item under two topics is one item, a line in
from each rectangle. An item waiting on other items has no line from a
rectangle.
An agenda split into phases draws one such chart per phase, each with its
own rectangles, under its heading, as "Phase 1: Launch", the next
phase's below it.
No line joins two of them.
It opens left to right at every width, a phone's too. Flipped, it reads
from top to bottom, the rectangles side by side, and each device keeps the
way I last flipped it to.

The page wears the top rail every page does, on top whichever way the
chart flows. Its middle counts every item, then Mine, its number red, each
a button opening its list at the right, where a note opens. Then the
orders, how many columns of items there are, and a chip for each, and All.
A chip shows that order's items alone, their names and marks with them;
every line stays, and the chart never moves. Its tools sit together at
its right: a search, the zoom tools every chart wears, and the flip. The
search finds titles and notes as I type, and its hits fill the same list,
a title's before a note's. A list opens straight on its rows, with no
head. A row's click opens its item's note, as a click on the chart does.
Each row, and each item a note lists, wears its item's colour. Narrower than
1060, the counts lead the first line, and the search and the zoom tools end
it while they fit; what does not fit takes the next line. The orders take a
row of their own.

The chart is placed by the page itself, in the browser: each column's
order crosses as few lines as it can find, and each item sits between the
items it hangs on. The rectangles keep
their order, and a line from one to an item weighs a thousand crossings in
the search, so the items out of a rectangle stay beside it. The rectangles
stand the same distance apart, whatever their items. Lines bend only between
columns, so none crosses a name. The browser keeps the order it found
with the agenda's shape, so the same shape opens at once. Each topic wears
its own colour, lib/agenda.py's. An item waiting on nothing takes the
even mix of its topics' colours; any other the mix of what it waits on,
darker a column further out.

A click on an item opens its note, at the right, or over the chart on a
phone. An item whose note carries a Mine line wears a small red mark at its top right.
The note holds
Start: pressed, a session opens on its item, through tools/launch.py, its
first message the item, in my words.

A write into the folder is heard, and the page draws itself again in
place: its counts move, and its way, its size, its spot, its chip and an
open note or list stay. 1100 serves it at /agenda, and its JSON at
/agenda/data. FOLDER is the folder it draws: a test points it at a
copy.

1100 imports it. Run, it tests itself:

  agenda-page.py test   draws a scratch agenda in headless Chrome, and
                        fails when two neighbouring rectangles stand
                        other than 64 apart
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
import agenda  # noqa: E402
import iterm  # noqa: E402
import launch  # noqa: E402
import page  # noqa: E402
import registry  # noqa: E402
import serve  # noqa: E402

HERE =os.path.dirname(os.path.abspath(__file__))
FOLDER = agenda.FOLDER
LAUNCH = os.path.join(HERE, "launch.py")
# The browser the test draws in, headless, in a profile of its own.
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

STYLE = """<style>
  body > main { padding:0; overflow:hidden; }
  /* The top rail. Its middle holds the counts, each a button opening its
     list, then the orders, a chip for each and All. Its tools sit together
     at its right. */
  header.top.agenda .mid { display:flex; align-items:center; justify-self:stretch; justify-content:center;
    gap:4px; font-size:13px; font-weight:400; color:var(--text); }
  header.top.agenda .cts, header.top.agenda .ord { display:flex; align-items:center; gap:4px; min-width:0; }
  header.top.agenda .cts, header.top.agenda .ord > .ct { flex:none; }
  header.top.agenda .ct { display:inline-flex; align-items:center; gap:5px; height:28px; padding:0 8px;
    border:1px solid transparent; border-radius:4px; background:none; color:var(--dim); font-size:13px;
    font-weight:400; white-space:nowrap; }
  header.top.agenda .ct b { font-size:13px; color:var(--text); }
  header.top.agenda button.ct:hover { border-color:var(--line); }
  header.top.agenda .ct.on { background:var(--bg); border-color:var(--dim); }
  /* The Mine count wears the mark it counts, its number red too. */
  header.top.agenda .ct .mk { flex:none; width:7px; height:7px; border-radius:50%; background:var(--red); }
  header.top.agenda .ct b.rd { color:var(--red); }
  /* A chip shows one order alone, or All. The chips wear the launch page's
     pills, in its window and tab pills' shade. A row of chips too long for
     its space scrolls sideways. */
  header.top.agenda .sl { display:flex; min-width:0; overflow-x:auto; }
  header.top.agenda .sl .pills { flex:none; --g:var(--blue); }
  header.top.agenda .sl .group { gap:3px; }
  header.top.agenda .acts, header.top.agenda .tl { display:flex; align-items:center; gap:8px; }
  header.top.agenda .find { flex:0 1 220px; min-width:120px; }
  header.top.agenda .acts button { display:inline-flex; align-items:center; justify-content:center; height:28px;
    min-width:28px; padding:0 8px; border:1px solid var(--dim); border-radius:4px; background:var(--bg);
    color:var(--text); font-size:13px; font-weight:700; line-height:1; }
  header.top.agenda .acts button:hover:not(:disabled) { border-color:var(--text); }
  header.top.agenda .acts button:disabled { background:var(--bg); color:var(--dim); border-color:var(--line);
    cursor:default; }
  header.top.agenda .pct { font-size:12px; color:var(--dim); }
  /* Narrow, the counts lead the first line, then the search and the zoom
     tools at its right, each as long as it fits. What does not fit takes
     the next line, at the right. The orders and their chips take a row of
     their own, under them. */
  @media (max-width:1060px) {
    header.top.agenda { display:flex; flex-wrap:wrap; justify-content:flex-end; row-gap:6px; column-gap:8px; }
    header.top.agenda .mid, header.top.agenda .acts { display:contents; }
    header.top.agenda .find { flex:1 1 120px; min-width:120px; max-width:220px; margin-left:auto; }
    header.top.agenda .find input { width:0; }
    header.top.agenda .ord { order:1; flex-basis:100%; }
  }
  .ag { position:relative; display:flex; height:100%; }
  /* The chart's own window. Its bars hide, as every page's do: a swipe,
     the wheel, or a drag moves it, and a pinch zooms it. Smaller than its
     window, the chart sits in its middle. */
  .sc { flex:1; min-width:0; display:flex; overflow:auto; overscroll-behavior:contain; cursor:grab; }
  .sc.drag { cursor:grabbing; user-select:none; -webkit-user-select:none; }
  .map { display:block; flex:none; margin:auto; }
  .map text { font-family:ui-monospace,SFMono-Regular,Menlo,monospace; }
  .line { fill:none; stroke-width:2; }
  /* A topic's rectangle, outlined in its topic's colour. */
  .root rect { fill:var(--raised); stroke-width:1.5; }
  .rn { fill:var(--text); font-size:14px; font-weight:600; }
  /* A phase's heading, above its chart, and the rule between two phases. */
  .ph { fill:var(--text); font-size:18px; font-weight:700; }
  .split { stroke:var(--line); stroke-width:1; }
  .node { cursor:pointer; }
  .hit { fill:transparent; }
  .name { fill:var(--text); font-size:13px; }
  .node:hover .name { text-decoration:underline; }
  .ring { fill:none; stroke:var(--text); stroke-width:1.5; }
  /* An item whose next step is mine: a small red dot at its top right,
     edged in the page's dark. */
  .mine { fill:var(--red); stroke:var(--bg); stroke-width:1.5; }
  /* A chip hides every item of the other orders, its name and its marks
     with it. Every line stays. */
  .node.off { display:none; }
  .note { position:relative; flex:none; width:360px; overflow-y:auto; padding:18px 22px;
    background:var(--panel); border-left:1px solid var(--line); }
  .note[hidden] { display:none; }
  /* Its close button, the shell's, at its top right. */
  .note .close { position:absolute; top:10px; right:10px; }
  .nh { display:flex; align-items:center; gap:10px; margin:0 40px 12px 0; }
  .nh h3 { margin:0; font-size:17px; line-height:1.3; }
  .badge { position:relative; flex:none; width:22px; height:22px; border:2px solid var(--line);
    border-radius:50%; overflow:hidden; }
  .nt { margin:0 0 16px; line-height:1.55; white-space:pre-wrap; overflow-wrap:anywhere; }
  /* Start, under the title: it opens a session on the item. */
  .note .st { margin:0 0 14px; }
  .note h4 { margin:0 0 5px; font-size:10px; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
    color:var(--dim); }
  .note ul { margin:0 0 14px; padding-left:16px; }
  .note li { margin:0 0 2px; }
  /* A list, where a note opens: an item a row, its title. It opens straight
     on its rows, its first lines clear of the close button. */
  .note ul.rows { padding:0; list-style:none; }
  .note > .close + .rows > li:first-child, .note > .close + h4, .note > .close + h4 + .rows > li:first-child,
  .note > .close + .nt { margin-right:40px; }
  .rows button { display:block; width:100%; padding:5px 8px; border:0; border-radius:4px; background:none;
    color:var(--text); font:inherit; text-align:left; cursor:pointer; }
  .rows button:hover { background:var(--raised); }
  /* An item in a list leads with a small dot in its colour. A note's
     lists of items drop their bullets for it. */
  .cd { display:inline-block; width:9px; height:9px; margin-right:8px; border-radius:50%; vertical-align:middle; }
  .note ul.items { padding:0; list-style:none; }
  .bad { position:absolute; left:8px; bottom:8px; z-index:1; margin:0; font-size:12px; color:var(--dim); }
  .bad[hidden] { display:none; }
  /* Narrow, the note covers the chart, its close button over it. */
  @media (max-width:699px) {
    .note { position:absolute; inset:0; z-index:2; width:auto; border-left:0; }
  }
  /* A touch screen, as my phone, and never a Mac, however narrow its pane.
     Every control takes a fingertip: 44 by 44 points, Apple's minimum. */
  @media (hover:none) and (pointer:coarse) {
    .note .st .btn { min-width:44px; height:44px; }
    header.top.agenda .acts button, header.top.agenda .ct, header.top.agenda .pills button { min-width:44px;
      height:44px; }
    .rows button { min-height:44px; }
  }
</style>
"""

# The order chips wear the launch page's pills. The page's own sizes come
# after.
PILLS = page.rules(page.tool("launch-page").CSS, ".pills")

BODY = ('<div class="ag" id="ag"><div class="sc" id="sc"></div>'
        '<aside class="note" id="note" hidden></aside><p class="bad" id="bad" hidden></p></div>')

# The chart, drawn and moved by the page.
SCRIPT = r"""<script>
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const BG = '#0f1115', DIM = '#8b91a3';
  // A topic's rectangle, its name wrapped past 15 letters.
  const RECT_W = 150, RECT_H = 46, RECT_WRAP = 15;
  const R1 = 10, R2 = 8, ARROW = 8, LANE = 10;
  // How many lines into one item meet before it, to go in as one.
  const JOIN = 3;
  // The room between two columns, where their lines bend: 56 at least, and
  // half as much again as the furthest any line there moves across, up to
  // 240, or 130 between rows when flipped. A long move then bends gently,
  // and a phone still shows several rows at once.
  const GAP = 56, BEND = 0.5, GAP_MAX = {h: 240, v: 130};
  // Room around the chart to move into, how far in from the window's edge
  // the rectangles sit when the chart opens, and the least margin a first
  // view, or Fit, keeps.
  const ROOM = 200, INSET = 56, EDGE = 8;
  // The furthest the chart zooms in: four times its natural size.
  const MOST = 4;
  // The search for fewer crossings: at most 80 fresh starts, and it stops
  // once 20 in a row find nothing better. The places then settle 30 times.
  const TRIES = 80, STALE = 20, SWEEPS = 12, ROUNDS = 30;
  // How much harder an item waiting on several holds the middle of them
  // than its neighbours hold their places: enough that a crowded column
  // makes way for it.
  const HOLD = 1000;
  // How hard one stretch of a single line holds straight.
  const CHAIN = 8;
  // How far a step stretches before its pull holds steady.
  const KNEE = 12;
  // How far a line passing through a column keeps from an item's edge or a
  // name, and flipped, how far a name keeps from the next item, so it reads
  // with its own.
  const CLEAR = 24, NEXT = 36;
  const WRAP = 24, CHAR = 7.8;
  // The Mine mark's radius, at the item's top right.
  const MARK = 3.5;
  // The least two rectangles stand apart, centre to centre: one under the
  // other, or flipped, side by side.
  const APART = {h: 64, v: 168};
  // A line from a rectangle to an item counts as this many crossings in the
  // search, so the items out of a rectangle stay beside it.
  const STRICT = 1000;
  const FLIP_V = '%FLIP_V%', FLIP_H = '%FLIP_H%', CLOSE = '%CLOSE%';
  // The order the search last found for each phase's chart, kept in this
  // browser with the shape it was found for: the rectangles, each item,
  // what it waits on, and its topics. The same shape, on this visit or a
  // later one, opens on it at once. A title or a note never changes the
  // order; new code on this page starts afresh.
  const KEEP = 'agenda-order', CODE = '%CODE%';
  // The room between one phase's chart and the next, its heading in it.
  const SPLIT = 150;

  let D = JSON.parse($('data').textContent);
  const mean = v => v.reduce((s, x) => s + x, 0) / v.length;
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');

  // ---- colour ----

  const rgbOf = c => { const n = parseInt(c.slice(1), 16); return [(n >> 16) & 255, (n >> 8) & 255, n & 255]; };
  const hexOf = rgb => '#' + rgb.map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
  // A mix is an even blend.
  const mix = cs => { const all = cs.map(rgbOf);
    return hexOf([0, 1, 2].map(i => all.reduce((s, c) => s + c[i], 0) / all.length)); };
  // A shade runs toward the page, 10% a column, never past half.
  const shade = (c, depth) => { const t = Math.min(0.1 * (depth - 1), 0.5), a = rgbOf(c), b = rgbOf(BG);
    return hexOf([0, 1, 2].map(i => a[i] + (b[i] - a[i]) * t)); };

  // ---- names ----

  // A name wraps past `wrap` letters, at a space.
  function linesOf(title, wrap = WRAP) {
    const lines = [];
    let line = '';
    for (const word of title.split(' ')) {
      if (line && (line + ' ' + word).length > wrap) { lines.push(line); line = word; }
      else line = line ? line + ' ' + word : word;
    }
    if (line) lines.push(line);
    return lines;
  }
  const widthOf = lines => Math.max(...lines.map(l => l.length)) * CHAR;

  // ---- the drawing ----

  // One phase's chart, `key` its phase: its columns, order and places. The
  // rectangles are column 0, in their topics' order, each phase its own.
  // No item's file name starts with #.
  function treeOf(items, topics, key) {
    const rectOf = name => '#' + key + '#' + name;
    const store = KEEP + (key ? '-' + key : '');
    let kept = null;
    try { kept = JSON.parse(localStorage.getItem(store)); } catch (e) {}
    const byId = new Map(items.map(it => [it.id, it]));
    const rects = topics.map(t => rectOf(t.name)), tint = new Map(topics.map(t => [t.name, t.colour]));

    // A loop is refused before it is ever written. The drawing still
    // guards: a link closing one is left out.
    const loops = new Set();
    {
      const state = new Map();
      const walk = it => {
        state.set(it.id, 'walking');
        for (const id of it.after || []) {
          const parent = byId.get(id);
          if (!parent) continue;
          const seen = state.get(id);
          if (seen === 'walking') loops.add(id + '>' + it.id);
          else if (!seen) walk(parent);
        }
        state.set(it.id, 'done');
      };
      for (const it of items) if (!state.has(it.id)) walk(it);
    }
    const parentsOf = it => (it.after || []).filter(id => !loops.has(id + '>' + it.id))
      .map(id => byId.get(id)).filter(Boolean);
    // Its topics with a rectangle.
    const topicsOf = it => (it.topics || []).filter(t => tint.has(t));

    // Its column: one past the furthest item it waits on.
    const depths = new Map();
    const depthOf = it => {
      const known = depths.get(it.id);
      if (known) return known;
      const depth = 1 + Math.max(0, ...parentsOf(it).map(depthOf));
      depths.set(it.id, depth);
      return depth;
    };
    const radiusOf = it => depthOf(it) === 1 ? R1 : R2;
    // The bright colour it comes from: the even mix of what it waits on,
    // or waiting on nothing, of its topics' colours.
    const bases = new Map();
    const baseOf = it => {
      let c = bases.get(it.id);
      if (!c) {
        const parents = parentsOf(it), own = topicsOf(it);
        c = parents.length ? mix(parents.map(baseOf)) : own.length ? mix(own.map(t => tint.get(t))) : DIM;
        bases.set(it.id, c);
      }
      return c;
    };
    const colourOf = it => shade(baseOf(it), depthOf(it));

    // Every line becomes a chain of steps one column long, a bend in each
    // column it skips. Every step runs outward, away from the rectangles.
    // An item waiting on nothing is linked to each of its topics' rectangles.
    const graphOf = () => {
      const spots = new Map();
      const add = (id, kind, item, layer) => spots.set(id, {id, kind, item, layer, lower: [], upper: []});
      for (const id of rects) add(id, 'rect', null, 0);
      for (const it of items) add(it.id, 'item', it, depthOf(it));
      const link = (a, b) => {
        const one = spots.get(a), two = spots.get(b);
        if (!one || !two) return;
        one.upper.push(b);
        two.lower.push(a);
      };
      const chains = [];
      for (const it of items) {
        const parents = parentsOf(it);
        const sources = parents.length ? parents.map(p => p.id) : topicsOf(it).map(rectOf);
        for (const source of sources) {
          const from = spots.get(source), to = spots.get(it.id);
          if (!from || !to) continue;
          const path = [source];
          let last = source;
          for (let layer = from.layer + 1; layer < to.layer; layer++) {
            const id = source + '>' + it.id + '@' + layer;
            add(id, 'bend', null, layer);
            link(last, id);
            path.push(id);
            last = id;
          }
          link(last, it.id);
          path.push(it.id);
          chains.push({key: source + '-' + it.id, from: from.kind === 'rect' ? null : from.item, to: it, path});
        }
      }
      return {spots, chains};
    };

    // Each column, first in the order a walk out from the rectangles meets
    // it. A try after the first walks its neighbours shuffled. The
    // rectangles' own column keeps their topics' order.
    const layersOf = (spots, shuffle) => {
      const layers = new Map(), met = new Set();
      const mixed = ids => {
        if (!shuffle) return ids;
        const out = [...ids];
        for (let i = out.length - 1; i > 0; i--) {
          const j = Math.floor(shuffle() * (i + 1));
          [out[i], out[j]] = [out[j], out[i]];
        }
        return out;
      };
      const walk = id => {
        const spot = spots.get(id);
        if (!spot || met.has(id)) return;
        met.add(id);
        layers.set(spot.layer, [...(layers.get(spot.layer) || []), id]);
        for (const near of mixed([...spot.upper, ...spot.lower])) walk(near);
      };
      rects.forEach(walk);
      spots.forEach((_, id) => walk(id));
      layers.set(0, [...rects]);
      return layers;
    };

    // The order within each column that crosses the fewest lines it can
    // find. Sweeps sort a column by where its neighbours sit. Sifting moves
    // each spot to the place in its column where it crosses fewest. Several
    // tries, each from a fresh walk, and the best order of all is kept. The
    // rectangles never move, and a crossing among the lines out of them
    // counts STRICT.
    //
    // The search runs on numbers: each spot is one, its lines lists of
    // them, and its place in its column a slot in one array. A line only
    // ever joins two neighbouring columns, so while one column is sifted,
    // every line it crosses keeps its far end still: what any two of its
    // spots cost each other is counted once, before the sifting starts.
    const orderOf = spots => {
      const names = [...spots.keys()], num = new Map(names.map((id, i) => [id, i]));
      const lower = names.map(id => spots.get(id).lower.map(x => num.get(x)));
      const upper = names.map(id => spots.get(id).upper.map(x => num.get(x)));
      const at = new Int32Array(names.length), wish = new Float64Array(names.length);
      const slot = new Int32Array(names.length);
      const copy = layers => new Map([...layers].map(([k, ids]) => [k, [...ids]]));
      let seed = 20261013;
      const shuffle = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
      const first = layersOf(spots);
      let best = null, fewest = Infinity, since = 0;
      for (let attempt = 0; attempt < TRIES && fewest > 0 && since < STALE; attempt++) {
        const was = fewest;
        const walked = attempt === 0 ? first : layersOf(spots, shuffle);
        const layers = new Map([...walked].map(([k, ids]) => [k, ids.map(id => num.get(id))]));
        const keys = [...layers.keys()].sort((a, b) => a - b);
        const reindex = ids => { for (let i = 0; i < ids.length; i++) at[ids[i]] = i; };
        layers.forEach(reindex);
        // The lines between a column and the next that cross: two lines
        // cross when their two ends sit in opposite orders.
        const crossingsAt = k => {
          const from = [], to = [];
          for (const id of layers.get(k)) for (const up of upper[id]) { from.push(at[id]); to.push(at[up]); }
          let count = 0;
          for (let i = 0; i < from.length; i++) {
            for (let j = i + 1; j < from.length; j++) if ((from[i] - from[j]) * (to[i] - to[j]) < 0) count += 1;
          }
          return count * (k === 0 ? STRICT : 1);
        };
        const crossings = () => keys.reduce((s, k) => s + crossingsAt(k), 0);
        const sweep = outward => {
          const run = outward ? keys.slice(1) : keys.slice(1, -1).reverse();
          for (const k of run) {
            const ids = layers.get(k);
            for (const id of ids) {
              const near = outward ? lower[id] : upper[id];
              if (!near.length) { wish[id] = at[id]; continue; }
              let sum = 0;
              for (const n of near) sum += at[n];
              wish[id] = sum / near.length;
            }
            ids.sort((a, b) => wish[a] - wish[b]);
            reindex(ids);
          }
        };
        // Each spot of a column is known by where it sat when its sifting
        // began, its slot. Placed first, a spot crosses total[slot] of the
        // others' lines. Moved past another, its crossings change by
        // diff[slot * m + the other's slot].
        const sift = () => {
          for (const k of keys) {
            const start = layers.get(k), m = start.length;
            if (k === 0 || m < 2) continue;
            start.forEach((id, i) => { slot[id] = i; });
            // Where each spot's lines end, the lines in, then the lines out,
            // and what a crossing among each costs.
            const from = [], ends = [], cost = [k === 1 ? STRICT : 1, 1];
            for (const near of [lower, upper]) {
              const f = new Int32Array(m + 1);
              for (let i = 0; i < m; i++) f[i + 1] = f[i] + near[start[i]].length;
              const e = new Int32Array(f[m]);
              for (let i = 0; i < m; i++) near[start[i]].forEach((n, x) => { e[f[i] + x] = at[n]; });
              from.push(f);
              ends.push(e);
            }
            const diff = new Int32Array(m * m), total = new Int32Array(m);
            for (let i = 0; i < m; i++) {
              for (let j = i + 1; j < m; j++) {
                let ij = 0, ji = 0;
                for (let s = 0; s < 2; s++) {
                  const f = from[s], e = ends[s];
                  for (let a = f[i]; a < f[i + 1]; a++) {
                    for (let b = f[j]; b < f[j + 1]; b++) {
                      if (e[a] > e[b]) ij += cost[s];
                      else if (e[a] < e[b]) ji += cost[s];
                    }
                  }
                }
                diff[i * m + j] = ji - ij;
                diff[j * m + i] = ij - ji;
                total[i] += ij;
                total[j] += ji;
              }
            }
            const col = start.slice(), slots = Int32Array.from(start, (_, i) => i);
            for (const u of start) {
              const su = slot[u], row = su * m;
              let count = total[su], place = 0, least = count, p = 0;
              for (let q = 0; q < m; q++) {
                const sv = slots[q];
                if (sv === su) continue;
                count += diff[row + sv];
                p += 1;
                if (count < least) { least = count; place = p; }
              }
              const was = at[u];
              col.splice(was, 1);
              col.splice(place, 0, u);
              slots.copyWithin(was, was + 1);
              slots.copyWithin(place + 1, place, m - 1);
              slots[place] = su;
              reindex(col);
            }
            layers.set(k, col);
          }
        };
        for (let round = 0; round < SWEEPS; round++) {
          sweep(round % 2 === 0);
          sift();
          const count = crossings();
          if (count < fewest) { fewest = count; best = copy(layers); }
          if (fewest === 0) break;
        }
        since = fewest < was ? 0 : since + 1;
      }
      const named = best || new Map([...first].map(([k, ids]) => [k, ids.map(id => num.get(id))]));
      return {layers: new Map([...named].map(([k, ids]) => [k, ids.map(i => names[i])]))};
    };

    // How many lines cross in an order, each crossing once, kept on the
    // drawing for its tests.
    const crossingsOf = (spots, layers) => {
      const index = new Map();
      layers.forEach(ids => ids.forEach((id, i) => index.set(id, i)));
      let count = 0;
      layers.forEach(ids => {
        const from = [], to = [];
        for (const id of ids) for (const up of spots.get(id).upper) { from.push(index.get(id)); to.push(index.get(up)); }
        for (let i = 0; i < from.length; i++) {
          for (let j = i + 1; j < from.length; j++) if ((from[i] - from[j]) * (to[i] - to[j]) < 0) count += 1;
        }
      });
      return count;
    };

    // The search's order, or the one kept for this very shape.
    const orderKept = spots => {
      const shape = CODE + '|' + rects.join('|') + '|' + items.map(it => it.id + '<' + (it.after || []).join('<')
        + '>' + topicsOf(it).join('>')).join('|');
      if (kept && kept.shape === shape) {
        const layers = new Map(kept.layers.map(([k, ids]) => [k, [...ids]]));
        return {layers, crossings: crossingsOf(spots, layers)};
      }
      const found = orderOf(spots);
      kept = {shape, layers: [...found.layers].map(([k, ids]) => [k, [...ids]])};
      try { localStorage.setItem(store, JSON.stringify(kept)); } catch (e) {}
      return {layers: found.layers, crossings: crossingsOf(spots, found.layers)};
    };

    // Each spot's place across its column, the order fixed. Every line pulls
    // its two ends level, one stretch of a single line hardest, so a run of
    // single items, or a long line, runs straight. Column by column, each
    // spot moves to where its lines pull it, both ways: an item sits amid what
    // it waits on and what waits on it. Neighbours that crowd each other
    // pool into the least squared distance. An item waiting on several, or
    // under several topics, holds the middle of them.
    const placesOf = (spots, layers, way) => {
      const spot = id => spots.get(id);
      const at = new Map();
      // How far apart two spots sit along their column, a before b, centre
      // to centre. Two rectangles stand APART. Horizontal, a name sits under
      // its item; vertical, beside it, nearer its own item than the next. A
      // line passing through a column, at a bend, keeps CLEAR of the names
      // and items beside it, and vertical, as far from the next item as a name
      // keeps.
      const apart = (a, b) => {
        if (spot(a).kind === 'rect') return APART[way];
        const one = spot(a).item, two = spot(b).item;
        if (!one && !two) return 14;
        // From a's centre to the far end of its name.
        const end = !one ? 0 : way === 'h' ? radiusOf(one) + 4 + 16 * linesOf(one.title).length
                                          : radiusOf(one) + 8 + widthOf(linesOf(one.title));
        if (!two) return end + CLEAR;
        if (!one) return (way === 'h' ? CLEAR : NEXT) + radiusOf(two);
        return end + (way === 'h' ? 18 : NEXT) + radiusOf(two);
      };
      // Each spot pulls toward a place with a weight: how hard it holds that
      // place against its crowd. Its bounds, when it has any, are where it
      // must end: the column keeps them whenever its room allows every one at
      // once.
      const place = (ids, pulls, bounds) => {
        const offsets = [];
        ids.forEach((id, i) => offsets.push(i === 0 ? 0 : offsets[i - 1] + apart(ids[i - 1], id)));
        const pools = [];
        ids.forEach((id, i) => {
          const [w, x] = pulls(id);
          pools.push({sum: w * (x - offsets[i]), count: w, start: i, n: 1});
          while (pools.length > 1) {
            const last = pools[pools.length - 1], before = pools[pools.length - 2];
            if (before.sum / before.count <= last.sum / last.count) break;
            before.sum += last.sum;
            before.count += last.count;
            before.n += last.n;
            pools.pop();
          }
        });
        const z = [];
        for (const pool of pools) {
          for (let i = pool.start; i < pool.start + pool.n; i++) z[i] = pool.sum / pool.count;
        }
        if (bounds) {
          const lo = ids.map((id, i) => { const b = bounds(id); return b ? b[0] - offsets[i] : -Infinity; });
          const hi = ids.map((id, i) => { const b = bounds(id); return b ? b[1] - offsets[i] : Infinity; });
          for (let i = 1; i < lo.length; i++) lo[i] = Math.max(lo[i], lo[i - 1]);
          for (let i = hi.length - 2; i >= 0; i--) hi[i] = Math.min(hi[i], hi[i + 1]);
          if (lo.every((l, i) => l <= hi[i] + 0.001)) {
            for (let i = 0; i < z.length; i++) z[i] = Math.min(Math.max(z[i], lo[i]), hi[i]);
          }
        }
        ids.forEach((id, i) => at.set(id, z[i] + offsets[i]));
      };
      // How hard a line's step pulls its ends level, as Gansner's layered
      // drawing has it: from a bend 2, else 1. A step whose two ends link
      // to nothing else on the sides they face is one stretch of a single
      // line, as between two bends of a long line, or from an item to the
      // one item waiting on it alone: CHAIN, so it holds straight.
      const bend = id => spot(id).kind === 'bend';
      const single = (a, b) => {
        const [lo, up] = spot(a).layer < spot(b).layer ? [a, b] : [b, a];
        return spot(lo).upper.length === 1 && spot(up).lower.length === 1;
      };
      const pullOf = (a, b) => single(a, b) ? CHAIN : bend(a) || bend(b) ? 2 : 1;
      const x = id => at.get(id) || 0;
      // An item waiting on several holds the middle of them. What pulls on
      // it, its own lines and what waits on it, pulls on them instead,
      // shared: every pull then has its equal pull back, so nothing drags
      // the whole chart one way while it settles.
      const several = id => !!spot(id).item && spot(id).lower.length > 1;
      const middle = id => mean(spot(id).lower.map(x));
      // A pull grows with its stretch only up to KNEE, then holds steady:
      // a stretch the room forces gathers into one step, the weakest, and
      // the rest of its line runs straight.
      const ease = d => KNEE / Math.max(KNEE, Math.abs(d));
      const pulls = id => {
        if (several(id)) return [HOLD, middle(id)];
        const me = x(id);
        let w = 0, t = 0;
        const add = (weight, to) => { w += weight; t += weight * to; };
        for (const n of spot(id).lower) add(pullOf(id, n) * ease(x(n) - me), x(n));
        for (const n of spot(id).upper) {
          if (!several(n)) { add(pullOf(id, n) * ease(x(n) - me), x(n)); continue; }
          const ps = spot(n).lower, k = ps.length, m = middle(n), xn = x(n);
          // Its lines, each pulling its ends level, pull what it waits on
          // toward each other.
          let slope = 0, curve = 0;
          for (const l of ps) {
            const o = pullOf(l, n) * ease(x(l) - xn);
            if (l === id) { slope += o * (x(l) - m) * (1 - 1 / k); curve += o * (1 - 1 / k) ** 2; }
            else { slope -= o * (x(l) - m) / k; curve += o / (k * k); }
          }
          if (curve > 0) add(curve, me - slope / curve);
          // What waits on it pulls the middle it holds.
          for (const c of spot(n).upper) add(pullOf(n, c) * ease(x(c) - xn) / (k * k), me + k * (x(c) - m));
        }
        return w ? [w, t / w] : [1, me];
      };
      // The span between the items one waits on, when it waits on several.
      const between = id => {
        const near = spot(id).lower;
        if (near.length < 2) return null;
        const ats = near.map(x);
        return [Math.min(...ats), Math.max(...ats)];
      };
      // The rectangles never move: they stand APART from each other, whatever
      // their items. The items settle around them ROUNDS times, each round
      // ending walking outward, so an item is placed once what it waits on has
      // its place. Moved, the rectangles and their items drag each other on,
      // and the column splits wherever a rectangle has no item.
      const deepest = Math.max(...layers.keys());
      layers.forEach(ids => place(ids, () => [1, 0]));
      for (let round = 0; round < ROUNDS; round++) {
        for (let k = deepest - 1; k >= 1; k--) place(layers.get(k) || [], pulls, between);
        for (let k = 1; k <= deepest; k++) place(layers.get(k) || [], pulls, between);
      }
      return at;
    };

    // The order serves both ways; only the places differ.
    let graph = null, order = null;
    const laid = new Map();
    const laidOut = way => {
      if (laid.has(way)) return laid.get(way);
      if (!graph) { graph = graphOf(); order = orderKept(graph.spots); }
      const {spots, chains} = graph, layers = order.layers;
      const across = placesOf(spots, layers, way);
      // How far a spot, its rectangle, or its item and its name, reaches
      // along the way the chart grows, each side of its column's line, an
      // arrow's room included. Horizontal, a name sits under its item,
      // centred. Vertical, beside it.
      const reach = id => {
        const s = spots.get(id);
        if (s.kind === 'rect') return way === 'h' ? RECT_W / 2 : RECT_H / 2;
        if (!s.item) return 0;
        const r = radiusOf(s.item), lines = linesOf(s.item.title);
        return Math.max(r + ARROW + 4, way === 'h' ? widthOf(lines) / 2 + 4 : 8 * lines.length + 6);
      };
      // Each column's line, far enough past the last that every line between
      // them bends clear of both columns' names.
      const keys = [...layers.keys()].sort((a, b) => a - b);
      const edge = new Map(keys.map(k => [k, Math.max(0, ...layers.get(k).map(reach))]));
      const jump = new Map();
      spots.forEach((s, id) => s.upper.forEach(up => jump.set(s.layer,
        Math.max(jump.get(s.layer) || 0, Math.abs((across.get(up) || 0) - (across.get(id) || 0))))));
      const lineOf = new Map();
      keys.forEach((k, i) => {
        const was = keys[i - 1];
        lineOf.set(k, i === 0 ? 0 : lineOf.get(was) + edge.get(was)
          + Math.min(GAP + BEND * (jump.get(was) || 0), GAP_MAX[way]) + edge.get(k));
      });
      const points = new Map();
      spots.forEach((s, id) => {
        const a = across.get(id) || 0, l = lineOf.get(s.layer);
        points.set(id, way === 'h' ? {x: l, y: a} : {x: a, y: l});
      });
      // The drawing's bounds, its rectangles, items and names, and the span
      // across the chart of the rectangles and the items out of them.
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity, lo = Infinity, hi = -Infinity;
      points.forEach((p, id) => {
        const s = spots.get(id);
        let e;
        if (s.kind === 'rect') e = [p.x - RECT_W / 2, p.y - RECT_H / 2, p.x + RECT_W / 2, p.y + RECT_H / 2];
        else if (s.item) {
          const r = radiusOf(s.item), lines = linesOf(s.item.title), w = widthOf(lines);
          e = way === 'h'
            ? [p.x - Math.max(r, w / 2), p.y - r, p.x + Math.max(r, w / 2), p.y + r + 8 + lines.length * 16]
            : [p.x - r, p.y - Math.max(12, lines.length * 8), p.x + r + 8 + w, p.y + Math.max(12, lines.length * 8)];
        } else return;
        x0 = Math.min(x0, e[0]); y0 = Math.min(y0, e[1]); x1 = Math.max(x1, e[2]); y1 = Math.max(y1, e[3]);
        if (s.layer <= 1) { lo = Math.min(lo, way === 'h' ? e[1] : e[0]); hi = Math.max(hi, way === 'h' ? e[3] : e[2]); }
      });
      const canvas = {w: x1 - x0 + 2 * ROOM, h: y1 - y0 + 2 * ROOM, ox: ROOM - x0, oy: ROOM - y0};
      points.forEach((p, id) => points.set(id, {x: p.x + canvas.ox, y: p.y + canvas.oy}));
      // For the first view: the rectangles' near edge along the chart, the
      // next column's line and how far its names reach each side of it, and
      // the rectangles' and their items' span across.
      {
        const o = way === 'h' ? canvas.ox : canvas.oy, a = way === 'h' ? canvas.oy : canvas.ox;
        const next = keys[1] === undefined ? keys[0] : keys[1];
        canvas.first = {near: o - reach(rects[0]), line: o + lineOf.get(next), reach: edge.get(next),
                        lo: a + lo, hi: a + hi};
      }

      // Lines into one item arrive side by side, in the order of where they
      // come from: the one from higher up, or further left, arrives higher,
      // or further left, every one onto the item itself. Three or more leave
      // no room on an item for their arrows: they meet where its column
      // begins and go in as one line. Lines leaving a rectangle leave side
      // by side the same way, along its edge.
      const acrossOf = id => { const p = points.get(id) || {x: 0, y: 0}; return way === 'h' ? p.y : p.x; };
      const side = (list, key, near, room) => {
        const step = list.length > 1 ? Math.min(LANE, room / (list.length - 1)) : LANE;
        [...list].sort((a, b) => acrossOf(near(a)) - acrossOf(near(b)))
          .forEach((w, i) => { w.lanes[key] = {at: (i - (list.length - 1) / 2) * step, step}; });
      };
      const work = chains.map(c => ({c, lanes: {}}));
      const into = new Map();
      for (const w of work) into.set(w.c.to.id, [...(into.get(w.c.to.id) || []), w]);
      into.forEach((list, id) => {
        if (list.length < JOIN) side(list, 'end', w => w.c.path[w.c.path.length - 2], 2 * (radiusOf(byId.get(id)) - 1));
        else list.forEach(w => { w.joined = true; });
      });
      const leaving = new Map();
      for (const w of work) if (w.c.from === null) leaving.set(w.c.path[0], [...(leaving.get(w.c.path[0]) || []), w]);
      leaving.forEach(list => side(list, 'start', w => w.c.path[1], way === 'h' ? RECT_H - 16 : RECT_W - 24));
      // Each line, as where it starts and ends along the chart, and between
      // which two places each of its bends runs: past one column's names,
      // short of the next one's.
      const alongOf = id => { const p = points.get(id) || {x: 0, y: 0}; return way === 'h' ? p.x : p.y; };
      const o = way === 'h' ? canvas.ox : canvas.oy;
      const drawn = work.map(({c, lanes, joined}) => {
        const lane = lanes.end ? lanes.end.at : 0, r = radiusOf(c.to);
        const steps = c.path.slice(1).map((id, i) => {
          const from = spots.get(c.path[i]).layer, to = spots.get(id).layer;
          return {a: o + lineOf.get(from) + edge.get(from), b: o + lineOf.get(to) - edge.get(to)};
        });
        return {key: c.key, from: c.from, to: c.to, lane, steps, joined: !!joined,
          points: c.path.map(id => points.get(id) || {x: 0, y: 0}),
          start: c.from ? alongOf(c.from.id) + radiusOf(c.from) + 2 : alongOf(c.path[0]) + reach(c.path[0]),
          shift: lanes.start ? lanes.start.at : 0,
          tip: alongOf(c.to.id) - Math.sqrt(Math.max(r * r - lane * lane, 0)) - 1,
          head: lanes.end ? Math.min(4, Math.max(2.5, lanes.end.step / 2 - 0.5)) : 4};
      });
      const out = {points, chains: drawn, canvas, crossings: order.crossings};
      laid.set(way, out);
      return out;
    };

    const orders = Math.max(0, ...items.map(depthOf));
    return {items, byId, rects, rectOf, parentsOf, depthOf, radiusOf, colourOf, laidOut, orders};
  }

  // The whole agenda: one chart per phase, in the phases' order, each under
  // its heading, the next below it. A phase the project gives no heading
  // reads "Phase" and its name. An item in no phase, or in one the
  // project does not name, falls in a last chart of its own. With no phases,
  // one chart, and no heading. It answers as one chart does, its places
  // measured on the whole drawing.
  function boardOf(items, topics, phases, headings) {
    const sections = phases.length
      ? [...phases.map(p => ({key: p, name: headings[p] || 'Phase ' + p, items: items.filter(it => it.phase === p)})),
         {key: '?', name: 'No phase', items: items.filter(it => !phases.includes(it.phase))}]
        .filter((s, i) => i < phases.length || s.items.length)
      : [{key: '', name: '', items}];
    const trees = sections.map(s => ({...s, tree: treeOf(s.items, topics, s.key)}));
    const of = new Map(), byId = new Map();
    for (const {tree} of trees) for (const it of tree.items) { of.set(it.id, tree); byId.set(it.id, it); }
    const each = name => it => of.get(it.id)[name](it);
    // Each chart drawn at its own place down the whole: the first at the
    // top, each next one SPLIT below the last one's drawing.
    const laid = new Map();
    const laidOut = way => {
      if (laid.has(way)) return laid.get(way);
      const parts = trees.map(s => ({name: s.name, tree: s.tree, L: s.tree.laidOut(way), dy: 0}));
      parts.forEach((p, i) => { if (i) p.dy = parts[i - 1].dy + parts[i - 1].L.canvas.h - 2 * ROOM + SPLIT; });
      const last = parts[parts.length - 1], points = new Map();
      for (const p of parts) p.L.points.forEach((at, id) => points.set(id, {x: at.x, y: at.y + p.dy}));
      const out = {parts, points, crossings: parts.reduce((s, p) => s + p.L.crossings, 0),
                   canvas: {w: Math.max(...parts.map(p => p.L.canvas.w)), h: last.dy + last.L.canvas.h,
                            first: parts[0].L.canvas.first}};
      laid.set(way, out);
      return out;
    };
    return {items: trees.flatMap(s => s.tree.items), byId, rects: trees[0].tree.rects,
            parentsOf: each('parentsOf'), depthOf: each('depthOf'), radiusOf: each('radiusOf'),
            colourOf: each('colourOf'), laidOut, orders: Math.max(0, ...trees.map(s => s.tree.orders))};
  }

  const fix = v => Math.round(v * 100) / 100;

  // A line, as straight runs and bends. It leaves its item, or a
  // rectangle's edge, straight along the chart, and runs straight past
  // each column's names. It bends only between two columns, and every bend
  // there takes one shape: two lines then cross only where their order
  // says so, and never at an item they share. It ends on its item, its arrow
  // last. A line from a rectangle carries no arrow. A line that meets
  // others before its item ends where they meet; their one line in is its
  // stem.
  function pathOf(way, chain, stem) {
    const h = way === 'h', pts = chain.points, n = pts.length;
    const across = p => h ? p.y : p.x;
    const at = (a, x) => h ? `${fix(a)} ${fix(x)}` : `${fix(x)} ${fix(a)}`;
    const arrow = chain.from !== null;
    let x = across(pts[0]) + chain.shift, d = `M ${at(chain.start, x)}`;
    if (stem) { x = across(pts[n - 1]); d = `M ${at(chain.steps[n - 2].b, x)}`; }
    else {
      for (let i = 1; i < n; i++) {
        const {a, b} = chain.steps[i - 1], m = (a + b) / 2;
        const next = across(pts[i]) + (i === n - 1 ? chain.lane : 0);
        d += ` L ${at(a, x)} C ${at(m, x)}, ${at(m, next)}, ${at(b, next)}`;
        x = next;
      }
      if (chain.joined) return {d, head: null};
    }
    const end = arrow ? chain.tip - ARROW : chain.tip;
    d += ` L ${at(end, x)}`;
    if (!arrow) return {d, head: null};
    const w = chain.head;
    return {d, head: `${at(chain.tip, x)} ${at(end, x - w)} ${at(end, x + w)}`};
  }

  // ---- the page ----

  const sc = $('sc'), note = $('note'), flip = $('flip'), q = $('q');
  const counted = document.querySelector('header.top .mid');
  // The open item, ringed, with its note at the right; or a list there
  // instead: a count's, or the search's hits. One shows at a time. The
  // chip pressed: 'all', or one order.
  let tree = null, open = null, list = null, way = null, chip = 'all';
  // The chart's size, 1 its natural size. It opens at 1.
  let scale = 1;
  // It flows left to right at every width, until I flip it: each device
  // keeps the way I last flipped it to.
  try { way = localStorage.getItem('agenda-way'); } catch (e) {}
  if (way !== 'h' && way !== 'v') way = 'h';

  function build() {
    const items = (D.items || []).slice().sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0);
    tree = boardOf(items, D.topics || [], D.phases || [], D.headings || {});
    const bad = $('bad'), broken = D.broken || [];
    bad.hidden = !broken.length;
    bad.textContent = broken.length ? 'Could not read: ' + broken.join(', ') : '';
    counts();
  }

  // ---- the counts, the chips and the lists ----

  const byTitle = (a, b) => a.title.localeCompare(b.title, undefined, {sensitivity: 'base'});
  // The items a count's list holds, by title.
  function listed(kind) {
    return (kind === 'mine' ? tree.items.filter(it => it.mine) : tree.items).slice().sort(byTitle);
  }
  // The search's hits: the items whose title holds what I typed, then those
  // whose note alone holds it.
  function hits() {
    const words = q.value.trim().toLowerCase(), has = s => (s || '').toLowerCase().includes(words);
    return [tree.items.filter(it => has(it.title)).sort(byTitle),
            tree.items.filter(it => !has(it.title) && has(it.note)).sort(byTitle)];
  }
  // Whether an item shows under the chip pressed.
  const shown = it => chip === 'all' || tree.depthOf(it) === chip;

  // The rail's middle: every item and Mine, each a button opening its list,
  // one group, so they share one width. Then the orders, and their chips,
  // another group, in the launch page's pills. The counts read the whole
  // agenda, whatever the chip.
  const COUNTS = [['items', 'item'], ['mine', 'mine']];
  function counts() {
    const n = {items: tree.items.length, mine: tree.items.filter(it => it.mine).length}, all = tree.orders;
    if (chip !== 'all' && chip > all) chip = 'all';
    const chips = ['all', ...Array.from({length: all}, (_, i) => i + 1)];
    counted.innerHTML = '<span class="cts"><span class="group">' + COUNTS.map(([k, one]) => `<button type="button"`
      + ` class="ct${list === k ? ' on' : ''}" data-list="${k}">${k === 'mine' ? '<i class="mk"></i>' : ''}`
      + `<b${k === 'mine' ? ' class="rd"' : ''}>${n[k]}</b> ${n[k] === 1 ? one : k}</button>`).join('') + '</span></span>'
      + `<span class="ord"><span class="ct"><b>${all}</b> ${all === 1 ? 'order' : 'orders'}</span>`
      + '<span class="sl"><span class="pills"><span class="group">' + chips.map(c => `<button type="button"`
      + ` class="${chip === c ? 'on' : ''}" data-chip="${c}" aria-pressed="${chip === c}">`
      + `${c === 'all' ? 'All' : c}</button>`).join('') + '</span></span></span></span>';
  }

  // A chip pressed shows its order's items alone. Nothing else moves.
  function press(c) {
    chip = c;
    counts();
    sc.querySelectorAll('.node').forEach(g => g.classList.toggle('off', !shown(tree.byId.get(g.dataset.id))));
  }

  // An item named in a list wears its colour.
  const dotOf = it => `<i class="cd" style="background:${tree.colourOf(it)}"></i>`;
  const rows = its => '<ul class="rows">' + its.map(it => `<li><button type="button" data-id="${esc(it.id)}">`
    + `${dotOf(it)}${esc(it.title)}</button></li>`).join('') + '</ul>';
  // A list opens straight on its rows, with no head: the count I pressed,
  // or the words I typed, name it.
  function listOf() {
    const x = `<button type="button" class="close" id="nx" aria-label="Close">${CLOSE}</button>`;
    if (list !== 'hits') {
      const its = listed(list);
      return x + (its.length ? rows(its) : '<p class="nt">No item waits on you.</p>');
    }
    const [inTitle, inNote] = hits();
    if (!inTitle.length && !inNote.length) return x + '<p class="nt">No title or note holds it.</p>';
    return x + (inTitle.length ? '<h4>In the title</h4>' + rows(inTitle) : '')
      + (inNote.length ? '<h4>In the note</h4>' + rows(inNote) : '');
  }

  // The whole drawing: each phase's chart at its place, under its heading,
  // a rule above every heading but the first.
  function svgOf() {
    const B = tree.laidOut(way), {canvas} = B;
    let s = `<svg class="map" width="${canvas.w * scale}" height="${canvas.h * scale}"`
      + ` viewBox="0 0 ${canvas.w} ${canvas.h}"`
      + ` data-crossings="${B.crossings}" data-way="${way}">`;
    B.parts.forEach((p, i) => {
      s += `<g data-section="${i}" transform="translate(0 ${fix(p.dy)})">`;
      if (p.name) {
        if (i) s += `<line class="split" x1="${ROOM}" x2="${fix(canvas.w - ROOM)}" y1="${ROOM - 90}" y2="${ROOM - 90}"/>`;
        s += `<text class="ph" x="${ROOM}" y="${ROOM - 30}">${esc(p.name)}</text>`;
      }
      s += chartOf(p.tree, p.L) + '</g>';
    });
    return s + '</svg>';
  }

  // One phase's chart, as its own drawing places it.
  function chartOf(chart, L) {
    const {points} = L;
    let s = '';
    const stems = new Map();
    for (const c of L.chains) {
      const colour = chart.colourOf(c.from || c.to), p = pathOf(way, c);
      s += `<g data-key="${esc(c.key)}" data-to="${esc(c.to.id)}"><path d="${p.d}" class="line" style="stroke:${colour}"/>`
        + (p.head ? `<polygon points="${p.head}" style="fill:${colour}"/>` : '') + '</g>';
      if (c.joined) stems.set(c.to.id, c);
    }
    // The one line in, where lines meet before their item, in the item's
    // colour. Lines in from rectangles carry no arrow, so neither does
    // their stem.
    stems.forEach(c => {
      const colour = chart.colourOf(c.to), p = pathOf(way, c, true);
      s += `<g data-stem="${esc(c.to.id)}"><path d="${p.d}" class="line" style="stroke:${colour}"/>`
        + (p.head ? `<polygon points="${p.head}" style="fill:${colour}"/>` : '') + '</g>';
    });
    // The rectangles, each outlined in its topic's colour, its name
    // centred on one line or two.
    for (const t of D.topics || []) {
      const p = points.get(chart.rectOf(t.name)), lines = linesOf(t.name, RECT_WRAP);
      s += `<g class="root" data-topic="${esc(t.name)}"><rect x="${fix(p.x - RECT_W / 2)}" y="${fix(p.y - RECT_H / 2)}"`
        + ` width="${RECT_W}" height="${RECT_H}" rx="6" style="stroke:${t.colour}"/><text class="rn" text-anchor="middle">`
        + lines.map((l, i) => `<tspan x="${fix(p.x)}" y="${fix(p.y + 5 - (lines.length - 1) * 8 + i * 16)}">${esc(l)}</tspan>`)
          .join('') + '</text></g>';
    }
    for (const it of chart.items) {
      const p = points.get(it.id);
      if (!p) continue;
      const r = chart.radiusOf(it), lines = linesOf(it.title), w = widthOf(lines);
      const tall = Math.max(22, lines.length * 8 + 6);
      const hit = way === 'h'
        ? {x: p.x - Math.max(w / 2, 22), y: p.y - 22, w: Math.max(w, 44), h: 22 + r + 12 + lines.length * 16}
        : {x: p.x - 22, y: p.y - tall, w: 22 + r + 8 + w, h: 2 * tall};
      const colour = chart.colourOf(it);
      s += `<g class="node${shown(it) ? '' : ' off'}" data-id="${esc(it.id)}" data-depth="${chart.depthOf(it)}"`
        + ` data-colour="${colour}"` + (it.mine ? ' data-mine=""' : '') + '>'
        + `<rect class="hit" x="${hit.x}" y="${hit.y}" width="${hit.w}" height="${hit.h}"/>`
        + (open === it.id ? `<circle cx="${p.x}" cy="${p.y}" r="${r + 5}" class="ring"/>` : '')
        + `<circle cx="${p.x}" cy="${p.y}" r="${r}" style="fill:${colour}"/>`
        + (it.mine ? `<circle cx="${fix(p.x + r * Math.SQRT1_2)}" cy="${fix(p.y - r * Math.SQRT1_2)}" r="${MARK}"`
          + ' class="mine"/>' : '');
      const tx = way === 'h' ? p.x : p.x + r + 8;
      s += way === 'h'
        ? `<text x="${tx}" y="${p.y + r + 17}" class="name" text-anchor="middle">`
        : `<text x="${tx}" y="${p.y + 4.5 - (lines.length - 1) * 8}" class="name">`;
      s += lines.map((l, i) => `<tspan x="${tx}" dy="${i ? 16 : 0}">${esc(l)}</tspan>`).join('') + '</text></g>';
    }
    return s;
  }

  function paint() {
    flip.innerHTML = way === 'h' ? FLIP_V : FLIP_H;
    sc.innerHTML = svgOf();
    held = null;
    tools();
  }

  // ---- the chart's size ----

  // How many of the screen's pixels one of the window's own takes: 1100's
  // zoom of the whole page, which the chart's size never touches.
  const ratio = () => sc.getBoundingClientRect().width / sc.offsetWidth || 1;
  // Where the chart's top left corner sits in its window, in the window's
  // own pixels.
  function corner() {
    const svg = sc.querySelector('svg');
    if (!svg) return {x: 0, y: 0};
    const r = sc.getBoundingClientRect(), b = svg.getBoundingClientRect(), k = ratio();
    return {x: (b.left - r.left) / k, y: (b.top - r.top) / k};
  }
  // Moves the chart so its point (x, y), as the drawing counts it, sits at
  // (X, Y) in the window.
  function place(x, y, X, Y) {
    const at = corner();
    sc.scrollLeft += at.x + x * scale - X;
    sc.scrollTop += at.y + y * scale - Y;
  }
  function resize(s) {
    const svg = sc.querySelector('svg'), c = tree.laidOut(way).canvas;
    scale = s;
    svg.setAttribute('width', c.w * s);
    svg.setAttribute('height', c.h * s);
  }
  // Size s, holding still the point `at`, from the window's top left as the
  // screen measures it, or the window's middle. A pinch holds the point it
  // began on, while it goes on in one place and nothing pans: a chart still
  // too small to move stays in the middle, then brings that point back.
  let held = null;
  function zoomTo(s, at) {
    const k = ratio(), X = at ? at.x / k : sc.clientWidth / 2, Y = at ? at.y / k : sc.clientHeight / 2;
    const now = performance.now();
    if (!held || now - held.t > 400 || Math.abs(held.X - X) > 4 || Math.abs(held.Y - Y) > 4
        || held.left !== sc.scrollLeft || held.top !== sc.scrollTop) {
      const c = corner();
      held = {X, Y, x: (X - c.x) / scale, y: (Y - c.y) / scale};
    }
    resize(s);
    place(held.x, held.y, X, Y);
    Object.assign(held, {t: now, left: sc.scrollLeft, top: sc.scrollTop});
  }
  // Fitted, the whole drawing shows in the middle of the window, never
  // past its natural size.
  function fitScale() {
    const c = tree.laidOut(way).canvas;
    return Math.max(0.01, Math.min(1, (sc.clientWidth - 2 * EDGE) / (c.w - 2 * ROOM),
                                   (sc.clientHeight - 2 * EDGE) / (c.h - 2 * ROOM)));
  }
  function fit() {
    const c = tree.laidOut(way).canvas;
    resize(fitScale());
    place(c.w / 2, c.h / 2, sc.clientWidth / 2, sc.clientHeight / 2);
  }
  function fitted() {
    if (!tree || Math.abs(scale - fitScale()) > 1e-9) return false;
    const c = tree.laidOut(way).canvas, at = corner();
    return Math.abs(at.x + c.w * scale / 2 - sc.clientWidth / 2) < 1.5
      && Math.abs(at.y + c.h * scale / 2 - sc.clientHeight / 2) < 1.5;
  }
  // The rail's zoom tools, page.py's, as every chart wears them.
  const tools = zoomer(document.querySelector('header.top .zt'), sc, {
    scale: () => tree ? scale : 0, bounds: () => [fitScale(), MOST], to: zoomTo, fit, fitted});

  // The chart opens on the rectangles and the items out of them.
  // Horizontal, the rectangles sit near the left edge, their items' names in
  // view beside them; a window too narrow for both keeps the rectangles at
  // its very edge, their names always in view. Flipped, the rectangles sit
  // near the top. Across the chart, the rectangles and their items centre in
  // the window when they all fit; else the first rectangle sits near the
  // window's top, or flipped, its left.
  function home() {
    const c = tree.laidOut(way).canvas, t = c.first, W = sc.clientWidth, H = sc.clientHeight, s = scale;
    const across = size => (t.hi - t.lo) * s <= size ? [(t.lo + t.hi) / 2, size / 2] : [t.lo, INSET];
    if (way === 'h') {
      const [y, Y] = across(H);
      place(t.near, y, Math.max(EDGE, Math.min(INSET, W - EDGE - (t.line + t.reach - t.near) * s)), Y);
    } else {
      const [x, X] = across(W);
      place(x, t.near, X, INSET);
    }
  }

  function noteOf(it) {
    const waitsOn = tree.parentsOf(it), waiting = tree.items.filter(o => (o.after || []).includes(it.id));
    return `<button type="button" class="close" id="nx" aria-label="Close">${CLOSE}</button><div class="nh">`
      + `<span class="badge" style="background:${tree.colourOf(it)}"></span><h3>${esc(it.title)}</h3></div>`
      + '<p class="st"><button type="button" class="btn go" id="start">Start</button></p>'
      + (it.note ? `<p class="nt">${esc(it.note)}</p>` : '')
      + (waitsOn.length ? '<h4>Waits on</h4><ul class="items">' + waitsOn.map(o => `<li>${dotOf(o)}${esc(o.title)}</li>`).join('') + '</ul>' : '')
      + (waiting.length ? '<h4>Waiting on it</h4><ul class="items">' + waiting.map(o => `<li>${dotOf(o)}${esc(o.title)}</li>`).join('') + '</ul>' : '');
  }

  // The right side: the list, else the open item's note, else nothing.
  function side() {
    if (!list) return showNote();
    note.innerHTML = listOf();
    note.hidden = false;
    $('nx').onclick = () => { if (list === 'hits') q.value = ''; show(null); };
  }

  function showNote() {
    const it = open && tree.byId.get(open);
    if (!it) { open = null; note.hidden = true; note.innerHTML = ''; return; }
    note.innerHTML = noteOf(it);
    note.hidden = false;
    $('nx').onclick = () => pick(open);
    $('start').onclick = () => start(it.id);
  }

  // An item clicked, on the chart or in a list: it is ringed, and its note
  // opens. Clicked again on the chart, its note closes.
  function pick(id) {
    list = null;
    open = open === id ? null : id;
    counts();
    paint();
    showNote();
  }

  // A list at the right, in place of a note: a count's, or the search's
  // hits. null closes it.
  function show(kind) {
    list = kind;
    if (open) { open = null; paint(); }
    counts();
    side();
  }

  // Start opens a session on its item, through 1100. A refusal shows its
  // sentence. Start takes no second press until the pane has opened.
  async function start(id) {
    const b = $('start');
    if (b) b.disabled = true;
    try {
      const r = await fetch(location.pathname, {method: 'POST', redirect: 'manual',
                                                body: new URLSearchParams({start: id})});
      if (r.status === 409) { const bad = $('bad'); bad.textContent = await r.text(); bad.hidden = false; }
    } catch (e) {}
    if ($('start')) $('start').disabled = false;
  }

  sc.addEventListener('click', e => {
    const n = e.target.closest('.node');
    if (n) pick(n.dataset.id);
  });

  // A count pressed opens its list; pressed again, it closes it. A chip
  // pressed shows its order.
  counted.addEventListener('click', e => {
    const b = e.target.closest('button[data-list], button[data-chip]');
    if (!b) return;
    if (b.dataset.list) show(list === b.dataset.list ? null : b.dataset.list);
    else press(b.dataset.chip === 'all' ? 'all' : +b.dataset.chip);
  });

  // A row clicked opens its item's note, as a click on the chart does.
  note.addEventListener('click', e => {
    const b = e.target.closest('.rows button');
    if (b) pick(b.dataset.id);
  });

  // The search finds as I type. Its words stay until I clear them, and a
  // click into it brings their hits back. Escape clears it.
  q.addEventListener('input', () => { if (q.value.trim()) show('hits'); else if (list === 'hits') show(null); });
  q.addEventListener('focus', () => { if (q.value.trim() && list !== 'hits') show('hits'); });
  q.addEventListener('keydown', e => {
    if (e.key !== 'Escape') return;
    q.value = '';
    if (list === 'hits') show(null);
  });

  // Flipped, the chart opens on its rectangles again at its size, or fits
  // again when it was fitted.
  flip.addEventListener('click', () => {
    const was = fitted();
    way = way === 'h' ? 'v' : 'h';
    try { localStorage.setItem('agenda-way', way); } catch (e) {}
    paint();
    if (was) fit();
    else home();
    tools();
  });

  // A mouse drag anywhere off an item moves the chart, under the pointer at
  // any zoom: the drawing's own size on screen says how far a pixel of
  // scroll moves it. A finger moves it as any page scrolls.
  let drag = null;
  sc.addEventListener('pointerdown', e => {
    if (e.pointerType !== 'mouse' || e.button !== 0 || e.target.closest('.node')) return;
    const svg = sc.querySelector('svg');
    const k = svg ? svg.getBoundingClientRect().width / svg.width.baseVal.value || 1 : 1;
    drag = {x: e.clientX, y: e.clientY, left: sc.scrollLeft, top: sc.scrollTop, k};
    sc.classList.add('drag');
    try { sc.setPointerCapture(e.pointerId); } catch (x) {}
  });
  sc.addEventListener('pointermove', e => {
    if (!drag) return;
    sc.scrollLeft = drag.left - (e.clientX - drag.x) / drag.k;
    sc.scrollTop = drag.top - (e.clientY - drag.y) / drag.k;
  });
  const release = e => {
    if (!drag) return;
    drag = null;
    sc.classList.remove('drag');
    try { if (sc.hasPointerCapture(e.pointerId)) sc.releasePointerCapture(e.pointerId); } catch (x) {}
  };
  sc.addEventListener('pointerup', release);
  sc.addEventListener('pointercancel', release);

  // What stays still on screen while the chart is drawn again: the open
  // item, else the first rectangle.
  function anchor() {
    if (!sc.querySelector('svg')) return null;
    const L = tree.laidOut(way), id = open && L.points.get(open) ? open : tree.rects[0], p = L.points.get(id), at = corner();
    return {id, x: at.x + p.x * scale, y: at.y + p.y * scale};
  }
  function settle(a) {
    if (!a) return home();
    const L = tree.laidOut(way), p = L.points.get(a.id) || L.points.get(tree.rects[0]);
    place(p.x, p.y, a.x, a.y);
  }

  // Told the agenda moved: it is read again and drawn in place. Its counts
  // move. Its way, its size, the spot on screen, its chip and an open note
  // or list stay. Told again meanwhile, it draws once more after.
  let drawing = false, again = false;
  async function told(now) {
    const w = $('watch');
    if (w && now !== undefined) w.dataset.key = now;
    if (drawing) { again = true; return; }
    drawing = true;
    try {
      do {
        again = false;
        const r = await fetch(location.pathname.replace(/\/$/, '') + '/data', {cache: 'no-store'});
        if (!r.ok) break;
        const next = await r.json(), a = anchor();
        D = next;
        build();
        paint();
        settle(a);
        tools();
        side();
      } while (again);
    } catch (e) {}
    drawing = false;
  }
  window.told = told;

  // A pan, or a window grown or shrunk, changes what Fit and − can do.
  sc.addEventListener('scroll', tools, {passive: true});
  addEventListener('resize', tools);

  // How long the first drawing took, in milliseconds, kept for its tests.
  const t0 = performance.now();
  build();
  paint();
  home();
  $('ag').dataset.ms = String(Math.round(performance.now() - t0));
})();
</script>
"""

# Lucide's arrow-up-down and arrow-left-right: what a press of the flip
# button turns the chart to.
FLIP_V = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m21 16-4 4-4-4"/>'
          '<path d="M17 20V4"/><path d="m3 8 4-4 4 4"/><path d="M7 4v16"/></svg>')
FLIP_H = ('<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" '
          'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 3 4 7l4 4"/>'
          '<path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/></svg>')

# The page script's own fingerprint: an order a browser kept from other
# code is never used.
CODE = hashlib.sha256(SCRIPT.encode()).hexdigest()[:12]

# The top rail's tools, together at its right: the search, then the zoom
# tools every chart wears and the flip, which never part. Its middle holds
# the counts, drawn by the page.
TOOLS = (f'<label class="find">{page.icon("search", 14)}<input id="q" spellcheck="false" autocomplete="off" '
         'aria-label="Find an item by its title or its note" placeholder="Find: a title, a note"></label>'
         '<span class="tl">' + page.ZOOM_TOOLS
         + '<button type="button" class="flip" id="flip" aria-label="Flip"></button></span>')


def draw(d: dict, tail: str = "") -> str:
    """The page, from what the folder holds: {"topics": [{"name",
    "colour"}], "phases", "headings", "items": [{"id", "title", "after", "topics",
    "phase", "note", "mine"}], "broken", "live"}. `tail` is its watch."""
    data = json.dumps(d, ensure_ascii=False).replace("</", "<\\/")
    script = (SCRIPT.replace("%FLIP_V%", FLIP_V).replace("%FLIP_H%", FLIP_H)
              .replace("%CLOSE%", page.icon("close", 15)).replace("%CODE%", CODE))
    body = (PILLS + STYLE + BODY + f'<script type="application/json" id="data">{data}</script>' + tail
            + page.ZOOM + script)
    return page.render("00-agenda", [("", body)], page.head("agenda", "", "", TOOLS), refresh=0)


def mine(note: str) -> str:
    """The note's Mine line, its words alone, or "" when it carries none."""
    return next((text for name, text in agenda.note_lines(note) if name == "Mine"), "")


def world() -> dict:
    """What the folder holds, as the page draws it: the topics and the
    phases, then each item with its Mine line. It never raises: a folder
    that cannot be read draws as the empty start, so 1100 always draws."""
    try:
        d = agenda.world(FOLDER)
    except Exception:
        d = {"items": [], "broken": []}
    for it in d["items"]:
        it["mine"] = mine(it["note"])
    return {"topics": [{"name": name, "colour": colour} for name, colour in agenda.TOPICS],
            "phases": list(agenda.PHASES), "headings": agenda.HEADINGS, **d, "live": True}


def key() -> str:
    """The folder's key: a write into it moves the page."""
    return agenda.key(FOLDER)


def render() -> str:
    """The page, its watch wearing the key."""
    return draw(world(), page.watch(key()))


def answer() -> str:
    """The folder as JSON, for the page to draw again in place."""
    return json.dumps(world(), ensure_ascii=False)


def heard() -> list:
    """The folder: a write into it moves the page."""
    return [FOLDER]


def start(item: str) -> str:
    """A session opens on the item, through tools/launch.py, right of window
    1's last pane, its first message the item, handed over in my words. The
    answer waits for the pane alone: the session claims its number on its
    own.

    The press is mine, so no session launched it. A server started from a
    session's shell carries that session's process and pane in its
    environment, and launch.py would name it the caller: both are left out."""
    items, _ = agenda.read(FOLDER)
    try:
        i = agenda.find(items, item)
    except agenda.Refused as e:
        return str(e)
    tabs = [launch.leaves(t["root"]) for w in iterm.tree() for t in w["tabs"]]
    if not tabs:
        return "iTerm did not answer, so no session started."
    mine = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PID", "ITERM_SESSION_ID")}
    where = os.path.relpath(os.path.join(FOLDER, f"{i}.md"), registry.ROOT)
    run = subprocess.Popen([sys.executable, LAUNCH, "session", "--name", items[i]["title"],
                            "--message", f"There's this agenda item I'd like to look at: {items[i]['title']}, in {where}.",
                            "--from", tabs[0][-1], "--where", "right"],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True, start_new_session=True, env=mine)
    if not run.stdout.readline():
        return run.communicate()[1].strip() or "The session did not start."
    threading.Thread(target=run.communicate, daemon=True).start()
    return ""


def take(form: dict):
    """Start pressed on an item's note. A refusal comes back as its sentence,
    and the page shows it. The start waits on iTerm and the new pane, so it
    runs off 1100's draw queue: serve.Typing."""
    if "start" not in form:
        return ""
    item = (form.get("start") or [""])[0]
    return serve.Typing(lambda: start(item))


# ---- the test -----------------------------------------------------------------------------

# How far two neighbouring rectangles stand, centre to centre, one under
# the other, whatever their items.
APART = 64
# The scratch agenda the test draws, each item as (name, topics, what it
# waits on, its phase), each topic by its place in agenda.NAMES and each
# phase by its place in agenda.PHASES, wrapping round when the project
# names fewer: the first topic crowded, the third and sixth empty, an item
# under three topics, and a chain out of it, in the second phase.
SCRATCH = (
    ("Sign in", [0], [], 0), ("Sign up", [0], [], 0), ("Reset password", [0], [], 0),
    ("Profile page", [0], [], 0), ("Team invites", [0], ["Sign up"], 0),
    ("Billing screen", [0], ["Profile page"], 0), ("Keys page", [1], [], 0),
    ("Payouts", [3], [], 1), ("Shared ledger", [0, 3, 8], [], 1),
    ("Ledger export", [3], ["Shared ledger"], 1), ("Export audit", [7], ["Ledger export"], 1),
    ("Queue health", [4], [], 0), ("Docs search", [6], [], 0),
    ("Privacy review", [7], [], 0), ("Hook timing", [8], [], 0),
)


def test() -> list:
    """Draws SCRATCH in headless Chrome, the chart left to right, and
    returns each phase's chart that draws other than every topic's
    rectangle, each pair of neighbouring rectangles standing other than
    APART apart, and any arrowhead drawn with no points, each as a
    sentence, or what kept the page from drawing."""
    global FOLDER
    with tempfile.TemporaryDirectory() as tmp:
        FOLDER = os.path.join(tmp, "agenda")
        for name, places, after, phase in SCRATCH:
            tops = [agenda.NAMES[p % len(agenda.NAMES)] for p in places]
            agenda.add(FOLDER, name, tops, after, "What: Do, small: an item the test draws.",
                       agenda.PHASES[phase % len(agenda.PHASES)] if agenda.PHASES else "")
        html = os.path.join(tmp, "agenda.html")
        with open(html, "w", encoding="utf-8") as f:
            f.write(draw(world()))
        try:
            run = subprocess.run([CHROME, "--headless=new", "--disable-gpu", f"--user-data-dir={tmp}/chrome",
                                  "--window-size=1400,900", "--dump-dom", f"file://{html}"],
                                 capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as e:
            return [f"Chrome did not draw the page: {e}."]
    charts = re.split(r'<g data-section="\d+" transform="translate\(0 [-\d.]+\)">', run.stdout)[1:]
    if len(charts) != max(1, len(agenda.PHASES)):
        return [f"The page drew {len(charts)} charts, not {max(1, len(agenda.PHASES))}."]
    found = []
    for n, chart in enumerate(charts, 1):
        rects = [(name, float(y)) for name, y in
                 re.findall(r'<g class="root" data-topic="([^"]+)"><rect x="[-\d.]+" y="([-\d.]+)"', chart)]
        if len(rects) != len(agenda.TOPICS):
            found.append(f"Chart {n} drew {len(rects)} rectangles, not {len(agenda.TOPICS)}.")
        found += [f"In chart {n}, {a} and {b} stand {y2 - y1:g} apart, not {APART}."
                  for (a, y1), (b, y2) in zip(rects, rects[1:]) if abs(y2 - y1 - APART) > 0.01]
    bare = run.stdout.count('points="null"')
    if bare:
        found.append(f"The page drew {bare} arrowhead{'s' if bare > 1 else ''} with no points.")
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("test")
    ap.parse_args()
    found = test()
    print("\n".join(found) if found else f"The agenda page test: every two neighbouring rectangles stand {APART} apart, and every arrowhead has its points.")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
