#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont
from fontTools.misc import timeTools
from fontTools.ttLib.tables.O_S_2f_2 import Panose

FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"{FONT_PATH} が見つかりません")

# 独自に簡易版 getUnicodeRanges 実装
def getUnicodeRanges(codepoints):
    # 参考: https://docs.microsoft.com/en-us/typography/opentype/spec/os2#ulunicoderange1-ulunicoderange4
    # ここでは単純に範囲内に1が立つビットセットを返すのみ。
    ulUnicodeRange1 = 0
    ulUnicodeRange2 = 0
    ulUnicodeRange3 = 0
    ulUnicodeRange4 = 0

    for cp in codepoints:
        if 0x0000 <= cp <= 0x007F:
            ulUnicodeRange1 |= 1 << 0  # Basic Latin
        elif 0x0080 <= cp <= 0x00FF:
            ulUnicodeRange1 |= 1 << 1  # Latin-1 Supplement
        elif 0x0100 <= cp <= 0x017F:
            ulUnicodeRange1 |= 1 << 2  # Latin Extended-A
        elif 0x0180 <= cp <= 0x024F:
            ulUnicodeRange1 |= 1 << 3  # Latin Extended-B
        elif 0x0400 <= cp <= 0x04FF:
            ulUnicodeRange1 |= 1 << 6  # Cyrillic
        elif 0x0500 <= cp <= 0x052F:
            ulUnicodeRange1 |= 1 << 7  # Cyrillic Supplementary
        elif 0x0370 <= cp <= 0x03FF:
            ulUnicodeRange1 |= 1 << 9  # Greek and Coptic
        elif 0x2000 <= cp <= 0x206F:
            ulUnicodeRange1 |= 1 << 14  # General Punctuation
        elif 0x1F00 <= cp <= 0x1FFF:
            ulUnicodeRange1 |= 1 << 15  # Greek Extended
        elif 0x0400 <= cp <= 0x04FF:
            ulUnicodeRange1 |= 1 << 20  # Cyrillic (again)
        elif 0x0600 <= cp <= 0x06FF:
            ulUnicodeRange2 |= 1 << 3   # Arabic
        elif 0x0900 <= cp <= 0x097F:
            ulUnicodeRange2 |= 1 << 10  # Devanagari
        # 必要に応じてビットを増やしてください

    return ulUnicodeRange1, ulUnicodeRange2, ulUnicodeRange3, ulUnicodeRange4


font = TTFont(FONT_PATH, lazy=True)

# 元の cmap のコードポイントを保持
codepoints = set()
for table in font['cmap'].tables:
    codepoints.update(table.cmap.keys())

# ===== nameテーブル設定 =====
name_table = font["name"]
new_family_name = "Conlangg Universal"
new_subfamily_name = "Regular"
full_name = f"{new_family_name} {new_subfamily_name}"
postscript_name = f"{new_family_name.replace(' ', '')}-{new_subfamily_name}"

for record in name_table.names:
    try:
        encoding = "utf_16_be"  # 安定エンコード固定
        if record.nameID == 1:
            record.string = new_family_name.encode(encoding)
        elif record.nameID == 2:
            record.string = new_subfamily_name.encode(encoding)
        elif record.nameID == 4:
            record.string = full_name.encode(encoding)
        elif record.nameID == 6:
            record.string = postscript_name.encode(encoding)
        elif record.nameID == 0:
            record.string = b"Public Domain / Open License"
    except Exception:
        pass

# ===== OS/2テーブル設定 =====
os2 = font["OS/2"]
os2.usWeightClass = 400
os2.usWidthClass = 5
os2.fsType = 0
os2.ySubscriptXSize = 650
os2.ySubscriptYSize = 699
os2.ySuperscriptXSize = 650
os2.ySuperscriptYSize = 699

# Panose 設定
p = Panose()
p.bFamilyType = 2
p.bSerifStyle = 11
p.bWeight = 5
p.bProportion = 3
p.bContrast = 2
p.bStrokeVariation = 2
p.bArmStyle = 4
p.bLetterForm = 2
p.bMidline = 2
p.bXHeight = 4
os2.panose = p

# Unicode Range → 自前実装 getUnicodeRanges 関数で設定
ulUnicodeRange1, ulUnicodeRange2, ulUnicodeRange3, ulUnicodeRange4 = getUnicodeRanges(codepoints)
os2.ulUnicodeRange1 = ulUnicodeRange1
os2.ulUnicodeRange2 = ulUnicodeRange2
os2.ulUnicodeRange3 = ulUnicodeRange3
os2.ulUnicodeRange4 = ulUnicodeRange4

# ===== headテーブル設定 =====
head = font["head"]
head.fontRevision = 1.000
now_timestamp = timeTools.timestampNow()
head.created = now_timestamp
head.modified = now_timestamp

# ===== postテーブル設定 =====
post = font["post"]
post.isFixedPitch = 0
post.italicAngle = 0

# 保存（未参照グリフ削除しないように reorderTables=False）
font.save(FONT_PATH, reorderTables=False)

print(f"[OK] {FONT_PATH} を更新しました")
