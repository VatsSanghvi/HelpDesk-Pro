const { chromium } = require('playwright');
const B='http://localhost:8000';
(async()=>{
 const b=await chromium.launch();
 const ctx=await b.newContext({viewport:{width:1600,height:900},deviceScaleFactor:2});
 await require('./net')(ctx); const p=await ctx.newPage();
 await p.goto(B+'/login/',{waitUntil:'networkidle'});
 await p.fill('input[name=username]','james.wilson@vatsfinancial.com'); await p.fill('input[name=password]','VFS@2026Secure');
 await Promise.all([p.waitForNavigation(),p.click('button[type=submit]')]);
 await p.goto(B+'/ticket_create/',{waitUntil:'networkidle'}); await p.evaluate(()=>document.fonts.ready); await p.waitForTimeout(1500);
 let i=0; const snap=async()=>{await p.waitForTimeout(120); await p.screenshot({path:`shots/type/${String(i++).padStart(3,'0')}.png`});};
 const sels=await p.$$eval('select',s=>s.map(x=>x.name+':'+[...x.options].map(o=>o.value+'='+o.text).join(',')));
 console.log(sels.join('\n'));
 await snap();
 const catSel=await p.$('select[name=category]');
 const catVal=await p.$eval('select[name=category]',s=>[...s.options].find(o=>/Hardware/.test(o.text)).value);
 await p.selectOption('select[name=category]',catVal); await p.waitForTimeout(1200); await snap();
 const subVal=await p.$eval('select[name=subcategory]',s=>{const o=[...s.options].find(o=>/Laptop/.test(o.text));return o&&o.value;});
 console.log('sub',subVal); if(subVal) await p.selectOption('select[name=subcategory]',subVal); await snap();
 const title='Laptop not turning on after Windows update';
 await p.click('input[name=title]');
 for(let k=3;k<=title.length+2;k+=3){ await p.fill('input[name=title]',title.slice(0,k)); await snap(); }
 const desc='Screen stays black after last night\'s update. Power light is on but nothing boots.';
 await p.click('textarea');
 for(let k=6;k<=desc.length+5;k+=6){ await p.fill('textarea',desc.slice(0,k)); await snap(); }
 await p.hover('form:has(input[name=title]) button[type=submit]'); await snap();
 await Promise.all([p.waitForNavigation({timeout:30000}),p.click('form:has(input[name=title]) button[type=submit]')]);
 await p.waitForTimeout(1500); console.log('after submit',p.url()); await p.screenshot({path:'shots/after_submit.png'});
 await p.goto(B+'/my_tickets/',{waitUntil:'networkidle'}); await p.waitForTimeout(1500); await p.screenshot({path:'shots/mine_after.png'});
 console.log('frames',i); await b.close();
})();
