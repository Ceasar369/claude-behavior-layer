/* handover.js — the handover page's own script, on the contract.

   1100 draws the page, tools/handover-page.py's drawn(), and live.js puts
   each change in place. This script keeps my picks and sends Hand over.

   A pill picked names its value, and rides in the address, so a reload
   keeps it. A setting never picked shows what its successor launches on,
   the #picks data, and is never posted. Hand over posts its act and my
   picks; the page then follows the press through its file, and a refusal
   is said under the pills. It hears every click from the document, so a
   pill 1100 draws later needs no wiring. */
(() => {
  'use strict';
  const picks = {};
  let D = {};
  const read = () => { try { D = JSON.parse(document.getElementById('picks').textContent); } catch (e) { D = {}; } };
  const P = () => Object.assign({account: '', model: '', effort: ''}, picks);
  const show = () => {
    const p = Object.assign({}, D, picks);
    document.querySelectorAll('.hp .pills').forEach(g => g.querySelectorAll('button').forEach(b =>
      b.classList.toggle('on', b.dataset.v === p[g.dataset.k])));
  };

  async function handOver(b) {
    const all = [b, ...document.querySelectorAll('.hp .pills button')];
    all.forEach(x => x.disabled = true);
    const got = await live.post(Object.assign({act: 'handover'}, P()));
    if (got.ok) { b.textContent = 'Saving…'; return; }
    all.forEach(x => x.disabled = false);
    const say = document.getElementById('say'), why = got.ok === null ? '1100 did not answer. Nothing was typed.' : got.said;
    if (!say) return live.said(why);
    say.textContent = why;
    say.hidden = false;
  }

  document.addEventListener('click', e => {
    const go = e.target.closest('#go');
    if (go) { if (!go.disabled) handOver(go); return; }
    const b = e.target.closest('.hp .pills button');
    if (!b || b.disabled) return;
    picks[b.parentNode.dataset.k] = b.dataset.v;
    history.replaceState(null, '', '#' + new URLSearchParams(picks));
    show();
  });

  live.ready(() => {
    read();
    new URLSearchParams(location.hash.slice(1)).forEach((v, k) => { if (k in D) picks[k] = v; });
    show();
  });
  live.drawn(() => { read(); show(); });
})();
