/* skills.js — the skills page's own script, on the contract: lib/live.py.

   1100 draws every skill. This script copies a command on a click, and
   filters the rows as I type, each word marked where it shows. Nothing
   takes my keys until the filter is clicked; Enter copies the first row,
   Escape clears. What I filtered by outlives a reload.

   A marked word replaces its row's text on screen, so the words are always
   read from the picture 1100 last drew, and drawn again after each change
   1100 put in place.
*/
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  const safe = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // A row's words, as 1100 drew them.
  const drawnText = e => (live.drawnAs(e) || e).textContent;
  let first = null, timer = 0;

  // It flashes only once the copy landed.
  function copy(b) {
    navigator.clipboard.writeText(b.dataset.c).then(() => {
      document.querySelectorAll('.cmd.ok').forEach(x => x.classList.remove('ok'));
      b.classList.add('ok');
      clearTimeout(timer);
      timer = setTimeout(() => b.classList.remove('ok'), 1600);
    }).catch(() => {});
  }

  // One row's words, marked where each word shows, or plain.
  function mark(e, re) {
    const t = drawnText(e);
    if (re) {
      const want = esc(t).replace(re, '<mark>$1</mark>');
      if (e.innerHTML !== want) e.innerHTML = want;
    } else if (e.firstElementChild || e.textContent !== t) e.textContent = t;
  }

  function filter() {
    const q = $('q'), hm = $('hm');
    const words = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const re = words.length ? new RegExp('(' + words.map(safe).join('|') + ')', 'gi') : null;
    first = null;
    document.querySelectorAll('.sr').forEach(r => {
      const parts = [...r.querySelectorAll('.int, .cmd .t')];
      const said = parts.map(drawnText).join(' ').toLowerCase();
      const hit = words.every(w => said.includes(w));
      r.classList.toggle('none', !hit);
      parts.forEach(e => mark(e, re));
      if (hit && !first) first = r.querySelector('.cmd');
    });
    document.querySelectorAll('.skf').forEach(f => f.classList.toggle('none', !f.querySelector('.sr:not(.none)')));
    document.querySelector('.nomatch').style.display = first ? 'none' : 'block';
    const want = !words.length ? (live.drawnAs(hm) || hm).innerHTML
      : first ? '↵ copies <b>' + esc(first.dataset.c) + '</b>' : 'No match';
    if (hm.innerHTML !== want) hm.innerHTML = want;
  }

  const kept = () => sessionStorage.setItem('skills-filter', $('q').value);
  document.addEventListener('click', e => {
    const b = e.target.closest && e.target.closest('.cmd');
    if (b) copy(b);
  });
  document.addEventListener('input', e => {
    if (e.target.id !== 'q') return;
    kept();
    filter();
  });
  document.addEventListener('keydown', e => {
    const q = e.target;
    if (q.id !== 'q') return;
    if (e.key === 'Enter' && first && q.value.trim()) copy(first);
    if (e.key === 'Escape') { q.value = ''; kept(); filter(); }
  });

  // A change put in place: filtering, the rows are filtered again. With no
  // words, each row and the count read as 1100 drew them.
  live.drawn(() => {
    if ($('q').value.trim()) return filter();
    document.querySelectorAll('.int, .cmd .t').forEach(e => mark(e, null));
    const hm = $('hm'), want = (live.drawnAs(hm) || hm).innerHTML;
    if (hm.innerHTML !== want) hm.innerHTML = want;
  });
  live.ready(() => {
    $('q').value = sessionStorage.getItem('skills-filter') || '';
    if ($('q').value) filter();
  });
})();
