import os
import random

# 音素定義
initials = ["k", "g", "s", "z", "t", "d", "n", "m", "h", "y", "w", "r", "x", "j", "b", "p"]
vowels = ["a", "i", "u", "e", "o"]
dipthongs = ["ua", "uo", "ao", "ai"]
finals = ["s", "l", "ng", "n"]
accents = ["1", "2", "3"]

def generate_pronunciation(existing_prons):
    while True:
        # 12%の確率で子音なし
        onset = "" if random.random() < 0.12 else random.choice(initials)

        # 25%で二重母音
        vowel = random.choice(dipthongs) if random.random() < 0.25 else random.choice(vowels)

        if vowel == "uo" and random.random() < 0.40:
            base = onset + "uom"
        else:
            base = onset + vowel
            if random.random() < 0.33:
                base += random.choice(finals)

        accent = random.choice(accents)
        full_pron = base + accent

        if full_pron not in existing_prons:
            return full_pron

def load_existing(path):
    result = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if " - " in line:
                    key, val = line.strip().split(" - ", 1)
                    result[key] = val
    return result

def find_all_svgs():
    svg_names = set()
    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith(".svg"):
                name = os.path.splitext(f)[0]
                svg_names.add(name)
    return svg_names

def main():
    output_file = "pronunciations.txt"
    existing_map = load_existing(output_file)
    used_prons = set(existing_map.values())
    svg_names = find_all_svgs()

    new_entries = {}

    for name in sorted(svg_names):
        if name not in existing_map:
            pron = generate_pronunciation(used_prons)
            new_entries[name] = pron
            used_prons.add(pron)

    if not new_entries:
        print("🔁 新規追加なし")
        return

    # 統合して保存
    merged = {**existing_map, **new_entries}
    with open(output_file, "w", encoding="utf-8") as f:
        for k in sorted(merged):
            f.write(f"{k} - {merged[k]}\n")

    print(f"✅ {len(new_entries)} 件の発音を追加しました")

if __name__ == "__main__":
    main()
