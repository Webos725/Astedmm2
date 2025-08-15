#!/usr/bin/env python3
import os
import fontforge

SRC_PATH = os.path.abspath("downloads/font.ttf")
DST_PATH = os.path.abspath("outputs/new_font.ttf")

def copy_glyphs_with_fontforge(src_font_path, dst_font_path):
    if not os.path.exists(src_font_path):
        raise FileNotFoundError(f"Source font not found: {src_font_path}")

    # コピー元を開く
    src_font = fontforge.open(src_font_path)

    # 新しい空フォント作成
    dst_font = fontforge.font()
    dst_font.encoding = "UnicodeFull"
    dst_font.fontname = "NewFont"
    dst_font.familyname = "New Font"
    dst_font.fullname = "New Font"

    # グリフコピー
    for glyph in src_font.glyphs():
        if glyph.unicode != -1:  # 実在するUnicodeのみ
            dst_font.createChar(glyph.unicode)
            dst_font[glyph.unicode].clear()
            dst_font.selection.none()
            src_font.selection.none()

            src_font.selection.select(glyph.encoding)
            src_font.copy()
            dst_font.selection.select(glyph.encoding)
            dst_font.paste()

    # 保存
    os.makedirs(os.path.dirname(dst_font_path), exist_ok=True)
    dst_font.generate(dst_font_path)
    print(f"New font created at: {dst_font_path}")

if __name__ == "__main__":
    copy_glyphs_with_fontforge(SRC_PATH, DST_PATH)
