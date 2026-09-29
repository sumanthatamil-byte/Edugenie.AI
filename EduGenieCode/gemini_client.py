"""
Gemini Client Helper for EduGenie
Handles communication with the Google Gemini API using the modern google-genai SDK.
Provides fallback model selection and structured error reporting.
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("EduGenie.Gemini")

_client = None

def get_gemini_api_key() -> str:
    """Retrieve and validate Gemini API Key."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is missing or invalid. "
            "Please configure your Gemini API Key in the .env file."
        )
    return api_key

def get_genai_client():
    """Returns an initialized Google GenAI Client."""
    global _client
    api_key = get_gemini_api_key()
    try:
        from google import genai
        return genai.Client(api_key=api_key)
    except ImportError:
        raise RuntimeError(
            "The 'google-genai' package is not installed. "
            "Please run 'pip install google-genai' or 'pip install -r requirements.txt'."
        )

def generate_text_with_gemini(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7
) -> str:
    """
    Generate content using the Gemini API.
    Attempts primary configured model, with graceful fallbacks if specific model is unavailable.
    """
    client = get_genai_client()
    from google.genai import types

    primary_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip() or "gemini-3.6-flash"
    candidate_models = [primary_model]
    for fallback in [
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.5-flash",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-3.8-flash"
    ]:
        if fallback not in candidate_models:
            candidate_models.append(fallback)

    last_error = None
    config = types.GenerateContentConfig(
        temperature=temperature,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    for model_name in candidate_models:
        try:
            logger.info(f"Calling Gemini with model: {model_name}")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config,
            )
            if response and response.text:
                return response.text.strip()
            else:
                raise ValueError("Received an empty response from Gemini.")
        except Exception as e:
            last_error = e
            err_msg = str(e).lower()
            # If it's an authentication error, fail immediately without trying all fallbacks
            if "api key not valid" in err_msg or "unauthenticated" in err_msg or "permissiondenied" in err_msg:
                raise ValueError(f"Authentication failed with Gemini API: {e}")
            logger.warning(f"Model {model_name} failed with error: {e}. Trying next candidate if available...")

    raise RuntimeError(f"All Gemini model attempts failed. Last error: {last_error}")
