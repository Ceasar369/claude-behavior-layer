function tab(k) {
  k = String(k);
  document.querySelectorAll('.item').forEach(e => e.classList.toggle('on', e.id === 't-' + k));
  document.querySelectorAll('.tab').forEach(e => e.classList.toggle('on', e.dataset.k === k));
  history.replaceState(null, '', '#' + encodeURIComponent(k));
}
