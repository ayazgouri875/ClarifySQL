"""
LLM Client integration.
Supports Google Gemini with graceful fallback to semantic reasoning engine.
"""

import os
import re
from typing import Optional, Dict, Any
from app.core.config import settings

class LLMClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
        self.model = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                print(f"Initialized Gemini model: {settings.GEMINI_MODEL}")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client ({e}).")

    def generate_text(self, prompt: str) -> Optional[str]:
        """Calls Gemini model if available."""
        if not self.model and (settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")):
            self.api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY", "")
            self._init_client()

        if self.model:
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini API invocation error: {e}")
                return None
        return None

llm_client = LLMClient()
