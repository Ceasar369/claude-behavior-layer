// An embedded browser, like the Claude app's side panel, may refuse
// navigator.clipboard. So the copy goes through a hidden field first, inside
// the click, and the clipboard API only where that fails.
function copied(b) {
  let box = b.parentNode;
  while (box && !box.querySelector('.txt')) box = box.parentNode;
  const text = box.querySelector('.txt').textContent, word = b.querySelector('span'), was = word.textContent;
  const done = () => {
    b.classList.add('done');
    word.textContent = 'Copied';
    setTimeout(() => { b.classList.remove('done'); word.textContent = was; }, 1500);
  };
  const field = document.createElement('textarea');
  field.value = text;
  field.style.cssText = 'position:fixed;top:0;left:0;opacity:0';
  document.body.appendChild(field);
  field.select();
  const ok = document.execCommand('copy');
  field.remove();
  if (ok) done();
  else navigator.clipboard?.writeText(text).then(done, () => {});
}
