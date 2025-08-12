#!/usr/bin/env python3
import os
import sys
from fontTools.ttLib import TTFont

FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

def check_table_exists(font, table_name):
    if table_name not in font:
        print(f"[ERROR] Missing table: {table_name}")
        return False
    print(f"[OK] Table found: {table_name}")
    return True

def main():
    if not os.path.exists(FONT_PATH):
        print(f"[FATAL] Font file not found: {FONT_PATH}")
        sys.exit(1)

    print(f"[*] Checking font: {FONT_PATH}")
    try:
        font = TTFont(FONT_PATH)
    except Exception as e:
        print(f"[FATAL] Could not load font: {e}")
        sys.exit(1)

    required_tables = ["cmap", "name", "head", "hhea", "maxp", "hmtx", "OS/2", "post"]
    all_ok = True

    # テーブル存在確認
    for table in required_tables:
        if not check_table_exists(font, table):
            all_ok = False

    # cmap チェック
    if "cmap" in font:
        try:
            cmap_table = font["cmap"]
            subtables = cmap_table.tables
            print(f"[INFO] cmap subtables: {len(subtables)}")
            for st in subtables:
                print(f"  - PlatformID={st.platformID}, EncodingID={st.platEncID}, Format={st.format}, GlyphCount={len(st.cmap)}")
                if not st.cmap:
                    print("    [WARNING] cmap subtable has no mappings.")
        except Exception as e:
            print(f"[ERROR] Failed to read cmap: {e}")
            all_ok = False

    # name テーブル
    if "name" in font:
        try:
            name_table = font["name"]
            for record in name_table.names:
                try:
                    decoded = record.toUnicode()
                except Exception:
                    decoded = record.string
                print(f"  nameID={record.nameID} → {decoded}")
        except Exception as e:
            print(f"[ERROR] Failed to read name table: {e}")
            all_ok = False

    # グリフ一覧出力
    try:
        glyph_order = font.getGlyphOrder()
        print(f"[INFO] Total glyphs: {len(glyph_order)}")
        for i, glyph_name in enumerate(glyph_order):
            print(f"  GID {i}: {glyph_name}")
    except Exception as e:
        print(f"[ERROR] Failed to list glyphs: {e}")
        all_ok = False

    font.close()

    if all_ok:
        print("[SUCCESS] Font appears to have all required tables, mappings, and glyphs.")
    else:
        print("[FAIL] Some tables, mappings, or glyphs are missing/corrupted.")
        sys.exit(1)

if __name__ == "__main__":
    main()
