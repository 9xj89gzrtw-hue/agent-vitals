// Render vitals/chart.html to vitals/chart.png in a fresh headless browser
// (deliberately NOT the shared CDP Chrome: file:// navigation wedges it).
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');
(async () => {
  const html = fs.readFileSync(path.join(__dirname, 'chart.html'), 'utf8');
  const b = await chromium.launch({ channel: 'chrome' });
  const p = await b.newPage({ viewport: { width: 2000, height: 1180 }, deviceScaleFactor: 2 });
  await p.setContent(html, { waitUntil: 'load' });
  await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, 'chart.png') });
  await b.close();
  console.log('chart.png', fs.statSync(path.join(__dirname, 'chart.png')).size, 'bytes');
})();
