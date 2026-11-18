const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [dir, outdir] = process.argv.slice(2);
  const meta = JSON.parse(fs.readFileSync(path.join(dir, 'meta.json')));
  const b = await chromium.launch(); 
  for (const [k, [w, h]] of Object.entries(meta)) {
    const p = await b.newPage({ viewport: { width: Math.ceil(w), height: Math.ceil(h) }, deviceScaleFactor: 2 });
    await p.setContent(`<html><body style="margin:0">${fs.readFileSync(path.join(dir, k + '.svg'))}</body></html>`);
    await p.screenshot({ path: path.join(outdir, k + '.png'), clip: { x: 0, y: 0, width: w, height: h } });
    await p.close();
  }
  await b.close();
})();
