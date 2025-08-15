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

# ==== 4. src_fontのグリフ名リスト取得 ====
src_glyph_order = src_font.getGlyphOrder()
src_glyph_set = set(src_glyph_order)

# ==== 5. src_fontのglyf/hmtx取得 ====
src_glyf = src_font["glyf"]
src_hmtx = src_font["hmtx"]

# ==== 6. Notoの全グリフに対して、src_fontにあれば上書き ====
for gname in noto_font.getGlyphOrder():
    if gname in src_glyph_set:
        # glyfを上書き
        noto_font["glyf"].glyphs[gname] = src_glyf.glyphs[gname]
        # hmtxを上書き
        if gname in src_hmtx.metrics:
            noto_font["hmtx"].metrics[gname] = src_hmtx.metrics[gname]
        else:
            noto_font["hmtx"].metrics[gname] = (0, 0)  # メトリクスがない場合

# ==== 7. 保存 ====
noto_font.save(OUT_FONT_PATH)
print(f"[OK] Saved to {OUT_FONT_PATH}")
