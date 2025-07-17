import os
import random

# 音素セット（b, p を含む）
initials = ["k", "g", "s", "z", "t", "d", "n", "m", "h", "y", "w", "r", "x", "j", "b", "p"]
vowels = ["a", "i", "u", "e", "o"]
dipthongs = ["ua", "uo", "ao", "ai"]
finals = ["s", "l", "ng", "n"]

def generate_pronunciation(existing_prons):
    while True:
        onset = random.choice(initials)
        vowel_part = (
            random.choice(dipthongs) if random.random() < 0.25 else random.choice(vowels)
        )

        if vowel_part == "uo" and random.random() < 0.40:
            pron = onset + "uom"
        else:
            pron = onset + vowel_part
            if random.random() < 0.33:
                pron += random.choice(finals)

        if pron not in existing_prons:
            return pron

def load_existing_pronunciations(path):
    existing = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if " - " in line:
                    key, val = line.strip().split(" - ", 1)
                    existing[key] = val
    return existing

def main():
    svg_dir = "svgs"
    out_file_path = "pronunciations.txt"

    # 既存読み込み
    existing = load_existing_pronunciations(out_file_path)
    used_prons = set(existing.values())

    # 現在のSVG
    svg_files = [f for f in os.listdir(svg_dir) if f.endswith(".svg")]
    svg_keys = [os.path.splitext(f)[0] for f in svg_files]

    # 新規のみ追加
    new_entries = {}
    for char in svg_keys:
        if char not in existing:
            pron = generate_pronunciation(used_prons)
            new_entries[char] = pron
            used_prons.add(pron)

    # 結果をマージ
    full = {**existing, **new_entries}
    with open(out_file_path, "w", encoding="utf-8") as out:
        for k in sorted(full):  # ソートするかはお好みで
            out.write(f"{k} - {full[k]}\n")

    print(f"追加: {len(new_entries)} 件")

if __name__ == "__main__":
    main()
