"""
API client for communicating with the transliteration backend.
Handles all HTTP requests to the FastAPI backend.
"""

import requests
import io
from typing import Optional, Dict, Any
import streamlit as st

# API Configuration
API_BASE_URL = "http://localhost:8000"


class TransliterationAPIClient:
    """Client for transliteration API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def detect_language(self, text: Optional[str] = None, file_data: Optional[bytes] = None, 
                       filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Detect language/script of input text or file.
        
        Args:
            text: Text to detect language for
            file_data: Binary file data (for images/PDFs)
            filename: Original filename (for file uploads)
        
        Returns:
            Dictionary with detected_script, iso_code, confidence, available_scripts, etc.
        """
        url = f"{self.base_url}/detect-language"
        
        try:
            if text:
                response = self.session.post(url, data={"text": text})
            elif file_data:
                files = {"file": (filename or "upload", io.BytesIO(file_data))}
                response = self.session.post(url, files=files)
            else:
                return {"error": "Provide either text or file"}
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API Error: {str(e)}"}
    
    def confirm_language(self, detected_language: str, user_confirmed: bool, 
                        corrected_language: Optional[str] = None) -> Dict[str, Any]:
        """
        Confirm or correct detected language.
        
        Args:
            detected_language: Original detected ISO code
            user_confirmed: True if user confirmed, False to correct
            corrected_language: User's correction if not confirmed
        
        Returns:
            Dictionary with confirmed_source_script and message
        """
        url = f"{self.base_url}/confirm-language"
        
        payload = {
            "detected_language": detected_language,
            "user_confirmed": user_confirmed,
        }
        if corrected_language:
            payload["corrected_language"] = corrected_language
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API Error: {str(e)}"}
    
    def transliterate(self, text: Optional[str] = None, file_data: Optional[bytes] = None,
                     filename: Optional[str] = None, source_script: Optional[str] = None,
                     target_script: str = "Latn", context: Optional[str] = None,
                     skip_detection: bool = False) -> Dict[str, Any]:
        """
        Transliterate text from source script to target script.
        
        Args:
            text: Text to transliterate
            file_data: Binary file data (for images/PDFs)
            filename: Original filename
            source_script: Source script (auto-detected if not provided)
            target_script: Target script (default: Latin)
            context: Additional context for transliteration
            skip_detection: Skip auto-detection if True
        
        Returns:
            Dictionary with transliteration, explanation, etc.
        """
        url = f"{self.base_url}/transliterate"
        
        data = {
            "target_script": target_script,
            "skip_detection": "true" if skip_detection else "false"
        }
        
        if text:
            data["text"] = text
        
        if source_script:
            data["source_script"] = source_script
        
        if context:
            data["context"] = context
        
        try:
            if file_data:
                files = {"file": (filename or "upload", io.BytesIO(file_data))}
                response = self.session.post(url, data=data, files=files)
            else:
                response = self.session.post(url, data=data)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API Error: {str(e)}"}
    
    def chat(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Send a message to the chat endpoint (for follow-up questions).
        
        Args:
            session_id: Chat session ID
            message: User message
        
        Returns:
            Dictionary with assistant response
        """
        url = f"{self.base_url}/chat"
        
        payload = {
            "session_id": session_id,
            "message": message
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": f"API Error: {str(e)}"}


# Singleton instance
_client = None

def get_api_client() -> TransliterationAPIClient:
    """Get or create API client instance"""
    global _client
    if _client is None:
        _client = TransliterationAPIClient()
    return _client


def check_api_health() -> bool:
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False
