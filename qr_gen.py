# -*- coding: utf-8 -*-
import segno
url = "https://mba-driver-latitude-during.trycloudflare.com"
qr = segno.make(url, error='m')
# 表示用SVG（XML宣言なし＝show_widgetにそのまま渡せる）
qr.save("qr.svg", scale=6, border=3, dark="#0b1020", light="#ffffff", xmldecl=False)
# バックアップPNG
qr.save("qr.png", scale=9, border=3, dark="#0b1020", light="#ffffff")
print("OK", url)
