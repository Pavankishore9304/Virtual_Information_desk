import os
import requests
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv

# --- Load Configuration ---
load_dotenv()
PRIMARY_PROVIDER = os.getenv("PRIMARY_LLM_PROVIDER", "google").lower()
FALLBACK_PROVIDER = os.getenv("FALLBACK_LLM_PROVIDER", "google").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL_NAME")
TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", 45))

# --- Configure Google Gemini ---
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- Internal Helper Functions ---

def _call_google_api(prompt: str) -> str:
    """Calls the Google Gemini API."""
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not configured.")
    print("  - 📞 Calling Google Gemini API...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text.strip()

def _call_ollama_api(prompt: str) -> str:
    """Calls the local Ollama API with a timeout."""
    if not OLLAMA_BASE_URL or not OLLAMA_MODEL:
        raise ValueError("Ollama URL or model name not configured.")
    print(f"  - 📞 Calling local Ollama model '{OLLAMA_MODEL}' (timeout: {TIMEOUT}s)...")
    
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=TIMEOUT
    )
    response.raise_for_status()
    # The actual response content is a JSON string on each line
    return json.loads(response.text)['response'].strip()

# --- Main Public Function ---

def generate_response(prompt: str, role: str) -> str:
    """
    Generates a response using the primary LLM provider, with a fallback.
    
    Args:
        prompt (str): The prompt to send to the model.
        role (str): A string describing the agent's role (for logging).
    """
    primary_call = None
    fallback_call = _call_google_api # Default fallback is always Google

    if PRIMARY_PROVIDER == "ollama":
        primary_call = _call_ollama_api
    elif PRIMARY_PROVIDER == "google":
        primary_call = _call_google_api
    else:
        print(f"  - ⚠️ Unknown PRIMARY_LLM_PROVIDER '{PRIMARY_PROVIDER}'. Defaulting to Google.")
        primary_call = _call_google_api

    try:
        # Attempt to use the primary provider
        return primary_call(prompt)
    except Exception as e:
        print(f"  - ⚠️ Primary provider '{PRIMARY_PROVIDER}' failed: {e}")
        print(f"  - 🔄 Switching to fallback provider '{FALLBACK_PROVIDER}'...")
        
        # On failure, use the fallback provider
        try:
            return fallback_call(prompt)
        except Exception as fallback_e:
            error_message = f"  - ❌ Fallback provider also failed: {fallback_e}"
            print(error_message)
            return f"Error: Both the primary and fallback AI models failed to respond. Details: {fallback_e}"
