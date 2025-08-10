import requests
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # make sure this is set in your .env

def embedding_model(model: str, content: str):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:embedContent?key={GEMINI_API_KEY}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "content": {"parts": [{"text": content}]}
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["embedding"]
    else:
        raise Exception(f"Embedding API failed: {response.text}")
