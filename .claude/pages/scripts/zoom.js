function zoomer(tools, win, chart) {
  const STEP = 1.25, z = k => tools.querySelector('[data-z=' + k + ']'), pct = tools.querySelector('.pct');
  const paint = () => {
    const s = chart.scale(), [lo, hi] = s ? chart.bounds() : [0, 0];
    z('out').disabled = !s || s <= lo;
    z('in').disabled = !s || s >= hi;
    z('fit').disabled = !s || chart.fitted();
    pct.textContent = s ? Math.round(s * 100) + '%' : '';
  };
  // A size a hair from a bound lands on it, so a step back out ends fitted.
  const go = (s, at) => {
    const [lo, hi] = chart.bounds();
    chart.to(s <= lo * (1 + 1e-9) ? lo : s >= hi * (1 - 1e-9) ? hi : s, at);
    paint();
  };
  const point = e => { const r = win.getBoundingClientRect(); return {x: e.clientX - r.left, y: e.clientY - r.top}; };
  z('out').onclick = () => { if (chart.scale()) go(chart.scale() / STEP, null); };
  z('in').onclick = () => { if (chart.scale()) go(chart.scale() * STEP, null); };
  z('fit').onclick = () => { if (chart.scale()) { chart.fit(); paint(); } };
  // While a gesture runs, its Ctrl wheel is ignored, so nothing zooms twice.
  let pinch = 0;
  win.addEventListener('wheel', e => {
    if (!e.ctrlKey) return;
    e.preventDefault();
    if (pinch || !chart.scale()) return;
    const unit = e.deltaMode === 1 ? 16 : e.deltaMode === 2 ? win.clientHeight : 1;
    go(chart.scale() * Math.exp(-Math.max(-50, Math.min(50, e.deltaY * unit)) * 0.01), point(e));
  }, {passive: false});
  win.addEventListener('gesturestart', e => { e.preventDefault(); pinch = chart.scale(); });
  win.addEventListener('gesturechange', e => { e.preventDefault(); if (pinch) go(pinch * e.scale, point(e)); });
  win.addEventListener('gestureend', e => { e.preventDefault(); pinch = 0; });
  return paint;
}
