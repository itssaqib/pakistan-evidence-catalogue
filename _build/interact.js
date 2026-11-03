const puppeteer = require('puppeteer-core');
const B = 'http://localhost:8000';
const sleep = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const b = await puppeteer.launch({ executablePath: process.env.CHROME || '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
  const p = await b.newPage(); await p.setViewport({ width: 1440, height: 900 });
  const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error' && !/github/.test(m.text())) errs.push(m.text()); });
  // ATLAS click
  await p.goto(B + '/atlas/index.html', { waitUntil: 'networkidle2' }); await sleep(500);
  const pt = await p.evaluate(() => { const d = PEC_GEO.d.find(x => x.id === 'pb-lahore'); const c = document.getElementById('atlas-map'); const r = c.getBoundingClientRect(); const m = c.width / r.width; const map = c; return { vb: PEC_GEO.vb, c: d.c, r: [r.left, r.top, r.width, r.height] }; });
  const s = Math.min(pt.r[2] / pt.vb[0], pt.r[3] / pt.vb[1]); const ox = (pt.r[2] - pt.vb[0] * s) / 2, oy = (pt.r[3] - pt.vb[1] * s) / 2;
  await p.mouse.click(pt.r[0] + ox + pt.c[0] * s, pt.r[1] + oy + pt.c[1] * s); await sleep(300);
  console.log('ATLAS panel:', (await p.$eval('#atlas-panel', e => e.innerText)).slice(0, 400).replace(/\n+/g, ' | '));
  await p.click('[data-mode=footprint]'); await sleep(300);
  console.log('ATLAS fp legend:', await p.$eval('#atlas-legend', e => e.innerText.replace(/\n/g, ' | ')));
  await p.screenshot({ path: 'atlas-fp.png' });
  await p.click('[data-mode=lineage]'); await sleep(300);
  console.log('ATLAS lineage legend:', await p.$eval('#atlas-legend', e => e.innerText.replace(/\n/g, ' | ')));
  await p.goto(B + '/atlas/index.html?p=P33', { waitUntil: 'networkidle2' }); await sleep(400);
  console.log('ATLAS ?p=P33 sel:', await p.$eval('#atlas-prog', e => e.value), '|', (await p.$eval('#atlas-panel', e => e.innerText)).slice(0, 200).replace(/\n+/g, ' | '));
  // BROWSE filters
  await p.goto(B + '/programmes/index.html?tq=High&evidence=Unstudied', { waitUntil: 'networkidle2' }); await sleep(300);
  console.log('BROWSE preset:', await p.$eval('#count', e => e.innerText), '| chips:', await p.$eval('#chips', e => e.innerText.replace(/\n/g, ' ')));
  await p.goto(B + '/programmes/index.html', { waitUntil: 'networkidle2' });
  await p.click('.fgroup[data-f=region] > button'); await sleep(150);
  const opts = await p.$$eval('.fgroup[data-f=region] .fpanel button, .fgroup[data-f=region] .fpanel label', es => es.map(e => e.innerText.replace(/\n/g, ' ')).slice(0, 12));
  console.log('region options:', opts.join(' ; '));
  await p.type('#q', 'health'); await sleep(400);
  console.log('search health:', await p.$eval('#count', e => e.innerText));
  await p.click('.viewtoggle button[data-view=table]'); await sleep(200);
  console.log('table rows:', await p.$$eval('#table-view tr', e => e.length));
  // SEARCH overlay
  await p.keyboard.press('Escape'); await p.click('body'); await p.keyboard.press('/'); await sleep(200);
  await p.type('#search-input', 'PSLM'); await sleep(300);
  console.log('overlay results:', (await p.$eval('#search-results', e => e.innerText)).slice(0, 200).replace(/\n+/g, ' | '));
  await p.keyboard.press('Escape');
  // PROGRAMME: star, mde, dofile
  await p.goto(B + '/programmes/p33.html', { waitUntil: 'networkidle2' }); await sleep(400);
  await p.click('.p-actions [data-star]'); await sleep(100);
  console.log('star:', await p.$eval('.p-actions [data-star]', e => e.getAttribute('aria-pressed') + ' ' + e.innerText), 'count:', await p.$eval('[data-shortlist-count]', e => e.innerText));
  console.log('mde:', await p.$eval('#mde-out .big', e => e.innerText));
  await p.$eval('#mJ', e => { e.value = 126; e.dispatchEvent(new Event('input', { bubbles: true })); }); await sleep(100);
  console.log('mde J=126:', await p.$eval('#mde-out .big', e => e.innerText), '|', await p.$eval('#mde-out .expl', e => e.innerText.slice(0, 120)));
  console.log('dofile lines:', await p.$eval('#dofile', e => e.textContent.split('\n').length), '| legend:', await p.$eval('#p-legend', e => e.innerText.replace(/\n/g, ' | ')));
  console.log('replay visible:', await p.$eval('#p-replay', e => !e.hidden));
  await p.click('#p-cal ~ * [data-table-toggle], [data-table-toggle]'); await sleep(150);
  console.log('cal table rows:', await p.$$eval('#coverage .chart-table tr', e => e.length));
  // SHORTLIST
  await p.goto(B + '/shortlist/index.html', { waitUntil: 'networkidle2' }); await sleep(300);
  console.log('shortlist cols:', await p.$$eval('#compare tr:first-child td', e => e.length), 'tools hidden:', await p.$eval('#sl-tools', e => e.hidden));
  // INSIGHTS
  await p.goto(B + '/insights/index.html', { waitUntil: 'networkidle2' }); await sleep(500);
  for (const id of ['c-swim', 'c-era', 'c-heat', 'c-ds', 'c-cal']) console.log(id, await p.$eval('#' + id, e => e.querySelectorAll('rect,circle,path,line').length));
  const tbs = await p.$$('[data-table-toggle]'); for (const t of tbs) await t.click(); await sleep(200);
  console.log('tables:', await p.$$eval('.chart-table', es => es.map(e => e.querySelectorAll('tr').length).join(',')));
  // DATASETS filter
  await p.goto(B + '/datasets/index.html?p=P15', { waitUntil: 'networkidle2' }); await sleep(300);
  await p.click('[data-dsf=access][data-v="Open download"]'); await sleep(100);
  console.log('ds open:', await p.$eval('#ds-count', e => e.innerText), 'sel:', await p.$eval('#ds-prog', e => e.value));
  // TOOLKIT
  await p.goto(B + '/toolkit/index.html', { waitUntil: 'networkidle2' }); await sleep(300);
  console.log('toolkit mde:', await p.$eval('#mde-out .big', e => e.innerText));
  console.log('ERRORS:', errs);
  await b.close();
})();
