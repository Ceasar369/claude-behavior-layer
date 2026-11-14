#!/usr/bin/env python3
"""mark-test.py — the border on the spot the app chat just changed, on stand-ins.

Stand-in session 05's Transcript tab, drawn from lib/trial.py's made-up
folder, sits in a frame as 1100's home frames it, out of view. Home's two
messages for a draft_reply reach it there: the draft, then its mark,
"#words". Five seconds on, the tab comes into view. It passes when the
box holds the draft and still wears the border, a blue outline, and loses
it once I click in the box. Both engines, WebKit and Chromium. Its
screenshot, the tab just in view, lands in the folder it prints.

  mark-test.py
"""

import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lib"))
SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pages", "scripts")
import page  # noqa: E402
import trial  # noqa: E402

SCRIPT = r"""
(async () => {
const dir = process.env.MARK_DIR;
for (const engine of engines) {
  const b = await engine.launch(), p = await b.newPage();
  await p.goto('file://' + dir + '/home.html');
  const f = await (await p.waitForSelector('iframe', {state: 'attached'})).contentFrame();
  await f.waitForSelector('#words', {state: 'attached'});
  await wait(300);
  await p.evaluate(() => {
    const w = document.querySelector('iframe').contentWindow;
    w.postMessage({ws: 1, draft: 'Fold in item 3.'}, '*');
    w.postMessage({ws: 1, mark: '#words'}, '*');
  });
  await wait(5000);
  await p.evaluate(() => { document.querySelector('iframe').style.display = ''; });
  await wait(300);
  const shown = await f.evaluate(() => {
    const w = document.querySelector('#words');
    return {value: w.value, marked: w.classList.contains('ws-mark'), outline: getComputedStyle(w).outlineColor};
  });
  await p.screenshot({path: dir + '/' + engine.name() + '-border.png'});
  await f.click('#words');
  await wait(200);
  const after = await f.evaluate(() => document.querySelector('#words').classList.contains('ws-mark'));
  console.log(JSON.stringify({engine: engine.name(), ...shown, after}));
  await b.close();
}
})().catch(e => { console.error(e); process.exit(1); });
"""


def main() -> None:
    out = tempfile.mkdtemp(prefix="mark-test-")
    with trial.world():
        html = page.tool("transcript-page").drawn("05")
    # Its scripts, as 1100 serves them at /pages/, beside it.
    os.makedirs(os.path.join(out, "pages"))
    for name in re.findall(r'src="/pages/([\w.-]+\.js)', html):
        shutil.copy(os.path.join(SCRIPTS, name), os.path.join(out, "pages", name))
    with open(os.path.join(out, "transcript.html"), "w") as f:
        f.write(re.sub(r'src="/pages/', 'src="pages/', html))
    with open(os.path.join(out, "home.html"), "w") as f:
        f.write('<!doctype html><body style="margin:0"><iframe src="transcript.html" '
                'style="width:900px;height:700px;border:0;display:none"></iframe></body>')
    r = trial.browsers(SCRIPT, {"MARK_DIR": out})
    print(r.stdout.strip() or r.stderr.strip()[-2000:])
    results = [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]
    ok = bool(results) and all(x["value"] == "Fold in item 3." and x["marked"] and not x["after"] for x in results)
    print(("OK" if ok else "FAILED") + f": screenshots in {out}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
