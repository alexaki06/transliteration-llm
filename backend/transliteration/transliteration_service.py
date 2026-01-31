"""
Transliteration service with LLM integration.
Handles context-aware transliteration and explanation generation.
"""
from typing import Optional
from abc import ABC, abstractmethod
import subprocess

from backend.ocr.ocr_utils import ocr_from_image, ocr_from_pdf


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class OllamaClient(LLMClient):
    def __init__(self, model: str = "mistral"):
        self.model = model

    def generate(self, prompt: str) -> str:
        try:
            result = subprocess.run(
                ["ollama", "run", self.model],
                input=prompt,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            raise RuntimeError(
                "Ollama executable not found. Make sure Ollama is installed and on PATH."
            )

        if result.returncode != 0:
            raise RuntimeError(f"Ollama error: {result.stderr}")

        return result.stdout.strip()


class TransliterationService:
    SCRIPT_ALIASES = {
        "latin": "Latn", "Latin": "Latn",
        "cyrillic": "Cyrl", "Cyrillic": "Cyrl",
        "arabic": "Arab", "Arabic": "Arab",
        "devanagari": "Deva", "Devanagari": "Deva",
        "greek": "Grek", "Greek": "Grek",
        "hebrew": "Hebr", "Hebrew": "Hebr",
    }

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or OllamaClient()

    def normalize_script_code(self, script: str) -> str:
        if len(script) == 4 and script[0].isupper():
            return script
        normalized = self.SCRIPT_ALIASES.get(script)
        if normalized:
            return normalized
        raise ValueError(
            f"Unknown script: {script}. Use ISO 15924 codes (e.g., 'Latn') or common names."
        )

    def transliterate(
        self, text: str, source_script: str, target_script: str, context: Optional[str] = None
    ) -> dict:
        src = self.normalize_script_code(source_script)
        tgt = self.normalize_script_code(target_script)

        prompt = self._build_prompt(text, src, tgt, context)
        response = self.llm.generate(prompt)

        parts = response.split("|", 1)
        transliteration = parts[0].strip()
        explanation = parts[1].strip() if len(parts) > 1 else "No explanation provided."

        return {
            "original_text": text,
            "source_script": src,
            "target_script": tgt,
            "transliteration": transliteration,
            "explanation": explanation,
        }

    def _build_prompt(
        self, text: str, source_script: str, target_script: str, context: Optional[str] = None
    ) -> str:
        prompt = f"""Transliterate the following text from {source_script} to {target_script}.
Text: "{text}"
"""
        if context:
            prompt += f"Context: {context}\n"

        prompt += """Provide the transliteration followed by a brief explanation of your choices, separated by a pipe (|).
Format: [transliteration]|[explanation]

Answer:"""
        return prompt


class TransliterationApp:
    """Wrapper for OCR + transliteration with multi-language fallback."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.service = TransliterationService(llm_client)

    def process_image(
        self,
        image_path: str,
        source_script: str,
        target_script: str,
        context: Optional[str] = None,
        langs: Optional[str] = None,  # supports multiple languages like "eng+rus"
    ):
        text = ocr_from_image(image_path, lang=langs)

        if not text.strip():
            print("[Warning] OCR returned empty text, retrying with default language...")
            text = ocr_from_image(image_path)

        return self.service.transliterate(text, source_script, target_script, context)

    def process_pdf(
        self,
        pdf_path: str,
        source_script: str,
        target_script: str,
        context: Optional[str] = None,
        langs: Optional[str] = None,  # supports multiple languages like "eng+rus"
    ):
        text = ocr_from_pdf(pdf_path, lang=langs)

        if not text.strip():
            print("[Warning] PDF OCR returned empty text, retrying with default OCR...")
            text = ocr_from_pdf(pdf_path)

        return self.service.transliterate(text, source_script, target_script, context)


# Example usage
if __name__ == "__main__":
    app = TransliterationApp()

    # Test image with Russian text
    result_image = app.process_image(
        "moscow.png", "Cyrillic", "Latin", langs="rus+eng"
    )
    print("Image OCR + Transliteration Result:", result_image)

    # Test PDF with mixed text
    result_pdf = app.process_pdf(
        "example.pdf", "Cyrillic", "Latin", langs="rus+eng"
    )
    print("PDF OCR + Transliteration Result:", result_pdf)
