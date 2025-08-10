# agents/query_rewriter.py

import os
import google.generativeai as genai

class QueryRewriterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Set your GEMINI_API_KEY in the environment variables.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemma-3n-e4b-it")

    def process(self, query: str) -> str:
        prompt = f"""
        Rewrite this user query into a clearer, more structured form that separates out sub-questions 
        and makes it easier for downstream agents to process:\n\n
        User query: "{query}"
        
        Rewritten query:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"[Error rewriting query] {str(e)}"
