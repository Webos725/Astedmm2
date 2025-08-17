#!/usr/bin/env python3
import os
import sys
import traceback
from fontTools.ttLib import TTFont
from fontTools.pens.cairoPen import CairoPen
import cairo

FONT_PATH = os.path.abspath("downloads/font9.ttf")
OUTPUT_DIR = os.path.abspath("glyph_pngs")


def check_font(path: str):
    print("=== Font Full Check Report ===")
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {path}")
        return False

    try:
        font = TTFont(path, fontNumber=0, lazy=False)
        print(f"[OK] Font loaded successfully: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to load font: {e}")
        traceback.print_exc()
        return False

    # フォントタイプ
    sfntVersion = font.sfntVersion
    if sfntVersion == "\x00\x01\x00\x00":
        font_type = "TrueType (TTF)"
    elif sfntVersion == "OTTO":
        font_type = "OpenType/CFF (OTF)"
    elif sfntVersion == "true":
        font_type = "Apple TrueType"
    else:
        font_type = f"Unknown ({repr(sfntVersion)})"
    print(f"[INFO] Font type: {font_type}")

    # テーブル一覧
    print("[INFO] Available tables:")
    for table in font.keys():
        try:
            length = font.reader.tables[table].length
            print(f"  - {table} (size: {length} bytes)")
        except Exception:
            print(f"  - {table} (size unknown)")

    # 必須テーブル
    required_tables = ["head", "cmap", "hhea", "maxp", "name", "OS/2", "post", "hmtx"]
    print("[INFO] Required table check:")
    for tbl in required_tables:
        if tbl in font:
            print(f"  [OK] {tbl}")
        else:
            print(f"  [MISSING] {tbl}")

    # グリフ数
    try:
        glyph_count = font["maxp"].numGlyphs
        print(f"[INFO] Number of glyphs: {glyph_count}")
    except Exception:
        glyph_count = 0
        print("[WARN] Cannot read glyph count.")

    # .notdef glyph
    try:
        if ".notdef" in font.getGlyphOrder():
            print("[OK] .notdef glyph exists")
        else:
            print("[WARN] .notdef glyph missing")
    except Exception:
        print("[WARN] Cannot verify .notdef glyph")

    # cmap
    try:
        cmap = font.getBestCmap()
        if cmap:
            print(f"[INFO] cmap entries: {len(cmap)}")
            for i, (cp, name) in enumerate(cmap.items()):
                if i >= 5:
                    break
                print(f"    U+{cp:04X} -> {name}")
        else:
            print("[WARN] cmap empty")
    except Exception:
        print("[WARN] Cannot read cmap")

    # メトリクス
    try:
        hhea = font["hhea"]
        print(f"[INFO] Metrics: Ascender={hhea.ascent}, Descender={hhea.descent}, LineGap={hhea.lineGap}")
    except Exception:
        print("[WARN] Cannot read hhea metrics")

    # 名前テーブル
    try:
        name_table = font["name"]
        print("[INFO] Name table entries:")
        for record in name_table.names:
            try:
                value = record.toUnicode()
            except Exception:
                value = record.string.decode("latin-1", errors="replace")
            print(f"  - NameID {record.nameID}: {value}")
    except Exception:
        print("[WARN] Cannot read name table")

    # bbox
    try:
        head = font["head"]
        bbox = (head.xMin, head.yMin, head.xMax, head.yMax)
        print(f"[INFO] Font bounding box: {bbox}")
    except Exception:
        print("[WARN] Cannot read bounding box.")

    # === グリフ形状確認 ===
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        glyph_set = font.getGlyphSet()

        print(f"[INFO] Saving glyph shapes to: {OUTPUT_DIR}")
        for i, glyph_name in enumerate(glyph_set.keys()):
            if i >= 50:  # CI 負荷を避けるため最初の 50 glyph のみ保存
                print("[INFO] Limit reached: only first 50 glyphs saved as PNG")
                break

            glyph = glyph_set[glyph_name]
            width, height = 512, 512

            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)

            # 白背景
            ctx.set_source_rgb(1, 1, 1)
            ctx.paint()

            # 座標を中心に移動 & スケーリング
            ctx.translate(width // 2, height // 2)
            ctx.scale(0.05, -0.05)  # glyph を見やすく縮小 & Y軸反転

            pen = CairoPen(glyph_set, ctx)
            glyph.draw(pen)

            # 黒色で塗りつぶし
            ctx.set_source_rgb(0, 0, 0)
            ctx.fill()

            out_path = os.path.join(OUTPUT_DIR, f"{i:03d}_{glyph_name}.png")
            surface.write_to_png(out_path)

        print("[OK] Glyph PNG export complete")

    except Exception as e:
        print(f"[WARN] Failed to render glyphs: {e}")
        traceback.print_exc()

    font.close()
    print("=== Check complete ===")
    return True


if __name__ == "__main__":
    ok = check_font(FONT_PATH)
    sys.exit(0 if ok else 1)
