#!/usr/bin/env python3
"""Check framed prototype rendering at each dashboard zoom.

lib/trial.py's browsers() runs it, with the Playwright .mcp.json pins in
reach. One pixel is read from a one-pixel screenshot, inflated with
Node's own zlib. The page is drawn on the contract, its scripts served
from .claude/pages/.

It walks WebKit, then Chromium. One whose build is not installed is
skipped, and named.
"""

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lib"))
import trial  # noqa: E402

spec = importlib.util.spec_from_file_location("prototype_page", os.path.join(HERE, "prototype-page.py"))
page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page)
fixture = {"nn": "05", "tag": "05-test", "subject": "test", "live": "", "generations": [
    {"generation": 1, "variations": [{"id": "v1", "route": "/test/g1/v1"}]}]}
PAGES = os.path.join(os.path.dirname(HERE), "pages", "scripts")

TEST = r"""
const zlib = require('zlib');
const assert = require('assert');
const html = fs.readFileSync(0, 'utf8');
// A one-pixel PNG's red, green and blue: its one row is its filter byte,
// then the pixel, whatever the filter, since nothing sits left or above.
function pixel(png) {
  const idat = [];
  let depth = 0;
  for (let at = 8; at < png.length;) {
    const size = png.readUInt32BE(at), type = png.toString('ascii', at + 4, at + 8);
    if (type === 'IHDR') depth = png[at + 16];
    if (type === 'IDAT') idat.push(png.subarray(at + 8, at + 8 + size));
    at += 12 + size;
  }
  assert(depth === 8, 'screenshot is not 8 bits deep');
  return [...zlib.inflateSync(Buffer.concat(idat)).subarray(1, 4)];
}
// A frame shows white until its variation loads, and the page's script
// shows each view, and so starts its frames' loads, after the page loads.
// So the frame's own variation is waited for, then the page's script has
// zoomed it on its load.
async function edge(page, selector) {
  await page.waitForFunction(s => {
    const d = document.querySelector(s)?.contentDocument;
    return !!d && d.readyState === 'complete' && /variation/.test(d.body?.textContent || '');
  }, selector, {timeout: 10000});
  await page.waitForTimeout(100);
  const box = await page.locator(selector).boundingBox();
  assert(box && box.width > 15 && box.height > 15, selector + ' must be visible');
  const size = page.viewportSize();
  const x = Math.floor(box.x + box.width * .9), y = Math.floor(box.y + box.height * .2);
  assert(x >= 0 && y >= 0 && x < size.width && y < size.height, 'sample must be visible');
  const [r, g, b] = pixel(await page.screenshot({clip: {x, y, width: 1, height: 1}}));
  assert(r < 30 && g < 30 && b < 30, selector + ' has a white gap at ' + x + ',' + y);
}
(async () => {
  const ran = [];
  for (const engine of engines) {
    ran.push(engine.name());
    const browser = await engine.launch({headless:true});
    const context = await browser.newContext({viewport:{width:1000,height:800}});
    const p = await context.newPage();
    await p.route('http://prototype.test/**', route => {
      const at = new URL(route.request().url()).pathname;
      // The page's own scripts, live.js and prototype.js, as 1100 serves them.
      if (at.startsWith('/pages/'))
        return route.fulfill({contentType:'text/javascript',body:fs.readFileSync(path.join(process.env.ZOOM_PAGES, path.basename(at)))});
      return route.fulfill({contentType:'text/html',body: at === '/' ? html :
        '<style>html,body{margin:0;min-height:100%;background:#000}</style><p style="color:white">variation</p>'});
    });
    await p.goto('http://prototype.test/');
    await p.waitForSelector('#items section.item.on');
    // The page's script is enclosed: a view is named by the hash, as the app door names it.
    const view = k => p.evaluate(k => { location.hash = k; }, k);
    for (const z of [.5,.75,1,1.25,2]) {
      await p.evaluate(z => {document.documentElement.style.zoom = String(z); dispatchEvent(new Event('ws-zoom'))}, z);
      await view('all');
      await p.waitForTimeout(100);
      await edge(p, '#items .thumb iframe');
      await view('1/v1');
      await p.waitForTimeout(100);
      await edge(p, 'section.item.v.on iframe');
      await view('pick');
      await p.waitForTimeout(100);
      await edge(p, '#pf');
    }
    await browser.close();
  }
  assert(ran.length, 'no browser build is installed');
  console.log(`Prototype thumbnails, full views, and picks fill their frames in ${ran.join(' and ')}.`);
// A failure leaves its browser open, which would hold node forever.
})().catch(e => {console.error(e);process.exit(1)});
"""

r = trial.browsers(TEST, env={"ZOOM_PAGES": PAGES}, stdin=page.drawn_page(fixture))
print(r.stdout, end="")
print(r.stderr, end="", file=sys.stderr)
sys.exit(r.returncode)
