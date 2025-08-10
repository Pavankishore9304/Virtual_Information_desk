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

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model Names - Now read from .env
GOOGLE_MODEL = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-flash")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL_NAME", "claude-3-haiku-20240307")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL_NAME")

# Other Config
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", 45))

# --- Configure APIs ---
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# --- Internal Helper Functions ---

def _call_google_api(prompt: str) -> str:
    """Calls the Google Gemini API."""
    if not GOOGLE_API_KEY: raise ValueError("GOOGLE_API_KEY not configured.")
    print(f"  - 📞 Calling Google Gemini API ({GOOGLE_MODEL})...")
    model = genai.GenerativeModel(GOOGLE_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()

def _call_anthropic_api(prompt: str) -> str:
    """Calls the Anthropic Claude API."""
    if not ANTHROPIC_API_KEY: raise ValueError("ANTHROPIC_API_KEY not configured.")
    print(f"  - 📞 Calling Anthropic Claude API ({ANTHROPIC_MODEL})...")
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": ANTHROPIC_MODEL,
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        },
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return response.json()['content'][0]['text'].strip()

def _call_ollama_api(prompt: str) -> str:
    """Calls the local Ollama API with a timeout."""
    if not OLLAMA_BASE_URL or not OLLAMA_MODEL: raise ValueError("Ollama URL or model name not configured.")
    print(f"  - 📞 Calling local Ollama model '{OLLAMA_MODEL}' (timeout: {TIMEOUT}s)...")
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=TIMEOUT
    )
    response.raise_for_status()
    return json.loads(response.text)['response'].strip()

# --- Main Public Function ---

def generate_response(prompt: str, role: str) -> str:
    """Generates a response using the primary LLM provider, with a fallback."""
    provider_map = {
        "google": _call_google_api,
        "anthropic": _call_anthropic_api,
        "ollama": _call_ollama_api
    }
    primary_call = provider_map.get(PRIMARY_PROVIDER)
    fallback_call = provider_map.get(FALLBACK_PROVIDER, _call_google_api)
    
    if not primary_call:
        print(f"  - ⚠️ Unknown PRIMARY_LLM_PROVIDER '{PRIMARY_PROVIDER}'. Defaulting to Google.")
        primary_call = _call_google_api

    try:
        return primary_call(prompt)
    except Exception as e:
        print(f"  - ⚠️ Primary provider '{PRIMARY_PROVIDER}' failed: {e}")
        if PRIMARY_PROVIDER == FALLBACK_PROVIDER:
            return f"Error: The primary provider '{PRIMARY_PROVIDER}' failed and it is also the fallback. Error: {e}"
        
        print(f"  - 🔄 Switching to fallback provider '{FALLBACK_PROVIDER}'...")
        try:
            return fallback_call(prompt)
        except Exception as fallback_e:
            error_message = f"  - ❌ Fallback provider also failed: {fallback_e}"
            print(error_message)
            return f"Error: Both the primary and fallback AI models failed to respond. Details: {fallback_e}"