# Context-Aware Transliteration LLM

A context-aware transliteration backend powered by large language models (LLMs) that supports **text, image, and PDF inputs**.  
The system performs **OCR with automatic language and script detection**, transliterates between writing systems, and provides **clear linguistic explanations** for how and why transliteration decisions were made.

This project is designed as a modular, production-style backend and serves as a portfolio project demonstrating applied NLP, OCR, and LLM integration.

---

##  Features

- **Context-aware transliteration**
  - Uses linguistic context to resolve ambiguities
  - Handles names, phrases, and mixed-script text

- **Automatic script & language detection**
  - Detects writing systems using Unicode analysis
  - Maps scripts to OCR languages and ISO 15924 codes

- **Multi-language OCR**
  - Image and PDF input support
  - Works with Latin, Cyrillic, Arabic, Hebrew, Greek, Devanagari, Chinese, Japanese, and Korean scripts

- **Linguistic explanations**
  - Explains transliteration choices step-by-step
  - Designed for learning and interpretability

- **Unified API**
  - Single endpoint for text or file input
  - Structured JSON output for easy frontend integration

---

##  How It Works 

1. **Input**
   - Raw text **or** uploaded image/PDF
2. **OCR (if needed)**
   - Image preprocessing
   - Language & script detection
   - Text extraction via Tesseract
3. **Script Normalization**
   - Maps detected scripts to ISO 15924 standards
4. **LLM Transliteration**
   - Context-aware transliteration
   - Explanation generation
5. **Structured Output**
   - Original text
   - Detected script & confidence
   - Transliteration result
   - Linguistic explanation

---

##  Technologies Used

- **Python**
- **FastAPI**
- **Large Language Models**
  - Local inference via Ollama (Mistral)
- **OCR**
  - Tesseract (multi-language)
- **Image Processing**
  - OpenCV
  - Pillow
- **PDF Parsing**
  - pdfplumber

---

##  Project Structure

```text
backend/
├─ api/                 # FastAPI routes (includes WebSocket chat at /ws/chat)
├─ ocr/                 # OCR, preprocessing, language detection
├─ transliteration/     # LLM clients and transliteration logic
├─ main.py              # Application entry point
└─ README.md


## Chat WebSocket (MVP)

A lightweight WebSocket chat is available at `/ws/chat`. It supports initializing sessions with optional context (e.g., a transliteration result) and streaming assistant replies in chunks. The transliteration endpoint returns `session_id` so you can follow up about a transliteration directly via chat.

