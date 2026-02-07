from fastapi import FastAPI
from api.routes import router
from api.chat import chat_router

app = FastAPI(title="Transliteration LLM API")

# Include routers without prefix
app.include_router(router)
app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Transliteration LLM API is running. Visit /docs for interactive docs."}

