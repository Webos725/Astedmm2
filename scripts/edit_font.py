#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable

INPUT_PATH = os.path.abspath("downloads/font.ttf")
OUTPUT_PATH = os.path.abspath("downloads/font2.ttf")

if not os.path.exists(INPUT_PATH):
    raise FileNotFoundError(f"{INPUT_PATH} が見つかりません")

font = TTFont(INPUT_PATH)

# 1. cmap修正（Windows BMP対応追加）
cmap_table = font["cmap"]
has_format4_win = any(t.platformID == 3 and t.platEncID == 1 and t.format == 4 for t in cmap_table.tables)

if not has_format4_win:
    # Unicodeの最初のサブテーブルをコピーして作成
    unicode_tbl = next((t for t in cmap_table.tables if t.platformID == 0), None)
    if unicode_tbl:
        new_tbl = CmapSubtable.newSubtable(4)
        new_tbl.platformID = 3
        new_tbl.platEncID = 1
        new_tbl.language = 0
        new_tbl.cmap = dict(unicode_tbl.cmap)
        cmap_table.tables.append(new_tbl)
        print("[*] Windows用format4 cmapを追加しました。")
    else:
        raise RuntimeError("Unicode cmapが見つかりません。")

# 2. nameテーブルの英語化
new_names = {
    1: "Sakalti",
    2: "Regular",
    4: "Sakalti Regular",
    6: "Sakalti-Regular"
}
for nid, text in new_names.items():
    font["name"].setName(text, nid, 3, 1, 0x0409)

# 3. 不要テーブル削除（任意）
for t in ["TSI0", "TSI1", "TSI2", "TSI3"]:
    if t in font:
        del font[t]

# 保存
font.save(OUTPUT_PATH)
print(f"[+] 変換完了: {OUTPUT_PATH}")
