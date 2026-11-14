/* library.js — the library page's own script, on the contract: lib/live.py.

   1100 draws the whole book. This script opens the word or graph the
   address's hash names, folds the rail, finds words as I type, drags the
   rail's width, a graph's split and its length, shuts the rail by its tab,
   switches the review marks, and sends a review button's press. Nothing
   takes my keys until Find is clicked: Enter opens the first word found,
   Escape clears. The hash is a word, "graph:NAME", or "graph:NAME/WORD"
   with a box's word on the left.

   What I folded, typed, dragged and shut outlives a reload, and is put back
   after each change 1100 put in place. Clicks, keys and drags are heard
   from the document.
*/
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const stored = (k, d) => { try { return JSON.parse(sessionStorage.getItem(k)) ?? d; } catch (e) { return d; } };
  const keep = (k, v) => { try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) {} };
  const open = new Set(stored('library-open', []));
  const main = () => document.querySelector('main');

  function set(f, on) {
    f.classList.toggle('on', on);
    on ? open.add(f.dataset.k) : open.delete(f.dataset.k);
    keep('library-open', [...open]);
  }
  const unfold = row => { for (let f = row && row.closest('.fold'); f; f = f.parentElement.closest('.fold')) set(f, true); };

  // The word or graph the hash names, shown; every other hidden. `moved`,
  // the page scrolls back to its top.
  function show(hash, moved = true) {
    const tree = $('tree');
    const [g, w] = hash.startsWith('graph:') ? hash.slice(6).split('/') : ['', hash];
    const graph = g && $('g-' + g), page = w && $('p-' + w);
    document.querySelectorAll('.reading').forEach(a => a.hidden = !!graph || a !== page);
    document.querySelectorAll('.graph').forEach(a => a.hidden = a !== graph);
    if (graph && graph.querySelector('.gx-word')) {
      const text = graph.querySelector('.gx-text'), slot = graph.querySelector('.gx-word');
      text.hidden = !!page;
      slot.hidden = !page;
      const want = page ? page.innerHTML : '';
      if (slot.querySelector('.gx-slot').innerHTML !== want) slot.querySelector('.gx-slot').innerHTML = want;
      graph.querySelectorAll('.gx-box[data-w]').forEach(b => b.classList.toggle('on', !!page && b.dataset.w === w));
      if (moved) graph.querySelector('.gx-col').scrollTop = 0;
      const len = stored('library-length', {})[g];
      if (len) graph.querySelector('.gx-lanes').style.setProperty('--length', len + 'px');
    }
    document.querySelectorAll('.t-word[data-w]').forEach(b => b.classList.toggle('on', !!page && b.dataset.w === w));
    document.querySelectorAll('.t-graph').forEach(b => b.classList.toggle('on', !!graph && !page && b.dataset.g === g));
    $('blank').hidden = !!(graph || page);
    document.body.classList.toggle('reading-word', !!(graph || page));
    if (moved) main().scrollTop = 0;
    if (!tree) return;
    unfold(graph ? tree.querySelector(`.t-graph[data-g="${g}"]`) : page && tree.querySelector(`.t-word[data-w="${w}"]`));
    if (graph && page) unfold(tree.querySelector(`.t-word[data-w="${w}"]`));
  }
  const hash = () => decodeURIComponent(location.hash.slice(1));
  const go = h => { history.replaceState(null, '', h ? '#' + h : location.pathname); show(h); };

  function narrow() {
    const q = $('q'), hits = [...$('found').querySelectorAll('.t-word')];
    const words = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    $('tree').hidden = !!words.length;
    $('found').hidden = !words.length;
    hits.forEach(b => b.hidden = !words.every(w => b.textContent.toLowerCase().includes(w)));
    $('none').hidden = hits.some(b => !b.hidden);
    keep('library-find', q.value);
    return hits;
  }

  const shut = on => {
    document.body.classList.toggle('rail-shut', on);
    $('adv').classList.toggle('open', !on);
    $('atab').setAttribute('aria-expanded', !on);
    keep('library-shut', on);
  };
  const showMarks = on => {
    document.body.classList.toggle('marks-off', !on);
    $('marks').setAttribute('aria-pressed', on);
    try { localStorage.setItem('library-marks', on ? 'on' : 'off'); } catch (e) {}
  };

  // Every click, heard from the document.
  document.addEventListener('click', async e => {
    const t = e.target;
    if (!t.closest || !$('tree')) return;
    let b;
    if ((b = t.closest('#tree .t-1, #tree .t-2'))) set(b.parentElement, !b.parentElement.classList.contains('on'));
    else if ((b = t.closest('aside .t-word'))) go(b.dataset.g ? 'graph:' + b.dataset.g : b.dataset.w);
    else if (t.closest('#atab')) shut(!document.body.classList.contains('rail-shut'));
    else if (t.closest('#marks')) showMarks(document.body.classList.contains('marks-off'));
    else if ((b = t.closest('main .rv-set'))) {
      // A review button posts its item. 1100 then puts its marks and counts in place.
      b.disabled = true;
      const got = await live.post({item: b.dataset.item, to: b.dataset.to});
      b.disabled = false;
      live.said(got.ok ? '' : got.ok === null ? '1100 did not answer. Nothing was marked.' : got.said);
    } else if (t.closest('main')) {
      const at = t.closest('.graph'), g = at && at.dataset.g;
      if (t.closest('.back')) go('');
      else if ((b = t.closest('.gx-box[data-w]'))) go(`graph:${g}/${b.dataset.w}`);
      else if (t.closest('.gx-return')) go('graph:' + g);
      else if ((b = t.closest('.explained'))) go('graph:' + b.dataset.g);
    }
  });
  document.addEventListener('input', e => { if (e.target.id === 'q') narrow(); });
  document.addEventListener('keydown', e => {
    const q = e.target;
    if (q.id !== 'q') return;
    if (e.key === 'Enter') { const b = narrow().find(b => !b.hidden); if (b && q.value.trim()) go(b.dataset.w); }
    if (e.key === 'Escape') { q.value = ''; narrow(); }
  });

  // The divider sets the text's share of the width, 26% to 62%, for every
  // graph. The bottom edge sets that graph's length, never under what its
  // boxes need. The rail's edge sets its width, 200px to 60% of the glass.
  let drag = null;
  document.addEventListener('pointerdown', e => {
    const handle = e.target.closest && e.target.closest('.gx-bar, .gx-edge, .t-bar');
    if (!handle) return;
    const graph = handle.closest('.graph');
    drag = {handle, graph, from: 0};
    if (handle.classList.contains('gx-edge')) {
      drag.from = e.clientY - graph.querySelector('.gx-lanes .gx-chart').getBoundingClientRect().height;
    }
    try { handle.setPointerCapture(e.pointerId); } catch (x) {}
    handle.classList.add('drag');
    if (!handle.classList.contains('gx-edge')) moved(e);
  });
  function moved(e) {
    const {handle, graph} = drag;
    if (handle.classList.contains('gx-bar')) {
      const box = graph.getBoundingClientRect();
      const pct = Math.min(62, Math.max(26, (e.clientX - box.left) / box.width * 100));
      document.body.style.setProperty('--split', pct + '%');
      keep('library-split', pct);
    } else if (handle.classList.contains('gx-edge')) {
      const len = Math.round(Math.min(1400, Math.max(300, e.clientY - drag.from)));
      graph.querySelector('.gx-lanes').style.setProperty('--length', len + 'px');
      const all = stored('library-length', {});
      all[graph.dataset.g] = len;
      keep('library-length', all);
    } else {
      const rail = document.querySelector('aside');
      const px = Math.round(Math.min(innerWidth * 0.6, Math.max(200, e.clientX - rail.getBoundingClientRect().left)));
      rail.style.width = px + 'px';
      keep('library-rail', px);
    }
  }
  document.addEventListener('pointermove', e => {
    if (drag && drag.handle.hasPointerCapture && drag.handle.hasPointerCapture(e.pointerId)) moved(e);
  });
  document.addEventListener('pointerup', () => {
    if (drag) drag.handle.classList.remove('drag');
    drag = null;
  });

  // What I folded, dragged, shut and typed, put back on the page as 1100
  // drew it: on load, and after each change it put in place.
  function again(moved) {
    if (!$('tree')) return;
    document.querySelectorAll('.fold').forEach(f => f.classList.toggle('on', open.has(f.dataset.k)));
    document.body.style.setProperty('--split', stored('library-split', 46) + '%');
    const wide = stored('library-rail', 0);
    if (wide) document.querySelector('aside').style.width = wide + 'px';
    shut(stored('library-shut', false));
    let on = true;
    try { on = localStorage.getItem('library-marks') !== 'off'; } catch (e) {}
    showMarks(on);
    narrow();
    show(hash(), moved);
  }
  addEventListener('hashchange', () => show(hash()));
  live.drawn(() => again(false));
  live.ready(() => {
    if ($('q')) $('q').value = stored('library-find', '');
    again(true);
  });
})();
