"""
Transliteration LLM - Streamlit Web App
A language learning tool for transliteration between writing systems.
"""

import streamlit as st
import sys
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.api_client import get_api_client, check_api_health
from utils.session_manager import SessionManager, TransliterationSession
from utils.ui_components import (
    display_detection_result,
    language_confirmation_widget,
    display_transliteration_result,
    batch_input_widget,
    file_upload_widget,
    script_selector_widget,
    context_input_widget,
    settings_sidebar,
    info_section,
    display_chat_interface
)


# Page config
st.set_page_config(
    page_title="Transliteration Tutor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.3rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
SessionManager.init_session_state()

# Sidebar settings
settings = settings_sidebar()

# Main content
st.markdown('<div class="main-header">🌍 Transliteration Tutor</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Convert text between writing systems with AI-powered explanations</div>', unsafe_allow_html=True)

# Check API health
if not check_api_health():
    st.error("""
    ❌ **API Connection Error**
    
    The backend API is not running. Please start it with:
    ```bash
    cd backend
    python -m uvicorn main:app --reload
    ```
    
    Make sure the API is running on http://localhost:8000
    """)
    st.stop()

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["✍️ Translate", "📚 History", "⚡ Batch", "❓ Help"])

# ============================================================================
# TAB 1: Main Translation Interface
# ============================================================================
with tab1:
    st.markdown("### 📝 Input Text or Upload File")
    
    # Input options
    input_mode = st.radio(
        "Choose input method:",
        options=["Type Text", "Upload File"],
        horizontal=True,
        key="input_mode"
    )
    
    input_text = None
    file_data = None
    filename = None
    
    if input_mode == "Type Text":
        input_text = st.text_area(
            "Enter text to transliterate",
            height=150,
            placeholder="Type text here... or paste text in any language",
            label_visibility="collapsed"
        )
    else:
        file_upload = file_upload_widget(accepted_types=['txt', 'jpg', 'jpeg', 'png', 'pdf', 'gif', 'bmp'])
        if file_upload:
            file_data, filename = file_upload
            st.success(f"✅ File uploaded: {filename}")
    
    # Proceed to detection
    if (input_text and input_text.strip()) or file_data:
        st.markdown("---")
        
        # Step 1: Language Detection
        st.markdown("### 🔍 Step 1: Language Detection")
        
        if st.button("🔍 Detect Language", key="detect_btn"):
            st.session_state.detect_clicked = True
        
        if st.session_state.get("detect_clicked", False):
            with st.spinner("Detecting language..."):
                client = get_api_client()
                
                if input_text:
                    detection_result = client.detect_language(text=input_text)
                else:
                    detection_result = client.detect_language(file_data=file_data, filename=filename)
            
            if "error" not in detection_result:
                # Store detection result
                st.session_state.detection_result = detection_result
                st.session_state.show_confirmation = True
                
                # Display detection
                display_detection_result(detection_result)
            else:
                st.error(detection_result["error"])
                st.session_state.detect_clicked = False
        
        # Step 2: Language Confirmation
        if st.session_state.get("show_confirmation", False):
            st.markdown("---")
            st.markdown("### ✓ Step 2: Confirm Language")
            
            detection_result = st.session_state.get("detection_result", {})
            confirmed_script = language_confirmation_widget(detection_result)
            
            if confirmed_script:
                st.session_state.confirmed_source_script = confirmed_script
                st.session_state.show_confirmation = False
                st.session_state.show_transliteration = True
                st.rerun()
        
        # Step 3: Choose Target Script and Transliterate
        if st.session_state.get("show_transliteration", False):
            st.markdown("---")
            st.markdown("### 🎯 Step 3: Choose Target Script & Transliterate")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                target_script = script_selector_widget(key_prefix="main")
            
            with col2:
                context = context_input_widget(key_prefix="main")
            
            if st.button("🚀 Transliterate", key="transliterate_btn"):
                st.session_state.transliterate_clicked = True
            
            if st.session_state.get("transliterate_clicked", False):
                with st.spinner("Transliterating..."):
                    client = get_api_client()
                    
                    confirmed_source = st.session_state.get("confirmed_source_script", "Latn")
                    
                    if input_text:
                        result = client.transliterate(
                            text=input_text,
                            source_script=confirmed_source,
                            target_script=target_script,
                            context=context,
                            skip_detection=True
                        )
                    else:
                        result = client.transliterate(
                            file_data=file_data,
                            filename=filename,
                            source_script=confirmed_source,
                            target_script=target_script,
                            context=context,
                            skip_detection=True
                        )
                
                if "error" not in result:
                    # Store session
                    session = TransliterationSession(
                        session_id=result.get("session_id", "session_" + str(int(__import__("time").time()))),
                        input_text=result.get("input_text", ""),
                        source_script=result.get("source_script", "Unknown"),
                        target_script=result.get("target_script", "Unknown"),
                        transliteration=result.get("transliteration", ""),
                        explanation=result.get("explanation", ""),
                        confidence=result.get("script_confidence", 0),
                        detection_status=result.get("detection_status", "user-provided")
                    )
                    SessionManager.add_session(session)
                    
                    st.session_state.transliterate_result = result
                    st.session_state.show_result = True
                    st.session_state.transliterate_clicked = False
                else:
                    st.error(result.get("error", "Unknown error"))
                    st.session_state.transliterate_clicked = False
        
        # Step 4: Display Result
        if st.session_state.get("show_result", False):
            st.markdown("---")
            st.markdown("### 📋 Result")
            
            result = st.session_state.get("transliterate_result", {})
            display_transliteration_result(result)
            
            # Chat interface for follow-ups
            if result.get("session_id"):
                st.markdown("---")
                session = SessionManager.get_current_session()
                if session:
                    display_chat_interface(result.get("session_id"), session.messages)
            
            # Reset button
            if st.button("🔄 Start Over", key="reset_btn"):
                st.session_state.detect_clicked = False
                st.session_state.show_confirmation = False
                st.session_state.show_transliteration = False
                st.session_state.show_result = False
                st.rerun()


# ============================================================================
# TAB 2: History
# ============================================================================
with tab2:
    st.markdown("### 📚 Translation History")
    
    history = SessionManager.get_history()
    
    if not history:
        st.info("No translations yet. Start by using the Translate tab!")
    else:
        st.markdown(f"**Total translations: {len(history)}**")
        st.markdown("---")
        
        for idx, session in enumerate(history, 1):
            with st.expander(
                f"{idx}. {session.input_text[:60]}... → {session.source_script} to {session.target_script}",
                expanded=False
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Original Text:**")
                    st.code(session.input_text)
                    
                    st.markdown("**Source Script:**")
                    st.text(session.source_script)
                    
                    st.markdown("**Date:**")
                    st.text(session.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
                
                with col2:
                    st.markdown("**Transliteration:**")
                    st.code(session.transliteration)
                    
                    st.markdown("**Target Script:**")
                    st.text(session.target_script)
                    
                    st.markdown("**Confidence:**")
                    st.text(f"{session.confidence*100:.1f}%")
                
                st.markdown("**Explanation:**")
                st.info(session.explanation)
                
                if session.messages:
                    st.markdown(f"**Chat Messages: {len(session.messages)} messages**")


# ============================================================================
# TAB 3: Batch Processing
# ============================================================================
with tab3:
    st.markdown("### ⚡ Batch Transliteration")
    st.markdown("Transliterate multiple texts at once")
    
    col1, col2 = st.columns(2)
    
    with col1:
        batch_texts = batch_input_widget()
        target_script = script_selector_widget(key_prefix="batch")
    
    with col2:
        context = context_input_widget(key_prefix="batch")
        st.markdown("**Source Script (optional)**")
        source_script = st.text_input(
            "Leave empty for auto-detection",
            placeholder="e.g., Cyrl, Arab, Latn",
            key="batch_source_script",
            label_visibility="collapsed"
        )
    
    if batch_texts and st.button("🚀 Transliterate Batch", key="batch_btn"):
        client = get_api_client()
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, text in enumerate(batch_texts):
            status_text.text(f"Processing {idx+1}/{len(batch_texts)}...")
            
            # First detect language
            detection = client.detect_language(text=text)
            detected_source = detection.get("iso_code", source_script or "Latn")
            
            # Then transliterate
            result = client.transliterate(
                text=text,
                source_script=source_script or detected_source,
                target_script=target_script,
                context=context,
                skip_detection=bool(source_script)
            )
            
            results.append(result)
            progress_bar.progress((idx + 1) / len(batch_texts))
        
        status_text.empty()
        progress_bar.empty()
        
        # Display results
        st.markdown("---")
        st.markdown(f"### ✅ Results ({len(results)} translations)")
        
        # Create results table
        results_data = []
        for result in results:
            if "error" not in result:
                results_data.append({
                    "Original": result.get("input_text", "")[:40],
                    "Transliteration": result.get("transliteration", ""),
                    "Source": result.get("source_script", ""),
                    "Target": result.get("target_script", "")
                })
        
        if results_data:
            st.dataframe(results_data, use_container_width=True)
        
        # Download option
        import json
        download_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download Results as JSON",
            data=download_data,
            file_name="batch_transliteration_results.json",
            mime="application/json"
        )


# ============================================================================
# TAB 4: Help & Info
# ============================================================================
with tab4:
    info_section()
    
    st.markdown("---")
    
    st.markdown("### 🎓 Learn More")
    st.markdown("""
    - **[Full API Documentation](http://localhost:8000/docs)** - Interactive API docs
    - **[Language Detection Guide](http://localhost:8000/docs)** - How detection works
    - **[Batch Processing Guide](http://localhost:8000/docs)** - Process multiple texts
    """)
    
    st.markdown("### 💬 About This Tool")
    st.markdown("""
    **Transliteration Tutor** is an educational tool designed for:
    - Language learners
    - Linguists and researchers
    - Content creators and translators
    - Anyone interested in writing systems
    
    The tool uses advanced AI to:
    - Automatically detect input language/script
    - Transliterate text between major writing systems
    - Provide linguistic explanations
    - Support batch processing for efficiency
    """)
    
    st.markdown("### 📊 Supported Scripts")
    
    scripts_info = {
        "Latin (Latn)": "English, Spanish, French, German, Portuguese, Italian, Polish, etc.",
        "Cyrillic (Cyrl)": "Russian, Ukrainian, Serbian, Bulgarian, Macedonian, Belarusian, etc.",
        "Arabic (Arab)": "Arabic, Urdu, Persian/Farsi, Uyghur, etc.",
        "Hebrew (Hebr)": "Hebrew, Yiddish",
        "Devanagari (Deva)": "Hindi, Sanskrit, Marathi, Nepali, etc.",
        "Greek (Grek)": "Greek",
        "Han (Hani)": "Chinese (Simplified & Traditional), Japanese Kanji",
        "Hiragana (Hira)": "Japanese Hiragana",
        "Katakana (Kana)": "Japanese Katakana",
        "Hangul (Hang)": "Korean"
    }
    
    cols = st.columns(2)
    for idx, (script, languages) in enumerate(scripts_info.items()):
        with cols[idx % 2]:
            st.markdown(f"**{script}**")
            st.text(languages)


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    🌍 Transliteration Tutor | Built with Streamlit & FastAPI<br>
    <small>For language learning and linguistic research</small>
</div>
""", unsafe_allow_html=True)
