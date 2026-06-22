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
    "name": "元の英単語帳 ターゲット1900",
    "short_name": "ターゲット1900",
    "start_url": "./index.html",
    "scope": "./",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#0f1320",
    "theme_color": "#4f46e5",
    "lang": "ja",
    "icons": [{"src": "icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}]
}
(BASE / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

# 3) アイコン（シンプルなSVG）
icon = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
    '<rect width="512" height="512" rx="112" fill="#ff6a1a"/>'
    '<circle cx="256" cy="240" r="150" fill="#ffffff" stroke="#14181f" stroke-width="12"/>'
    '<g fill="none" stroke="#14181f" stroke-width="11" stroke-linecap="round">'
    '<path d="M256 96 C 230 168 230 312 256 384"/>'
    '<path d="M256 96 C 150 150 132 290 202 380"/>'
    '<path d="M256 96 C 362 150 380 290 310 380"/>'
    '<path d="M120 214 C 200 196 312 196 392 214"/>'
    '</g>'
    '<text x="256" y="470" font-size="76" font-family="Arial,sans-serif" font-weight="bold" '
    'fill="#ffffff" text-anchor="middle">1900</text></svg>'
)
(BASE / "icon.svg").write_text(icon, encoding="utf-8")

# 4) Service Worker（オフラインキャッシュ）
sw = """const CACHE='tango1900-v13';
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
