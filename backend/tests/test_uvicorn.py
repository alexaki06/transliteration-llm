import pytest
pytest.importorskip("fastapi")
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}
