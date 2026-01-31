from fastapi import FastAPI
from pydantic import BaseModel
from .transliteration.transliteration_service import TransliterationService, OllamaClient

app = FastAPI()

# Initialize Ollama client and service
llm_client = OllamaClient(model="mistral")
transliteration_service = TransliterationService(llm_client=llm_client)


class TransliterationRequest(BaseModel):
    text: str
    source_script: str
    target_script: str
    context: str | None = None


@app.post("/transliterate")
async def transliterate(request: TransliterationRequest):
    """Transliterate text between writing systems."""
    result = transliteration_service.transliterate(
        text=request.text,
        source_script=request.source_script,
        target_script=request.target_script,
        context=request.context
    )
    return result

@app.get("/health")
def health():
    return {"status": "ok"}
