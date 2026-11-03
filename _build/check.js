const puppeteer = require('puppeteer-core');
const BASE = 'http://localhost:8000';
const PAGES = [
  ['/index.html', '#hero-map', 'home'],
  ['/programmes/index.html', '#grid .tile', 'browse'],
  ['/programmes/p07.html', '#dofile', 'p07'],
  ['/programmes/p33.html', '#dofile', 'p33'],
  ['/programmes/p01.html', '#dofile', 'p01'],
  ['/programmes/p43.html', '#dofile', 'p43'],
  ['/atlas/index.html', '#atlas-map', 'atlas'],
  ['/insights/index.html', '#c-swim svg', 'insights'],
  ['/datasets/index.html', '#ds-cal svg', 'datasets'],
  ['/toolkit/index.html', '#mde-out .big', 'toolkit'],
  ['/guide/index.html', '.guide-item', 'guide'],
  ['/guide/timing.html', 'table', 'timing'],
  ['/guide/caveats.html', '.guide-item', 'caveats'],
  ['/about/index.html', 'h2', 'about'],
  ['/contribute/index.html', 'h3', 'contribute'],
  ['/shortlist/index.html', '#sl-empty', 'shortlist'],
  ['/404.html', 'h1', '404'],
];
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox', '--disable-dev-shm-usage'] });
  for (const [url, wait, name] of PAGES) {
    for (const vp of [{ width: 1440, height: 900 }, { width: 390, height: 844, isMobile: true, deviceScaleFactor: 1 }]) {
      const p = await b.newPage(); await p.setViewport(vp);
      const errs = [];
      p.on('console', m => { if (m.type() === 'error' && !/api\.github\.com/.test(m.text())) errs.push(m.text().slice(0, 200)); });
      p.on('pageerror', e => errs.push('PAGEERROR ' + e.message.slice(0, 300)));
      p.on('requestfailed', r => { if (!/github/.test(r.url())) errs.push('REQFAIL ' + r.url()); });
      p.on('response', r => { if (r.status() >= 400 && !/github|favicon/.test(r.url())) errs.push('HTTP ' + r.status() + ' ' + r.url()); });
      try { await p.goto(BASE + url, { waitUntil: 'networkidle2', timeout: 20000 }); await p.waitForSelector(wait, { timeout: 6000 }); }
      catch (e) { errs.push('WAIT ' + wait + ' ' + e.message.split('\n')[0]); }
      await new Promise(r => setTimeout(r, 400));
      const info = await p.evaluate(() => ({
        ow: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
        wide: [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.right > document.documentElement.clientWidth + 1 && r.width > 0 && !e.closest('.rail,.table-wrap,.chart,.code,pre,.compare,.opp,.overlay,[hidden]'); }).slice(0, 4).map(e => e.tagName + '.' + e.className.toString().slice(0, 40) + ' ' + Math.round(e.getBoundingClientRect().right)),
      }));
      const tag = vp.width < 500 ? 'm' : 'd';
      console.log(`${name.padEnd(10)} ${tag} ${errs.length ? 'ERR' : 'ok '} overflow=${info.ow > info.cw ? info.ow : 'no'} ${info.wide.join(' | ')}`);
      errs.slice(0, 6).forEach(e => console.log('     ' + e));
      await p.close();
    }
  }
  await b.close();
})();
