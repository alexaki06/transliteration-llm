from fastapi import APIRouter
from pydantic import BaseModel

from backend.transliteration.transliteration_service import (
    TransliterationService,
    OllamaClient,
)

router = APIRouter()

llm_client = OllamaClient(model="mistral")
transliteration_service = TransliterationService(llm_client=llm_client)


class TransliterationRequest(BaseModel):
    text: str
    source_script: str
    target_script: str
    context: str | None = None


@router.post("/transliterate")
async def transliterate(request: TransliterationRequest):
    return transliteration_service.transliterate(
        text=request.text,
        source_script=request.source_script,
        target_script=request.target_script,
        context=request.context,
    )
