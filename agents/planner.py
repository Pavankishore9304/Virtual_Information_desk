import google.generativeai as genai
import json
from core.db.schema_inspector import get_db_summary_for_planner_agent

class PlannerAgent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        # This prompt is now much more explicit about the *type* of question for each tool.
        self.prompt_template = """
        You are a master planner AI. Your job is to analyze a user's query and select the single best tool to answer it.

        **Your Decision-Making Process:**
        1.  First, determine if the user is asking for a specific, factual piece of data that would be in a database table (e.g., a name, a count, a specific ID, a credit number).
        2.  If it is a factual lookup, use the `SQL` tool.
        3.  If the question is descriptive, open-ended, or asks for explanations, objectives, history, or anything that sounds like it would be in a document, use the `VECTOR_SEARCH` tool.
        4.  If the query is just a greeting, use the `GENERAL` tool.

        **Tool Descriptions:**
        1.  **SQL**: The best tool for **specific, factual data lookups**. Use this for questions asking "what is the name", "how many", "list all", "what is the credit count", etc. The available tables are:
            {db_summary}
        2.  **VECTOR_SEARCH**: The best tool for **descriptive or open-ended questions**. Use this for questions asking "what are the objectives of", "tell me about the history of", "explain how...", etc.
        3.  **GENERAL**: Use only for conversational greetings like "hello" or "thank you".

        **Your most important rule is to be efficient. Create a plan with only one step for the most appropriate tool.**

        **Example 1 (Factual Lookup):**
        User Query: "How many credits is the Python course?"
        Plan:
        [
          {{
            "sub_query": "How many credits is the Python course?",
            "tool": "SQL"
          }}
        ]

        **Example 2 (Descriptive Question):**
        User Query: "What are the learning objectives for the Python course?"
        Plan:
        [
          {{
            "sub_query": "What are the learning objectives for the Python course?",
            "tool": "VECTOR_SEARCH"
          }}
        ]

        **Your Turn:**
        User Query: "{query}"
        Plan:
        """

    def process(self, query: str) -> list:
        prompt = self.prompt_template.format(
            db_summary=get_db_summary_for_planner_agent(),
            query=query
        )
        response = self.model.generate_content(prompt)
        
        try:
            plan_text = response.text.strip().replace('`', '').replace('json', '').strip()
            plan = json.loads(plan_text)
            return plan
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error parsing plan: {e}. Defaulting to a simple plan.")
            # Default to VECTOR_SEARCH as it's better for general queries.
            return [{"sub_query": query, "tool": "VECTOR_SEARCH"}]