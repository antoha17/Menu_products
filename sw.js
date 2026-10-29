const CACHE="korzina-f128aea1";
const FILES=["./","index.html","manifest.webmanifest","apple-touch-icon.png","icon-180.png","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==CACHE).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const u=new URL(r.url);
  if(/\.(png|webmanifest)$/.test(u.pathname))return;
  if(u.origin===location.origin){
    // app files: ask the server for the fresh version (GitHub Pages lets browsers cache for 10 min), but on a slow
    // or missing connection do not keep a black screen: after 1.5 s the saved copy opens, the fresh one is saved for next time
    const net=fetch(r.url,{cache:"no-cache",credentials:"same-origin"}).then(res=>{if(res.ok){const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c))}return res});
    const saved=()=>caches.match(r).then(m=>m||caches.match("index.html"));
    e.respondWith(new Promise(done=>{let over=false;const finish=v=>{if(!over&&v){over=true;done(v)}};
      const t=setTimeout(()=>saved().then(finish),1500);
      net.then(res=>{clearTimeout(t);finish(res)}).catch(()=>{clearTimeout(t);saved().then(m=>finish(m||Response.error()))})}));
    e.waitUntil(net.catch(()=>{}));
  }else if(/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)){
    e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c));return res})));
  }
});
