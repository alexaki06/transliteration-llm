# 🚀 Complete System Setup Guide

Get the entire Transliteration LLM system running end-to-end!

## Overview

The system consists of two main components:
1. **Backend API** - FastAPI transliteration service
2. **Frontend GUI** - Streamlit web application

---

## ⚡ Quick Start (5 Minutes)

### Terminal 1: Start Backend API

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

✅ **API is running at**: http://localhost:8000  
✅ **Docs available at**: http://localhost:8000/docs

### Terminal 2: Start Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Expected output:
```
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

✅ **App is running at**: http://localhost:8501  
✅ **Open in browser**: http://localhost:8501

---

## 🎯 Verify Everything is Working

### Check Backend Health
```bash
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

### Check Frontend Connection
1. Open http://localhost:8501
2. You should see the Transliteration Tutor app
3. No "API Connection Error" message

### Test a Translation
1. In the app, type: "Привет мир"
2. Click "Detect Language" → Should detect Cyrillic
3. Confirm language
4. Select target: "Latin"
5. Click "Transliterate" → Should see "Privet mir"

---

## 📁 System Architecture

```
transliteration-llm/
│
├── backend/                    # FastAPI Server
│   ├── main.py                 # Main application
│   ├── requirements.txt        # Backend dependencies
│   ├── api/
│   │   ├── routes.py           # API endpoints
│   │   └── chat.py             # Chat functionality
│   ├── llm/                    # LLM integration
│   ├── ocr/                    # OCR processing
│   │   └── language_detection.py
│   ├── transliteration/        # Core logic
│   └── tests/                  # Test suite
│
├── frontend/                   # Streamlit Web App
│   ├── app.py                  # Main app
│   ├── requirements.txt        # Frontend dependencies
│   ├── utils/
│   │   ├── api_client.py       # Backend communication
│   │   ├── session_manager.py  # Session handling
│   │   └── ui_components.py    # UI widgets
│   ├── pages/                  # Future multi-page
│   ├── README.md               # Frontend docs
│   └── QUICKSTART.md           # Quick start
│
└── Documentation/              # Guides & docs
    ├── START_HERE.md
    ├── LANGUAGE_DETECTION_README.md
    └── ... (10+ documentation files)
```

---

## 🔌 API Endpoints Overview

### Language Detection
```bash
POST /detect-language
# Input: text or file
# Output: detected_script, iso_code, confidence, available_scripts
```

### Language Confirmation
```bash
POST /confirm-language
# Input: detected_language, user_confirmed, corrected_language
# Output: confirmed_source_script
```

### Transliteration
```bash
POST /transliterate
# Input: text/file, source_script, target_script, context
# Output: transliteration, explanation, session_id
```

### Chat (Follow-ups)
```bash
POST /chat
# Input: session_id, message
# Output: assistant_reply
```

**Full API Docs**: http://localhost:8000/docs

---

## 🎨 Frontend Features

### Main Tabs
- **✍️ Translate** - Single text transliteration
- **📚 History** - View past translations
- **⚡ Batch** - Process multiple texts
- **❓ Help** - Usage guide and info

### Key Features
- ✅ Text and file input (images, PDFs)
- ✅ Automatic language detection
- ✅ User confirmation workflow
- ✅ Language correction/switching
- ✅ Batch processing with progress
- ✅ Chat for follow-up questions
- ✅ Translation history tracking
- ✅ JSON export functionality
- ✅ Settings and preferences
- ✅ Help and documentation

### Supported Scripts
10 major writing systems:
- Latin, Cyrillic, Arabic, Hebrew
- Devanagari, Greek, Han
- Hiragana, Katakana, Hangul

---

## 🧪 Testing the System

### Test 1: Simple Translation
```
1. Frontend: Type "Привет"
2. Detect language → Should show "Cyrillic"
3. Confirm → "Yes"
4. Target: "Latin"
5. Transliterate → Result: "Privet"
```

### Test 2: File Upload
```
1. Frontend: Upload an image with text
2. Detect language → Should OCR and detect
3. Confirm or correct language
4. Choose target script
5. Transliterate
```

### Test 3: Batch Processing
```
1. Frontend → Batch tab
2. Enter texts:
   - Привет
   - مرحبا
   - नमस्ते
3. Target: "Latin"
4. Process → View results table
5. Download as JSON
```

### Test 4: Chat Follow-up
```
1. Complete a translation
2. Ask in chat: "Why did you transliterate it this way?"
3. Get AI explanation
```

---

## 🛠️ Troubleshooting

### Backend Issues

**Backend won't start**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Try different port
python -m uvicorn main:app --port 8001
```

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**LLM not responding**
- Make sure Ollama is installed and running
- Or check LLM configuration

---

### Frontend Issues

**Streamlit won't start**
```bash
# Clear cache
streamlit cache clear

# Run with debug
streamlit run app.py --logger.level=debug
```

**API connection error**
- Check backend is running: `curl http://localhost:8000/health`
- Check API URL in `frontend/utils/api_client.py`
- Check for firewall issues

**Out of memory**
- Close other applications
- Reduce batch size
- Restart Streamlit

---

### Slow Performance

**Detection is slow**
- Check text length (too long?)
- Check API response time at http://localhost:8000/docs

**Transliteration is slow**
- LLM response time is expected (1-5 seconds)
- Check if CPU/GPU is utilized
- May need optimization

---

## 📊 Example Workflows

### Workflow 1: Language Learner
```
1. Frontend → Translate tab
2. Type: "أهلا وسهلا" (Arabic)
3. Detect language → "Arabic (100%)"
4. Select target: "Latin"
5. Transliterate → See romanization
6. Read explanation → Learn about Arabic
7. Ask questions in chat → Get context
```

### Workflow 2: Researcher
```
1. Frontend → Batch tab
2. Upload list of names (Cyrillic)
3. Batch transliterate to Latin
4. Download results as JSON
5. Use in research paper
```

### Workflow 3: Content Creator
```
1. Frontend → Upload PDF
2. OCR extracts text in multiple scripts
3. Transliterate to target audience script
4. Export results
5. Use in content
```

---

## 🔐 Security Notes

- No sensitive data stored locally
- All API calls can be HTTPS (with proper setup)
- File uploads are temporary
- No authentication needed (add as needed)
- Input validation on all endpoints

---

## 📦 Dependencies Overview

### Backend
- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Tesseract** - OCR
- **Ollama** - LLM inference
- **python-dotenv** - Environment variables

### Frontend
- **Streamlit** - Web app framework
- **requests** - HTTP client
- **python-dateutil** - Date utilities

---

## 🚀 Deployment (Optional)

### Production Setup

**Backend**
```bash
# Use Gunicorn + Uvicorn for production
pip install gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

**Frontend**
```bash
# Streamlit Cloud or Docker
# See Streamlit documentation for deployment
```

**Using Docker**
```bash
# Create Dockerfile for backend
# Create Dockerfile for frontend
# Use docker-compose to orchestrate
```

---

## 📈 Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Detection | <1s | Based on text length |
| Transliteration | 1-5s | LLM dependent |
| Batch (10 items) | 15-30s | Sequential |
| Batch (100 items) | 2-5 min | Large batch |
| File upload | <2s | Size dependent |

---

## 🎓 Learning Resources

### In-App Help
- Frontend: Help tab with full guide
- API: http://localhost:8000/docs (interactive)

### Documentation
- Backend: `backend/api/LANGUAGE_DETECTION.md`
- Frontend: `frontend/README.md`
- System: `START_HERE.md`

### Code Examples
- API: `backend/tests/test_language_detection.py`
- Frontend: `frontend/app.py` (well-commented)

---

## ✅ Checklist: System Ready?

- [ ] Backend running on http://localhost:8000
- [ ] Frontend running on http://localhost:8501
- [ ] API health check passes
- [ ] Frontend connects to backend (no error)
- [ ] Test translation works
- [ ] Batch processing works
- [ ] History tracking works
- [ ] Export functionality works

---

## 🎯 Next Steps

1. **Explore the Frontend**
   - Try different translations
   - Experiment with file uploads
   - Test batch processing

2. **Read Documentation**
   - Frontend: `frontend/README.md`
   - Backend: `backend/api/LANGUAGE_DETECTION.md`

3. **Test the API**
   - Open http://localhost:8000/docs
   - Try endpoints interactively

4. **Customize as Needed**
   - Change API URL if needed
   - Adjust UI styling
   - Add new features

---

## 📞 Support

1. **Quick Start**: `frontend/QUICKSTART.md`
2. **Full Guide**: `frontend/README.md`
3. **API Docs**: http://localhost:8000/docs
4. **System Guide**: `START_HERE.md`

---

## 🎉 You're All Set!

The complete Transliteration LLM system is now running!

**Backend API**: http://localhost:8000  
**Frontend GUI**: http://localhost:8501  
**API Docs**: http://localhost:8000/docs

Start transliterating! 🌍

---

**Last Updated**: February 7, 2026  
**Status**: ✅ READY TO USE
