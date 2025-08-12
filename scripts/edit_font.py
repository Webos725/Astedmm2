#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont
from fontTools.misc import timeTools
from fontTools.ttLib.tables.O_S_2f_2 import Panose

FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"{FONT_PATH} が見つかりません")

def get_unicode_ranges(codepoints):
    ranges = [0, 0, 0, 0]

    for cp in codepoints:
        if 0x0000 <= cp <= 0x007F:
            ranges[0] |= 1 << 0
        elif 0x0080 <= cp <= 0x00FF:
            ranges[0] |= 1 << 1
        elif 0x0100 <= cp <= 0x017F:
            ranges[0] |= 1 << 2
        elif 0x0180 <= cp <= 0x024F:
            ranges[0] |= 1 << 3
        elif 0x0250 <= cp <= 0x02AF:
            ranges[0] |= 1 << 4
        elif 0x0300 <= cp <= 0x036F:
            ranges[0] |= 1 << 5
        elif 0x0370 <= cp <= 0x03FF:
            ranges[0] |= 1 << 6
        elif 0x0400 <= cp <= 0x04FF:
            ranges[0] |= 1 << 7
        elif 0x0530 <= cp <= 0x058F:
            ranges[0] |= 1 << 8
        elif 0x0590 <= cp <= 0x05FF:
            ranges[0] |= 1 << 9
        elif 0x0600 <= cp <= 0x06FF:
            ranges[0] |= 1 << 10
        elif 0x0700 <= cp <= 0x074F:
            ranges[0] |= 1 << 11
        elif 0x0780 <= cp <= 0x07BF:
            ranges[0] |= 1 << 12
        elif 0x0900 <= cp <= 0x097F:
            ranges[0] |= 1 << 13
        elif 0x0980 <= cp <= 0x09FF:
            ranges[0] |= 1 << 14
        elif 0x0A00 <= cp <= 0x0A7F:
            ranges[0] |= 1 << 15
        elif 0x0A80 <= cp <= 0x0AFF:
            ranges[0] |= 1 << 16
        elif 0x0B00 <= cp <= 0x0B7F:
            ranges[0] |= 1 << 17
        elif 0x0B80 <= cp <= 0x0BFF:
            ranges[0] |= 1 << 18
        elif 0x0C00 <= cp <= 0x0C7F:
            ranges[0] |= 1 << 19
        elif 0x0C80 <= cp <= 0x0CFF:
            ranges[0] |= 1 << 20
        elif 0x0D00 <= cp <= 0x0D7F:
            ranges[0] |= 1 << 21
        elif 0x0D80 <= cp <= 0x0DFF:
            ranges[0] |= 1 << 22
        elif 0x0E00 <= cp <= 0x0E7F:
            ranges[0] |= 1 << 23
        elif 0x0E80 <= cp <= 0x0EFF:
            ranges[0] |= 1 << 24
        elif 0x0F00 <= cp <= 0x0FFF:
            ranges[0] |= 1 << 25
        elif 0x1000 <= cp <= 0x109F:
            ranges[0] |= 1 << 26
        elif 0x10A0 <= cp <= 0x10FF:
            ranges[0] |= 1 << 27
        elif 0x1100 <= cp <= 0x11FF:
            ranges[0] |= 1 << 28
        elif 0x1200 <= cp <= 0x137F:
            ranges[0] |= 1 << 29
        elif 0x13A0 <= cp <= 0x13FF:
            ranges[0] |= 1 << 30
        elif 0x1400 <= cp <= 0x167F:
            ranges[0] |= 1 << 31
        # 省略可能。必要なら ulUnicodeRange2～4 の範囲も追加してください。

    return tuple(ranges)


# lazy=False（デフォルト）で読み込み。上書き保存可能に。
font = TTFont(FONT_PATH)

codepoints = set()
for table in font['cmap'].tables:
    codepoints.update(table.cmap.keys())

name_table = font["name"]
new_family_name = "Conlangg Universal"
new_subfamily_name = "Regular"
full_name = f"{new_family_name} {new_subfamily_name}"
postscript_name = f"{new_family_name.replace(' ', '')}-{new_subfamily_name}"

for record in name_table.names:
    try:
        encoding = "utf_16_be"
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

os2 = font["OS/2"]
os2.usWeightClass = 400
os2.usWidthClass = 5
os2.fsType = 0
os2.ySubscriptXSize = 650
os2.ySubscriptYSize = 699
os2.ySuperscriptXSize = 650
os2.ySuperscriptYSize = 699

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

ulUnicodeRange1, ulUnicodeRange2, ulUnicodeRange3, ulUnicodeRange4 = get_unicode_ranges(codepoints)
os2.ulUnicodeRange1 = ulUnicodeRange1
os2.ulUnicodeRange2 = ulUnicodeRange2
os2.ulUnicodeRange3 = ulUnicodeRange3
os2.ulUnicodeRange4 = ulUnicodeRange4

head = font["head"]
head.fontRevision = 1.000
now_timestamp = timeTools.timestampNow()
head.created = now_timestamp
head.modified = now_timestamp

post = font["post"]
post.isFixedPitch = 0
post.italicAngle = 0

font.save(FONT_PATH, reorderTables=False)

print(f"[OK] {FONT_PATH} を更新しました")
