# scripts/convert.py
import fontforge
import os

# 入力と出力パス
input_path = "downloads/Conlangg.ttf"
output_path = "downloads/Conlang.woff"

if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} が見つかりません")

# 元フォントを開く
source_font = fontforge.open(input_path)

# 新しいフォントを作成
new_font = fontforge.font()
new_font.encoding = source_font.encoding
new_font.fontname = source_font.fontname
new_font.familyname = source_font.familyname
new_font.fullname = source_font.fullname

# グリフをすべてコピー
for glyph in source_font.glyphs():
    new_glyph = new_font.createChar(glyph.unicode, glyph.glyphname)
    new_glyph.width = glyph.width
    new_glyph.importOutlines(glyph.exportTmp())

# WOFF形式で保存
os.makedirs(os.path.dirname(output_path), exist_ok=True)
new_font.generate(output_path)

print(f"変換完了: {output_path}")
