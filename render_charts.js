// Renders the SVG charts listed in a manifest to PNG with Chromium.
// usage: node render_charts.js <manifest.json>
// manifest: [{ "svg": "<path to .svg>", "png": "<output .png>" }, ...]
const fs = require("fs");
const path = require("path");
let chromium;
try { ({ chromium } = require("playwright")); } catch (e) { ({ chromium } = require("/opt/node-tools/node_modules/playwright")); }

(async () => {
  const items = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });
  for (const it of items) {
    const svg = fs.readFileSync(it.svg, "utf8");
    const w = +svg.match(/width="(\d+)"/)[1], h = +svg.match(/height="(\d+)"/)[1];
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(
      `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;padding:0;background:#fff}` +
      `svg{display:block}</style></head><body>${svg}</body></html>`);
    await page.evaluate(() => document.fonts.ready);
    await page.locator("svg").screenshot({ path: it.png });
    process.stdout.write(path.basename(it.png) + " ");
  }
  await browser.close();
  console.log("\ndone", items.length);
})();
