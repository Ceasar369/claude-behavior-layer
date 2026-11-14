/* explanation.js — the Explanation tab's own script, on the contract: its
   list, and each document.

   1100 draws both, tools/explanation-page.py's pictured(), and live.js puts
   each change in place. This script draws what the browser alone can: each
   chart, the way it opens, the rail lit by the section in view, the list's
   order, the rail's tab, Export, and Download all. It loads after
   charts.js, and adds a document's states and kinds to its marks. It touches the
   screen only from live.ready and live.drawn, and hears every click from
   the document, so a part 1100 draws later needs no wiring. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const main = () => document.querySelector('main');

  /* The states and the kinds a box wears, added to the charts' marks before
     any draws. A kind has no word of its own: its chart's line names it. */
  try {
    for (const [k, [like, word]] of Object.entries(JSON.parse($('states').textContent))) {
      const s = STD[like], h = HUE[like]; delete STD[k]; STD[k] = s; WORD[k] = word; HUE[k] = h;
    }
    for (const [k, c] of Object.entries(JSON.parse($('kinds').textContent))) {
      STD[k] = `fill:${c}26,stroke:${c},stroke-width:2px,color:#e6e8ee`; HUE[k] = c;
    }
  } catch (e) {}

  /* A chart shrinks to the glass's height only while its labels, 13px,
     stay 10px or more. A taller chart keeps its width's size, and the page
     scrolls past it.
     A flowchart opens in the direction that shows it biggest in its window,
     left to right on a near tie. Its strip still flips it. A chart waits as
     pre.wait, out of the charts' sight, until its direction is known. A
     page in a hidden frame has no width, so nothing is measured until it
     shows. */
  READ = 10 / 13;
  const sized = svg => { const m = svg.match(/viewBox="[-\d.]+ [-\d.]+ ([\d.]+) ([\d.]+)"/);
    return m ? {w: +m[1], h: +m[2]} : null; };
  async function directions() {
    if (!innerWidth) return;
    for (const el of [...document.querySelectorAll('pre.wait')]) {
      const src = el.textContent, m = main();
      const room = el.parentElement.clientWidth, high = (m ? m.clientHeight : innerHeight) - 90;
      const fit = s => s ? Math.min(1, room / s.w, high / s.h >= READ ? high / s.h : 1) : 0;
      if (flow(src) && !DIR[src]) try {
        const lr = sized(await svgOf(src, 'LR')), tb = sized(await svgOf(src, 'TB'));
        DIR[src] = fit(tb) > fit(lr) * 1.05 ? 'TB' : 'LR';
      } catch (e) {}
      el.className = 'mmd';
    }
  }
  const drawAll = () => directions().then(charts);
  addEventListener('resize', () => setTimeout(drawAll, 60));

  /* The rail lights the last section whose top has passed the upper fifth
     of main. */
  function light() {
    const m = main(), links = [...document.querySelectorAll('.ed-rail a')];
    if (!m || !links.length) return;
    const top = m.getBoundingClientRect().top + m.clientHeight * 0.2;
    const secs = [...document.querySelectorAll('.ed-sec')];
    const at = secs.filter(s => s.getBoundingClientRect().top < top).pop() || secs[0];
    links.forEach(a => a.classList.toggle('on', !!at && a.dataset.id === at.id));
  }

  /* The rail's tab, the advisor's: it hides the rail and shows it again, and
     each device keeps which. The document then has the glass, and its
     charts and margin measure again. */
  function rail(open, moved) {
    const adv = $('adv'), tab = $('atab');
    if (!adv) return;
    adv.classList.toggle('open', open);
    document.body.classList.toggle('rail-shut', !open);
    tab.setAttribute('aria-expanded', open);
    try { localStorage.setItem('explanation-rail', open ? '1' : ''); } catch (e) {}
    if (moved) dispatchEvent(new Event('resize'));
  }
  function railKept() {
    let was = '1';
    try { was = localStorage.getItem('explanation-rail') ?? '1'; } catch (e) {}
    rail(!!was, false);
  }

  /* The list's order, on each device: its documents sorted by number, so a
     document 1100 adds lands in its place whichever way the list reads. */
  function order(o) {
    const list = document.querySelector('.ed-list'), pills = [...document.querySelectorAll('#order button')];
    if (!list || !pills.length) return;
    const n = card => parseInt((card.querySelector('.ed-n') || {}).textContent, 10) || 0;
    const cards = [...list.children], sorted = [...cards].sort((a, b) => o === 'up' ? n(a) - n(b) : n(b) - n(a));
    if (sorted.some((c, i) => c !== cards[i])) list.append(...sorted);
    list.dataset.order = o;
    pills.forEach(b => { b.classList.toggle('on', b.dataset.o === o); b.setAttribute('aria-pressed', b.dataset.o === o); });
  }
  const orderKept = () => { let o = 'down'; try { o = localStorage.getItem('explanation-order') === 'up' ? 'up' : 'down'; } catch (e) {} order(o); };

  /* Download all, on this Mac: 1100 makes the folder in Downloads. Refused,
     or on any other device, the press saves the zip, and Download as zip,
     the same press there, leaves. */
  const HERE = ['localhost', '127.0.0.1'].includes(location.hostname);
  const zipOnly = () => { const z = document.querySelector('a.ed-zip'); if (z && !HERE) z.style.display = 'none'; };
  let busy = false, zip = false;
  function downloadAll(all, e) {
    if (!HERE || zip) { zip = false; return; }
    e.preventDefault();
    if (busy) return;
    busy = true;
    const words = all.querySelector('span'), was = words.textContent;
    fetch(all.href, {method: 'POST', redirect: 'manual'}).then(r => {
      if (r.type !== 'opaqueredirect') throw new Error(r.status);
      words.textContent = 'Saved to Downloads';
      all.classList.add('done');
      setTimeout(() => { words.textContent = was; all.classList.remove('done'); busy = false; }, 2500);
    }).catch(() => { busy = false; zip = true; all.click(); });
  }

  /* Export saves the document as one HTML file, for anyone, in any browser.
     It keeps the page's look, and each chart as it draws now: a still
     picture as wide as it draws, never past the glass, its legend and its
     title, and no script. The way back, the copy buttons and each chart's
     strip stay behind. */
  const STILL = 'html, body { height:auto; overflow:visible; } body { display:block; } main { overflow:visible; }'
    + ' .ed-still svg { display:block; margin:0 auto; height:auto; }';
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  function exported(b) {
    const items = $('items'), out = items.cloneNode(true);
    const drawn = [...items.querySelectorAll('.chart')];
    out.querySelectorAll('.chart').forEach((d, i) => {
      const c = drawn[i] && drawn[i].chart, svg = d.querySelector('.cz svg'), still = document.createElement('div');
      still.className = 'ed-still';
      if (svg && c) {
        svg.removeAttribute('height');
        svg.setAttribute('width', '100%');
        svg.style.cssText = `max-width:${Math.ceil(c.nat.w)}px; aspect-ratio:${c.nat.w} / ${c.nat.h};`;
        still.append(svg);
      }
      const lg = d.querySelector('.legend');
      if (lg) still.append(lg);
      d.replaceWith(still);
    });
    out.querySelectorAll('.back, .cp').forEach(e => e.remove());
    const css = [...document.querySelectorAll('style')].filter(s => !s.closest('svg'))
      .map(s => s.textContent).join('\n') + STILL;
    const h = out.querySelector('h1'), title = h && h.lastChild ? h.lastChild.textContent : '';
    const html = '<!doctype html>\n<meta charset="utf-8">\n'
      + '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
      + `<title>${esc(title)}</title>\n<style>${css}</style>\n<main>${out.outerHTML}</main>\n`;
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([html], {type: 'text/html'}));
    a.download = b.dataset.file;
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 60000);
  }

  document.addEventListener('click', e => {
    const link = e.target.closest('.ed-rail a[data-id]');
    if (link) { e.preventDefault(); const s = $(link.dataset.id); if (s) s.scrollIntoView({block: 'start'}); return; }
    if (e.target.closest('#atab')) return rail(!$('adv').classList.contains('open'), true);
    const ex = e.target.closest('#export');
    if (ex) return exported(ex);
    const pill = e.target.closest('#order button');
    if (pill) { order(pill.dataset.o); try { localStorage.setItem('explanation-order', pill.dataset.o); } catch (e) {} return; }
    const all = e.target.closest('a.ed-all');
    if (all) downloadAll(all, e);
  });

  /* The page as 1100 drew it, brought in line with this device. */
  function stand() {
    railKept();
    orderKept();
    zipOnly();
    drawAll();
    light();
  }
  live.ready(() => {
    stand();
    const m = main();
    if (m) m.addEventListener('scroll', light, {passive: true});
  });
  live.drawn(stand);
})();
