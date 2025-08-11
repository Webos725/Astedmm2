#!/usr/bin/env python3
import os
from datetime import datetime
from fontTools.ttLib import TTFont

FONT_PATH = os.path.abspath("downloads/Conlangg.ttf")

if not os.path.exists(FONT_PATH):
    raise FileNotFoundError(f"{FONT_PATH} が見つかりません")

# フォント読み込み
font = TTFont(FONT_PATH)

# ===== nameテーブル設定 =====
name_table = font["name"]

new_family_name = "Conlangg Universal"
new_subfamily_name = "Regular"
full_name = f"{new_family_name} {new_subfamily_name}"
postscript_name = f"{new_family_name.replace(' ', '')}-{new_subfamily_name}"

for record in name_table.names:
    try:
        if record.nameID == 1:  # Family
            record.string = new_family_name.encode(record.getEncoding())
        elif record.nameID == 2:  # Subfamily
            record.string = new_subfamily_name.encode(record.getEncoding())
        elif record.nameID == 4:  # Full name
            record.string = full_name.encode(record.getEncoding())
        elif record.nameID == 6:  # PostScript name
            record.string = postscript_name.encode(record.getEncoding())
        elif record.nameID == 0:  # Copyright
            record.string = b"Public Domain / Open License"
    except Exception:
        pass

# ===== OS/2テーブル設定 =====
os2 = font["OS/2"]
os2.usWeightClass = 400  # Regular
os2.usWidthClass = 5     # Medium
os2.fsType = 0           # Installable embedding
os2.ySubscriptXSize = 650
os2.ySubscriptYSize = 699
os2.ySuperscriptXSize = 650
os2.ySuperscriptYSize = 699
os2.panose = (2, 11, 5, 3, 2, 2, 4, 2, 2, 4)  # Sans-serif Regular

# Unicode範囲（全域）
os2.ulUnicodeRange1 = 0xFFFFFFFF
os2.ulUnicodeRange2 = 0xFFFFFFFF
os2.ulUnicodeRange3 = 0xFFFFFFFF
os2.ulUnicodeRange4 = 0xFFFFFFFF

# ===== headテーブル設定 =====
head = font["head"]
head.fontRevision = 1.000
head.created = head.modified = datetime.utcnow()

# ===== postテーブル設定 =====
post = font["post"]
post.isFixedPitch = 0
post.italicAngle = 0

# ===== 保存 =====
font.save(FONT_PATH)
print(f"[OK] {FONT_PATH} を更新しました")
