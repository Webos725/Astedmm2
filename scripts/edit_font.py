#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont, getTableModule
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

INPUT_PATH = os.path.abspath("downloads/font.ttf")
OUTPUT_PATH = os.path.abspath("downloads/font2.ttf")
GLYPH_LIST_OUTPUT = os.path.abspath("downloads/font2_glyphs.txt")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"{INPUT_PATH} が見つかりません")

# --- 元フォント読み込み ---
source_font = TTFont(INPUT_PATH)

# --- 1. 新規フォント作成 ---
font2 = TTFont()

# --- 2. 必須テーブルコピー ---
for table_tag in ["head", "hhea", "maxp", "hmtx", "OS/2", "post"]:
    if table_tag in source_font:
        font2[table_tag] = source_font[table_tag]

# --- 3. nameテーブル作成 / 英語化 ---
name_table = getTableModule("name").table__n_a_m_e()
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

# --- 4. グリフ自動割り当て ---
unicode_map = {}
available_glyphs = source_font.getGlyphOrder()[1:]  # .notdefを除く
assigned_glyphs = []

def assign_range(start, end):
    global available_glyphs
    for cp in range(start, end + 1):
        if available_glyphs:
            gname = available_glyphs.pop(0)
            unicode_map[cp] = gname
            assigned_glyphs.append(gname)

assign_range(0x20, 0x7E)  # ASCII
assign_range(0xA0, 0xFF)  # Latin-1

extra_cp = 0x0100
while available_glyphs:
    gname = available_glyphs.pop(0)
    unicode_map[extra_cp] = gname
    assigned_glyphs.append(gname)
    extra_cp += 1

# グリフ順序更新（.notdef + 自動割当順）
font2.setGlyphOrder([".notdef"] + assigned_glyphs)
font2["hmtx"] = source_font["hmtx"]

# --- 5. cmap作成（安定版） ---
CmapTableClass = getTableModule("cmap").table__c_m_a_p
cmap_table = CmapTableClass()
# 明示的に初期化
cmap_table.tableVersion = 0
cmap_table.tables = []

# Windows format4
sub4 = CmapSubtable.newSubtable(4)
sub4.platformID = 3
sub4.platEncID = 1
sub4.language = 0
sub4.cmap = dict(unicode_map)
cmap_table.tables.append(sub4)

# Windows format12
sub12 = CmapSubtable.newSubtable(12)
sub12.platformID = 3
sub12.platEncID = 10
sub12.language = 0
sub12.cmap = dict(unicode_map)
cmap_table.tables.append(sub12)

font2["cmap"] = cmap_table

# --- 6. 不要テーブル削除 ---
for t in ["TSI0", "TSI1", "TSI2", "TSI3"]:
    if t in font2:
        del font2[t]

# --- 7. 保存 ---
font2.save(OUTPUT_PATH)
print(f"[+] 新規フォント作成完了: {OUTPUT_PATH}")

# --- 8. グリフ一覧出力 ---
with open(GLYPH_LIST_OUTPUT, "w", encoding="utf-8") as f:
    for cp, gname in sorted(unicode_map.items()):
        f.write(f"U+{cp:04X}: {gname}\n")

print(f"[+] グリフ一覧テキスト出力完了: {GLYPH_LIST_OUTPUT}")
