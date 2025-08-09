from core.llm.llm_client import generate_response

class ReasonerAgent:
    def __init__(self):
        self.prompt_template = """
Given the user query and context chunks, extract only directly relevant facts.
If nothing relevant: output exactly "No relevant information found."
User Query: {query}
Context:
{context}
Answer:
"""
    def process(self, query: str, chunks: list[str]) -> str:
        context = "\n---\n".join(chunks)
        prompt = self.prompt_template.format(query=query, context=context)
        return generate_response(prompt, role="REASONER")