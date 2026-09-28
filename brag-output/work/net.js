const fs=require('fs'),path=require('path'),{execFileSync}=require('child_process');
const NM=path.join(__dirname,'cdn/node_modules');
const map=[
 [/cdn\.jsdelivr\.net\/npm\/chart\.js@[^/]+\/(.*)/, m=>'chart.js/'+m[1].replace('chart.umd.min.js','chart.umd.js')],
 [/cdn\.jsdelivr\.net\/npm\/@tabler\/icons-webfont@[^/]+\/(.*)/, m=>'@tabler/icons-webfont/dist/'+m[1].replace(/^dist\//,'')],
 [/stackpath\.bootstrapcdn\.com\/bootstrap\/[^/]+\/(.*)/, m=>'bootstrap/dist/'+m[1]],
 [/code\.jquery\.com\/jquery-3\.5\.1\.min\.js/, m=>'jquery/dist/jquery.min.js'],
 [/cdnjs\.cloudflare\.com\/ajax\/libs\/popper\.js\/[^/]+\/umd\/(.*)/, m=>'popper.js/dist/umd/'+m[1]],
];
const ct=u=>u.match(/\.css/)?'text/css':u.match(/\.js/)?'application/javascript':u.match(/woff2/)?'font/woff2':u.match(/woff/)?'font/woff':u.match(/ttf/)?'font/ttf':u.match(/png/)?'image/png':'application/octet-stream';
const cacheDir=path.join(__dirname,'netcache'); fs.mkdirSync(cacheDir,{recursive:true});
module.exports=async (ctx)=>{
 await ctx.route(u=>!/^https?:\/\/(localhost|127\.0\.0\.1)/.test(u.href) && /^https?:/.test(u.href), async route=>{
  const url=route.request().url(); const clean=url.split('?')[0].split('#')[0];
  for(const [re,f] of map){const m=clean.match(re); if(m){const p=path.join(NM,f(m)); if(fs.existsSync(p)) return route.fulfill({status:200,contentType:ct(clean),body:fs.readFileSync(p)}); else {console.log('MISSING',p); return route.abort();}}}
  const key=path.join(cacheDir,Buffer.from(url).toString('base64url').slice(0,200));
  try{ if(!fs.existsSync(key)) execFileSync('curl',['-sSfL','--max-time','20','-A','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36','-o',key,url]);
   const body=fs.readFileSync(key); const type=url.includes('fonts.googleapis.com/css')?'text/css':ct(clean);
   return route.fulfill({status:200,contentType:type,body,headers:{'access-control-allow-origin':'*'}});
  }catch(e){console.log('FAIL',url); return route.abort();}
 });
};
