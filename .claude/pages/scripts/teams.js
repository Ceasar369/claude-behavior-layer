/* teams.js — the Teams tab's own script, teams-page.py's.

   A click on a card opens its team in section 2. The open team is mine,
   not 1100's, so a redraw keeps it.

   A pill press posts one launch choice of one team. The tab calls
   teams.py set with it, and 1100 redraws the row from teams.json. */
(() => {
  let open = '';
  const show = () => {
    const cards = [...document.querySelectorAll('.tcard')];
    if (!cards.some(c => c.dataset.seat === open)) open = cards.length ? cards[0].dataset.seat : '';
    for (const c of cards) c.classList.toggle('on', c.dataset.seat === open);
    for (const o of document.querySelectorAll('.opened')) o.classList.toggle('on', o.id === 'team-' + open);
  };
  live.ready(() => {
    show();
    live.drawn(show);
    document.addEventListener('click', e => {
      const card = e.target.closest('.tcard');
      if (card) { open = card.dataset.seat; show(); return; }
      const b = e.target.closest('#rows .pills button[data-k]');
      if (b && !b.disabled) live.pressed(b, {act: 'set', seat: b.dataset.seat, k: b.dataset.k, v: b.dataset.v});
    });
  });
})();
