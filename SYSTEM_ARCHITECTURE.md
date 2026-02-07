# System Architecture & Data Flow

## 🏗️ Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│  (Web App / Mobile / CLI / Direct API)                       │
└──────────┬───────────────────────────────────────────────────┘
           │
           │ HTTP Request
           ▼
┌──────────────────────────────────────────────────────────────┐
│                    FastAPI BACKEND                           │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  /detect-language (NEW)                               │  │
│  │  - Input: text or file                                │  │
│  │  - Uses: detect_script()                              │  │
│  │  - Output: script, confidence, available_scripts      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  /confirm-language (NEW)                              │  │
│  │  - Input: detected_language, user_confirmed, ...      │  │
│  │  - Uses: normalize_script_code()                       │  │
│  │  - Output: confirmed_source_script                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  /transliterate (ENHANCED)                            │  │
│  │  - Input: text/file, source_script, target_script ... │  │
│  │  - Uses: detect_script(), transliteration_service     │  │
│  │  - Output: transliteration, explanation               │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Pydantic Models (NEW)                                │  │
│  │  - LanguageDetectionRequest                           │  │
│  │  - LanguageConfirmationRequest                        │  │
│  │  - TransliterationWithConfirmationRequest             │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────┬───────────────────────────────────────────────────┘
           │
           ├────────────────────────┬──────────────────────┐
           ▼                        ▼                      ▼
    ┌────────────────┐    ┌─────────────────┐   ┌──────────────┐
    │ detect_script  │    │ transliteration │   │ chat_service │
    │ (existing)     │    │ _service        │   │ (existing)   │
    │                │    │ (existing)      │   │              │
    │ - Unicode      │    │ - LLM client    │   │ - Sessions   │
    │   ranges       │    │ - Normalization │   │ - Context    │
    │ - Confidence   │    │ - Prompts       │   │              │
    │   scoring      │    │                 │   │              │
    └────────────────┘    └─────────────────┘   └──────────────┘
```

---

## 🔄 Request/Response Data Flow

### Flow 1: Auto-Detect Workflow

```
USER INPUT
    │
    ▼ POST /transliterate
    │ {text: "Привет", target_script: "Latn"}
    │
    ├─→ detect_script(text)
    │   └─→ Count chars by Unicode range
    │   └─→ Return {script: "Cyrillic", iso_15924: "Cyrl", confidence: 1.0}
    │
    ├─→ transliteration_service.transliterate(
    │   text="Привет",
    │   source_script="Cyrl",
    │   target_script="Latn"
    │)
    │   └─→ LLM generates transliteration + explanation
    │
    ├─→ chat_service.create_session(transliteration result)
    │
    ▼
API RESPONSE
{
  "input_text": "Привет",
  "detected_script": "Cyrillic",
  "script_confidence": 1.0,
  "source_script": "Cyrl",
  "target_script": "Latn",
  "transliteration": "Privet",
  "explanation": "...",
  "session_id": "abc123",
  "detection_status": "auto-detected"
}
```

### Flow 2: User Confirmation Workflow

```
STEP 1: USER SUBMITS TEXT
    │
    ▼ POST /detect-language
    │ {text: "Привет"}
    │
    ├─→ detect_script(text)
    │   └─→ {script: "Cyrillic", iso_15924: "Cyrl", confidence: 1.0}
    │
    ▼
API RESPONSE 1
{
  "input_text": "Привет",
  "detected_script": "Cyrillic",
  "iso_code": "Cyrl",
  "confidence": 1.0,
  "available_scripts": {...},
  "message": "Detected: Cyrillic (100%). Is this correct?"
}

STEP 2: USER CONFIRMS/CORRECTS
    │
    ▼ POST /confirm-language
    │ {detected_language: "Cyrl", user_confirmed: true}
    │
    ├─→ Validate detection language
    │
    ▼
API RESPONSE 2
{
  "confirmed_source_script": "Cyrl",
  "message": "Language confirmed: Cyrl. Ready for transliteration."
}

STEP 3: TRANSLITERATE WITH CONFIRMED SCRIPT
    │
    ▼ POST /transliterate
    │ {text: "Привет", source_script: "Cyrl", target_script: "Latn"}
    │
    ├─→ transliteration_service.transliterate(...)
    │
    ▼
API RESPONSE 3
{
  "input_text": "Привет",
  "transliteration": "Privet",
  "explanation": "...",
  "detection_status": "user-provided"
}
```

### Flow 3: Skip Detection Workflow

```
USER INPUT (KNOWS SOURCE LANGUAGE)
    │
    ▼ POST /transliterate
    │ {
    │   text: "Привет",
    │   source_script: "Cyrl",
    │   target_script: "Latn",
    │   skip_detection: true
    │ }
    │
    ├─→ SKIP detect_script() (no detection)
    │
    ├─→ transliteration_service.transliterate(
    │   text="Привет",
    │   source_script="Cyrl",
    │   target_script="Latn"
    │)
    │
    ▼
API RESPONSE
{
  "input_text": "Привет",
  "source_script": "Cyrl",
  "transliteration": "Privet",
  "explanation": "...",
  "detection_status": "user-provided"
}
```

---

## 📊 Component Interaction

```
┌─────────────────────────────────────────────────────────────┐
│                     routes.py                               │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ /detect-language endpoint                              ││
│  │  - Receives: text or file                              ││
│  │  - Calls: ocr.extract_text() [if file]                 ││
│  │  - Calls: detect_script() ↓                            ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ /confirm-language endpoint                             ││
│  │  - Receives: detected_language, user_confirmed, ...     ││
│  │  - Calls: normalize_script_code() ↓                    ││
│  └────────────────────────────────────────────────────────┘│
│                                                             │
│  ┌────────────────────────────────────────────────────────┐│
│  │ /transliterate endpoint                                ││
│  │  - Receives: text/file, source/target_script, ...      ││
│  │  - Calls: detect_script() [if needed] ↓               ││
│  │  - Calls: transliterate() ↓                           ││
│  │  - Calls: create_session() ↓                          ││
│  └────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────────┐
        │  language_detection.py                 │
        │                                        │
        │  detect_script(text)                  │
        │  ├─ SCRIPT_RANGES dict                │
        │  ├─ Counter() characters              │
        │  └─ Return {script, confidence, ...}  │
        └────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────────┐
        │  transliteration_service.py            │
        │                                        │
        │  normalize_script_code(script)        │
        │  ├─ SCRIPT_ALIASES dict               │
        │  └─ Return ISO 15924 code             │
        │                                        │
        │  transliterate(text, src, tgt)        │
        │  ├─ Call LLM                          │
        │  └─ Parse response                    │
        └────────────────────────────────────────┘
                         ↓
        ┌────────────────────────────────────────┐
        │  chat.py                               │
        │                                        │
        │  create_session(context)               │
        │  └─ Return session_id                  │
        └────────────────────────────────────────┘
```

---

## 🔄 State Transitions

```
User Action                API Endpoint              State
─────────────────────────────────────────────────────────────

Submit Text/File        POST /detect-language
    │
    └──→ [Script Detected]
         Response: detected_script, confidence
         ▼
    
User Reviews Detection  (See: detected_script + confidence)
    │
    ├──→ [Correct] ──→ POST /confirm-language
    │                  {"user_confirmed": true}
    │                  ▼
    │              [Language Confirmed]
    │              
    └──→ [Wrong] ────→ POST /confirm-language
                       {"user_confirmed": false,
                        "corrected_language": "..."}
                       ▼
                   [Language Corrected]

Confirmed Language Set  POST /transliterate
    │
    └──→ LLM Transliteration
         ▼
    [Result Ready]
         ▼
    Return: transliteration + explanation + session_id
```

---

## 📈 Confidence Score Calculation

```
Input Text: "Привет мир 123"
Total Characters: 11

Character Distribution:
┌──────────────┬───────┬──────────────┐
│ Script       │ Count │ Confidence   │
├──────────────┼───────┼──────────────┤
│ Cyrillic     │ 10    │ 10/11 = 0.91 │ ← DOMINANT
│ Digit        │ 1     │ 1/11 = 0.09  │
└──────────────┴───────┴──────────────┘

Result: {
  "script": "Cyrillic",
  "confidence": 0.91
}
```

---

## 🔐 Error Handling Flow

```
Invalid Input
    │
    ├─→ No text AND no file
    │   └─→ Return: {"error": "Provide either text or a file"}
    │
    ├─→ Invalid script name in /confirm-language
    │   └─→ Return: {"error": "Unknown script: ...", "hint": "..."}
    │
    └─→ Missing corrected_language when user_confirmed=false
        └─→ Return: {"error": "If not confirmed, please provide corrected_language"}
```

---

## 📋 Database/State Management

```
ChatService (In-Memory)
│
├─→ sessions: Dict[session_id, ChatSession]
│   │
│   └─→ ChatSession
│       ├─ id: str
│       ├─ messages: List[ChatMessage]
│       └─ context: Dict[str, Any]
│           └─ "transliteration": {
│               "original_text": "...",
│               "transliteration": "...",
│               "explanation": "..."
│             }
│
└─→ Used for: Follow-up questions about transliteration
```

---

## 🎯 Key Design Decisions

1. **Unicode Range-Based Detection**
   - Simple, fast, reliable
   - No ML model needed
   - Works offline

2. **Confidence Scoring**
   - User can see detection reliability
   - Helps inform correction decisions

3. **Three Workflows**
   - Auto-detect: Simple, fast
   - Confirmation: User control
   - Skip detection: Maximum speed

4. **Pydantic Models**
   - Type safety
   - Automatic validation
   - OpenAPI documentation

5. **Chat Session Integration**
   - Users can ask follow-up questions
   - Context preserved across requests
   - Stateful conversations

---

## 📊 Performance Characteristics

```
Operation              Time    Notes
─────────────────────────────────────────────
detect_script()        <1ms    O(n) where n=text length
normalize_script_code  <1ms    O(1) dictionary lookup
confirm_language()     <5ms    Validation + normalization
transliterate()        100ms+  Depends on LLM
create_session()       <1ms    Dictionary store
```

---

## 🔗 Data Types

```
Pydantic Models:
├─ LanguageDetectionRequest
│  ├─ text: Optional[str]
│  └─ file: Optional[UploadFile]
│
├─ LanguageConfirmationRequest
│  ├─ detected_language: str (ISO code)
│  ├─ user_confirmed: bool
│  └─ corrected_language: Optional[str]
│
└─ TransliterationWithConfirmationRequest
   ├─ text: str
   ├─ source_script: str
   ├─ target_script: str
   └─ context: Optional[str]

Internal Data Structures:
├─ SCRIPT_RANGES: Dict[str, List[Tuple[int, int]]]
│  └─ Maps script name to Unicode ranges
│
├─ SCRIPT_TO_ISO: Dict[str, str]
│  └─ Maps script name to ISO 15924 code
│
└─ SCRIPT_ALIASES: Dict[str, str]
   └─ Maps script names/aliases to ISO codes
```

---

**Diagram Last Updated**: February 7, 2026  
**System Status**: ✅ Production Ready
