# 🚀 Frontend Quick Start Guide

Get the Streamlit web app running in 2 minutes!

## Step 1: Install Dependencies

```bash
cd frontend
pip install -r requirements.txt
```

## Step 2: Start the Backend API (Terminal 1)

```bash
cd backend
python -m uvicorn main:app --reload
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
Press CTRL+C to quit
```

## Step 3: Start Streamlit App (Terminal 2)

```bash
cd frontend
streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

## Step 4: Use the App

1. Open browser to: **http://localhost:8501**
2. Enter text or upload a file
3. Click "Detect Language"
4. Confirm or correct the language
5. Choose target script
6. Click "Transliterate"
7. View results!

---

## 🎯 Try These Examples

### Example 1: Russian to English
1. Text: `Привет мир`
2. Target: Latin
3. Result: `Privet mir`

### Example 2: Arabic to Latin
1. Text: `مرحبا بك`
2. Target: Latin
3. Result: Transliterated Arabic

### Example 3: Hindi to English
1. Text: `नमस्ते`
2. Target: Latin
3. Result: `namaste`

---

## 📊 Main Features

### ✍️ Translate Tab
- Single text transliteration
- File upload (images/PDFs)
- Language confirmation workflow
- Chat for follow-up questions

### 📚 History Tab
- View all past translations
- See confidence scores
- View explanations
- Export history as JSON

### ⚡ Batch Tab
- Transliterate multiple texts
- Progress tracking
- Download results as JSON
- Bulk processing

### ❓ Help Tab
- Usage guide
- Supported scripts
- Tips for best results
- API documentation links

---

## 🔧 Troubleshooting

### Backend not connecting?
Check that API is running:
```bash
curl http://localhost:8000/health
```

Should return: `{"status": "ok"}`

### Streamlit not starting?
Try:
```bash
streamlit run app.py --logger.level=debug
```

### Need to clear cache?
```bash
streamlit cache clear
```

---

## 📁 Project Structure

```
frontend/
├── app.py              # Main app (run this)
├── requirements.txt    # Dependencies
├── utils/              # Helper modules
│   ├── api_client.py
│   ├── session_manager.py
│   └── ui_components.py
└── README.md           # Full documentation
```

---

## 🎓 What You Can Do

✅ Transliterate text between 10 major writing systems  
✅ Upload images and PDFs for OCR + transliteration  
✅ Get AI-powered explanations for each transliteration  
✅ Process multiple texts in batch  
✅ Ask follow-up questions via chat  
✅ Export results as JSON  
✅ Track translation history  

---

## 💡 Pro Tips

1. **Use Context**: Add context like "place name" or "technical term" for better results
2. **Batch Processing**: Use the Batch tab for multiple translations at once
3. **Export Results**: Download your history for further analysis
4. **Ask Questions**: Use the chat interface to ask about transliteration choices
5. **Check Confidence**: Look at the confidence score to verify detection accuracy

---

## 🌐 Supported Scripts

- Latin → Cyrillic, Arabic, Hebrew, Devanagari, Greek, Han, etc.
- Cyrillic → Latin, Arabic, Hebrew, Devanagari, Greek, Han, etc.
- And all other major writing systems!

---

## 📞 Need Help?

1. Check the **Help** tab in the app
2. Review the [full README.md](README.md)
3. Check API docs at: http://localhost:8000/docs
4. Review FastAPI interactive API documentation

---

**Status**: ✅ Ready to use!  
**Last Updated**: February 7, 2026
