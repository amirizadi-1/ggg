// Re-renders the page background with a different exam title.
// usage: node make_background.js <in.png> <out.png> "<title>"
const fs = require("fs");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { ({ chromium } = require("/opt/node-tools/node_modules/playwright")); }
(async () => {
  const [src, out, title] = process.argv.slice(2);
  const b64 = fs.readFileSync(src).toString("base64");
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{margin:0;padding:0}
    #pg{position:relative;width:1786px;height:2526px;background:url(data:image/png;base64,${b64}) no-repeat;background-size:1786px 2526px}
    #cover{position:absolute;left:880px;top:52px;width:560px;height:78px;background:rgb(40,35,96)}
    #t{position:absolute;right:${1786 - 1432}px;top:48px;font-family:"B Nazanin";font-size:54px;color:#fff;direction:rtl;white-space:nowrap;line-height:80px}
  </style></head><body><div id="pg"><div id="cover"></div><div id="t">${title}</div></div></body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1786, height: 2526 } });
  await page.setContent(html);
  await page.evaluate(() => document.fonts.ready);
  await page.locator("#pg").screenshot({ path: out });
  await browser.close();
})();
