#!/usr/bin/env python3
import os
import requests
from fontTools.ttLib import TTFont

# ==== パス設定 ====
NOTO_URL = "https://github.com/notofonts/notofonts.github.io/raw/noto-monthly-release-2025.08.01/fonts/NotoSans/hinted/ttf/NotoSans-Regular.ttf"
NOTO_PATH = os.path.abspath("downloads/noto_sans.ttf")
SRC_FONT_PATH = os.path.abspath("downloads/font.ttf")   # コピー元
OUT_FONT_PATH = os.path.abspath("downloads/font2.ttf")  # 出力先

os.makedirs("downloads", exist_ok=True)

# ==== 1. Noto Sansをダウンロード ====
print("[*] Downloading Noto Sans...")
r = requests.get(NOTO_URL)
r.raise_for_status()
with open(NOTO_PATH, "wb") as f:
    f.write(r.content)
print(f"[OK] Downloaded to {NOTO_PATH}")

# ==== 2. フォントを開く ====
noto_font = TTFont(NOTO_PATH)
src_font = TTFont(SRC_FONT_PATH)

# ==== 3. 名前を変更 ====
name_table = noto_font["name"]
for record in name_table.names:
    if record.nameID in (1, 4, 6):
        record.string = "jibun font".encode("utf-16-be")

# ==== 4. 既存グリフをすべて消去 ====
keep_glyphs = {".notdef"}
for glyph_name in noto_font.getGlyphOrder():
    if glyph_name not in keep_glyphs:
        noto_font["glyf"].glyphs[glyph_name] = noto_font["glyf"].glyphs[".notdef"]

for table in noto_font["cmap"].tables:
    table.cmap.clear()

# ==== 5. コピー元グリフを追加 ====
src_glyph_order = src_font.getGlyphOrder()
new_glyph_order = list(keep_glyphs) + [g for g in src_glyph_order if g not in keep_glyphs]

# glyfコピー
for glyph_name in src_glyph_order:
    noto_font["glyf"].glyphs[glyph_name] = src_font["glyf"].glyphs[glyph_name]

# hmtxコピー
for glyph_name in src_glyph_order:
    if glyph_name in src_font["hmtx"].metrics:
        noto_font["hmtx"].metrics[glyph_name] = src_font["hmtx"].metrics[glyph_name]
    else:
        # 幅情報がなければ.notdefの幅を使う
        noto_font["hmtx"].metrics[glyph_name] = noto_font["hmtx"].metrics[".notdef"]

# cmapコピー
src_cmap = {}
for table in src_font["cmap"].tables:
    src_cmap.update(table.cmap)
for table in noto_font["cmap"].tables:
    table.cmap.update(src_cmap)

# ==== 6. glyphOrderをセット ====
noto_font.setGlyphOrder(new_glyph_order)

# ==== 7. 保存 ====
noto_font.save(OUT_FONT_PATH)
print(f"[OK] Saved to {OUT_FONT_PATH}")
