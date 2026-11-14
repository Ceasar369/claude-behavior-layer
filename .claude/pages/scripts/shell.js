/* Framed by 1100's home, a page wears home's zoom from its first draw, so
   nothing it lays out moves once home applies it. FRAME follows it after. */
try { if (parent !== window) { const z = +localStorage.getItem('home-zoom');
  if (z && z !== 1) document.documentElement.style.zoom = String(z); } } catch (e) {}
/* When I last typed into a field here: a page never reloads within three
   seconds of it, so a reload never takes a box away mid-word. WATCH and
   home's watch both wait on it. */
addEventListener('input', () => { window.typedAt = Date.now(); }, true);
addEventListener('wheel', e => { if (e.ctrlKey) e.preventDefault(); }, {passive: false});
addEventListener('gesturestart', e => e.preventDefault());
addEventListener('gesturechange', e => e.preventDefault());
(() => {
  let settle = 0;
  addEventListener('resize', () => {
    clearTimeout(settle);
    settle = setTimeout(() => {
      const s = document.body.style;
      s.transform = 'translateZ(0)';
      requestAnimationFrame(() => requestAnimationFrame(() => { s.transform = ''; }));
    }, 150);
  });
})();
