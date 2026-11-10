import sys, os, json, hashlib, shutil
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out,exist_ok=True)
page = open(src, encoding='utf8').read()
# the built-in product catalogue lives in tools/foods.txt and is inlined into the page
foods = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'foods.txt'), encoding='utf8').read().strip()
page = page.replace('/*FOODS*/""', json.dumps(foods, ensure_ascii=False))
micro = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'micro.txt'), encoding='utf8').read().strip()
page = page.replace('/*MICRO*/""', json.dumps(micro, ensure_ascii=False))
ver = hashlib.sha1(page.encode()).hexdigest()[:8]
head = '''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Корзина">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#F3F5F1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121714" media="(prefers-color-scheme: dark)">

<link rel="manifest" href="manifest.webmanifest?v=VER">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png"><link rel="apple-touch-icon" href="apple-touch-icon.png"><link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0;font:14px/1.4 system-ui,-apple-system,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
'''
tail = '''
<script>if("serviceWorker" in navigator){window.addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));
navigator.serviceWorker.addEventListener("message",e=>{if(e.data&&e.data.t==="updated"&&performance.now()<6000&&!document.activeElement?.matches?.("input,textarea")&&!document.querySelector(".sheet.on"))location.reload()})}</script>
</body></html>
'''
open(f'{out}/index.html','w',encoding='utf8').write(head.replace('VER',ver)+page+tail)
open(f'{out}/manifest.webmanifest','w',encoding='utf8').write(json.dumps({
 "name":"Корзина на неделю","short_name":"Корзина","lang":"ru","id":"./","start_url":"./","scope":"./","display":"standalone",
 "background_color":"#F3F5F1","theme_color":"#2D6A4C",
 "icons":[{"src":"apple-touch-icon.png","sizes":"180x180","type":"image/png","purpose":"any"},{"src":"icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},{"src":"icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"}]},ensure_ascii=False,indent=1))
open(f'{out}/sw.js','w',encoding='utf8').write('''const CACHE="korzina-%s";
const FILES=["./","index.html","manifest.webmanifest","apple-touch-icon.png","icon-180.png","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==CACHE).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const u=new URL(r.url);
  if(/\\.(png|webmanifest)$/.test(u.pathname))return;
  if(u.origin===location.origin){
    // app files: open the saved copy at once (instant start, works offline), fetch the fresh one in the background;
    // if it changed, save it and tell the page, which reloads only if it was opened a moment ago
    const net=fetch(r.url,{cache:"no-cache",credentials:"same-origin"});
    e.respondWith(caches.match(r).then(m=>m||(r.mode==="navigate"?caches.match("index.html"):null)).then(saved=>{const savedCopy=saved&&saved.clone();
      const upd=net.then(async res=>{if(!res.ok)return res;const fresh=res.clone();const c=await caches.open(CACHE);
        if(saved&&r.mode==="navigate"){const [a,b]=await Promise.all([savedCopy.text(),res.clone().text()]);
          if(a!==b){await c.put(r,fresh);const cl=await self.clients.matchAll({type:"window"});cl.forEach(x=>x.postMessage({t:"updated"}))}}
        else await c.put(r,fresh);return res});
      e.waitUntil(upd.catch(()=>{}));
      return saved||upd.catch(()=>caches.match("index.html").then(m=>m||Response.error()))}));
  }else if(/fonts\\.(googleapis|gstatic)\\.com$/.test(u.hostname)){
    e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c));return res})));
  }
});
''' % ver)
# icon: green tile with a white basket
def icon(n):
    s=4*n; im=Image.new("RGBA",(s,s),"#2D6A4C"); d=ImageDraw.Draw(im)
    w=s*0.05
    d.arc([s*.30,s*.16,s*.70,s*.56],200,340,fill="white",width=int(w))
    d.polygon([(s*.18,s*.42),(s*.82,s*.42),(s*.72,s*.80),(s*.28,s*.80)],fill="white")
    for x in (.38,.5,.62):
        d.line([(s*x,s*.50),(s*x,s*.72)],fill="#2D6A4C",width=int(w*.7))
    return im.resize((n,n),Image.LANCZOS).convert("RGB")
for n in (180,192,512): icon(n).save(f'{out}/icon-{n}.png')
# iPhone also looks for these exact names at the site root
icon(180).save(f'{out}/apple-touch-icon.png'); icon(180).save(f'{out}/apple-touch-icon-precomposed.png')
print("built",ver)
