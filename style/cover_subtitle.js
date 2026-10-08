// Replaces the subtitle «دفترچهٔ سؤالات» on the 10th-grade cover image with another text.
// usage: node cover_subtitle.js <cover.jpg> <out.jpg> "<text>"
const fs = require("fs");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { ({ chromium } = require("/opt/node-tools/node_modules/playwright")); }
(async () => {
  const [src, out, text] = process.argv.slice(2);
  const b64 = fs.readFileSync(src).toString("base64");
  // subtitle box in the original: x 794–1024, y 1508–1553 (centre x ≈ 909); ruled line just above at y 1506
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{margin:0}
    #pg{position:relative;width:1819px;height:2573px;overflow:hidden}
    #bg{position:absolute;left:0;top:0}
    #patch{position:absolute;left:640px;top:1490px;width:540px;height:72px;
           background:url(data:image/jpeg;base64,${b64}) -190px -1490px no-repeat}
    #t{position:absolute;left:909px;top:1504px;transform:translateX(-50%);white-space:nowrap;direction:rtl;
       font-family:"Vazirmatn";font-weight:700;font-size:38px;line-height:56px;color:rgb(68,140,210)}
  </style></head><body><div id="pg"><img id="bg" src="data:image/jpeg;base64,${b64}">
  <div id="patch"></div><div id="t">${text}</div></div></body></html>`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1819, height: 2573 } });
  await page.setContent(html);
  await page.evaluate(() => document.fonts.ready);
  await page.locator("#pg").screenshot({ path: out, type: "jpeg", quality: 95 });
  await browser.close();
})();
