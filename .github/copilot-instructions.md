# Copilot Instructions for Transliteration LLM

## Project Overview
A FastAPI-based context-aware transliteration service that converts text between writing systems while providing linguistic explanations. Current phase focuses on text-based transliteration; OCR and PDF support are planned features.

## Architecture
- **Backend**: `backend/main.py` - Single FastAPI application with modular expansion potential
- **Current State**: MVP with skeleton endpoint `/transliterate` accepting `TransliterationRequest` (text, source_script, target_script)
- **Response Format**: JSON with original_text, transliteration, and explanation fields

## Key Development Patterns

### Pydantic Models for Input Validation
Use Pydantic `BaseModel` for all request/response schemas. Currently:
- `TransliterationRequest`: text (str), source_script (str), target_script (str)
- Future additions should maintain this pattern (e.g., `TransliterationResponse`, context fields)

### API Endpoints
- POST `/transliterate` is the primary endpoint
- Design new endpoints following REST conventions
- Return consistent JSON responses with explanation fields for all transliteration decisions

## Dependencies & Technologies
- **FastAPI**: Web framework (not yet in requirements.txt - add it)
- **Pydantic**: Data validation
- **LLMs**: TBD (API-based integration)
- **OCR**: Tesseract/EasyOCR (planned, not yet implemented)
- **PDF Parsing**: TBD (planned)

## Critical Developer Workflows

### Setup
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Current Gaps
- requirements.txt is empty - add: fastapi, uvicorn, pydantic, and any LLM/OCR libraries
- `/transliterate` endpoint returns hardcoded "TODO" - implement actual transliteration logic
- No LLM client or service layer yet needed

## Immediate Next Steps (If Implementing)
1. Populate requirements.txt with framework dependencies
2. Create service layer (e.g., `transliteration_service.py`) for LLM integration logic
3. Implement LLM API calls (provider TBD) for transliteration and explanation generation
4. Add context field to `TransliterationRequest` (currently commented out)
5. Add comprehensive error handling for missing/invalid scripts

## Conventions
- Keep endpoint logic thin; delegate to service classes
- Use descriptive variable names matching linguistic terminology (source_script, target_script, not src, tgt)
- Document script naming conventions (ISO 15924 codes vs common names?)
