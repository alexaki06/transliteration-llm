import shutil
import pytest

from backend.llm.ollama_streaming import OllamaStreamingClient


@pytest.mark.skipif(not shutil.which("ollama"), reason="ollama not installed")
def test_ollama_streaming_integration_smoke():
    """Smoke test for environments with Ollama installed. Skipped when not available."""
    client = OllamaStreamingClient(model="mistral")
    # This will actually call ollama; we just ensure it yields (may be empty in some setups)
    async def collect():
        chunks = []
        async for c in client.stream_generate("Hello"):
            chunks.append(c)
        return chunks

    import asyncio

    chunks = asyncio.get_event_loop().run_until_complete(collect())
    assert isinstance(chunks, list)
