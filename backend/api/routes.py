from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional

from ocr.ocr import extract_text
from transliteration.transliteration_service import TransliterationService
from api.chat import service as chat_service
from ocr.language_detection import detect_script

router = APIRouter()
transliteration_service = TransliterationService()


# Pydantic models for language detection confirmation flow
class LanguageDetectionRequest(BaseModel):
    """Request model for initial text submission with language detection."""
    text: Optional[str] = None
    file: Optional[UploadFile] = None


class LanguageConfirmationRequest(BaseModel):
    """Request model for confirming or changing detected language."""
    detected_language: str  # The automatically detected script (ISO 15924 code)
    user_confirmed: bool  # True if user confirms, False if they want to change
    corrected_language: Optional[str] = None  # User's correction if not confirmed


class TransliterationWithConfirmationRequest(BaseModel):
    """Request model for transliteration after language confirmation."""
    text: str
    source_script: str  # User-confirmed source script
    target_script: str  # Target script for transliteration
    context: Optional[str] = None


# POST endpoint to detect language and ask for user confirmation
@router.post("/detect-language")
async def detect_language(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
):
    """
    Detect the script/language of provided text or OCR'd file.
    Returns detected language with confidence score and asks user to confirm.
    
    Response includes:
    - detected_script: Name of detected script (e.g., "Latin", "Cyrillic")
    - iso_code: ISO 15924 code (e.g., "Latn", "Cyrl")
    - confidence: Confidence score (0-1)
    - available_scripts: List of common scripts user can switch to
    - message: Asks user to confirm or provide correction
    """
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

    # Available scripts for user to switch to
    available_scripts = {
        "Latn": "Latin",
        "Cyrl": "Cyrillic",
        "Arab": "Arabic",
        "Hebr": "Hebrew",
        "Deva": "Devanagari",
        "Grek": "Greek",
        "Hani": "Han (Chinese)",
        "Hira": "Hiragana (Japanese)",
        "Kana": "Katakana (Japanese)",
        "Hang": "Hangul (Korean)",
    }

    return {
        "input_text": input_text,
        "detected_script": detected["script"],
        "iso_code": detected["iso_15924"],
        "confidence": detected["confidence"],
        "tesseract_lang": detected["tesseract_lang"],
        "available_scripts": available_scripts,
        "message": f"Detected language: {detected['script']} (confidence: {detected['confidence']}). "
                   f"Is this correct? If not, provide the correct ISO 15924 code or script name from available_scripts.",
        "instructions": {
            "next_step": "Call /confirm-language with your confirmation",
            "user_confirmed": "Set to true if detection is correct, false to correct it",
            "corrected_language": "If user_confirmed=false, provide ISO code (e.g., 'Latn') or script name"
        }
    }


# POST endpoint to confirm/correct detected language
@router.post("/confirm-language")
async def confirm_language(
    request: LanguageConfirmationRequest
):
    """
    User confirms or corrects the detected language.
    Returns the confirmed source script for use in transliteration.
    
    Request:
    - detected_language: Original detected ISO code
    - user_confirmed: True if correct, False to override
    - corrected_language: User's correction (if user_confirmed=False)
    """
    if request.user_confirmed:
        confirmed_script = request.detected_language
        message = f"Language confirmed: {confirmed_script}. Ready for transliteration."
    else:
        if not request.corrected_language:
            return {
                "error": "If not confirmed, please provide corrected_language",
                "example": "corrected_language: 'Latn' or 'Latin'"
            }
        try:
            # Normalize the user's correction
            confirmed_script = transliteration_service.normalize_script_code(request.corrected_language)
            message = f"Language changed to: {confirmed_script}. Ready for transliteration."
        except ValueError as e:
            return {
                "error": str(e),
                "hint": "Use ISO 15924 codes (e.g., 'Latn', 'Cyrl', 'Arab') or common names (e.g., 'Latin', 'Cyrillic')"
            }

    return {
        "confirmed_source_script": confirmed_script,
        "message": message,
        "next_step": "Call /transliterate with text, source_script, and target_script"
    }


# POST endpoint for actual transliteration
@router.post("/transliterate")
async def transliterate(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    target_script: str = Form(...),
    source_script: Optional[str] = Form(None),
    context: Optional[str] = Form(None),
    skip_detection: bool = Form(False),
):
    """
    Transliterate text from source script to target script.
    
    Args:
    - text or file: Input to transliterate
    - target_script: Target script (required)
    - source_script: Source script (optional, auto-detected if not provided)
    - context: Additional context for transliteration
    - skip_detection: If True, use provided source_script without detection
    
    Returns:
    - input_text: The text to transliterate
    - detected_script: Auto-detected script (if not provided)
    - script_confidence: Confidence of detection
    - source_script: Source script used (user-confirmed or auto-detected)
    - target_script: Target script
    - transliteration: The transliterated result
    - explanation: Explanation of transliteration choices
    - session_id: Chat session for follow-up questions
    """
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
    if skip_detection or source_script:
        src_script = source_script or detected["iso_15924"]
    else:
        src_script = detected["iso_15924"]

    result = transliteration_service.transliterate(
        text=input_text,
        source_script=src_script,
        target_script=target_script,
        context=context,
    )

    # Create a chat session containing this transliteration as context so users can ask follow-ups
    session_id = chat_service.create_session(initial_context={"transliteration": result})

    return {
        "input_text": input_text,
        "detected_script": detected["script"],
        "script_confidence": detected["confidence"],
        "source_script": src_script,
        "target_script": target_script,
        "transliteration": result["transliteration"],
        "explanation": result["explanation"],
        "session_id": session_id,
        "detection_status": "auto-detected" if not source_script else "user-provided"
    }


# Optional GET endpoint for browser testing
@router.get("/transliterate")
def transliterate_get():
    return {
        "message": "Send a POST request with 'text' or 'file' and 'target_script' to transliterate."
    }
