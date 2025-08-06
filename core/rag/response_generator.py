import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(model_name='gemma-3n-e2b-it', generation_config={
    'temperature': 0.7,
    'top_p': 1,
    'top_k': 1,
    'max_output_tokens': 1024
})

def generate_response(query, retrieved_chunks):
    context = "\n\n".join(retrieved_chunks)
    prompt = f"""
You are a smart assistant helping students and visitors. Use the following context to answer the query intelligently.
Context:
{context}

User Query: {query}
Answer:
"""
    response = model.generate_content(prompt)
    return response.text.strip()
