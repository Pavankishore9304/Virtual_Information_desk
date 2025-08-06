import google.generativeai as genai
from duckduckgo_search import DDGS

class WebSearchAgent:
    """
    An agent that searches the web, grounds its findings in sources,
    and summarizes the results factually.
    """
    def __init__(self):
        """Initializes the WebSearchAgent."""
        self.model = genai.GenerativeModel('gemma-3n-e4b-it')
        self.prompt_template = """
        You are a factual research assistant. Your task is to answer the user's query based *only* on the provided search results.
        - Synthesize a clear, concise answer from the snippets.
        - For each piece of information in your answer, you MUST cite the source number (e.g., [Source 1], [Source 2]).
        - If the search results do not contain enough information to answer the query, you MUST state: "Based on the web search, I could not find a definitive answer to this question."
        - Do not add any information that is not present in the search results. Do not make assumptions or fill in gaps.

        User Query: "{query}"

        Search Results:
        ---
        {search_results}
        ---

        Factual Answer with Citations:
        """

    def process(self, query: str) -> str:
        """
        Searches the web for the given query and returns a factual, cited answer.
        """
        print(f"  - [WebSearch] Performing deep research on the web for: '{query}'")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
            
            if not results:
                print("  - [WebSearch] No results found on the web.")
                return "No relevant information was found on the web for this query."

            # Format snippets with numbered sources for citation
            snippets = [f"[Source {i+1}]: {r['body']} (URL: {r['href']})" for i, r in enumerate(results)]
            search_context = "\n\n".join(snippets)

            # Use the LLM to generate a factual, cited summary
            prompt = self.prompt_template.format(query=query, search_results=search_context)
            response = self.model.generate_content(prompt)
            print("  - [WebSearch] ✅ Web research summarized with citations.")
            return response.text.strip()
        except Exception as e:
            print(f"  - [WebSearch] Error during web search: {e}")
            return f"Sorry, I encountered an error while searching the web: {e}"