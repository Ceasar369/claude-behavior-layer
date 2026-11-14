const NOT_TYPED = 'Not typed', UNANSWERED = '1100 did not answer. Nothing was typed.';
async function typePost(data, to = location.pathname) {
  try {
    const r = await fetch(to, {method: 'POST', redirect: 'manual', body: new URLSearchParams(data)});
    if (r.status === 409) return await r.text();
    return r.ok || r.type === 'opaqueredirect' ? '' : null;
  } catch (e) { return null; }
}
// The sentence a refused press says, until the next press or eight seconds on.
let refusalTimer = 0;
function refusal(said) {
  let p = document.getElementById('refusal');
  if (!p && !said) return;
  if (!p) {
    p = document.createElement('p');
    p.id = 'refusal';
    p.className = 'refusal';
    p.setAttribute('role', 'status');
    document.body.appendChild(p);
  }
  clearTimeout(refusalTimer);
  p.textContent = said;
  p.hidden = !said;
  if (said) refusalTimer = setTimeout(() => { p.hidden = true; }, 8000);
}
async function pressed(b, data, unsent) {
  if ('was' in b.dataset) { b.innerHTML = b.dataset.was; b.title = b.dataset.tip; delete b.dataset.was; }
  b.classList.remove('gone');
  refusal('');
  b.disabled = true;
  const said = await typePost(data);
  b.disabled = false;
  if (said === '') {
    const was = b.innerHTML;
    if (unsent) b.textContent = 'Typed';
    b.classList.add('done');
    setTimeout(() => { b.innerHTML = was; b.classList.remove('done'); }, 1500);
    return said;
  }
  const why = said || UNANSWERED;
  b.dataset.was = b.innerHTML;
  b.dataset.tip = b.title;
  b.textContent = NOT_TYPED;
  b.title = why;
  b.classList.add('gone');
  refusal(why);
  return said;
}
