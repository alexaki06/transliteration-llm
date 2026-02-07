# Language Detection - Quick Start Guide

## Overview
This API now automatically detects the language/script of input text and lets users confirm or correct the detection before transliteration.

## Three Simple Workflows

### Option 1: Let API Detect (Simplest)
Just transliterate and the API auto-detects the source language:

```bash
curl -X POST http://localhost:8000/transliterate \
  -F "text=Привет мир" \
  -F "target_script=Latn"

# Response:
{
  "detected_script": "Cyrillic",
  "script_confidence": 0.95,
  "source_script": "Cyrl",
  "transliteration": "Privet mir",
  "explanation": "...",
  "detection_status": "auto-detected"
}
```

### Option 2: Ask User to Confirm (Recommended for UI)
Three-step process with user confirmation:

**Step 1: Detect**
```bash
curl -X POST http://localhost:8000/detect-language \
  -F "text=Привет мир"

# Response shows: detected_script, confidence, available_scripts
```

**Step 2: User Confirms/Corrects**
```bash
# If correct:
curl -X POST http://localhost:8000/confirm-language \
  -H "Content-Type: application/json" \
  -d '{
    "detected_language": "Cyrl",
    "user_confirmed": true
  }'

# If incorrect, user corrects:
curl -X POST http://localhost:8000/confirm-language \
  -H "Content-Type: application/json" \
  -d '{
    "detected_language": "Cyrl",
    "user_confirmed": false,
    "corrected_language": "Latn"
  }'
```

**Step 3: Transliterate**
```bash
curl -X POST http://localhost:8000/transliterate \
  -F "text=Привет мир" \
  -F "source_script=Cyrl" \
  -F "target_script=Latn"
```

### Option 3: Skip Detection (Fastest)
If you already know the source language:

```bash
curl -X POST http://localhost:8000/transliterate \
  -F "text=Привет мир" \
  -F "source_script=Cyrl" \
  -F "target_script=Latn" \
  -F "skip_detection=true"
```

## Available Scripts
```
Latn = Latin        (English, Spanish, French, etc.)
Cyrl = Cyrillic     (Russian, Ukrainian, Serbian, etc.)
Arab = Arabic       (Arabic, Urdu, Persian, etc.)
Hebr = Hebrew       (Hebrew, Yiddish)
Deva = Devanagari   (Hindi, Sanskrit, Marathi)
Grek = Greek        (Greek)
Hani = Han          (Chinese, Japanese Kanji)
Hira = Hiragana     (Japanese)
Kana = Katakana     (Japanese)
Hang = Hangul       (Korean)
```

## Python Example

```python
import requests

API_URL = "http://localhost:8000"

# Step 1: Detect language
response = requests.post(
    f"{API_URL}/detect-language",
    files={"text": "Привет мир"}
)
detection = response.json()
print(f"Detected: {detection['detected_script']} (confidence: {detection['confidence']})")

# Step 2: User confirms
response = requests.post(
    f"{API_URL}/confirm-language",
    json={
        "detected_language": detection["iso_code"],
        "user_confirmed": True
    }
)
confirmation = response.json()
source_script = confirmation["confirmed_source_script"]

# Step 3: Transliterate
response = requests.post(
    f"{API_URL}/transliterate",
    data={
        "text": "Привет мир",
        "source_script": source_script,
        "target_script": "Latn"
    }
)
result = response.json()
print(f"Result: {result['transliteration']}")
print(f"Explanation: {result['explanation']}")
```

## JavaScript/Fetch Example

```javascript
const API_URL = "http://localhost:8000";

async function transliterateWithConfirmation(text, targetScript) {
  // Step 1: Detect
  const detectResp = await fetch(`${API_URL}/detect-language`, {
    method: "POST",
    body: new FormData(Object.assign(new FormData(), { text }))
  });
  const detection = await detectResp.json();
  
  console.log(`Detected: ${detection.detected_script} 
              (confidence: ${detection.confidence})`);
  
  // Assuming user confirmed, Step 2: Confirm language
  const confirmResp = await fetch(`${API_URL}/confirm-language`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      detected_language: detection.iso_code,
      user_confirmed: true
    })
  });
  const confirmation = await confirmResp.json();
  const sourceScript = confirmation.confirmed_source_script;
  
  // Step 3: Transliterate
  const translitBody = new FormData();
  translitBody.append("text", text);
  translitBody.append("source_script", sourceScript);
  translitBody.append("target_script", targetScript);
  
  const translitResp = await fetch(`${API_URL}/transliterate`, {
    method: "POST",
    body: translitBody
  });
  const result = await translitResp.json();
  
  console.log(`Result: ${result.transliteration}`);
  return result;
}

// Usage
transliterateWithConfirmation("Привет мир", "Latn");
```

## Testing in FastAPI Docs

Visit `http://localhost:8000/docs` for interactive testing:
1. Try `/detect-language` with your text
2. Copy the `iso_code` from response
3. Use `/confirm-language` with that code
4. Use `/transliterate` with confirmed source script

## Key Features

✓ **Automatic Detection**: Uses Unicode character ranges  
✓ **Confidence Scores**: Shows how confident detection is (0-1)  
✓ **User Confirmation**: Ask users before transliterating  
✓ **Easy Correction**: Users can switch to different script  
✓ **Multiple Workflows**: Use simple auto-detect or full confirmation  
✓ **Script Aliases**: Accept "Latn" or "Latin", "Cyrl" or "Cyrillic"  
✓ **Error Messages**: Clear guidance on available options  

## Common Issues

**Q: How accurate is the detection?**  
A: >90% for pure-script text. Mixed scripts return dominant. Example: "Привет123" is detected as Cyrillic (confidence 0.67).

**Q: What if language isn't detected correctly?**  
A: Use `/confirm-language` endpoint and provide the correct ISO code or script name.

**Q: Can I skip detection?**  
A: Yes! Use `/transliterate` with `source_script` and `skip_detection=true`.

**Q: What formats does the API accept?**  
A: Text strings and image files (OCR-enabled).

## Need Help?

- Check [LANGUAGE_DETECTION.md](./LANGUAGE_DETECTION.md) for detailed API docs
- Run `test_language_detection.py` for example usage
- Visit `/docs` in FastAPI for interactive testing
