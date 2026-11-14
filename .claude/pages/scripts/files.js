/* files.js — Files' own script, on the contract.

   1100 draws every session's folder, tools/files-page.py's drawn(), and
   live.js puts each change in place. This script fills a folder the first
   time it opens, from /tree/NN/REL, keeps each folder as I left it on this
   device, and shows the file I pick from /text/NN/REL, its address naming
   it so a reload keeps it. The picked file's mark comes in the page's
   #picked data: once 1100 draws a new one, its text is drawn again in
   place, where I scrolled. An open folder whose count 1100 moves fills
   again by itself; Refresh fills each open folder again. Copy
   copies the whole file, never the shortened preview. How long ago ticks
   on its own.

   It touches the screen only from live.ready and live.drawn, and hears
   every click, key and toggle from the document. */
(() => {
  'use strict';
  const K = 'files-open', opened = () => { try { return JSON.parse(localStorage.getItem(K) || '{}'); } catch (e) { return {}; } };
  const $ = id => document.getElementById(id);
  const box = () => document.querySelector('.files'), view = () => $('fview');
  const tree = () => document.querySelector('.tree .scroll');
  const marked = () => { try { return JSON.parse($('picked').textContent).mark; } catch (e) { return 'none'; } };
  const ago = t => { const d = Math.max(0, Math.floor(Date.now() / 1000 - t));
    return d < 60 ? d + 's' : d < 3600 ? Math.floor(d / 60) + 'm' : Math.floor(d / 3600) + 'h'; };
  const tick = () => document.querySelectorAll('[data-since]').forEach(e => { e.textContent = ago(+e.dataset.since); });
  const text = f => '/text/' + f.split('/').map(encodeURIComponent).join('/');

  /* A folder's rows, asked once. Each folder inside opens as I left it. */
  let busy = 0, settle;
  const settled = new Promise(r => { settle = r; });
  function fill(d) {
    if (d.filled) return d.filled;
    busy++;
    d.counted = counted(d);
    const [nn, ...rel] = d.dataset.k.split('/');
    return d.filled = (async () => {
      try {
        const r = await fetch('/tree/' + nn + '/' + rel.map(encodeURIComponent).join('/'));
        const rows = await r.text();
        [...d.children].filter(c => c.tagName !== 'SUMMARY').forEach(c => c.remove());
        d.insertAdjacentHTML('beforeend', rows);
        d.querySelectorAll('.frow.file').forEach(a => a.classList.toggle('on', a.dataset.f === shown));
        tick();
        restore(d);
      } catch (e) {}
      if (!--busy) settle();
    })();
  }
  function restore(root) {
    const s = opened();
    root.querySelectorAll('details[data-k]').forEach(d => {
      if (d.restored) return;
      d.restored = true;
      if (s[d.dataset.k]) { d.open = true; fill(d); }
    });
  }
  /* A folder's count of files, as 1100 last drew it on its line. */
  const counted = d => { const n = d.querySelector(':scope > summary .fs'); return n ? n.textContent : ''; };
  /* Each open session folder asks for its rows again: all of them, or only
     those whose count 1100 moved since they filled. A folder inside another
     fills again with it. */
  function refill(all) {
    document.querySelectorAll('.tree details[open][data-k]').forEach(d => {
      if (d.parentElement.closest('details[data-k]') || !d.filled) return;
      if (!all && counted(d) === d.counted) return;
      d.filled = null;
      fill(d);
    });
  }
  /* Refresh: every open folder fills again, and the page is brought in line. */
  function again() {
    refill(true);
    live.now();
  }

  /* The picked file: shown, and drawn again in place once its mark moves. */
  let shown = '', selection = 0, mark = '';
  function show(html) {
    const v = view();
    v.innerHTML = html;
    const got = v.querySelector('.picked');
    $('fpath').textContent = got ? got.dataset.path + ' · ' + got.dataset.size : shown;
    $('copy').disabled = !got;
  }
  async function pick(f) {
    const picked = ++selection;
    shown = f;
    box().dataset.picked = f ? '1' : '0';
    $('copy').disabled = true;
    $('copy-status').textContent = '';
    view().textContent = f ? 'Loading…' : '';
    $('fpath').textContent = f;
    history.replaceState(null, '', f ? '?f=' + encodeURIComponent(f) : location.pathname);
    // 1100 is asked about the address, which now names this file.
    live.now();
    const parts = f ? f.split('/') : [];
    for (let i = 1; i < parts.length; i++) {
      const d = tree().querySelector(`details[data-k="${CSS.escape(parts.slice(0, i).join('/'))}"]`);
      if (!d) break;
      d.open = true;
      await fill(d);
      if (picked !== selection) return;
    }
    document.querySelectorAll('.frow.file').forEach(a => a.classList.toggle('on', a.dataset.f === f));
    if (!f) return;
    try {
      const response = await fetch(text(f));
      if (!response.ok) throw new Error('file');
      const html = await response.text();
      if (picked !== selection) return;
      show(html);
    } catch (e) { if (picked === selection) view().textContent = 'Could not open this file.'; }
  }
  async function redrawn() {
    const f = shown, picked = selection, v = view(), top = v.scrollTop;
    if (!f) return;
    try {
      const html = await (await fetch(text(f))).text();
      if (picked === selection) { show(html); v.scrollTop = top; }
    } catch (e) {}
  }

  /* Copy the complete file. Clipboard writes start in the click itself,
     including on browsers requiring that gesture. */
  async function copy() {
    const f = shown, info = view().querySelector('.picked'), status = $('copy-status');
    if (!f || !info) return;
    const kind = info.dataset.copy;
    const url = '/raw/' + f.split('/').map(encodeURIComponent).join('/');
    status.textContent = 'Copying…';
    try {
      if (!navigator.clipboard || !window.ClipboardItem) throw new Error('Clipboard unavailable.');
      const type = kind === 'text' ? 'text/plain' : kind === 'image' ? 'image/png' : 'application/octet-stream';
      if (kind === 'file' && (!ClipboardItem.supports || !ClipboardItem.supports(type)))
        throw new Error('This browser cannot copy this file type.');
      const data = fetch(url).then(r => {
        if (!r.ok) throw new Error('File unavailable.');
        return r.blob();
      }).then(async blob => {
        if (kind === 'text') return new Blob([new TextDecoder('utf-8', {fatal: true}).decode(await blob.arrayBuffer())], {type});
        if (kind === 'file') return new Blob([blob], {type: 'application/octet-stream'});
        const image = new Image(), src = URL.createObjectURL(blob);
        try {
          image.src = src;
          await image.decode();
          const canvas = document.createElement('canvas');
          canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
          canvas.getContext('2d').drawImage(image, 0, 0);
          return await new Promise((resolve, reject) => canvas.toBlob(b => b ? resolve(b) : reject(new Error('Image unavailable.')), 'image/png'));
        } finally { URL.revokeObjectURL(src); }
      });
      await navigator.clipboard.write([new ClipboardItem({[type]: data})]);
      if (f === shown) status.textContent = kind === 'file' ? 'Copied; the destination must support this format.' : 'Copied';
    } catch (e) { if (f === shown) status.textContent = e.message || 'Could not copy this file.'; }
  }

  live.ready(() => {
    mark = marked();
    document.addEventListener('toggle', e => {
      const d = e.target;
      if (!(d instanceof HTMLDetailsElement) || !d.dataset.k || !d.closest('.tree')) return;
      const s = opened();
      s[d.dataset.k] = d.open;
      localStorage.setItem(K, JSON.stringify(s));
      if (d.open) fill(d);
    }, true);
    document.addEventListener('click', e => {
      const a = e.target.closest('.tree .frow.file');
      if (a) {
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
        e.preventDefault();
        return pick(a.dataset.f);
      }
      const b = e.target.closest('button');
      if (!b) return;
      if (b.id === 'shut') pick('');
      else if (b.id === 'again') again();
      else if (b.id === 'copy') copy();
    });
    addEventListener('keydown', e => { if (e.key === 'Escape') pick(''); });
    addEventListener('beforeunload', () => {
      sessionStorage.setItem('files-scroll', tree().scrollTop);
      sessionStorage.setItem('files-view', view().scrollTop);
    });
    restore(tree());
    if (!busy) settle();
    // The tree scrolls back once every folder I left open has its rows.
    settled.then(() => { tree().scrollTop = +sessionStorage.getItem('files-scroll') || 0; });
    tick();
    setInterval(tick, 5000);
    const first = new URLSearchParams(location.search).get('f') || decodeURIComponent(location.hash.slice(1));
    pick(first).then(() => {
      view().scrollTop = +sessionStorage.getItem('files-view') || 0;
      sessionStorage.removeItem('files-view');
    });
    live.drawn(() => {
      tick();
      restore(tree());
      refill(false);
      if (marked() !== mark) { mark = marked(); redrawn(); }
    });
  });
})();
