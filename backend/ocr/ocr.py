from fastapi import UploadFile
from PIL import Image
import pytesseract
import io

from .ocr_utils import check_tesseract_installed
from .language_detection import detect_tesseract_lang
from .preprocessing import preprocess_image


def extract_text(file: UploadFile) -> str:
    """
    Main OCR entry point for images.
    """
    check_tesseract_installed()

    contents = file.file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")

    processed = preprocess_image(image)
    lang = detect_tesseract_lang(processed)

    text = pytesseract.image_to_string(processed, lang=lang)
    return text.strip()
