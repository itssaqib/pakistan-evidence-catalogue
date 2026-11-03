const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox', '--force-color-profile=srgb'] });
  const p = await b.newPage(); await p.setViewport({ width: 1400, height: 800, deviceScaleFactor: 2 });
  for (const f of ['density', 'footprints']) {
    await p.goto('http://localhost:8000/_build/render/fig.html?f=' + f, { waitUntil: 'networkidle0' });
    await p.waitForSelector('body[data-ready]'); await new Promise(r => setTimeout(r, 200));
    const el = await p.$('#root'); await el.screenshot({ path: require('path').resolve(__dirname, '..') + '/paper/fig-' + f + '.png' });
  }
  await b.close();
})();
