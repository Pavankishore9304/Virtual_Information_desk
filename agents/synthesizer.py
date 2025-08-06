import google.generativeai as genai

class SynthesizerAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.prompt_template = """
        You are a helpful AI assistant. Your job is to synthesize the provided context into a single, clear, and coherent answer to the user's original query.
        - Address each part of the user's query separately.
        - Base your answer *strictly* on the information given in the "Collected Context".
        - If the context for a specific part of the query says "No data found", "No relevant information found", or contains an error message, you must explicitly state that the information could not be found for that part of the query. Do not try to answer it from your own knowledge.
        - Keep the answer concise and easy to read.

        User's Original Query: "{query}"

        Collected Context:
        ---
        {context}
        ---

        Final Answer:
        """

    def process(self, query: str, context: str) -> str:
        print("✍️ Synthesizing final answer...")
        prompt = self.prompt_template.format(query=query, context=context)
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error during synthesis: {e}")
            return "I'm sorry, but I encountered an error while generating the final answer."