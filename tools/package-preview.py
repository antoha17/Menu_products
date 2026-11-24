from pathlib import Path
import json,hashlib,shutil,zipfile,re
r=Path(__file__).resolve().parent.parent;p=r/'preview'
s=(p/'index.html').read_text().replace('content="Корзина"','content="Корзина тест"').replace('<title>Корзина на неделю</title>','<title>Корзина · тест</title>')
(p/'index.html').write_text(s)
m=json.loads((p/'manifest.webmanifest').read_text());m.update(name='Корзина · тест',short_name='Корзина тест',description='Отдельная тестовая версия: Классик и Стекло')
(p/'manifest.webmanifest').write_text(json.dumps(m,ensure_ascii=False,indent=2))
# Do not delete any production caches; only own this preview path.
v=hashlib.sha256(s.encode()).hexdigest()[:10]
(p/'sw.js').write_text('''const CACHE="korzina-preview-'''+v+'''";
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
''')
shutil.copytree(r/'vendor',p/'vendor',dirs_exist_ok=True)
# Different icon badge to distinguish the two installed apps.
from PIL import Image,ImageDraw
for name in ['icon-180.png','icon-192.png','icon-512.png','apple-touch-icon.png','apple-touch-icon-precomposed.png']:
 im=Image.open(p/name);d=ImageDraw.Draw(im);n=im.width;d.ellipse((n*.65,n*.05,n*.94,n*.34),fill='#A6E8CD',outline='#163F30',width=max(1,n//90));d.line([(n*.72,n*.12),(n*.87,n*.12)],fill='#163F30',width=max(2,n//35));d.line([(n*.795,n*.12),(n*.795,n*.27)],fill='#163F30',width=max(2,n//35));im.save(p/name)
out=r/'downloads';out.mkdir(exist_ok=True)
shutil.copy(p/'index.html',out/'korzina-test.html')
with zipfile.ZipFile(out/'korzina-test.zip','w',zipfile.ZIP_DEFLATED) as z:
 for f in p.rglob('*'):
  if f.is_file() and f.suffix!='.zip':z.write(f,'korzina-test/'+str(f.relative_to(p)))

shutil.copy(out/'korzina-test.zip',p/'korzina-test.zip')
