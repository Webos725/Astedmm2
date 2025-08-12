#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

INPUT_PATH = os.path.abspath("downloads/font.ttf")
OUTPUT_PATH = os.path.abspath("downloads/font2.ttf")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"{INPUT_PATH} が見つかりません")

font = TTFont(INPUT_PATH)

# --- 1. グリフ順序をASCII順＋Latin-1順に並び替え ---
order = font.getGlyphOrder()
# すべてのUnicode→glyph名マッピングを取得
unicode_map = {}
for table in font["cmap"].tables:
    for code, name in table.cmap.items():
        unicode_map[code] = name

# ASCII(0x20〜0x7E)、Latin-1(0xA0〜0xFF)順に並べ替え
desired_order = []
for cp in list(range(0x20, 0x7F)) + list(range(0xA0, 0x100)):
    if cp in unicode_map and unicode_map[cp] not in desired_order:
        desired_order.append(unicode_map[cp])

# 残りのグリフ（未割当）は後ろへ
for g in order:
    if g not in desired_order:
        desired_order.append(g)

font.setGlyphOrder(desired_order)
print(f"[*] グリフ順序をASCII+Latin-1順に並び替えました ({len(desired_order)} glyphs)")

# --- 2. cmapのWindows用format4とformat12追加 ---
cmap_table = font["cmap"]

# Unicodeサブテーブルを基に作成
unicode_tbl = next((t for t in cmap_table.tables if t.platformID == 0), None)
if not unicode_tbl:
    raise RuntimeError("Unicode cmapが見つかりません。")

# format 4
if not any(t.platformID == 3 and t.platEncID == 1 and t.format == 4 for t in cmap_table.tables):
    sub4 = CmapSubtable.newSubtable(4)
    sub4.platformID = 3
    sub4.platEncID = 1
    sub4.language = 0
    sub4.cmap = dict(unicode_tbl.cmap)
    cmap_table.tables.append(sub4)
    print("[*] Windows用format4 cmapを追加しました。")

# format 12（32bit Unicode用）
if not any(t.platformID == 3 and t.platEncID == 10 and t.format == 12 for t in cmap_table.tables):
    sub12 = CmapSubtable.newSubtable(12)
    sub12.platformID = 3
    sub12.platEncID = 10
    sub12.language = 0
    sub12.cmap = dict(unicode_tbl.cmap)
    cmap_table.tables.append(sub12)
    print("[*] Windows用format12 cmapを追加しました。")

# --- 3. nameテーブル英語化 ---
new_names = {
    1: "Sakalti",
    2: "Regular",
    4: "Sakalti Regular",
    6: "Sakalti-Regular"
}
for nid, text in new_names.items():
    font["name"].setName(text, nid, 3, 1, 0x0409)  # Windows Unicode
    font["name"].setName(text, nid, 1, 0, 0)       # Macintosh Roman

print("[*] フォント名を英語化しました。")

# --- 4. 不要テーブル削除 ---
for t in ["TSI0", "TSI1", "TSI2", "TSI3"]:
    if t in font:
        del font[t]
        print(f"[*] 不要テーブル {t} を削除しました。")

# 保存
font.save(OUTPUT_PATH)
print(f"[+] 変換完了: {OUTPUT_PATH}")
