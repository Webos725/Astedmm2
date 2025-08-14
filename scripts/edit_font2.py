#!/usr/bin/env python3
import os
import requests
from fontTools.ttLib import TTFont

# ==== パス設定 ====
NOTO_URL = "https://github.com/notofonts/notofonts.github.io/raw/noto-monthly-release-2025.08.01/fonts/NotoSans/hinted/ttf/NotoSans-Regular.ttf"
NOTO_PATH = os.path.abspath("downloads/noto_sans.ttf")
SRC_FONT_PATH = os.path.abspath("downloads/font.ttf")
OUT_FONT_PATH = os.path.abspath("downloads/font2.ttf")

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
for record in noto_font["name"].names:
    if record.nameID in (1, 4, 6):
        record.string = "jibun font".encode("utf-16-be")

# ==== 4. 新しいグリフ順を作成 ====
keep_glyphs = [".notdef"]
src_glyph_order = src_font.getGlyphOrder()
new_glyph_order = keep_glyphs + [g for g in src_glyph_order if g not in keep_glyphs]

# ==== 5. glyf と hmtx を完全作り直し ====
new_glyf = {}
new_hmtx = {}

src_glyf = src_font["glyf"]
src_hmtx = src_font["hmtx"]

# .notdefは元Noto Sansのを使う
new_glyf[".notdef"] = noto_font["glyf"].glyphs[".notdef"]
new_hmtx[".notdef"] = noto_font["hmtx"].metrics[".notdef"]

# コピー元の全グリフ追加
for gname in src_glyph_order:
    if gname == ".notdef":
        continue
    new_glyf[gname] = src_glyf.glyphs[gname]
    if gname in src_hmtx.metrics:
        new_hmtx[gname] = src_hmtx.metrics[gname]
    else:
        new_hmtx[gname] = new_hmtx[".notdef"]

# 置き換え
noto_font["glyf"].glyphs.clear()
noto_font["glyf"].glyphs.update(new_glyf)

noto_font["hmtx"].metrics.clear()
noto_font["hmtx"].metrics.update(new_hmtx)

# ==== 6. cmap更新 ====
src_cmap_data = {}
for table in src_font["cmap"].tables:
    src_cmap_data.update(table.cmap)
for table in noto_font["cmap"].tables:
    table.cmap.clear()
    table.cmap.update(src_cmap_data)

# ==== 7. glyphOrder設定 ====
noto_font.setGlyphOrder(new_glyph_order)

# ==== 8. 保存 ====
noto_font.save(OUT_FONT_PATH)
print(f"[OK] Saved to {OUT_FONT_PATH}")
