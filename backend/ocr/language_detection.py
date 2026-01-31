from typing import Optional

# Unicode ranges for dominant script detection
SCRIPT_RANGES = {
    "Latn": [(0x0041, 0x007A)],
    "Cyrl": [(0x0400, 0x04FF)],
    "Arab": [(0x0600, 0x06FF)],
    "Deva": [(0x0900, 0x097F)],
    "Grek": [(0x0370, 0x03FF)],
    "Hebr": [(0x0590, 0x05FF)],
    "Hang": [(0xAC00, 0xD7AF)],
    "Jpan": [(0x3040, 0x30FF), (0x4E00, 0x9FFF)],
    "Hans": [(0x4E00, 0x9FFF)],
    "Hant": [(0x4E00, 0x9FFF)],
    "Thai": [(0x0E00, 0x0E7F)],
    "Taml": [(0x0B80, 0x0BFF)],
    "Telu": [(0x0C00, 0x0C7F)],
    "Knda": [(0x0C80, 0x0CFF)],
    "Mlym": [(0x0D00, 0x0D7F)],
}


# Default OCR language per script
SCRIPT_TO_TESSERACT = {
    "Latn": "eng",
    "Cyrl": "rus",
    "Arab": "ara",
    "Deva": "hin",
    "Grek": "ell",
    "Hebr": "heb",
    "Hang": "kor",
    "Jpan": "jpn",
    "Hans": "chi_sim",
    "Hant": "chi_tra",
    "Thai": "tha",
    "Taml": "tam",
    "Telu": "tel",
    "Knda": "kan",
    "Mlym": "mal",
}


MULTI_LANG_FALLBACK = (
    "eng+rus+ara+hin+jpn+kor+chi_sim+chi_tra+tha+tam+tel+kan+mal"
)


def detect_script(text: str) -> Optional[str]:
    """
    Detect dominant script using Unicode ranges.
    """
    counts = {script: 0 for script in SCRIPT_RANGES}

    for char in text:
        code = ord(char)
        for script, ranges in SCRIPT_RANGES.items():
            for start, end in ranges:
                if start <= code <= end:
                    counts[script] += 1

    script = max(counts, key=counts.get)
    return script if counts[script] > 0 else None


def script_to_tesseract_lang(script: Optional[str]) -> str:
    """
    Map detected script to Tesseract OCR language.
    """
    if script and script in SCRIPT_TO_TESSERACT:
        return SCRIPT_TO_TESSERACT[script]
    return MULTI_LANG_FALLBACK
