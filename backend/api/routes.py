from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

from backend.ocr.ocr import extract_text
from backend.transliteration.transliteration_service import TransliterationService
from backend.ocr.language_detection import detect_script

router = APIRouter()
transliteration_service = TransliterationService()


# POST endpoint for actual transliteration
@router.post("/transliterate")
async def transliterate(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    target_script: str = Form(...),
    source_script: Optional[str] = Form(None),
    context: Optional[str] = Form(None),
):
    if not file and not text:
        return {"error": "Provide either text or a file"}

    # OCR path
    if file:
        ocr_result = extract_text(file)
        input_text = ocr_result["text"]
        detected = ocr_result
    else:
        input_text = text
        detected = detect_script(text)

    # Auto source script unless user overrides
    src_script = source_script or detected["iso_15924"]

    result = transliteration_service.transliterate(
        text=input_text,
        source_script=src_script,
        target_script=target_script,
        context=context,
    )

    return {
        "input_text": input_text,
        "detected_script": detected["script"],
        "script_confidence": detected["confidence"],
        "source_script": src_script,
        "target_script": target_script,
        "transliteration": result["transliteration"],
        "explanation": result["explanation"],
    }


# Optional GET endpoint for browser testing
@router.get("/transliterate")
def transliterate_get():
    return {
        "message": "Send a POST request with 'text' or 'file' and 'target_script' to transliterate."
    }
