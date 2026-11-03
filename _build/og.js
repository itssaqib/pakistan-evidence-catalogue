const puppeteer = require('puppeteer-core');
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox', '--force-color-profile=srgb'] });
  const p = await b.newPage(); await p.setViewport({ width: 1200, height: 630, deviceScaleFactor: 1 });
  const ids = [null]; for (let i = 1; i <= 67; i++) ids.push('P' + String(i).padStart(2, '0'));
  const OUT = require('path').resolve(__dirname, '..') + '/assets/og/';
  for (const id of ids) {
    await p.goto('http://localhost:8000/_build/render/og.html' + (id ? '?p=' + id : ''), { waitUntil: 'networkidle0' });
    await p.waitForSelector('body[data-ready]'); await new Promise(r => setTimeout(r, 120));
    await p.screenshot({ path: OUT + (id ? id.toLowerCase() : 'home') + '.jpg', type: 'jpeg', quality: 80 });
  }
  await b.close();
})();
