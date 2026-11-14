/* jury.js — the jury tab's own script, on the contract.

   1100 draws the tab, tools/jury-page.py's drawn(), and live.js puts each
   change in place. This script saves my edits to the plan as I go, sends
   Launch, and opens a claim's jurors under it.

   It reads the plan as 1100 last drew it from the page's #plan data, null
   once launched. An edit not yet saved wins over a picture drawn since. It
   hears every click, key and edit from the document, so a part 1100 draws
   later needs no wiring. */
(() => {
  'use strict';
  let PLAN = null, timer = 0;
  const read = () => { if (timer) return; try { PLAN = JSON.parse(document.getElementById('plan').textContent); } catch (e) { PLAN = null; } };
  const flush = () => { clearTimeout(timer); timer = 0; return live.post({act: 'plan', run: PLAN.run, plan: JSON.stringify(PLAN)}); };
  const save = () => { clearTimeout(timer); timer = setTimeout(flush, 300); };
  const put = (path, v) => {
    const ks = path.split('.'), last = ks.pop();
    ks.reduce((o, k) => o[k], PLAN)[last] = v;
  };

  /* A word edited in place is a box live.js keeps while my cursor is in it. */
  document.addEventListener('input', e => {
    const el = e.target.closest && e.target.closest('[data-f]');
    if (el && PLAN) { put(el.dataset.f, el.textContent.trim()); save(); }
  });
  document.addEventListener('keydown', e => {
    const el = e.target.closest && e.target.closest('[data-f]');
    if (el && e.key === 'Enter') { e.preventDefault(); el.blur(); }
  });
  document.addEventListener('click', async e => {
    const go = e.target.closest('#launch');
    if (go) {
      if (go.disabled || !PLAN) return;
      if (timer) await flush();
      return live.pressed(go, {act: 'launch', run: PLAN.run}, {not: 'Not typed'});
    }
    const b = e.target.closest('.pills[data-k] button');
    if (b && PLAN && !b.disabled) {
      const k = b.parentNode.dataset.k;
      b.parentNode.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
      put(k, b.dataset.v);
      if (k === 'shape') document.querySelectorAll('.jt-shape').forEach(s => { s.textContent = b.dataset.v; });
      return save();
    }
    /* A claim's row opens its jurors under it, and folds them again. */
    const tr = e.target.closest('tr.jt-row');
    if (tr) {
      const box = tr.nextElementSibling, shut = box.hidden;
      box.hidden = !shut;
      tr.querySelector('.jt-arrow').textContent = shut ? '▾' : '▸';
    }
  });
  addEventListener('beforeunload', () => { if (timer) flush(); });

  live.ready(read);
  live.drawn(read);
})();
