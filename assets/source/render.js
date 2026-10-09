const { chromium } = require('playwright');
const D = __dirname;
const jobs = [['hero',1000,520,true],['collage',1000,640,true],['how-it-works',1000,470,true],['og',1200,630,false]];
(async () => {
  const b = await chromium.launch({ headless: true });
  for (const [n,w,h,t] of jobs) {
    const p = await b.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: t ? 2 : 1 });
    await p.route('**/*', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.goto('file://' + D + '/' + n + '.html'); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
    await p.screenshot({ path: D + '/' + n + '.png', omitBackground: t, clip: { x: 0, y: 0, width: w, height: h } });
    await p.close();
  }
  await b.close(); console.log('rendered');
})();