# Transliteration Tutor - Streamlit Web App

A beautiful, user-friendly web interface for the transliteration API. Designed as an educational tool for language learners, linguists, and researchers.

## Features

### 🎯 Core Features
- **Text & File Input** - Type text or upload images/PDFs
- **Automatic Language Detection** - Detects 10 major writing systems with confidence scores
- **User Confirmation** - Confirm or correct detected language before transliteration
- **Interactive Transliteration** - Real-time transliteration between writing systems
- **Linguistic Explanations** - AI-generated explanations for transliteration choices
- **Batch Processing** - Transliterate multiple texts at once
- **Chat Interface** - Ask follow-up questions about results
- **History Tracking** - Keep track of all translations
- **Export Functionality** - Download results as JSON

### 🌍 Supported Writing Systems
- **Latin** (Latn) - English, Spanish, French, German, etc.
- **Cyrillic** (Cyrl) - Russian, Ukrainian, Serbian, Bulgarian, etc.
- **Arabic** (Arab) - Arabic, Urdu, Persian, etc.
- **Hebrew** (Hebr) - Hebrew, Yiddish
- **Devanagari** (Deva) - Hindi, Sanskrit, Marathi, etc.
- **Greek** (Grek) - Greek
- **Han** (Hani) - Chinese, Japanese Kanji
- **Hiragana** (Hira) - Japanese Hiragana
- **Katakana** (Kana) - Japanese Katakana
- **Hangul** (Hang) - Korean

### 📚 Use Cases
- **Language Learning** - Learn how different writing systems work
- **Academic Research** - Study transliteration patterns
- **Content Creation** - Convert text between writing systems
- **Professional Translation** - Assist with multilingual content

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- The transliteration backend API running (http://localhost:8000)

### Step 1: Install Frontend Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

### Step 2: Start the Backend API

In a separate terminal:

```bash
cd backend
python -m uvicorn main:app --reload
```

The API should be running at: `http://localhost:8000`

### Step 3: Run Streamlit App

```bash
cd frontend
streamlit run app.py
```

The app will open in your browser at: `http://localhost:8501`

---

## Usage Guide

### Basic Workflow

#### Option 1: Simple Translation
1. Enter text or upload a file
2. Click "Detect Language"
3. Confirm or correct the detected language
4. Choose target script
5. Click "Transliterate"
6. View results and explanation

#### Option 2: Batch Processing
1. Go to "Batch" tab
2. Enter multiple texts (one per line)
3. Choose target script
4. Click "Transliterate Batch"
5. Download results as JSON

#### Option 3: Interactive Chat
1. Complete a translation
2. Use the chat interface to ask follow-up questions
3. Get AI-powered responses about the transliteration

### Features Explained

#### Language Detection
- Automatically detects the source writing system
- Shows confidence score (0-100%)
- Suggests other possible scripts
- User can confirm or correct

#### Transliteration
- Converts text between writing systems
- Uses AI for context-aware decisions
- Provides linguistic explanations
- Shows detection confidence and method

#### Batch Processing
- Process multiple texts efficiently
- Consistent settings for all texts
- Export results as JSON
- Progress tracking

#### History
- All translations are saved automatically
- View past translations with full details
- Export entire history
- Clear history when needed

---

## Project Structure

```
frontend/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/
│   ├── __init__.py
│   ├── api_client.py     # API communication
│   ├── session_manager.py # Session & history management
│   └── ui_components.py  # Reusable UI components
└── README.md             # This file
```

### File Descriptions

#### `app.py` - Main Application
- Streamlit app setup and configuration
- Four main tabs: Translate, History, Batch, Help
- Handles user input and API calls
- Displays results and manages state

#### `utils/api_client.py` - API Client
- HTTP communication with backend
- Methods for language detection, confirmation, transliteration
- Error handling and response parsing
- Health check for API availability

#### `utils/session_manager.py` - Session Management
- Stores translation history
- Manages Streamlit session state
- User preferences storage
- Export/import functionality

#### `utils/ui_components.py` - UI Components
- Reusable Streamlit components
- Language detection display
- Transliteration result display
- File upload, batch input widgets
- Settings and info sections

---

## Configuration

### API Connection
Edit `utils/api_client.py` to change the API URL:

```python
API_BASE_URL = "http://localhost:8000"  # Change this if API is elsewhere
```

### Preferences (Saved in Session)
- **Theme**: Light/Dark/Auto
- **Auto-confirm**: Skip confirmation if confidence > 90%
- **Show Explanations**: Display linguistic explanations
- **Export History**: Download translations as JSON

---

## Advanced Usage

### Custom Settings

```python
# In Streamlit session state
st.session_state.user_preferences = {
    "target_script": "Latn",
    "auto_confirm": True,
    "show_explanations": True,
    "theme": "dark"
}
```

### Batch Processing Script

```python
from utils.api_client import get_api_client

client = get_api_client()

texts = ["Привет", "مرحبا", "नमस्ते"]
target = "Latn"

for text in texts:
    result = client.transliterate(text=text, target_script=target)
    print(result)
```

### Session History Export

```python
from utils.session_manager import SessionManager

history_json = SessionManager.export_history()
# Save to file or use elsewhere
```

---

## Troubleshooting

### API Connection Error
**Problem**: "API Connection Error - The backend API is not running"

**Solution**:
1. Make sure backend is running:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```
2. Check API is on http://localhost:8000
3. Verify `API_BASE_URL` in `utils/api_client.py`

### Language Detection Not Working
**Problem**: Language not detected correctly

**Solution**:
1. Ensure text is not too short (<5 characters)
2. Check confidence score - low confidence may be inaccurate
3. Try providing context information
4. Manually select language if auto-detect fails

### File Upload Issues
**Problem**: Can't upload image/PDF files

**Solution**:
1. Check file size (keep under 10MB)
2. Verify file format (JPG, PNG, PDF supported)
3. For PDFs, ensure it's readable (not corrupted)
4. For images, ensure text is clear and not rotated

### Slow Performance
**Problem**: App is slow to respond

**Solution**:
1. Reduce batch size (process fewer texts at once)
2. Use shorter text inputs
3. Close other applications using RAM
4. Check API response times in browser console

---

## Tips for Best Results

### Text Input
- Provide complete words/sentences (avoid fragments)
- Use context when helpful (place names, technical terms)
- Check spelling - typos may confuse detection

### File Upload
- Ensure good image quality and contrast
- Proper lighting for handwritten text
- OCR works best with clear, printed text
- For PDFs, single-page files are simpler

### Batch Processing
- Keep batch size under 100 texts for best performance
- Use consistent formatting
- Provide context if texts are ambiguous

### Chat Questions
- Ask about specific words or phrases
- Request clarification on transliteration choices
- Inquire about language or script origins
- Get help with linguistic concepts

---

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Language Detection | <1s | Based on text length |
| Transliteration | 1-5s | Depends on LLM response |
| Batch (100 items) | 1-5 min | Parallel processing |
| File Upload | <2s | Size dependent |

---

## Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

**Note**: Works best in modern browsers with JavaScript enabled

---

## Keyboard Shortcuts

- `Ctrl+Enter` in text area: Submit
- `Shift+Click`: Multi-select
- `Ctrl+A`: Select all

---

## Future Enhancements

- [ ] Voice input support
- [ ] Audio output for pronunciation
- [ ] Downloadable PDF reports
- [ ] Mobile app version
- [ ] Collaborative features
- [ ] Custom user vocabularies
- [ ] Language pair favorites
- [ ] Dark mode improvements

---

## Contributing

To contribute improvements:

1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

## License

This project is part of the Transliteration LLM system. See main README for license details.

---

## Support

For issues or questions:
1. Check the Help tab in the app
2. Review backend API documentation
3. Check FastAPI docs at http://localhost:8000/docs
4. Review logs for error messages

---

## System Requirements

### Minimum
- Python 3.8+
- 2GB RAM
- 500MB disk space
- Modern web browser

### Recommended
- Python 3.10+
- 4GB+ RAM
- GPU (for faster LLM responses)
- SSD for faster I/O

---

**Last Updated**: February 7, 2026  
**Status**: ✅ Production Ready
