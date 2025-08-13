#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

INPUT_PATH = os.path.abspath("downloads/font.ttf")
OUTPUT_PATH = os.path.abspath("downloads/font2.ttf")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"{INPUT_PATH} が見つかりません")

# 元フォント読み込み
source_font = TTFont(INPUT_PATH)

# --- 1. 新規フォント作成 ---
font2 = TTFont()

# --- 2. 必須テーブルをコピー ---
for table_tag in ["head", "hhea", "maxp", "hmtx", "OS/2", "post"]:
    if table_tag in source_font:
        font2[table_tag] = source_font[table_tag]

# --- 3. nameテーブル作成 / 英語化 ---
name_table = newTable("name")
name_table.names = []

new_names = {
    1: "Sakalti",            # フォントファミリー
    2: "Regular",            # サブファミリー
    4: "Sakalti Regular",    # フルネーム
    6: "Sakalti-Regular"     # PostScript名
}

for nid, text in new_names.items():
    name_table.setName(text, nid, 3, 1, 0x0409)  # Windows Unicode
    name_table.setName(text, nid, 1, 0, 0)       # Macintosh Roman

font2["name"] = name_table

# --- 4. グリフコピー ---
font2.setGlyphOrder(source_font.getGlyphOrder())
font2["hmtx"] = source_font["hmtx"]

# --- 5. cmap作成（tableVersionを明示） ---
cmap_table = newTable("cmap")
cmap_table.tableVersion = 0      # ←ここが必須
cmap_table.tables = []

# 元のUnicode cmapを参照
unicode_tbl = next((t for t in source_font["cmap"].tables if t.platformID == 0), None)
if not unicode_tbl:
    raise RuntimeError("Unicode cmapが見つかりません。")

# Windows BMP format4
sub4 = CmapSubtable.newSubtable(4)
sub4.platformID = 3
sub4.platEncID = 1
sub4.language = 0
sub4.cmap = dict(unicode_tbl.cmap)
cmap_table.tables.append(sub4)

# Windows 32bit format12
sub12 = CmapSubtable.newSubtable(12)
sub12.platformID = 3
sub12.platEncID = 10
sub12.language = 0
sub12.cmap = dict(unicode_tbl.cmap)
cmap_table.tables.append(sub12)

font2["cmap"] = cmap_table

# --- 6. 保存 ---
font2.save(OUTPUT_PATH)
print(f"[+] 新規フォント作成完了: {OUTPUT_PATH}")

font2["name"] = name_table

# --- 4. グリフコピー ---
font2.setGlyphOrder(source_font.getGlyphOrder())

# hmtx もコピー
font2["hmtx"] = source_font["hmtx"]

# --- 5. cmapテーブル作成 ---
cmap_table = newTable("cmap")
cmap_table.tables = []

# 元のUnicode cmapを参照
unicode_tbl = next((t for t in source_font["cmap"].tables if t.platformID == 0), None)
if not unicode_tbl:
    raise RuntimeError("Unicode cmapが見つかりません。")

# Windows BMP format4
sub4 = CmapSubtable.newSubtable(4)
sub4.platformID = 3
sub4.platEncID = 1
sub4.language = 0
sub4.cmap = dict(unicode_tbl.cmap)
cmap_table.tables.append(sub4)

# Windows 32bit format12
sub12 = CmapSubtable.newSubtable(12)
sub12.platformID = 3
sub12.platEncID = 10
sub12.language = 0
sub12.cmap = dict(unicode_tbl.cmap)
cmap_table.tables.append(sub12)

font2["cmap"] = cmap_table

# --- 6. 保存 ---
font2.save(OUTPUT_PATH)
print(f"[+] 新規フォント作成完了: {OUTPUT_PATH}")
