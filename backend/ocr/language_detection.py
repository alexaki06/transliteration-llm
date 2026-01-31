import unicodedata
from collections import Counter

# Unicode script ranges (simplified but effective)
SCRIPT_RANGES = {
    "Latin": [(0x0041, 0x024F)],
    "Cyrillic": [(0x0400, 0x052F)],
    "Greek": [(0x0370, 0x03FF)],
    "Arabic": [(0x0600, 0x06FF)],
    "Hebrew": [(0x0590, 0x05FF)],
    "Devanagari": [(0x0900, 0x097F)],
    "Han": [(0x4E00, 0x9FFF)],
    "Hiragana": [(0x3040, 0x309F)],
    "Katakana": [(0x30A0, 0x30FF)],
    "Hangul": [(0xAC00, 0xD7AF)],
}

SCRIPT_TO_TESSERACT = {
    "Latin": "eng",
    "Cyrillic": "rus",
    "Greek": "ell",
    "Arabic": "ara",
    "Hebrew": "heb",
    "Devanagari": "hin",
    "Han": "chi_sim",
    "Hiragana": "jpn",
    "Katakana": "jpn",
    "Hangul": "kor",
}

SCRIPT_TO_ISO = {
    "Latin": "Latn",
    "Cyrillic": "Cyrl",
    "Greek": "Grek",
    "Arabic": "Arab",
    "Hebrew": "Hebr",
    "Devanagari": "Deva",
    "Han": "Hani",
    "Hiragana": "Hira",
    "Katakana": "Kana",
    "Hangul": "Hang",
}


def detect_script(text: str) -> dict:
    counts = Counter()

    for char in text:
        code = ord(char)
        for script, ranges in SCRIPT_RANGES.items():
            for start, end in ranges:
                if start <= code <= end:
                    counts[script] += 1

    if not counts:
        return {
            "script": "Unknown",
            "confidence": 0.0,
            "tesseract_lang": "eng",
            "iso_15924": "Latn",
        }

    script, count = counts.most_common(1)[0]
    total = sum(counts.values())

    return {
        "script": script,
        "confidence": round(count / total, 2),
        "tesseract_lang": SCRIPT_TO_TESSERACT.get(script, "eng"),
        "iso_15924": SCRIPT_TO_ISO.get(script, "Latn"),
    }
