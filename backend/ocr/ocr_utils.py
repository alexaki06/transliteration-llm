from typing import Optional
from PIL import Image
import pytesseract
import pdfplumber

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
def ocr_from_image(image_path: str, lang: Optional[str] = None) -> str:
    """
    Extract text from an image using pytesseract.
    Args:
        image_path: Path to image file
        lang: Optional Tesseract language code (e.g., 'eng', 'rus', 'ara')
    Returns:
        Extracted text as string
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=lang) if lang else pytesseract.image_to_string(img)
    return text.strip()


def ocr_from_pdf(pdf_path: str, lang: Optional[str] = None) -> str:
    """
    Extract text from a PDF using pdfplumber.
    Args:
        pdf_path: Path to PDF file
        lang: Optional Tesseract language code for OCR on scanned pages
    Returns:
        Extracted text as string
    """
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                # If page is scanned image, run OCR on image
                page_image = page.to_image(resolution=300).original
                text += pytesseract.image_to_string(page_image, lang=lang) + "\n"
    return text.strip()
