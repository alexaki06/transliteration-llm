"""
Session management utilities for Streamlit app.
Handles conversation history, user preferences, etc.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st


class TransliterationSession:
    """Represents a single transliteration session with history"""
    
    def __init__(self, session_id: str, input_text: str, source_script: str, 
                 target_script: str, transliteration: str, explanation: str,
                 confidence: float = 0.0, detection_status: str = "auto-detected"):
        self.session_id = session_id
        self.input_text = input_text
        self.source_script = source_script
        self.target_script = target_script
        self.transliteration = transliteration
        self.explanation = explanation
        self.confidence = confidence
        self.detection_status = detection_status
        self.timestamp = datetime.now()
        self.messages = []  # For chat follow-ups
    
    def add_message(self, role: str, content: str):
        """Add a chat message to this session"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "session_id": self.session_id,
            "input_text": self.input_text,
            "source_script": self.source_script,
            "target_script": self.target_script,
            "transliteration": self.transliteration,
            "explanation": self.explanation,
            "confidence": self.confidence,
            "detection_status": self.detection_status,
            "timestamp": self.timestamp.isoformat(),
            "messages": self.messages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create from dictionary"""
        obj = cls(
            session_id=data["session_id"],
            input_text=data["input_text"],
            source_script=data["source_script"],
            target_script=data["target_script"],
            transliteration=data["transliteration"],
            explanation=data["explanation"],
            confidence=data.get("confidence", 0.0),
            detection_status=data.get("detection_status", "auto-detected")
        )
        obj.timestamp = datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat()))
        obj.messages = data.get("messages", [])
        return obj


class SessionManager:
    """Manages all transliteration sessions"""
    
    SESSION_HISTORY_KEY = "transliteration_history"
    CURRENT_SESSION_KEY = "current_session"
    USER_PREFERENCES_KEY = "user_preferences"
    
    @staticmethod
    def init_session_state():
        """Initialize Streamlit session state"""
        if SessionManager.SESSION_HISTORY_KEY not in st.session_state:
            st.session_state[SessionManager.SESSION_HISTORY_KEY] = []
        
        if SessionManager.CURRENT_SESSION_KEY not in st.session_state:
            st.session_state[SessionManager.CURRENT_SESSION_KEY] = None
        
        if SessionManager.USER_PREFERENCES_KEY not in st.session_state:
            st.session_state[SessionManager.USER_PREFERENCES_KEY] = {
                "target_script": "Latn",
                "auto_confirm": False,
                "show_explanations": True,
                "theme": "light"
            }
    
    @staticmethod
    def add_session(session: TransliterationSession):
        """Add a new session to history"""
        SessionManager.init_session_state()
        st.session_state[SessionManager.SESSION_HISTORY_KEY].append(session)
        st.session_state[SessionManager.CURRENT_SESSION_KEY] = session
    
    @staticmethod
    def get_history() -> List[TransliterationSession]:
        """Get all sessions"""
        SessionManager.init_session_state()
        return st.session_state[SessionManager.SESSION_HISTORY_KEY]
    
    @staticmethod
    def get_current_session() -> Optional[TransliterationSession]:
        """Get current active session"""
        SessionManager.init_session_state()
        return st.session_state[SessionManager.CURRENT_SESSION_KEY]
    
    @staticmethod
    def clear_history():
        """Clear all history"""
        st.session_state[SessionManager.SESSION_HISTORY_KEY] = []
        st.session_state[SessionManager.CURRENT_SESSION_KEY] = None
    
    @staticmethod
    def get_preferences() -> Dict[str, Any]:
        """Get user preferences"""
        SessionManager.init_session_state()
        return st.session_state[SessionManager.USER_PREFERENCES_KEY]
    
    @staticmethod
    def set_preference(key: str, value: Any):
        """Set user preference"""
        SessionManager.init_session_state()
        st.session_state[SessionManager.USER_PREFERENCES_KEY][key] = value
    
    @staticmethod
    def export_history() -> str:
        """Export history as JSON"""
        history = SessionManager.get_history()
        data = [s.to_dict() for s in history]
        return json.dumps(data, indent=2, default=str)
    
    @staticmethod
    def get_history_summary() -> str:
        """Get summary of history for display"""
        history = SessionManager.get_history()
        if not history:
            return "No history yet."
        
        lines = []
        for i, session in enumerate(history, 1):
            lines.append(f"{i}. {session.input_text[:50]} → {session.source_script} to {session.target_script}")
        
        return "\n".join(lines)
