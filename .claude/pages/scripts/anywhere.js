function anywhere(typeIn, tabIn) {
  if (matchMedia('(hover: none) and (pointer: coarse)').matches) return;
  const field = e => e.target.closest && e.target.closest('input, textarea, [contenteditable]');
  const chrome = /(?:Chrome|Chromium)\//.test(navigator.userAgent);
  window.typeIn = typeIn;
  if (tabIn) window.tabIn = tabIn;
  addEventListener('keydown', e => {
    if (field(e) || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === 'Tab' && !e.shiftKey) { if (tabIn && tabIn()) e.preventDefault(); return; }
    if (e.key.length === 1 && e.key !== ' ' && typeIn(e.key)) e.preventDefault();
  });
  addEventListener('paste', e => {
    const t = field(e), clip = e.clipboardData;
    if (!e.defaultPrevented && chrome && t && t.matches('textarea:not(:disabled):not([readonly])')
        && clip && !clip.files.length) {
      const text = clip.getData('text/plain');
      if (text && document.execCommand('insertText', false, text)) { e.preventDefault(); return; }
    }
    if (!e.defaultPrevented && !field(e) && typeIn(e.clipboardData.getData('text'))) e.preventDefault();
  });
}
