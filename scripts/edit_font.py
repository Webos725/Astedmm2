#!/usr/bin/env python3
import os
from fontTools.ttLib import TTFont
from fontTools.misc import timeTools
from fontTools.ttLib.tables.O_S_2f_2 import Panose

FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"{FONT_PATH} が見つかりません")

# lazy=True で開く
font = TTFont(FONT_PATH, lazy=True)

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

# Unicode Range → 実際の cmap に基づく範囲に設定
cmap = font["cmap"]
codepoints = set()
for table in cmap.tables:
    codepoints.update(table.cmap.keys())

# ここでは安全のため、範囲自動設定関数を呼ぶ
from fontTools.ttLib.tables._o_s_2f_2 import getUnicodeRanges
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

# 保存（上書き、テーブル順保持）
font.save(FONT_PATH, reorderTables=False)
print(f"[OK] {FONT_PATH} を更新しました")
