/* system.js — System's own script, on the contract.

   1100 draws every part, tools/system-page.py's drawn(), and live.js puts
   each change in place. Each instant comes as its epoch. This script says
   it on this Mac's clock, ticks how far it is from now, and reads a
   window 0 once its reset passed, as 1100 did before the contract. It
   sends each press, and nothing reloads: a save lands, 1100 hears its
   file, and the part it moves is put in place. It keeps the rail's size,
   on this device.

   It touches the screen only from live.ready and live.drawn, and hears
   every click and key from the document, so a part 1100 draws later needs
   no wiring. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const data = () => { try { return JSON.parse($('system').textContent); } catch (e) { return {known: '', zooms: [1]}; } };
  const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const two = n => String(n).padStart(2, '0');

  /* An instant on this Mac's clock: 14:20 today, Mon 18:00 on another day. */
  function clock(epoch) {
    const t = new Date(epoch * 1000), now = new Date();
    const hm = two(t.getHours()) + ':' + two(t.getMinutes());
    return t.toDateString() === now.toDateString() ? hm : DAYS[t.getDay()] + ' ' + hm;
  }
  const far = s => {
    const m = Math.round(Math.abs(s) / 60), h = Math.round(m / 60), d = Math.round(h / 24);
    return m < 60 ? `${m} minute${m === 1 ? '' : 's'}` : h < 48 ? `${h} hour${h === 1 ? '' : 's'}` : `${d} days`;
  };
  /* Every instant said, and every window whose reset passed read 0. */
  function tick() {
    const now = Date.now() / 1000;
    document.querySelectorAll('[data-at]').forEach(e => { e.textContent = (e.dataset.before || '') + clock(+e.dataset.at); });
    document.querySelectorAll('[data-reset]').forEach(e => {
      e.textContent = (+e.dataset.reset > now ? 'resets ' : 'reset ') + clock(+e.dataset.reset);
    });
    document.querySelectorAll('.use [data-t]').forEach(e => {
      const s = +e.dataset.t - now;
      e.textContent = Math.abs(s) < 60 ? (s > 0 ? ', in under a minute' : ', just now')
                    : s > 0 ? `, in ${far(s)}` : `, ${far(s)} ago`;
    });
    /* A window reads as 1100 drew it until its reset passes, then 0. */
    document.querySelectorAll('.win[data-window]').forEach(w => {
      const was = live.drawnAs(w), passed = +w.dataset.window <= now;
      if (!was) return;
      const b = w.querySelector('.wl b'), bar = w.querySelector('.meter i');
      const pb = was.querySelector('.wl b'), pbar = was.querySelector('.meter i');
      // Only what differs is written: a node 1100 drew stays the one it puts its changes on.
      const set = (now, want, put) => { if (now !== want) put(want); };
      if (b && pb) set(b.textContent, passed ? '0%' : pb.textContent, v => { b.textContent = v; });
      if (bar && pbar) set(bar.style.width, passed ? '0%' : pbar.style.width, v => { bar.style.width = v; });
      set(w.title, passed ? was.title.replace(/\d+% used$/, '0% used') : was.title, v => { w.title = v; });
    });
  }

  /* Each port's link opens at the address System itself was opened at, as home's links do. */
  function linked() {
    document.querySelectorAll('a[data-port]').forEach(a => {
      a.href = `${location.protocol}//${location.hostname}:${a.dataset.port}/`;
    });
  }

  /* The rail's own zoom, on this device, kept as rail-zoom, which home hears change. */
  function zoom() { const z = +localStorage.getItem('rail-zoom'); return data().zooms.includes(z) ? z : 1; }
  function paint() {
    const tools = $('rail');
    if (!tools) return;
    const z = zoom(), zooms = data().zooms;
    tools.querySelector('.pct').textContent = Math.round(z * 100) + '%';
    tools.querySelector('[data-z="-1"]').disabled = z === zooms[0];
    tools.querySelector('[data-z="1"]').disabled = z === zooms[zooms.length - 1];
  }

  /* The app view this page sits in, when its home was opened as /?app: its
     row among the app views is marked. Home's address names the view. */
  function here() {
    let view = '';
    try {
      const q = new URLSearchParams(parent.location.search);
      if (parent !== window && q.has('app')) view = /^[1-9][0-9]?$/.test(q.get('app') || '') ? q.get('app') : '1';
    } catch (e) {}
    document.querySelectorAll('#views .op[data-view]').forEach(r => r.classList.toggle('here', r.dataset.view === view));
  }
  function drawn() { tick(); linked(); paint(); here(); }

  /* One setting saved: it posts to /, as before the contract. Refused, its
     sentence shows along the foot. Done, the page is brought in line at once. */
  async function save(body, box) {
    const got = await live.post(body, '/');
    if (got.ok) { if (box) live.sent(box); live.now(); }
    else live.said(got.said);
    return got;
  }

  /* A finding's button: End asks once more first, its buttons giving way
     to its question. The guard's answer shows under its line. */
  const flip = row => row.querySelectorAll(':scope > .bs, :scope > .q').forEach(e => { e.hidden = !e.hidden; });
  async function guard(b, row) {
    if (b.dataset.verb === 'end' && !('sure' in b.dataset)) return flip(row);
    if ('back' in b.dataset) return flip(row);
    const all = row.querySelectorAll('button'), sure = 'sure' in b.dataset;
    row.querySelectorAll('.said').forEach(s => s.remove());
    all.forEach(x => { x.disabled = true; });
    const got = await live.post({act: b.dataset.verb, finding: row.dataset.id});
    all.forEach(x => { x.disabled = false; });
    if (sure) flip(row);
    if (got.said) {
      row.insertAdjacentHTML('beforeend', '<span class="said"></span>');
      row.lastChild.textContent = got.said;
    }
  }

  const FORMS = {set: ['order', 'order'], limit: ['threshold', 'threshold'], wrapup: ['wrap', 'wrapup']};
  const valid = (id, v) => id === 'order' ? new RegExp(`^[\\s,${data().known}]*$`).test(v)
                                          : /^\d{1,2}$/.test(v.trim()) && +v > 0;

  live.ready(() => {
    drawn();
    live.drawn(drawn);
    setInterval(tick, 30000);
    addEventListener('storage', e => { if (e.key === 'rail-zoom') paint(); });

    document.addEventListener('input', e => {
      const box = e.target;
      if (box.matches && box.matches('#order, #threshold, #wrap')) box.classList.toggle('bad', !valid(box.id, box.value));
    });
    document.addEventListener('submit', e => {
      const form = e.target, [id, name] = FORMS[form.id] || [];
      if (!id) return;
      e.preventDefault();
      const box = $(id);
      if (!valid(id, box.value)) return;
      save({[name]: id === 'order' ? box.value : box.value.trim()}, box);
    });
    document.addEventListener('click', e => {
      const b = e.target.closest('button');
      if (!b || b.disabled) return;
      const row = b.closest('#mem .row');
      if (row) return guard(b, row);
      if (b.matches('.mbar')) { const to = $(b.dataset.to); if (to) to.scrollIntoView(); return; }
      if (b.matches('.use .sn')) {
        if (parent !== window) parent.postMessage({ws: 1, open: 'session', nn: b.dataset.nn}, '*');
        else location.href = '/#' + b.dataset.nn;
        return;
      }
      if (b.matches('#rail [data-z]')) {
        const zooms = data().zooms;
        localStorage.setItem('rail-zoom', zooms[Math.max(0, Math.min(zooms.length - 1, zooms.indexOf(zoom()) + +b.dataset.z))]);
        return paint();
      }
      const group = b.parentNode.dataset.k;
      if (b.matches('#effort button, #model button')) return save({[group]: b.dataset.v});
      const own = b.closest('.own'), eng = b.closest('.eng');
      if (own) return save({own: own.dataset.a, ['own_' + group]: b.dataset.v});
      if (eng) return save({engine: eng.dataset.e, ['engine_' + group]: b.dataset.v});
    });
  });
})();
