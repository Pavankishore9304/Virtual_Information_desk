import google.generativeai as genai

class ReasonerAgent:
    def __init__(self):
        # Using a powerful model is good for reasoning tasks
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def process(self, query: str, chunks: list) -> str:
        """
        Analyzes, filters, and synthesizes retrieved chunks to create a concise, relevant context.
        """
        print(f"🧠 Reasoning with {len(chunks)} chunks...")
        
        context = "\n\n".join([f"--- Chunk {i+1} ---\n{chunk}" for i, chunk in enumerate(chunks)])
        
        prompt = f"""
You are a reasoning agent. Your task is to analyze the following retrieved text chunks and synthesize a concise, factual, and relevant context that directly addresses the user's query.

Filter out any information that is irrelevant, redundant, or contradictory. Prioritize facts and direct answers.
Combine the relevant information into a single, clean block of text. Do not answer the query yourself, simply provide the refined context.

User Query: "{query}"

Retrieved Chunks:
{context}

Refined Context:
"""
        
        try:
            response = self.model.generate_content(prompt)
            refined_context = response.text.strip()
            print("✅ Context refined.")
            return refined_context
        except Exception as e:
            print(f"Error during reasoning: {e}")
            # Fallback: If reasoning fails, just combine the original chunks.
            return "\n\n".join(chunks)