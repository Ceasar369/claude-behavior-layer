/* advisor.js — the advisor's panel's own script, on the contract.

   1100 draws the panel's rows inside the advisor's Transcript tab,
   tools/advisor-page.py's drawn(), and live.js puts each change in place.
   This script opens and closes the panel, each device keeping which, draws
   the rows' bar, and sends each press. A page with no panel loads it too,
   so a session turning advisor reloads nothing.

   A row's Type leaves its line in the advisor's prompt, and its Send then
   presses Return alone. A Type pressed stays pressed while 1100 draws the
   rows again. The rows' bar shows only while they run past the panel, its
   thumb as tall as the share in view, placed where the view sits. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const typed = new Set();
  let sized = null;

  function place() {
    const r = $('advrows'), bar = $('advsb');
    if (!r || !bar) return;
    const thumb = bar.firstElementChild, room = r.clientHeight, all = r.scrollHeight;
    bar.classList.toggle('on', all > room + 1);
    if (all <= room + 1) return;
    const h = Math.max(24, room * room / all);
    bar.style.top = r.offsetTop + 'px';
    bar.style.height = room + 'px';
    thumb.style.height = h + 'px';
    thumb.style.top = (room - h) * r.scrollTop / (all - room) + 'px';
  }
  function show(open) {
    $('adv').classList.toggle('open', open);
    $('atab').setAttribute('aria-expanded', open);
    try { localStorage.setItem('advise-open', open ? '1' : ''); } catch (e) {}
  }
  // The panel, wired once it shows: as the page stands, or once 1100 draws it.
  function wire() {
    const rows = $('advrows');
    if (!$('adv') || !rows || sized) return;
    sized = new ResizeObserver(place);
    sized.observe(rows);
    let was = '1';
    try { was = localStorage.getItem('advise-open') ?? '1'; } catch (e) {}
    show(!!was);
  }

  document.addEventListener('scroll', e => {
    const adv = $('adv');
    if (adv && e.target instanceof Node && adv.contains(e.target)) place();
  }, true);
  document.addEventListener('click', async e => {
    if (!e.target.closest || !$('adv')) return;
    if (e.target.closest('#atab')) return show(!$('adv').classList.contains('open'));
    const b = e.target.closest('#adv .row button[data-act]');
    if (!b || b.disabled) return;
    const nn = b.closest('.row').dataset.nn, how = b.dataset.act;
    const only = how === 'send' && typed.has(nn) ? 'return' : '';
    const got = await live.pressed(b, {act: 'advise', how, nn, only},
                                   {word: how === 'send' ? '' : 'Typed', not: 'Not typed'});
    if (!got.ok) return;
    if (how === 'type') typed.add(nn);
    else if (how === 'send') typed.clear();
  });

  live.ready(wire);
  live.drawn(() => { wire(); place(); });
})();
