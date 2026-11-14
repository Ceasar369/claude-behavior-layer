(() => {
  if (parent === window) return;
  const root = document.documentElement;
  root.classList.add('framed');
  const zoom = () => parseFloat(root.style.zoom) || 1;
  const glass = () => root.style.setProperty('--vh', innerHeight / zoom() / 100 + 'px');
  let was = zoom();
  glass();
  addEventListener('resize', glass);
  new MutationObserver(() => {
    if (zoom() === was) return;
    was = zoom();
    glass();
    dispatchEvent(new Event('ws-zoom'));
  }).observe(root, {attributes: true, attributeFilter: ['style']});
  addEventListener('message', e => {
    const d = e.data || {};
    if (e.source !== parent || !d.ws) return;
    if ('slim' in d) root.classList.toggle('slim', !!d.slim);
    if ('zoom' in d) root.style.zoom = d.zoom === 1 ? '' : String(d.zoom);
    if (d.go) dispatchEvent(new Event('ws-' + d.go));
    if (typeof d.draft === 'string') dispatchEvent(new CustomEvent('ws-draft', {detail: d.draft}));
    if (typeof d.mark === 'string') mark(d.mark);
  });
  /* The spot the app chat just changed, bordered until I click or type
     there. The page is often out of view when it lands, so the border
     waits for me: kept for this page through a reload, and put back on
     whatever stands at that spot each time the page redraws it. */
  const css = document.createElement('style');
  css.textContent = '.ws-mark { outline: 3px solid var(--blue, #4b6bd6) !important; outline-offset: 2px; }';
  document.head.appendChild(css);
  const KEPT = 'ws-marks:' + location.pathname;
  let marks = [];
  try { marks = JSON.parse(sessionStorage.getItem(KEPT) || '[]'); } catch (e) {}
  const keep = () => { try { sessionStorage.setItem(KEPT, JSON.stringify(marks)); } catch (e) {} };
  const put = () => marks.forEach(selector => {
    let found = [];
    try { found = document.querySelectorAll(selector); } catch (e) {}
    found.forEach(el => {
      if (el.classList.contains('ws-mark')) return;
      el.classList.add('ws-mark');
      el.scrollIntoView({block: 'nearest'});
    });
  });
  function mark(selector) {
    if (!marks.includes(selector)) { marks.push(selector); keep(); }
    put();
    parent.postMessage({ws: 1, marked: 1}, '*');
  }
  // My click or my typing inside a bordered spot takes its border off.
  const seen = e => {
    const el = e.target.closest && e.target.closest('.ws-mark');
    if (!el) return;
    marks = marks.filter(selector => { try { return !el.matches(selector); } catch (x) { return false; } });
    keep();
    el.classList.remove('ws-mark');
  };
  addEventListener('pointerdown', seen, true);
  addEventListener('keydown', seen, true);
  new MutationObserver(() => { if (marks.length) put(); }).observe(document.body, {childList: true, subtree: true});
  put();
  parent.postMessage({ws: 1, hello: 1}, '*');
})();
