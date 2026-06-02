/**
 * Export any deck to PDF.
 *
 * Usage (from /Slides root, server must be running on port 4000):
 *   node export-pdf.mjs <deck-path>
 *
 * Examples:
 *   node export-pdf.mjs trstd/trstd.html
 *   node export-pdf.mjs myproject/myproject.html
 *
 * Output: <deck-folder>/<deck-name>.pdf
 */

import puppeteer from 'puppeteer';
import { writeFileSync, unlinkSync } from 'fs';
import { resolve, dirname, basename } from 'path';

const arg = process.argv[2];
if (!arg) {
  console.error('Usage: node export-pdf.mjs <deck-path>  e.g. trstd/trstd.html');
  process.exit(1);
}

const BASE   = 'http://localhost:4000';
const URL    = `${BASE}/${arg}`;
const outDir = dirname(resolve(arg));
const stem   = basename(arg, '.html');
const OUT    = `${outDir}/${stem}.pdf`;
const W      = 1920;
const H      = 1080;

console.log(`Exporting: ${URL}`);

const browser = await puppeteer.launch({ headless: 'new' });
const page    = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 2 });
await page.goto(URL, { waitUntil: 'networkidle0' });
await new Promise(r => setTimeout(r, 1500));

const total = await page.evaluate(() => {
  const s = document.querySelector('deck-stage');
  return s ? s.querySelectorAll('section').length : 0;
});
console.log(`Slides: ${total}`);

const shots = [];
for (let i = 0; i < total; i++) {
  await page.evaluate(n => {
    const s = document.querySelector('deck-stage');
    if (s && s.goTo) s.goTo(n);
  }, i);
  await new Promise(r => setTimeout(r, 300));
  const buf = await page.screenshot({ type: 'png', clip: { x: 0, y: 0, width: W, height: H } });
  shots.push(buf.toString('base64'));
  process.stdout.write(`  ${i + 1}/${total}\r`);
}

console.log('\nBuilding PDF...');

const imgTags = shots.map(b64 =>
  `<div class="slide"><img src="data:image/png;base64,${b64}"/></div>`
).join('\n');

const html = `<!doctype html><html><head><meta charset="utf-8"/>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#000; }
  .slide { width:${W}px; height:${H}px; page-break-after:always; overflow:hidden; }
  .slide img { width:100%; height:100%; display:block; }
</style></head><body>${imgTags}</body></html>`;

const tmp = '/tmp/deck-export.html';
writeFileSync(tmp, html);

const p2 = await browser.newPage();
await p2.setViewport({ width: W, height: H });
await p2.goto(`file://${tmp}`, { waitUntil: 'load' });
await p2.pdf({
  path: OUT,
  width: `${W}px`,
  height: `${H}px`,
  printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 },
});

await browser.close();
try { unlinkSync(tmp); } catch {}
console.log(`\nSaved: ${OUT}`);
