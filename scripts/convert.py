import fontforge
import os

input_path = "downloads/Conlangg.ttf"
output_path = "downloads/Conlang.woff"

if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} が見つかりません")

source_font = fontforge.open(input_path)

new_font = fontforge.font()
new_font.encoding = source_font.encoding
new_font.fontname = source_font.fontname
new_font.familyname = source_font.familyname
new_font.fullname = source_font.fullname

for glyph in source_font.glyphs():
    if glyph.isWorthOutputting():
        new_glyph = new_font.createChar(glyph.unicode, glyph.glyphname)
        new_glyph.width = glyph.width
        glyph.copy()
        new_glyph.paste()

new_font.generate(output_path)

print(f"変換完了: {output_path}")
