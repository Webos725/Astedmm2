#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont
from fontTools.misc import timeTools
from fontTools.ttLib.tables.O_S_2f_2 import Panose

FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"{FONT_PATH} が見つかりません")

font = TTFont(FONT_PATH)

# ===== nameテーブル設定 =====
name_table = font["name"]
new_family_name = "Conlangg Universal"
new_subfamily_name = "Regular"
full_name = f"{new_family_name} {new_subfamily_name}"
postscript_name = f"{new_family_name.replace(' ', '')}-{new_subfamily_name}"

for record in name_table.names:
    try:
        if record.nameID == 1:
            record.string = new_family_name.encode(record.getEncoding())
        elif record.nameID == 2:
            record.string = new_subfamily_name.encode(record.getEncoding())
        elif record.nameID == 4:
            record.string = full_name.encode(record.getEncoding())
        elif record.nameID == 6:
            record.string = postscript_name.encode(record.getEncoding())
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

# Panose をオブジェクトで設定
p = Panose()
p.bFamilyType = 2      # Latin Text
p.bSerifStyle = 11     # Normal Sans
p.bWeight = 5          # Medium
p.bProportion = 3
p.bContrast = 2
p.bStrokeVariation = 2
p.bArmStyle = 4
p.bLetterForm = 2
p.bMidline = 2
p.bXHeight = 4
os2.panose = p

# Unicode 全範囲サポート
os2.ulUnicodeRange1 = 0xFFFFFFFF
os2.ulUnicodeRange2 = 0xFFFFFFFF
os2.ulUnicodeRange3 = 0xFFFFFFFF
os2.ulUnicodeRange4 = 0xFFFFFFFF

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

# 保存
font.save(FONT_PATH)
print(f"[OK] {FONT_PATH} を更新しました")
