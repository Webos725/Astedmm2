#!/usr/bin/env python3
import fontforge
import glob
import os
from PIL import Image

OUTPUT_TTF = "output/MyFont.ttf"
TEMP_SVG_DIR = "temp_svg"
os.makedirs(TEMP_SVG_DIR, exist_ok=True)

# フォント作成
font = fontforge.font()
font.encoding = "UnicodeFull"
font.fontname = "MyFont"
font.fullname = "My Font"
font.familyname = "My Font"

# すべての PNG を取得してソート
images = sorted(glob.glob("Let/*.png"))

def png_to_svg(png_path, svg_path, size=(100, 100)):
    """PNGをSVGに変換して保存 (100x100サイズに合わせる)"""
    img = Image.open(png_path).convert("L")  # グレースケール
    img = img.resize(size)

    # SVG出力 (モノクロしきい値化)
    w, h = img.size
    pixels = img.load()
    with open(svg_path, "w") as f:
        f.write('<?xml version="1.0" standalone="no"?>\n')
        f.write('<svg xmlns="http://www.w3.org/2000/svg" ')
        f.write(f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n')
        f.write('<g fill="black">\n')
        for y in range(h):
            for x in range(w):
                if pixels[x, y] < 128:  # 黒塗り
                    f.write(f'<rect x="{x}" y="{y}" width="1" height="1"/>\n')
        f.write('</g></svg>\n')

# 大文字 A-Z に割り当て
for i, img in enumerate(images[:26]):
    svg_path = os.path.join(TEMP_SVG_DIR, f"A_{i}.svg")
    png_to_svg(img, svg_path)
    glyph = font.createChar(ord('A') + i)
    glyph.importOutlines(svg_path)
    glyph.width = 100  # 横幅100に設定
    glyph.vwidth = 100 # 縦幅100に設定
    glyph.autoHint()

# 小文字 a-z に割り当て
for i, img in enumerate(images[:26]):
    svg_path = os.path.join(TEMP_SVG_DIR, f"a_{i}.svg")
    png_to_svg(img, svg_path)
    glyph = font.createChar(ord('a') + i)
    glyph.importOutlines(svg_path)
    glyph.width = 100
    glyph.vwidth = 100
    glyph.autoHint()

# 出力
os.makedirs(os.path.dirname(OUTPUT_TTF), exist_ok=True)
font.generate(OUTPUT_TTF)
print(f"Font generated: {OUTPUT_TTF}")
