#!/usr/bin/env python3
import os
import requests
from fontTools.ttLib import TTFont

# ==== パス設定 ====
NOTO_URL = "https://github.com/google/fonts/raw/main/ofl/notosans/NotoSans-Regular.ttf"
NOTO_PATH = os.path.abspath("downloads/noto_sans.ttf")
SRC_FONT_PATH = os.path.abspath("downloads/font.ttf")   # コピー元
OUT_FONT_PATH = os.path.abspath("downloads/font2.ttf")  # 出力先

# ==== 1. Noto Sansをダウンロード ====
print("[*] Downloading Noto Sans...")
os.makedirs("downloads", exist_ok=True)
r = requests.get(NOTO_URL)
r.raise_for_status()
with open(NOTO_PATH, "wb") as f:
    f.write(r.content)
print(f"[OK] Downloaded to {NOTO_PATH}")

# ==== 2. フォントを開く ====
print("[*] Loading Noto Sans font...")
noto_font = TTFont(NOTO_PATH)

# ==== 3. 名前を変更 ====
name_table = noto_font["name"]
for record in name_table.names:
    if record.nameID in (1, 4, 6):  # 1=Font Family, 4=Full Font Name, 6=PostScript Name
        record.string = "jibun font".encode("utf-16-be")

# ==== 4. 既存グリフをすべて削除 ====
# 'glyphOrder'の最初は'.notdef'なので残す
print("[*] Removing existing glyphs from Noto Sans...")
glyph_order = noto_font.getGlyphOrder()
keep_glyphs = {".notdef"}
for glyph_name in glyph_order:
    if glyph_name not in keep_glyphs:
        noto_font["glyf"].glyphs[glyph_name] = noto_font["glyf"].glyphs[".notdef"]

# cmapのマッピングもクリア
cmap_table = noto_font["cmap"]
for table in cmap_table.tables:
    table.cmap.clear()

# ==== 5. コピー元フォントのグリフを読み込み ====
print("[*] Loading source font:", SRC_FONT_PATH)
src_font = TTFont(SRC_FONT_PATH)

# ==== 6. コピー元のグリフをNoto Sansへ追加 ====
print("[*] Copying glyphs...")
src_glyph_order = src_font.getGlyphOrder()
noto_glyf = noto_font["glyf"]
src_glyf = src_font["glyf"]

# グリフ順を統合
new_glyph_order = list(keep_glyphs) + [g for g in src_glyph_order if g not in keep_glyphs]
noto_font.setGlyphOrder(new_glyph_order)

# グリフデータコピー
for glyph_name in src_glyph_order:
    if glyph_name not in noto_glyf.glyphs:
        noto_glyf.glyphs[glyph_name] = src_glyf.glyphs[glyph_name]
    else:
        noto_glyf.glyphs[glyph_name] = src_glyf.glyphs[glyph_name]

# cmapもコピー
for table in noto_font["cmap"].tables:
    table.cmap.update({code: glyph for code, glyph in src_font["cmap"].tables[0].cmap.items()})

# ==== 7. 保存 ====
noto_font.save(OUT_FONT_PATH)
print(f"[OK] Saved to {OUT_FONT_PATH}")
