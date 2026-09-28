const { chromium } = require('playwright');
const B = 'http://localhost:8000';
async function session(b, email){
  const ctx = await b.newContext({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });
  await require('./net')(ctx); const p = await ctx.newPage();
  await p.goto(B + '/login/', {waitUntil:'networkidle'}); await p.waitForTimeout(800);
  if(email==='admin@vatsfinancial.com') await p.screenshot({ path: 'shots/login.png' });
  await p.fill('input[name=username]', email); await p.fill('input[name=password]', 'VFS@2026Secure');
  await Promise.all([p.waitForNavigation(), p.click('button[type=submit], input[type=submit]')]);
  return p;
}
async function shot(p,u,n,full){ await p.goto(B+u,{waitUntil:'networkidle'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(2500); await p.screenshot({path:`shots/${n}.png`,fullPage:!!full}); console.log(n,p.url()); }
(async () => {
  const b = await chromium.launch();
  const p = await session(b,'admin@vatsfinancial.com');
  await shot(p,'/','dashboard',true);
  await shot(p,'/ticket_list/','tickets',true);
  const hrefs = await p.$$eval('a[href*="ticket_detail"]', as=>as.map(a=>a.getAttribute('href')+' | '+a.closest('tr')?.innerText.replace(/\s+/g,' ').slice(0,120)));
  console.log(hrefs.slice(0,40).join('\n'));
  await shot(p,'/ticket_list/Pending','pending',true);
  await shot(p,'/ticket_detail/32','detail',true);
  await shot(p,'/ticket_detail/8','detail8',true);
  await shot(p,'/user_list/','users');
  const v = await session(b,'james.wilson@vatsfinancial.com');
  await shot(v,'/ticket_create/','create',true);
  await shot(v,'/my_tickets/','mine',true);
  await b.close();
})();
