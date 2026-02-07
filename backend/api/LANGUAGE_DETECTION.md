# Language Detection and Confirmation Flow

## Overview
The transliteration API now includes automatic language/script detection with user confirmation. This allows users to:
1. Upload text or a file
2. Receive auto-detected script/language with confidence score
3. Confirm the detection or switch to a different language
4. Proceed with transliteration using the confirmed language

## New Endpoints

### 1. `/detect-language` (POST)
Detects the script of provided text and asks for user confirmation.

**Request:**
```json
{
  "text": "Привет мир",  // OR
  "file": <binary file content>
}
```

**Response:**
```json
{
  "input_text": "Привет мир",
  "detected_script": "Cyrillic",
  "iso_code": "Cyrl",
  "confidence": 0.95,
  "tesseract_lang": "rus",
  "available_scripts": {
    "Latn": "Latin",
    "Cyrl": "Cyrillic",
    "Arab": "Arabic",
    "Hebr": "Hebrew",
    "Deva": "Devanagari",
    "Grek": "Greek",
    "Hani": "Han (Chinese)",
    "Hira": "Hiragana (Japanese)",
    "Kana": "Katakana (Japanese)",
    "Hang": "Hangul (Korean)"
  },
  "message": "Detected language: Cyrillic (confidence: 0.95). Is this correct?...",
  "instructions": {
    "next_step": "Call /confirm-language with your confirmation",
    "user_confirmed": "Set to true if detection is correct, false to correct it",
    "corrected_language": "If user_confirmed=false, provide ISO code (e.g., 'Latn') or script name"
  }
}
```

**Usage Flow:**
1. User submits text/file
2. API detects script and returns confidence
3. User sees available_scripts list
4. User can confirm or provide correction

---

### 2. `/confirm-language` (POST)
User confirms or corrects the detected language.

**Request (if confirmed):**
```json
{
  "detected_language": "Cyrl",
  "user_confirmed": true
}
```

**Request (if user wants to correct):**
```json
{
  "detected_language": "Cyrl",
  "user_confirmed": false,
  "corrected_language": "Latn"  // ISO code or script name
}
```

**Response:**
```json
{
  "confirmed_source_script": "Cyrl",
  "message": "Language confirmed: Cyrl. Ready for transliteration.",
  "next_step": "Call /transliterate with text, source_script, and target_script"
}
```

---

### 3. `/transliterate` (POST) - Enhanced
Transliterate text from source to target script. Now supports the `skip_detection` flag.

**Request (with auto-detection):**
```json
{
  "text": "Привет",
  "target_script": "Latn"
  // source_script is auto-detected
}
```

**Request (with user-confirmed language):**
```json
{
  "text": "Привет",
  "source_script": "Cyrl",  // User provided/confirmed
  "target_script": "Latn",
  "skip_detection": true    // Trust user-provided source_script
}
```

**Response:**
```json
{
  "input_text": "Привет",
  "detected_script": "Cyrillic",
  "script_confidence": 0.95,
  "source_script": "Cyrl",
  "target_script": "Latn",
  "transliteration": "Privet",
  "explanation": "Cyrillic 'П' → 'P', 'р' → 'r'...",
  "session_id": "abc123",
  "detection_status": "auto-detected"
}
```

---

## Supported Scripts

The API supports detection and transliteration for:
| ISO Code | Script Name | Example |
|----------|------------|---------|
| Latn | Latin | Hello |
| Cyrl | Cyrillic | Привет |
| Arab | Arabic | مرحبا |
| Hebr | Hebrew | שלום |
| Deva | Devanagari | नमस्ते |
| Grek | Greek | Γεια |
| Hani | Han (Chinese) | 你好 |
| Hira | Hiragana (Japanese) | ひらがな |
| Kana | Katakana (Japanese) | カタカナ |
| Hang | Hangul (Korean) | 안녕 |

---

## Usage Example: Complete Flow

```
Step 1: Detect Language
POST /detect-language
{
  "text": "Привет мир"
}

Response: {
  "detected_script": "Cyrillic",
  "iso_code": "Cyrl",
  "confidence": 0.95,
  "available_scripts": {...}
}

Step 2: User confirms detection is correct
POST /confirm-language
{
  "detected_language": "Cyrl",
  "user_confirmed": true
}

Response: {
  "confirmed_source_script": "Cyrl",
  "message": "Language confirmed"
}

Step 3: Transliterate with confirmed language
POST /transliterate
{
  "text": "Привет мир",
  "source_script": "Cyrl",
  "target_script": "Latn"
}

Response: {
  "transliteration": "Privet mir",
  "explanation": "Phonetic transliteration from Cyrillic to Latin...",
  "session_id": "abc123"
}
```

---

## Alternative: One-Step Transliteration

If users are confident about the source language, they can still use `/transliterate` directly:

```
POST /transliterate
{
  "text": "Привет",
  "source_script": "Cyrl",
  "target_script": "Latn",
  "skip_detection": true
}
```

This skips auto-detection and uses the provided `source_script` directly.

---

## Implementation Notes

### Detection Algorithm
- Uses Unicode ranges to identify script blocks
- Returns confidence score (0-1) based on character distribution
- Supports multi-script text (returns dominant script)

### Confidence Score
- Calculated as: `characters_in_script / total_characters`
- Example: "Привет123" → Cyrillic confidence = 6/9 = 0.67

### Error Handling
- If user provides invalid ISO code, API returns helpful error with available options
- If both `text` and `file` are missing, API returns error
- Normalization handles common variations (e.g., "Latin" → "Latn", "cyrillic" → "Cyrl")

---

## Future Enhancements
- [ ] Language code detection (e.g., detect Russian vs Bulgarian using Cyrillic)
- [ ] Mixed-script handling (e.g., "Hello мир" → suggest dominant + minority)
- [ ] User history/preferences to improve confidence scores
- [ ] Integration with language-specific tokenizers
