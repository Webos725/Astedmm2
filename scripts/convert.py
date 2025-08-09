# scripts/convert.py
from fontTools.ttLib import TTFont
import os

input_path = "downloads/Conlangg.ttf"
output_path = "downloads/Conlangg.woff"

if not os.path.exists(input_path):
    raise FileNotFoundError(f"{input_path} が見つかりません")

os.makedirs(os.path.dirname(output_path), exist_ok=True)

font = TTFont(input_path)
font.flavor = "woff"
font.save(output_path)
print(f"変換完了: {output_path}")
