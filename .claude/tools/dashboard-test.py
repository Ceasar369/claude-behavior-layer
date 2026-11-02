#!/usr/bin/env python3
"""Exercise dashboard interactions in an isolated browser.

Run with Node and Playwright on NODE_PATH. No live dashboard is changed.
"""

import ast
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def constants(name, keys):
    with open(os.path.join(HERE, name)) as f:
        tree = ast.parse(f.read())
    return {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
            if isinstance(node, ast.Assign) and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name) and node.targets[0].id in keys}


launch = constants("launch-page.py", {"SCRIPT", "CSS"})
files = constants("sessions-dashboard.py", {"FILES_SCRIPT"})
station = constants("workstation.py", {"HOME"})
shared = constants("../lib/page.py", {"ANYWHERE"})

TEST = r"""
const assert = require('assert');
const { chromium, webkit } = require('playwright');
const fs = require('fs');
const source = JSON.parse(fs.readFileSync(0, 'utf8'));
const data = {layout:[{window:'w',tabs:[{tab:'t',root:{pane:'live',w:1000,h:600,number:'01',label:'live'}}]}],
  starter:'live', rows:[{uid:1,n:'02',name:'first',pos:0,win:'L:w',tab:'L:t',at:{anchor:'p:live',side:'right'}}],
  accounts:[],models:[],efforts:[],order:{order:[],next:0},fallback:'',system:{},after:''};
const launch = '<style>:root {--blue:#60a5fa;--panel:#ddd;--line:#aaa} main{width:1000px}</style>' + source.launch.CSS
  + '<main><div id="save-error" hidden></div><div id="launch-error" hidden></div><div id="map"></div>'
  + '<div id="rows"></div><button id="launch"></button><button id="add"></button><button id="addweb"></button></main>'
  + '<script>window.fail=true;window.post=async f=>{if(window.fail)return false;window.saved=JSON.parse(f.rows);window.savedMoves=JSON.parse(f.moves);window.savedLayouts=JSON.parse(f.layouts);return true};'
  + 'window.fetch=async()=>({json:async()=>structuredClone(window.saved)});</script>'
  + source.launch.SCRIPT.replace('%(data)s',JSON.stringify(data)).replaceAll('%%','%');
const files = '<div class="files"><div class="tree"><div class="scroll"></div></div><div id="fview"></div>'
  + '<div id="fpath"></div><div id="watch"></div><div id="copy-status"></div><button id="copy"></button>'
  + '<button id="shut"></button><button id="again"></button></div>'
  + '<script>class CI {constructor(x){this.data=x} static supports(){return false}};window.ClipboardItem=CI;'
  + 'Object.defineProperty(navigator,"clipboard",{value:{write:async items=>{window.copied=await Object.values(items[0].data)[0]}}});</script>'
  + source.files.FILES_SCRIPT;
const pause = ms => new Promise(r=>setTimeout(r,ms));
async function boxOf(page, selector) {
  await page.locator(selector).waitFor({state:'visible'});
  for (let n=0;n<10;n++) {
    const box=await page.locator(selector).boundingBox();
    if (box) return box;
    await pause(25);
  }
  throw new Error('Could not measure '+selector);
}
(async()=>{
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage();
  const errors=[]; page.on('pageerror', e=>errors.push(e.message));
  await page.setContent(launch);
  await page.evaluate(async()=>{ROWS[0].name='unsaved'; await changed()});
  assert.equal(await page.locator('#save-error').evaluate(el=>el.hidden),false);
  assert.equal(await page.evaluate(()=>ROWS[0].name),'unsaved');
  await page.evaluate(async()=>{window.fail=false; await persist(true)});
  assert.equal(await page.locator('#save-error').evaluate(el=>el.hidden),true);
  assert.equal(await page.evaluate(()=>window.saved[0].name),'unsaved');
  // A lost capture must restore the removed pane without saving a move.
  const lost=await page.evaluate(()=>{
    const map=document.getElementById('map'), capture=map.setPointerCapture;
    map.setPointerCapture=()=>{};
    const box=document.querySelector('[data-anchor="r:1"]').getBoundingClientRect();
    dragStart({pointerId:777,button:0,clientX:box.x+5,clientY:box.y+5},0);
    dragMove({pointerId:777,clientX:box.x+20,clientY:box.y+5,preventDefault(){}});
    const removed=!document.querySelector('[data-anchor="r:1"]');
    map.dispatchEvent(new PointerEvent('lostpointercapture',{pointerId:777,bubbles:true}));
    map.setPointerCapture=capture;
    return {removed,restored:!!document.querySelector('[data-anchor="r:1"]'),idle:drag===null};
  });
  assert.deepStrictEqual(lost,{removed:true,restored:true,idle:true});
  // A new primary press clears a drag whose end never arrived.
  const resumed=await page.evaluate(()=>{
    const map=document.getElementById('map'), capture=map.setPointerCapture;
    map.setPointerCapture=()=>{};
    const box=document.querySelector('[data-anchor="r:1"]').getBoundingClientRect();
    dragStart({pointerId:778,button:0,clientX:box.x+5,clientY:box.y+5},0);
    dragMove({pointerId:778,clientX:box.x+20,clientY:box.y+5,preventDefault(){}});
    window.dispatchEvent(new PointerEvent('pointerdown',{pointerId:779,isPrimary:true,button:0,bubbles:true,cancelable:true}));
    map.setPointerCapture=capture;
    return {restored:!!document.querySelector('[data-anchor="r:1"]'),idle:drag===null};
  });
  assert.deepStrictEqual(resumed,{restored:true,idle:true});
  let box=await page.locator('[data-anchor="p:live"]').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
  await page.mouse.down();
  await page.mouse.move(box.x+box.width/2+10,box.y+box.height/2);
  box=await page.locator('[data-anchor="r:1"]').boundingBox();
  await page.mouse.move(box.x+box.width*.95,box.y+box.height/2);
  await page.mouse.up();
  await page.waitForFunction(()=>window.savedMoves && window.savedMoves.length===1);
  assert.deepStrictEqual(await page.evaluate(()=>window.savedMoves[0]),
    {win:'L:w',tab:'L:t',source:'p:live',anchor:'r:1',side:'right'});
  assert.equal(await page.evaluate(()=>[...document.querySelectorAll('#map .pane')].map(n=>n.dataset.anchor).join(',')),'r:1,p:live');
  assert.deepStrictEqual(await page.evaluate(()=>window.savedLayouts[0].root),
    {split:'columns',children:[{ref:'r:1'},{ref:'p:live'}]});
  box=await page.locator('[data-anchor="r:1"]').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height/2);
  await page.mouse.down();
  await page.mouse.move(box.x+box.width/2+10,box.y+box.height/2);
  box=await page.locator('[data-anchor="p:live"]').boundingBox();
  await page.mouse.move(box.x+box.width/2,box.y+box.height*.95);
  await page.mouse.up();
  await page.waitForFunction(()=>window.savedMoves && window.savedMoves.length===2);
  assert.deepStrictEqual(await page.evaluate(()=>window.savedLayouts[0].root),
    {split:'rows',children:[{ref:'p:live'},{ref:'r:1'}]});
  await page.getByText('Undo move').click();
  await page.waitForFunction(()=>window.savedMoves && window.savedMoves.length===1);
  await page.getByText('Undo move').click();
  await page.waitForFunction(()=>window.savedMoves && window.savedMoves.length===0);

  // A touch must capture the stable map before the touched pane is redrawn.
  const touchData=structuredClone(data);
  touchData.rows.push({uid:2,n:'03',name:'second',pos:1,win:'L:w',tab:'L:t',at:{anchor:'r:1',side:'down'}});
  const touchContext=await browser.newContext({viewport:{width:1200,height:900},hasTouch:true,isMobile:true});
  const touch=await touchContext.newPage(); touch.on('pageerror',e=>errors.push(e.message));
  await touch.setContent(launch.replace(JSON.stringify(data),JSON.stringify(touchData)));
  let touchBox=await boxOf(touch,'[data-anchor="r:2"]');
  await touch.touchscreen.tap(touchBox.x+touchBox.width/2,touchBox.y+touchBox.height/2);
  assert.equal(await touch.evaluate(()=>ROWS[active].uid),2);
  await touch.evaluate(()=>{
    window.captureBeforeRedraw=null;
    document.getElementById('map').addEventListener('gotpointercapture',e=>{
      if(e.target.id==='map') window.captureBeforeRedraw=!!document.querySelector('[data-anchor="r:2"]');
    });
    window.fail=false;
  });
  const touchClient=await touchContext.newCDPSession(touch);
  touchBox=await boxOf(touch,'[data-anchor="r:2"]');
  await touchClient.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:touchBox.x+touchBox.width/2,y:touchBox.y+touchBox.height/2}]});
  await touchClient.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:touchBox.x+touchBox.width/2+10,y:touchBox.y+touchBox.height/2}]});
  const liveBox=await boxOf(touch,'[data-anchor="p:live"]');
  await touchClient.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:liveBox.x+liveBox.width*.9,y:liveBox.y+liveBox.height/2}]});
  await touchClient.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await touch.waitForFunction(()=>window.saved && window.saved.at(-1).uid===2);
  assert.equal(await touch.evaluate(()=>window.captureBeforeRedraw),true);
  assert.equal(await touch.evaluate(()=>drag===null),true);
  assert.deepStrictEqual(await touch.evaluate(()=>window.saved.at(-1).at),{anchor:'p:live',side:'right'});
  await touchContext.close();

  const fpage = await browser.newPage();
  fpage.on('pageerror', e=>errors.push(e.message));
  await fpage.route('http://dashboard.test/**',async route=>{
    const url=new URL(route.request().url());
    if(url.pathname==='/files') return route.fulfill({contentType:'text/html',body:files});
    if(url.pathname==='/text/01/slow.md') { await pause(250); return route.fulfill({body:'<div class="picked" data-copy="text" data-path="slow"></div>old'}); }
    if(url.pathname==='/text/01/fast.md') return route.fulfill({body:'<div class="picked" data-copy="text" data-path="fast"></div>new'});
    if(url.pathname==='/text/01/file.bin') return route.fulfill({body:'<div class="picked" data-copy="file" data-path="binary"></div>'});
    if(url.pathname==='/text/01/picture.png') return route.fulfill({body:'<div class="picked" data-copy="image" data-path="picture"></div>'});
    if(url.pathname==='/raw/01/fast.md') return route.fulfill({body:'a'.repeat(500001)});
    if(url.pathname==='/raw/01/picture.png') return route.fulfill({contentType:'image/png',body:Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+pZSsAAAAASUVORK5CYII=','base64')});
    return route.fulfill({body:''});
  });
  await fpage.goto('http://dashboard.test/files');
  await fpage.evaluate(()=>{
    const tree=document.querySelector('.tree .scroll');
    tree.innerHTML='<a class="frow file" data-f="01/slow.md" href="#">slow</a><a class="frow file" data-f="01/fast.md" href="#">fast</a><a class="frow file" data-f="01/file.bin" href="#">binary</a><a class="frow file" data-f="01/picture.png" href="#">picture</a>';
  });
  await fpage.locator('[data-f="01/slow.md"]').click();
  await fpage.locator('[data-f="01/fast.md"]').click();
  await pause(350);
  assert.equal(await fpage.locator('#fview').innerText(),'new');
  await fpage.locator('#copy').click();
  await fpage.waitForFunction(()=>window.copied);
  assert.equal((await fpage.evaluate(()=>window.copied.text())).length,500001);
  await fpage.locator('[data-f="01/picture.png"]').click();
  await fpage.evaluate(()=>{window.copied=null});
  await fpage.locator('#copy').click();
  await fpage.waitForFunction(()=>window.copied);
  assert.equal(await fpage.evaluate(()=>window.copied.type),'image/png');
  await fpage.locator('[data-f="01/file.bin"]').click();
  await fpage.locator('#copy').click();
  assert.match(await fpage.locator('#copy-status').innerText(),/cannot copy/);

  const rail = source.station.HOME.match(/function drawRail\(\) \{[\s\S]*?\n\}/)[0];
  const rpage = await browser.newPage();
  rpage.on('pageerror', e=>errors.push(e.message));
  await rpage.setContent('<div id="pin"><button>Skills</button></div><div id="tools"><button data-nn="02">02</button></div>'
    + '<script>const $=id=>document.getElementById(id), view={kind:"hub"}, ICONS={skills:""}, nb={hidden:false};'
    + 'function tools(){return `<button data-nn="02">02</button>`} function edges(){};' + rail + '</script>');
  await rpage.locator('[data-nn="02"]').focus();
  await rpage.evaluate(()=>drawRail());
  assert.equal(await rpage.evaluate(()=>document.activeElement.dataset.nn),'02');

  // Chrome must insert the text carried by the paste event immediately.
  // Wispr can change the clipboard before Chrome's default insertion.
  const pastePage=await browser.newPage();
  await pastePage.setContent('<textarea id="entry">start middle end</textarea><input id="other">'
    + source.shared.ANYWHERE + '<script>anywhere(()=>false);window.inputs=0;'
    + 'document.querySelector("textarea").addEventListener("input",()=>inputs++);</script>');
  const pasted=await pastePage.evaluate(()=>{
    const t=document.querySelector('textarea');t.focus();t.setSelectionRange(6,12);
    const data=new DataTransfer();data.setData('text/plain','replacement');
    const event=new ClipboardEvent('paste',{bubbles:true,cancelable:true,clipboardData:data});
    t.dispatchEvent(event);data.clearData();
    return {text:t.value,prevented:event.defaultPrevented,inputs,caret:t.selectionStart};
  });
  assert.deepStrictEqual(pasted,{text:'start replacement end',prevented:true,inputs:1,caret:17});
  assert.equal(await pastePage.evaluate(()=>document.execCommand('undo')),true);
  assert.equal(await pastePage.locator('#entry').inputValue(),'start middle end');
  const other=await pastePage.evaluate(()=>{
    const t=document.querySelector('#other');t.focus();const data=new DataTransfer();data.setData('text/plain','x');
    const e=new ClipboardEvent('paste',{bubbles:true,cancelable:true,clipboardData:data});t.dispatchEvent(e);return e.defaultPrevented;
  });
  assert.equal(other,false);
  assert.deepStrictEqual(errors,[]);
  await browser.close();
  const safari=await webkit.launch({headless:true});
  const webkitPage=await safari.newPage();
  await webkitPage.setContent('<textarea id="entry"></textarea>'+source.shared.ANYWHERE+'<script>anywhere(()=>false)</script>');
  assert.equal(await webkitPage.evaluate(()=>{
    const t=document.querySelector('textarea');t.focus();const data=new DataTransfer();data.setData('text/plain','x');
    const e=new ClipboardEvent('paste',{bubbles:true,cancelable:true,clipboardData:data});t.dispatchEvent(e);return e.defaultPrevented;
  }),false);
  await webkitPage.close();
  for(const viewport of [{width:390,height:844},{width:844,height:390}]){
    const ctx=await safari.newContext({viewport,isMobile:true,hasTouch:true});
    const mobile=await ctx.newPage(); mobile.on('pageerror',e=>errors.push(e.message));
    await mobile.setContent('<meta name="viewport" content="width=device-width,initial-scale=1">'+launch);
    await mobile.evaluate(()=>{window.fail=false;document.querySelector('main').style.width='100%'});
    let b=await boxOf(mobile,'[data-anchor="r:1"]');
    await mobile.mouse.move(b.x+b.width/2,b.y+b.height/2);await mobile.mouse.down();
    await mobile.mouse.move(b.x+b.width/2+10,b.y+b.height/2);
    b=await boxOf(mobile,'[data-anchor="p:live"]');
    await mobile.mouse.move(b.x+b.width*.9,b.y+b.height/2);await mobile.mouse.up();
    await mobile.waitForFunction(()=>window.saved && window.saved[0].at.side==='right');
    assert.equal(await mobile.evaluate(()=>drag===null),true);
    await ctx.close();
  }
  // Home-screen iPhones keep controls clear of the status-bar blur.
  const homeStyle=source.station.HOME.match(/<style>([\s\S]*?)<\/style>/)[0];
  const fit=source.station.HOME.match(/function fit\(\) \{[\s\S]*?\n\}/)[0];
  for (const standalone of [true,false]) {
    const ctx=await safari.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
    const mobile=await ctx.newPage();
    await mobile.addInitScript(standalone => Object.defineProperty(navigator,'standalone',{value:standalone}),standalone);
    await mobile.route('http://home.test/',route=>route.fulfill({contentType:'text/html',body:
      '<meta name="viewport" content="width=device-width,initial-scale=1">'+homeStyle+
      '<aside class="rail"></aside><main></main><script>'+fit+';fit();addEventListener("resize",fit)</script>'}));
    await mobile.goto('http://home.test/');
    assert.equal(await mobile.evaluate(()=>parseFloat(getComputedStyle(document.body).paddingTop)),standalone?24:0);
    await mobile.setViewportSize({width:844,height:390});
    await mobile.waitForFunction(()=>innerWidth>innerHeight);
    assert.equal(await mobile.evaluate(()=>parseFloat(getComputedStyle(document.body).paddingTop)),0);
    await ctx.close();
  }
  await safari.close();
  assert.deepStrictEqual(errors,[]);
  console.log('Touch, dragging, saves, files, paste, focus, and iPhone clearance passed.');
})().catch(e=>{console.error(e);process.exit(1)});
"""

result = subprocess.run(["node", "-e", TEST], input=json.dumps({"launch": launch, "files": files, "station": station,
                                                                "shared": shared}),
                        text=True, check=False)
sys.exit(result.returncode)
