import sys, os, json, hashlib, shutil
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out,exist_ok=True)
page = open(src, encoding='utf8').read()
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
<script>if("serviceWorker" in navigator)window.addEventListener("load",()=>navigator.serviceWorker.register("sw.js").catch(()=>{}));</script>
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
    // app files: always ask the server (GitHub Pages lets browsers cache for 10 min), fall back to cache offline
    e.respondWith(fetch(r.url,{cache:"no-cache",credentials:"same-origin"}).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c));return res}).catch(()=>caches.match(r).then(m=>m||caches.match("index.html"))));
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
