from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="Transliteration LLM API")

# Include router without prefix
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Transliteration LLM API is running. Visit /docs for interactive docs."}

