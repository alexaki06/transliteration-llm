from typing import Optional
import subprocess
from abc import ABC, abstractmethod

# LLM Client (Ollama)
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


# Translation Service
class TranslationService:
    """Context-aware literary translation service."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or OllamaClient()

    def translate(
        self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None
    ) -> dict:
        prompt = self._build_prompt(text, source_lang, target_lang, context)
        response = self.llm.generate(prompt)

        # Parse response: "translation|explanation"
        parts = response.split("|", 1)
        translation = parts[0].strip()
        explanation = parts[1].strip() if len(parts) > 1 else "No explanation provided."

        return {
            "original_text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "translation": translation,
            "explanation": explanation,
        }

    def _build_prompt(
        self, text: str, source_lang: str, target_lang: str, context: Optional[str] = None
    ) -> str:
        prompt = f"""Translate the following text from {source_lang} to {target_lang} accurately.
Text: "{text}"
"""
        if context:
            prompt += f"Context: {context}\n"

        prompt += """Provide the translated text followed by a brief explanation of your translation choices, separated by a pipe (|).
Format: [translation]|[explanation]

Answer:"""
        return prompt


# Interactive Loop
if __name__ == "__main__":
    service = TranslationService()
    print("=== Interactive Literary Translation Service ===")
    print("Type 'exit' at any time to quit.\n")

    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower().strip() == "exit":
            print("Goodbye!")
            break

        try:
            # Simple parsing for: 'from <source> to <target>: <text>'
            if "from" in user_input and "to" in user_input and ":" in user_input:
                parts = user_input.split(":")
                preamble = parts[0].strip()
                text = ":".join(parts[1:]).strip()  # support colons in text
                source_lang = preamble.split("from")[1].split("to")[0].strip()
                target_lang = preamble.split("to")[1].strip()

                result = service.translate(text, source_lang, target_lang)
                print("\nTranslation:", result["translation"])
                print("Explanation:", result["explanation"], "\n")
            else:
                print("Please use the format: 'from <source> to <target>: <text>'\n")
        except Exception as e:
            print("Error:", e, "\n")
