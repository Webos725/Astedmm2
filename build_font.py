# build_font.py
import subprocess
import os
import fontforge

OUTPUT_TTF = "fonts/custom_font.ttf"

def find_svg_files():
    result = subprocess.run(["find", ".", "-name", "*.svg"], stdout=subprocess.PIPE, text=True)
    return result.stdout.strip().split('\n')

def get_char_from_filename(filename):
    name = os.path.basename(filename).rsplit('.', 1)[0]
    if name.startswith("U+"):
        return chr(int(name[2:], 16))
    elif len(name) == 1:
        return name
    else:
        raise ValueError(f"{filename} は変換できる形式ではありません")

def build_font(svg_files):
    font = fontforge.font()
    font.encoding = "UnicodeFull"
    font.fontname = "CustomFont"
    font.familyname = "CustomFont"
    font.fullname = "CustomFont"

    for svg_path in svg_files:
        if not svg_path.strip():
            continue
        try:
            ch = get_char_from_filename(svg_path)
            glyph = font.createChar(ord(ch))
            glyph.importOutlines(svg_path)
            glyph.width = 1000
            print(f"✔️ {svg_path} → '{ch}'")
        except Exception as e:
            print(f"⚠️ {svg_path} エラー: {e}")

    os.makedirs("fonts", exist_ok=True)
    font.generate(OUTPUT_TTF)
    print(f"✅ フォント生成完了: {OUTPUT_TTF}")

if __name__ == "__main__":
    svg_files = find_svg_files()
    build_font(svg_files)
