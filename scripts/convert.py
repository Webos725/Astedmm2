import fontforge
import os

input_path = "downloads/Conlangg.ttf"
output_path = "downloads/Conlang.woff"

if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} が見つかりません")

source_font = fontforge.open(input_path)

new_font = fontforge.font()
new_font.encoding = source_font.encoding

# 名前関連をすべてコピー
new_font.fontname = source_font.fontname
new_font.familyname = source_font.familyname
new_font.fullname = source_font.fullname
new_font.appendSFNTName('English (US)', 'Preferred Family', source_font.familyname)
new_font.appendSFNTName('English (US)', 'Preferred Styles', 'Regular')
new_font.appendSFNTName('English (US)', 'Version', source_font.version)

# メトリクスや範囲もコピー
new_font.em = source_font.em
new_font.ascent = source_font.ascent
new_font.descent = source_font.descent
new_font.upos = source_font.upos
new_font.uwidth = source_font.uwidth

# グリフコピー
for glyph in source_font.glyphs():
    if glyph.isWorthOutputting():
        new_glyph = new_font.createChar(glyph.unicode, glyph.glyphname)
        new_glyph.width = glyph.width

        source_font.selection.none()
        source_font.selection.select(glyph.glyphname)
        source_font.copy()

        new_font.selection.none()
        new_font.selection.select(new_glyph.glyphname)
        new_font.paste()

# WOFF保存（メタ情報込み）
os.makedirs(os.path.dirname(output_path), exist_ok=True)
new_font.generate(output_path)

print(f"変換完了: {output_path}")
