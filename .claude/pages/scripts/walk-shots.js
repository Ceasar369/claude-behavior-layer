/* walk-shots.js — the Screenshots tab's own script, on the contract.

   1100 draws the rail, tools/walk-shots-page.py's drawn(), and live.js puts
   each new screenshot in place. This script only walks them: Back, Play,
   Next and Speed, left and right to step, space to play, and a #K naming
   screenshot K, counted from 1, as the app door's show_page sets it.

   It reads the screenshots as 1100 last drew them from the page's #shots
   data. My place is the screenshot itself, its journey, name and time,
   never where it sat in the list, so a screenshot arriving keeps it. My
   place, my speed and whether it plays outlive a reload. It touches the
   screen only from live.ready and live.drawn, and hears every click and
   key from the document. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  let D = {shots: [], speeds: [1], base: 1500, pic: ''};
  let at = 0, playing = 0, speed = 0, timer = 0;
  const S = () => D.shots, last = () => S().length - 1;
  const idOf = s => s.j + '|' + s.name + '|' + s.time;
  const KEPT = 'shots:' + location.pathname;
  const keep = () => { try { sessionStorage.setItem(KEPT, JSON.stringify({id: idOf(S()[at]), playing, speed})); } catch (e) {} };

  function show() {
    const s = S()[at], view = $('view'), shot = $('shot');
    if (!s || !shot) return;
    document.querySelectorAll('.ws-row').forEach(r => {
      const on = +r.dataset.i === at;
      r.classList.toggle('on', on);
      if (on) r.scrollIntoView({block: 'nearest'});
    });
    // A new screenshot starts at its top.
    if (shot.dataset.id !== idOf(s)) { shot.dataset.id = idOf(s); view.scrollTop = 0; }
    shot.src = D.pic + '/' + at;
    shot.alt = s.name;
    $('mid').textContent = `${s.name} · ${at + 1} of ${S().length}`;
    $('back').disabled = at === 0;
    $('next').disabled = at === last();
    $('play').textContent = playing ? 'Pause' : 'Play';
    $('speed').textContent = D.speeds[speed] + '×';
    keep();
  }
  function go(i) { at = Math.max(0, Math.min(i, last())); show(); }
  function stop() { playing = 0; clearInterval(timer); show(); }
  function play() {
    if (playing) return stop();
    playing = 1;
    clearInterval(timer);
    timer = setInterval(() => { if (at >= last()) return stop(); at++; show(); }, D.base / D.speeds[speed]);
    show();
  }
  function faster() { speed = (speed + 1) % D.speeds.length; if (playing) { playing = 0; play(); } else show(); }
  function read() { try { D = JSON.parse($('shots').textContent); } catch (e) {} }
  // A hash names screenshot K, counted from 1. It is taken once, then
  // dropped, so a reload keeps my own place.
  function hashed() {
    const k = parseInt(location.hash.slice(1), 10);
    if (k > 0) { stop(); go(k - 1); history.replaceState(null, '', location.pathname + location.search); }
  }

  document.addEventListener('click', e => {
    const t = e.target.closest('.ws-row, #back, #play, #next, #speed');
    if (!t || !$('shots')) return;
    if (t.id === 'back') go(at - 1);
    else if (t.id === 'next') go(at + 1);
    else if (t.id === 'play') play();
    else if (t.id === 'speed') faster();
    else go(+t.dataset.i);
  });
  document.addEventListener('keydown', e => {
    if (!$('shots')) return;
    if (e.key === 'ArrowRight') go(at + 1);
    if (e.key === 'ArrowLeft') go(at - 1);
    if (e.key === ' ') { e.preventDefault(); play(); }
  });
  addEventListener('hashchange', hashed);

  live.ready(() => {
    read();
    if (!$('shots')) return;
    let was = null;
    try { was = JSON.parse(sessionStorage.getItem(KEPT) || 'null'); } catch (e) {}
    if (was) { at = Math.max(0, S().findIndex(s => idOf(s) === was.id)); speed = D.speeds[was.speed] ? was.speed : 0; }
    show();
    if (was && was.playing) play();
    hashed();
  });
  // 1100 drew the screenshots again: the one I was on stays mine, wherever it now sits.
  live.drawn(() => {
    const held = S()[at] && idOf(S()[at]);
    read();
    if (!$('shots')) { clearInterval(timer); playing = 0; return; }
    const i = S().findIndex(s => idOf(s) === held);
    at = i >= 0 ? i : Math.min(at, last());
    show();
  });
})();
