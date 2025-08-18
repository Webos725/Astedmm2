#!/usr/bin/env python3
import fontforge
import glob
import os

OUTPUT_TTF = "output/MyFont.ttf"

# フォント作成
font = fontforge.font()
font.encoding = "UnicodeFull"
font.fontname = "MyFont"
font.fullname = "My Font"
font.familyname = "My Font"

# すべての PNG を取得してソート
images = sorted(glob.glob("Let/*.png"))

# 大文字 A-Z に割り当て
for i, img in enumerate(images[:26]):
    glyph = font.createChar(ord('A') + i)
    glyph.importOutlines(img)
    glyph.autoHint()

# 小文字 a-z に割り当て
for i, img in enumerate(images[:26]):
    glyph = font.createChar(ord('a') + i)
    glyph.importOutlines(img)
    glyph.autoHint()

# 出力
os.makedirs(os.path.dirname(OUTPUT_TTF), exist_ok=True)
font.generate(OUTPUT_TTF)
print(f"Font generated: {OUTPUT_TTF}")
