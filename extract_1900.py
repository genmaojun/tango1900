# -*- coding: utf-8 -*-
"""英単語ターゲット1900 PDF から全単語を抽出して JSON 化する。"""
import json, re
from pathlib import Path

BASE = Path(r"C:\Users\HSS_DG517\Documents\◆AI関連\claude　Code\単語アプリ")
PDF = BASE / "target1900_source.pdf"
OUT_JSON = BASE / "words_1900.json"

CJK = re.compile(r"[ぁ-んァ-ヶ一-龯、，。（）()／]")

def split_en_ja(s):
    """'believe を信じる' のような行を英語と日本語に分割（最初の日本語文字で切る）。"""
    m = CJK.search(s)
    if not m:
        return s.strip(), ""
    i = m.start()
    return s[:i].strip(), s[i:].strip()

rows = []  # (no, en, ja)

import pdfplumber
with pdfplumber.open(str(PDF)) as pdf:
    npages = len(pdf.pages)
    for page in pdf.pages:
        tbl = page.extract_table()
        if tbl:
            for r in tbl:
                if not r or len(r) < 3:
                    continue
                no, en, ja = (r[0] or "").strip(), (r[1] or "").strip(), (r[2] or "").strip()
                if not no.isdigit():
                    continue  # ヘッダ行や空行を除外
                # セル内改行を整理
                en = " ".join(en.split())
                ja = " ".join(ja.replace("\n", " ").split())
                rows.append((int(no), en, ja))
        else:
            # フォールバック：テキスト行を解析
            txt = page.extract_text() or ""
            for line in txt.splitlines():
                m = re.match(r"^(\d+)\s+(.*)$", line.strip())
                if not m:
                    continue
                no = int(m.group(1))
                en, ja = split_en_ja(m.group(2))
                if en:
                    rows.append((no, en, ja))

# No 順に整列・重複排除（No キー）
seen = {}
for no, en, ja in rows:
    if no not in seen:
        seen[no] = (en, ja)
items = []
for no in sorted(seen):
    en, ja = seen[no]
    # Part 判定（6訂版: 1-800 基本 / 801-1500 重要 / 1501-1900 難）
    if no <= 800:
        part = 1
    elif no <= 1500:
        part = 2
    else:
        part = 3
    section = (no - 1) // 100 + 1  # 100語ごと
    items.append({"no": no, "en": en, "ja": ja, "part": part, "section": section})

OUT_JSON.write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")

# 統計（ASCII中心で表示）
print("pages:", npages)
print("count:", len(items))
if items:
    print("min_no:", items[0]["no"], "max_no:", items[-1]["no"])
    nos = [it["no"] for it in items]
    missing = [n for n in range(items[0]["no"], items[-1]["no"]+1) if n not in seen]
    print("missing_count:", len(missing), "missing_first20:", missing[:20])
    # 英語が空 / 日本語が空のもの
    empty_en = [it["no"] for it in items if not it["en"]]
    empty_ja = [it["no"] for it in items if not it["ja"]]
    print("empty_en:", empty_en[:20], "empty_ja:", empty_ja[:20])
    print("sample_en:", [it["en"] for it in items[:10]])
print("WROTE", OUT_JSON.name)
