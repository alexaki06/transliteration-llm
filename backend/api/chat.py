from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import asyncio


class ChatMessage(BaseModel):
    role: str  # 'user' | 'assistant' | 'system'
    text: str


class ChatSession:
    def __init__(self, session_id: Optional[str] = None, initial_context: Optional[Dict[str, Any]] = None):
        self.id = session_id or str(uuid.uuid4())
        self.messages: List[ChatMessage] = []
        self.context: Dict[str, Any] = initial_context or {}

    def add_message(self, role: str, text: str):
        msg = ChatMessage(role=role, text=text)
        self.messages.append(msg)
        return msg


class ChatService:
    """In-memory Chat service for MVP. Stores sessions and contextual artifacts (e.g., transliteration results).

    This version can optionally stream replies from an LLM via a `streaming_llm` adapter with an
    `async def stream_generate(prompt) -> AsyncIterator[str]` method. The default behavior falls back to
    simple deterministic replies for environments without an LLM.
    """

    def __init__(self, streaming_llm=None):
        self.sessions: Dict[str, ChatSession] = {}
        self.streaming_llm = streaming_llm

    def create_session(self, initial_context: Optional[Dict[str, Any]] = None) -> str:
        session = ChatSession(initial_context=initial_context)
        self.sessions[session.id] = session
        return session.id

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.sessions.get(session_id)

    def add_context(self, session_id: str, key: str, value: Any):
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        session.context[key] = value

    def add_message(self, session_id: str, role: str, text: str):
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        return session.add_message(role, text)

    async def generate_reply(self, session_id: str, text: str):
        """Async generator that yields assistant reply chunks.

        Yields strings representing partial content. Consumers can track final chunk when iterator completes.
        """
        session = self.get_session(session_id)
        if not session:
            # Fallback: treat as ephemeral session
            session = ChatSession(session_id=session_id)
            self.sessions[session.id] = session

        # store user message
        session.add_message("user", text)

        lower = text.lower()
        # quick context-based answers (no LLM) for direct explanation requests
        if "explain" in lower or "why" in lower or "how" in lower:
            if "transliteration" in session.context:
                expl = session.context["transliteration"].get("explanation")
                if expl:
                    session.add_message("assistant", expl)
                    yield expl
                    return
            if "translation" in session.context:
                expl = session.context["translation"].get("explanation")
                if expl:
                    session.add_message("assistant", expl)
                    yield expl
                    return

        # Build a prompt for the LLM
        prompt = self._build_prompt_from_session(session, text)

        # If we have a streaming LLM adapter, use it to stream back chunks
        if self.streaming_llm:
            async for chunk in self.streaming_llm.stream_generate(prompt):
                session.add_message("assistant", chunk)
                yield chunk
            return

        # Otherwise fall back to deterministic echoing behavior
        reply = f"Assistant: I received your message: '{text}'. How can I help further?"
        session.add_message("assistant", reply)
        # stream the reply in small fragments to mimic streaming
        words = reply.split()
        chunk = []
        max_words = 6
        for i, w in enumerate(words, start=1):
            chunk.append(w)
            if i % max_words == 0 or i == len(words):
                yield " ".join(chunk)
                chunk = []
                await asyncio.sleep(0.03)

    def _build_prompt_from_session(self, session: ChatSession, user_text: str) -> str:
        # Build a simple prompt using available context
        ctx_parts = []
        if "transliteration" in session.context:
            tl = session.context["transliteration"]
            ctx_parts.append(f"Transliteration: {tl.get('transliteration')} Explanation: {tl.get('explanation')}")
        if "translation" in session.context:
            tr = session.context["translation"]
            ctx_parts.append(f"Translation: {tr.get('translation')} Explanation: {tr.get('explanation')}")
        ctx_text = "\n".join(ctx_parts)

        prompt = f"You are a helpful linguistics assistant.\n"
        if ctx_text:
            prompt += f"Context:\n{ctx_text}\n\n"
        prompt += f"User: {user_text}\nAssistant:"
        return prompt


chat_router = APIRouter()

# Create a streaming LLM adapter around the transliteration service's LLM for now
import shutil
from llm.streaming_client import StreamingLLMClient

# Prefer a direct Ollama streaming client when available; otherwise fall back to the adapter
try:
    from llm.ollama_streaming import OllamaStreamingClient
    if shutil.which("ollama"):
        try:
            streaming_adapter = OllamaStreamingClient()
        except Exception:
            # fallback to synchronous adapter using OllamaClient if streaming fails to initialize
            from transliteration.transliteration_service import OllamaClient
            streaming_adapter = StreamingLLMClient(llm_client=OllamaClient())
    else:
        streaming_adapter = None
except Exception:
    # If the Ollama streaming module is not usable, attempt to use the synchronous Ollama client as fallback
    try:
        from transliteration.transliteration_service import OllamaClient
        streaming_adapter = StreamingLLMClient(llm_client=OllamaClient())
    except Exception:
        streaming_adapter = None

service = ChatService(streaming_llm=streaming_adapter)


@chat_router.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")

            # Client asks to initialize a session
            if msg_type == "init":
                initial_context = data.get("context")
                session_id = service.create_session(initial_context=initial_context)
                await ws.send_json({"type": "session", "session_id": session_id})
                continue

            # Client sends a user message
            if msg_type in ("user", "message"):
                session_id = data.get("session_id")
                text = data.get("text", "")

                if not session_id:
                    # create ephemeral session if none provided
                    session_id = service.create_session()
                    await ws.send_json({"type": "session", "session_id": session_id})

                # Stream the reply using the service's async generator
                async for chunk_text in service.generate_reply(session_id, text):
                    # send partial chunk; clients will receive an explicit final marker after generator completes
                    await ws.send_json({"type": "assistant", "text": chunk_text, "partial": True, "session_id": session_id})
                # explicit final marker to indicate the end of the reply
                await ws.send_json({"type": "assistant", "text": "", "partial": False, "session_id": session_id})
                continue

            # unknown message
            await ws.send_json({"type": "error", "message": "Unknown message type"})
    except WebSocketDisconnect:
        return
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
        return
