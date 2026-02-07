"""
UI components and helper functions for Streamlit app.
Reusable components for common UI patterns.
"""

import streamlit as st
from typing import Dict, Any, Optional, List
from utils.api_client import get_api_client


def display_detection_result(detection_result: Dict[str, Any]):
    """Display language detection result with user-friendly formatting"""
    
    if "error" in detection_result:
        st.error(f"❌ Detection Error: {detection_result['error']}")
        return None
    
    detected_script = detection_result.get("detected_script", "Unknown")
    iso_code = detection_result.get("iso_code", "Unknown")
    confidence = detection_result.get("confidence", 0)
    
    # Display detection result
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Detected Script", detected_script)
    with col2:
        st.metric("ISO Code", iso_code)
    with col3:
        st.metric("Confidence", f"{confidence*100:.1f}%")
    
    return detection_result


def language_confirmation_widget(detection_result: Dict[str, Any]) -> Optional[str]:
    """
    Widget for user to confirm or correct detected language.
    Returns confirmed ISO code or None if cancelled.
    """
    
    detected_script = detection_result.get("detected_script", "Unknown")
    iso_code = detection_result.get("iso_code", "Unknown")
    available_scripts = detection_result.get("available_scripts", {})
    
    st.markdown("### ✓ Confirm Language")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Yes, that's correct", key="confirm_yes"):
            return iso_code
    
    with col2:
        if st.button("❌ No, let me correct it", key="confirm_no"):
            st.session_state.show_correction = True
    
    # Show correction UI if needed
    if st.session_state.get("show_correction", False):
        st.markdown("**Select correct language:**")
        
        # Create two-column layout for script selection
        script_options = list(available_scripts.items())
        cols = st.columns(2)
        
        for idx, (code, name) in enumerate(script_options):
            with cols[idx % 2]:
                if st.button(f"{name} ({code})", key=f"script_{code}"):
                    st.session_state.show_correction = False
                    return code
    
    return None


def display_transliteration_result(result: Dict[str, Any]):
    """Display transliteration result with explanation"""
    
    if "error" in result:
        st.error(f"❌ Transliteration Error: {result['error']}")
        return
    
    transliteration = result.get("transliteration", "")
    explanation = result.get("explanation", "")
    source_script = result.get("source_script", "Unknown")
    target_script = result.get("target_script", "Unknown")
    
    # Main result
    st.markdown("### 📝 Transliteration Result")
    
    # Result box
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Source Text:**")
        st.code(result.get("input_text", ""), language=None)
    with col2:
        st.markdown("**Transliteration:**")
        st.code(transliteration, language=None)
    
    # Explanation
    if explanation:
        st.markdown("### 💡 Explanation")
        st.info(explanation)
    
    # Metadata
    with st.expander("📊 Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Source", source_script)
        with col2:
            st.metric("Target", target_script)
        with col3:
            detection_status = result.get("detection_status", "unknown")
            st.metric("Detection", detection_status)
        
        if result.get("script_confidence"):
            st.metric("Confidence", f"{result.get('script_confidence')*100:.1f}%")


def batch_input_widget() -> Optional[List[str]]:
    """Widget for batch text input (multiple lines)"""
    
    st.markdown("### 📋 Batch Input")
    st.markdown("Enter multiple texts (one per line):")
    
    batch_text = st.text_area(
        "Texts to transliterate",
        height=150,
        placeholder="Line 1\nLine 2\nLine 3\n...",
        label_visibility="collapsed"
    )
    
    if batch_text.strip():
        texts = [line.strip() for line in batch_text.split('\n') if line.strip()]
        return texts if texts else None
    
    return None


def file_upload_widget(accepted_types: List[str] = None) -> Optional[tuple]:
    """
    File upload widget. Returns (file_data, filename) or None.
    
    Args:
        accepted_types: List of accepted file types (e.g., ['jpg', 'png', 'pdf'])
    """
    
    if accepted_types is None:
        accepted_types = ['txt', 'jpg', 'jpeg', 'png', 'pdf', 'gif', 'bmp']
    
    st.markdown("### 📁 Or Upload a File")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=accepted_types,
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        file_data = uploaded_file.read()
        filename = uploaded_file.name
        return (file_data, filename)
    
    return None


def script_selector_widget(key_prefix: str = "script") -> str:
    """
    Widget to select target script.
    Returns ISO 15924 code.
    """
    
    scripts = {
        "Latn": "Latin (English, Spanish, French, etc.)",
        "Cyrl": "Cyrillic (Russian, Ukrainian, etc.)",
        "Arab": "Arabic (Arabic, Urdu, Persian, etc.)",
        "Hebr": "Hebrew (Hebrew, Yiddish)",
        "Deva": "Devanagari (Hindi, Sanskrit, etc.)",
        "Grek": "Greek (Greek)",
        "Hani": "Han (Chinese, Japanese Kanji)",
        "Hira": "Hiragana (Japanese)",
        "Kana": "Katakana (Japanese)",
        "Hang": "Hangul (Korean)",
    }
    
    selected = st.selectbox(
        "Target Script",
        options=list(scripts.keys()),
        format_func=lambda x: scripts[x],
        key=f"{key_prefix}_target_script",
        index=0
    )
    
    return selected


def context_input_widget(key_prefix: str = "context") -> Optional[str]:
    """Widget for optional context input for transliteration"""
    
    context = st.text_input(
        "📌 Optional Context (helps improve transliteration)",
        placeholder="e.g., 'This is a place name' or 'Technical term'",
        key=f"{key_prefix}_context"
    )
    
    return context if context.strip() else None


def copy_button(text: str, label: str = "📋 Copy"):
    """Utility button to copy text to clipboard"""
    st.write(f"*Click to copy:*")
    st.code(text, language=None)


def display_chat_interface(session_id: str, messages: List[Dict[str, str]] = None):
    """Display chat interface for follow-up questions"""
    
    if messages is None:
        messages = []
    
    st.markdown("### 💬 Ask Follow-up Questions")
    
    # Display existing messages
    for msg in messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])
    
    # Input for new message
    user_input = st.chat_input("Ask a follow-up question about the transliteration...")
    
    if user_input:
        client = get_api_client()
        
        # Display user message
        st.chat_message("user").write(user_input)
        
        # Get response from API
        with st.spinner("Thinking..."):
            response = client.chat(session_id, user_input)
        
        if "error" not in response:
            assistant_message = response.get("assistant_reply", "No response")
            st.chat_message("assistant").write(assistant_message)
            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": assistant_message})
        else:
            st.error(f"Error: {response['error']}")
    
    return messages


def settings_sidebar():
    """Display settings in sidebar"""
    
    st.sidebar.markdown("### ⚙️ Settings")
    
    # Theme selector
    theme = st.sidebar.radio(
        "Theme",
        options=["Light", "Dark", "Auto"],
        index=0
    )
    
    # Auto-confirm detection
    auto_confirm = st.sidebar.checkbox(
        "Auto-confirm language detection",
        value=False,
        help="Skip confirmation if confidence > 90%"
    )
    
    # Show explanations
    show_explanations = st.sidebar.checkbox(
        "Show linguistic explanations",
        value=True
    )
    
    # Export history
    if st.sidebar.button("📥 Export History"):
        from utils.session_manager import SessionManager
        history_json = SessionManager.export_history()
        st.sidebar.download_button(
            label="Download as JSON",
            data=history_json,
            file_name="transliteration_history.json",
            mime="application/json"
        )
    
    # Clear history
    if st.sidebar.button("🗑️ Clear History"):
        from utils.session_manager import SessionManager
        SessionManager.clear_history()
        st.rerun()
    
    return {
        "theme": theme,
        "auto_confirm": auto_confirm,
        "show_explanations": show_explanations
    }


def info_section():
    """Display help/info section"""
    
    with st.expander("ℹ️ How to Use", expanded=False):
        st.markdown("""
        ### Getting Started
        
        1. **Enter Text or Upload File**
           - Type text directly or upload an image/PDF
           - Supports all major writing systems
        
        2. **Confirm Language** (if needed)
           - The app detects the source language automatically
           - Confirm detection or correct if needed
        
        3. **Choose Target Language**
           - Select which script to transliterate to
        
        4. **View Results**
           - See the transliteration and linguistic explanation
           - Ask follow-up questions using the chat interface
        
        ### Supported Scripts
        - **Latin**: English, Spanish, French, German, etc.
        - **Cyrillic**: Russian, Ukrainian, Serbian, Bulgarian, etc.
        - **Arabic**: Arabic, Urdu, Persian, etc.
        - **Hebrew**: Hebrew, Yiddish
        - **Devanagari**: Hindi, Sanskrit, Marathi, etc.
        - **Greek**: Greek
        - **Han**: Chinese, Japanese Kanji
        - **Hiragana**: Japanese
        - **Katakana**: Japanese
        - **Hangul**: Korean
        
        ### Tips for Best Results
        - Provide context if available (place names, technical terms, etc.)
        - For handwritten text, ensure clear image quality
        - For PDFs, single-page files work best
        """)
