const CACHE="korzina-e6587f4b";
const FILES=["./","index.html","manifest.webmanifest","apple-touch-icon.png","icon-180.png","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(n=>n!==CACHE).map(n=>caches.delete(n)))).then(()=>self.clients.claim()))});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const u=new URL(r.url);
  if(/\.(png|webmanifest)$/.test(u.pathname))return;
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
  }else if(/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname)){
    e.respondWith(caches.match(r).then(m=>m||fetch(r).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c));return res})));
  }
});
