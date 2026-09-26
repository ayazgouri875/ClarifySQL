import logging
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    """Wrapper client for Google Gemini LLM with robust error handling and fallbacks."""
    def __init__(self):
        self._model = None
        self._initialized = False

    def _ensure_init(self):
        if self._initialized:
            return
        self._initialized = True
        api_key = getattr(settings, "GEMINI_API_KEY", "")
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
                self._model = genai.GenerativeModel(model_name)
                logger.info(f"Initialized Gemini model: {model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini API: {e}")
                self._model = None

    @property
    def is_available(self) -> bool:
        self._ensure_init()
        return self._model is not None

    def generate_text(self, prompt: str, temperature: float = 0.1) -> Optional[str]:
        """Generates text completion using Gemini. Returns None on failure or missing API key."""
        self._ensure_init()
        if not self._model:
            return None
        try:
            response = self._model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            if response and hasattr(response, "text"):
                return response.text.strip()
            return None
        except Exception as exc:
            logger.warning(f"Gemini API request failed: {exc}")
            return None

gemini_client = GeminiClient()
