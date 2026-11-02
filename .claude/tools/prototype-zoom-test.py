#!/usr/bin/env python3
"""Check framed prototype rendering at each dashboard zoom.

No package of the project holds playwright. The Playwright server
.mcp.json pins does, so the test runs inside that npx package, found on
the PATH npx gives it. One pixel is read from a one-pixel screenshot,
inflated with Node's own zlib.

It walks WebKit, then Chromium. One whose build is not installed is
skipped, and named with the command that fetches it.
"""

import importlib.util
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("prototype_page", os.path.join(HERE, "prototype-page.py"))
page = importlib.util.module_from_spec(spec)
spec.loader.exec_module(page)
fixture = {"nn": "05", "tag": "05-test", "subject": "test", "generations": [
    {"generation": 1, "variations": [{"id": "v1", "route": "/test/g1/v1"}]}]}

with open(os.path.join(os.path.dirname(os.path.dirname(HERE)), ".mcp.json")) as f:
    MCP = re.search(r"@playwright/mcp@[\w.-]+", f.read()).group()

TEST = r"""
const path = require('path');
const bin = process.env.PATH.split(':').find(p => p.includes('_npx') && p.endsWith(path.join('node_modules', '.bin')));
const {chromium, webkit} = require(path.join(bin, '..', 'playwright'));
const zlib = require('zlib');
const assert = require('assert');
const fs = require('fs');
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
async function edge(page, selector) {
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
  for (const engine of [webkit, chromium]) {
    if (!fs.existsSync(engine.executablePath())) {
      console.log(`${engine.name()} skipped: its build is not installed. npx -p ${process.env.ZOOM_MCP} playwright install ${engine.name()} fetches it.`);
      continue;
    }
    ran.push(engine.name());
    const browser = await engine.launch({headless:true});
    const context = await browser.newContext({viewport:{width:1000,height:800}});
    const p = await context.newPage();
    await p.route('http://prototype.test/**', route => route.fulfill({contentType:'text/html',body:
      new URL(route.request().url()).pathname === '/' ? html :
      '<style>html,body{margin:0;min-height:100%;background:#000}</style><p style="color:white">variation</p>'}));
    await p.goto('http://prototype.test/');
    for (const z of [.5,.75,1,1.25,2]) {
      await p.evaluate(z => {document.documentElement.style.zoom = String(z); dispatchEvent(new Event('ws-zoom')); show('all')}, z);
      await p.waitForTimeout(100);
      await edge(p, '#items .thumb iframe');
      await p.evaluate(() => show('1/v1'));
      await p.waitForTimeout(100);
      await edge(p, 'section.item.v.on iframe');
      await p.evaluate(() => show('pick'));
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

subprocess.run(["npx", "-y", "-p", MCP, "-c", 'node -e "$ZOOM_TEST"'], input=page.draw(fixture), text=True,
               check=True, env={**os.environ, "ZOOM_TEST": TEST, "ZOOM_MCP": MCP})
