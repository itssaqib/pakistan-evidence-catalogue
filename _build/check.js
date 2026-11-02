// Render pages in headless Chrome and report console errors + rendered row counts.
const puppeteer = require('puppeteer-core');

const BASE = 'http://localhost:8742';
const PAGES = [
  { url: '/',                       wait: '#chart-era rect', label: 'Home' },
  { url: '/programmes/',            wait: '#pbody tr td.id', label: 'Programme index' },
  { url: '/programmes/p35.html',    wait: '#tl circle',      label: 'Programme p35' },
  { url: '/programmes/p01.html',    wait: 'table.data tbody tr', label: 'Programme p01' },
  { url: '/matrix/',                wait: '#mbody tr td.id', label: 'Matrix' },
  { url: '/outcomes/',              wait: '#obody tr td.id', label: 'Outcomes' },
  { url: '/datasets/',              wait: '#dbody tr td.id', label: 'Datasets' },
  { url: '/methods/',               wait: 'table.data tbody tr', label: 'Methods' },
  { url: '/timing/',                wait: 'table.data tbody tr', label: 'Timing' },
  { url: '/caveats/',               wait: 'h3',              label: 'Caveats' },
  { url: '/data/',                  wait: '.dl-file',        label: 'Downloads' },
  { url: '/contribute/',            wait: 'h3',              label: 'Contribute' },
  { url: '/about/',                 wait: 'h2',              label: 'About' },
];

(async () => {
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/google-chrome',
    headless: 'new',
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  let failures = 0;

  for (const p of PAGES) {
    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 900 });
    const errs = [];
    // Google Fonts is unreachable from this sandbox; the site has local fallbacks.
    const isFontNoise = t => /ERR_TUNNEL_CONNECTION_FAILED|fonts\.g/.test(t);
    page.on('console', m => {
      if (m.type() === 'error' && !isFontNoise(m.text())) errs.push(m.text());
    });
    page.on('pageerror', e => errs.push('PAGEERROR: ' + e.message));
    page.on('requestfailed', r => {
      const u = r.url();
      if (!u.includes('fonts.g')) errs.push('REQFAIL: ' + u);
    });

    try {
      await page.goto(BASE + p.url, { waitUntil: 'networkidle2', timeout: 20000 });
      await page.waitForSelector(p.wait, { timeout: 8000 });
    } catch (e) {
      errs.push('WAIT FAILED for "' + p.wait + '": ' + e.message.split('\n')[0]);
    }

    const info = await page.evaluate(() => {
      const rows = document.querySelectorAll('table.data tbody tr').length;
      const count = document.querySelector('#count');
      const h1 = document.querySelector('h1');
      const facets = document.querySelectorAll('.facet').length;
      const svgKids = document.querySelectorAll('svg.chart *, svg.timeline *').length;
      return {
        rows,
        countText: count ? count.textContent.trim() : '',
        h1: h1 ? h1.textContent.trim().slice(0, 48) : '(none)',
        facets,
        svgKids,
        scrollW: document.documentElement.scrollWidth,
        clientW: document.documentElement.clientWidth,
      };
    });

    const overflow = info.scrollW > info.clientW + 2;
    const ok = errs.length === 0 && !overflow;
    if (!ok) failures++;
    console.log(
      (ok ? 'OK  ' : 'FAIL') + ' ' + p.label.padEnd(18) +
      ' rows=' + String(info.rows).padEnd(5) +
      ' facets=' + String(info.facets).padEnd(3) +
      ' svg=' + String(info.svgKids).padEnd(5) +
      (info.countText ? ' [' + info.countText + ']' : '') +
      (overflow ? ' H-OVERFLOW ' + info.scrollW + '>' + info.clientW : '')
    );
    errs.slice(0, 4).forEach(e => console.log('      ! ' + e.slice(0, 150)));
    await page.close();
  }

  // Mobile check
  const m = await browser.newPage();
  await m.setViewport({ width: 390, height: 800, isMobile: true });
  for (const u of ['/', '/programmes/', '/programmes/p13.html', '/matrix/']) {
    await m.goto(BASE + u, { waitUntil: 'networkidle2' });
    const r = await m.evaluate(() => ({
      sw: document.documentElement.scrollWidth,
      cw: document.documentElement.clientWidth,
      navHidden: getComputedStyle(document.querySelector('.mainnav')).display === 'none',
      toggleShown: getComputedStyle(document.querySelector('.navtoggle')).display !== 'none',
    }));
    const bad = r.sw > r.cw + 2;
    if (bad) failures++;
    console.log((bad ? 'FAIL' : 'OK  ') + ' mobile ' + u.padEnd(24) +
      ' width=' + r.sw + '/' + r.cw + ' nav-collapsed=' + (r.navHidden && r.toggleShown));
  }
  await m.close();

  // Interaction check: filter + sort + search on the programme index
  const i = await browser.newPage();
  await i.setViewport({ width: 1280, height: 900 });
  await i.goto(BASE + '/programmes/', { waitUntil: 'networkidle2' });
  await i.waitForSelector('#pbody tr td.id');
  const before = await i.$$eval('#pbody tr', r => r.length);
  await i.click('input[data-facet="quality_label"][value="High"]');
  await new Promise(r => setTimeout(r, 300));
  const afterFacet = await i.$$eval('#pbody tr', r => r.length);
  await i.type('#search', 'land');
  await new Promise(r => setTimeout(r, 400));
  const afterSearch = await i.$$eval('#pbody tr', r => r.length);
  const chips = await i.$$eval('.chip', c => c.length);
  await i.click('th[data-sort="n_outcomes"]');
  await new Promise(r => setTimeout(r, 200));
  const sortAttr = await i.$eval('th[data-sort="n_outcomes"]', t => t.getAttribute('aria-sort'));
  console.log(`OK   interaction      all=${before} -> High=${afterFacet} -> +"land"=${afterSearch}` +
              ` chips=${chips} sort=${sortAttr}`);
  if (!(afterFacet < before && afterSearch <= afterFacet && chips >= 2 && sortAttr)) {
    console.log('      ! interaction assertions failed'); failures++;
  }
  await i.close();

  // Deep-link check
  const dl = await browser.newPage();
  await dl.setViewport({ width: 1280, height: 900 });
  await dl.goto(BASE + '/programmes/?quality_label=High', { waitUntil: 'networkidle2' });
  await dl.waitForSelector('#pbody tr td.id');
  const dlRows = await dl.$$eval('#pbody tr', r => r.length);
  const dlChecked = await dl.$eval('input[data-facet="quality_label"][value="High"]', c => c.checked);
  console.log('OK   deep link        ?quality_label=High -> rows=' + dlRows + ' checkbox=' + dlChecked);
  if (!dlChecked || dlRows === 0) { console.log('      ! deep link failed'); failures++; }
  await dl.close();

  await browser.close();
  console.log(failures === 0 ? '\nALL CHECKS PASSED' : `\n${failures} CHECK(S) FAILED`);
  process.exit(failures === 0 ? 0 : 1);
})();
