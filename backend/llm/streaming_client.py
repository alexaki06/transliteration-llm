from typing import AsyncIterator, Optional
import asyncio

from transliteration.transliteration_service import LLMClient


class StreamingLLMClient:
    """Adapter that provides an async streaming interface around an existing LLMClient.

    Current implementation simulates streaming by calling the synchronous `generate` and
    yielding word chunks. Replace or extend this with a real streaming client for your
    provider (Ollama/OpenAI/etc.) when available.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None, chunk_words: int = 6, delay: float = 0.03):
        self.llm = llm_client
        self.chunk_words = chunk_words
        self.delay = delay

    async def stream_generate(self, prompt: str) -> AsyncIterator[str]:
        if not self.llm:
            # fallback deterministic echo
            yield "Assistant: I don't have an LLM configured."
            return

        # Synchronous generation (existing clients) then break into chunks
        response = self.llm.generate(prompt)

        words = response.split()
        chunk = []
        for i, w in enumerate(words, start=1):
            chunk.append(w)
            if i % self.chunk_words == 0 or i == len(words):
                yield " ".join(chunk)
                chunk = []
                # small sleep to simulate streaming
                await asyncio.sleep(self.delay)
