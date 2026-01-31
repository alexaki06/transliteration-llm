from fastapi import UploadFile
from PIL import Image
import pytesseract
import io

from .ocr_utils import check_tesseract_installed
from .preprocessing import preprocess_image
from .language_detection import detect_script


def extract_text(file: UploadFile) -> dict:
    """
    OCR entry point.
    Returns extracted text + detected script metadata.
    """
    check_tesseract_installed()

    contents = file.file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    processed = preprocess_image(image)

    # First-pass OCR in English to get raw text for detection
    raw_text = pytesseract.image_to_string(processed, lang="eng").strip()

    detection = detect_script(raw_text)

    # Second-pass OCR using detected language
    final_text = pytesseract.image_to_string(
        processed,
        lang=detection["tesseract_lang"]
    ).strip()

    return {
        "text": final_text,
        "detected_script": detection["script"],
        "script_confidence": detection["confidence"],
        "iso_15924": detection["iso_15924"],
    }
