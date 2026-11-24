const CACHE="korzina-preview-df385d3f68";
const ROOT=new URL('./',self.location.href);
const FILES=['./','index.html','manifest.webmanifest','apple-touch-icon.png','icon-180.png','icon-192.png','icon-512.png','vendor/zxing.min.js'];
self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k.startsWith('korzina-preview-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',e=>{
 const u=new URL(e.request.url);if(e.request.method!=='GET'||u.origin!==ROOT.origin||!u.pathname.startsWith(ROOT.pathname))return;
 e.respondWith(caches.open(CACHE).then(async c=>{
  if(e.request.mode==='navigate'){try{const res=await fetch(e.request);if(res.ok)await c.put(e.request,res.clone());return res}catch(err){return (await c.match(e.request))||(await c.match(new URL('index.html',ROOT).href))||Response.error()}}
  const saved=await c.match(e.request);if(saved)return saved;const res=await fetch(e.request);if(res.ok)await c.put(e.request,res.clone());return res;
 }));
});
