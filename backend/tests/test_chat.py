import pytest
pytest.importorskip("fastapi")
import json
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_init_session_and_echo():
    with client.websocket_connect("/ws/chat") as ws:
        # initialize session
        ws.send_json({"type": "init"})
        msg = ws.receive_json()
        assert msg["type"] == "session"
        session_id = msg["session_id"]

        # send a user message and receive streaming assistant chunks
        ws.send_json({"type": "user", "session_id": session_id, "text": "Hello there"})

        full_text = ""
        while True:
            chunk = ws.receive_json()
            assert chunk["type"] == "assistant"
            full_text += " " + chunk["text"]
            if not chunk.get("partial", False):
                break

        assert "Hello there" in full_text or "I received your message" in full_text


def test_contextual_explanation_from_init():
    with client.websocket_connect("/ws/chat") as ws:
        # create session with transliteration context
        ws.send_json({
            "type": "init",
            "context": {"transliteration": {"explanation": "Because of fidelity to original orthography."}},
        })
        msg = ws.receive_json()
        assert msg["type"] == "session"
        session_id = msg["session_id"]

        # Ask for explanation
        ws.send_json({"type": "user", "session_id": session_id, "text": "Can you explain the transliteration?"})

        full_text = ""
        while True:
            chunk = ws.receive_json()
            assert chunk["type"] == "assistant"
            full_text += " " + chunk["text"]
            if not chunk.get("partial", False):
                break

        assert "fidelity to original orthography" in full_text


import asyncio
from backend.llm.streaming_client import StreamingLLMClient


class DummyLLMForStream:
    def __init__(self, response: str):
        self.response = response

    def generate(self, prompt: str) -> str:
        return self.response


def test_generate_reply_streams_from_llm():
    response = "This is a long response that should be chunked by the streaming adapter into several parts."
    streaming_adapter = StreamingLLMClient(llm_client=DummyLLMForStream(response), chunk_words=4, delay=0)
    from backend.api.chat import ChatService
    chat_service = ChatService(streaming_llm=streaming_adapter)
    session_id = chat_service.create_session()

    async def collect():
        chunks = []
        async for c in chat_service.generate_reply(session_id, "Please elaborate"):
            chunks.append(c)
        return chunks

    chunks = asyncio.get_event_loop().run_until_complete(collect())

    assert len(chunks) >= 2
    # ensure the concatenation equals the original response when joined
    assert " ".join(chunks).strip() == response
