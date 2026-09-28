const { chromium } = require('playwright'); const fs=require('fs'); const {spawn}=require('child_process');
const mode=process.argv[2]||'stills'; const FPS=30, DUR=30.6;
(async()=>{
  const html=fs.readFileSync('comp.html','utf8').replace('__PBI__',fs.readFileSync('pbi_data.json','utf8'));
  fs.writeFileSync('comp_built.html',html);
  const b=await chromium.launch(); const ctx=await b.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  await require('./net')(ctx); const p=await ctx.newPage();
  p.on('console',m=>console.log('console:',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
  await p.goto('http://localhost:8123/brag-output/work/comp_built.html',{waitUntil:'networkidle'}); await p.evaluate(()=>window.ready); await p.waitForTimeout(500);
  if(mode==='stills'){
    const ts=(process.argv[3]||'0.3,1.2,2.2,3.0,3.4,4.2,5.4,6.3,7.0,8.0,8.6,9.4,10.5,11.2,12.5,13.8,14.2,15.9,16.3,17.5,18.6,19.1,20.5,22.4').split(',').map(Number);
    fs.mkdirSync('stills',{recursive:true});
    for(const t of ts){await p.evaluate(t=>window.render(t),t); await p.screenshot({path:`stills/s_${t.toFixed(2)}.jpg`,type:'jpeg',quality:85});}
    console.log('stills done');
  } else {
    const ff=spawn('ffmpeg',['-y','-f','image2pipe','-framerate',String(FPS),'-i','-','-c:v','libx264','-preset','slow','-crf','15','-pix_fmt','yuv420p','-r',String(FPS),'video_noaudio.mp4'],{stdio:['pipe','ignore','inherit']});
    const N=Math.round(DUR*FPS);
    for(let f=0;f<N;f++){await p.evaluate(t=>window.render(t),f/FPS); const buf=await p.screenshot({type:'png'}); if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r)); if(f%60===0) console.log('frame',f);}
    ff.stdin.end(); await new Promise(r=>ff.on('close',r)); console.log('video done');
  }
  await b.close();
})();
