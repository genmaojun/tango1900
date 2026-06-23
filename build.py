# -*- coding: utf-8 -*-
"""テンプレHTMLに1900語を流し込み、index.html＋PWA一式を生成し、公開用 dist/ を作る。"""
import json, shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
DIST = BASE / "dist"

# 1) アプリ本体 index.html
tpl = (BASE / "_app_template.html").read_text(encoding="utf-8")
words = json.loads((BASE / "words_1900.json").read_text(encoding="utf-8"))
data = json.dumps(words, ensure_ascii=False, separators=(",", ":"))
html = tpl.replace("__WORDS_JSON__", data)
assert "__WORDS_JSON__" not in html, "placeholder still present!"
(BASE / "index.html").write_text(html, encoding="utf-8")

# 2) PWA マニフェスト
manifest = {
    "name": "WORDCRAFT 元の英単語1900",
    "short_name": "WORDCRAFT",
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#1c2e16",
    "theme_color": "#5fae3a",
    "lang": "ja",
    "icons": [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]
}
(BASE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

# 3) アイコン（シンプルなSVG）
icon = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8" shape-rendering="crispEdges">'
    '<rect width="8" height="8" fill="#5fae3a"/>'
    '<rect width="8" height="1" fill="#6fc049"/>'
    '<g fill="#123612">'
    '<rect x="1" y="2" width="2" height="2"/>'
    '<rect x="5" y="2" width="2" height="2"/>'
    '<rect x="3" y="4" width="2" height="2"/>'
    '<rect x="2" y="6" width="4" height="1"/>'
    '<rect x="2" y="7" width="1" height="1"/>'
    '<rect x="5" y="7" width="1" height="1"/>'
    '</g></svg>'
)
(BASE / "icon.svg").write_text(icon, encoding="utf-8")

# 4) Service Worker（オフラインキャッシュ）
sw = """const CACHE='tango1900-v17';
const ASSETS=['./','./index.html','./manifest.json','./icon.svg','./pixel.ttf','./jp.ttf'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{if(e.request.method!=='GET')return;e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request).then(resp=>{const cp=resp.clone();caches.open(CACHE).then(c=>c.put(e.request,cp));return resp;}).catch(()=>caches.match('./index.html'))));});
"""
(BASE / "sw.js").write_text(sw, encoding="utf-8")

# 5) 公開用 dist/（アプリのみ。PDF・スクリプト類は含めない）
DIST.mkdir(exist_ok=True)
for f in ["index.html", "manifest.json", "icon.svg", "sw.js", "pixel.ttf", "jp.ttf"]:
    shutil.copy2(BASE / f, DIST / f)

print("words:", len(words))
print("index.html bytes:", (BASE / "index.html").stat().st_size)
print("dist files:", [p.name for p in sorted(DIST.iterdir())])
print("OK")
