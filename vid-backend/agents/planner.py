import json
import re
from core.db.schema_inspector import get_db_summary_for_planner_agent
from core.llm.llm_client import generate_response

class PlannerAgent:
    def __init__(self):
        self.prompt_template = (
            "You are an expert planner for a university information system. Your task is to decompose queries into tool calls.\n"
            "Return ONLY a JSON array. No prose, no markdown, no explanations.\n\n"
            
            "Available Tools:\n"
            "- SQL: Query database for structured data (lecturer details, club information, counts, specific facts)\n"
            "- VECTOR_SEARCH: Search documents for descriptive content (course details, policies, procedures, general university info)\n"
            "- GENERAL: Handle pure conversational elements (greetings, thanks)\n\n"
            
            "Tool Selection Guidelines:\n"
            "Use SQL for:\n"
            "- Lecturer queries: names, roles, education, subjects taught, research interests, experience\n"
            "- Club queries: names, categories, founding years, recruitment info\n"
            "- Specific factual lookups, counts, filtering\n"
            "- Examples: 'Who is Dr. Sandesh?', 'Show me professors', 'Which clubs were founded in 2020?'\n"
            "- IMPORTANT: For SQL tool, provide NATURAL LANGUAGE queries, not raw SQL commands\n\n"
            
            "Use VECTOR_SEARCH for:\n"
            "- Course curriculum, semester details, syllabus content\n"
            "- University policies, procedures, general information\n"
            "- Descriptive content that's not in structured database\n"
            "- Examples: 'What is taught in semester 5?', 'University admission process', 'Course objectives'\n\n"
            
            "Database contains:\n{db_summary}\n\n"
            
            "Output Format: JSON array with objects containing: step (int), thought (string), tool (SQL|VECTOR_SEARCH|GENERAL), sub_query (string)\n"
            "For multi-step queries, reference previous results using {{{{step_N_result}}}}\n\n"
            
            "User Query: \"{query}\"\n"
            "Plan:"
        )

    def _normalize_placeholders(self, plan):
        for obj in plan:
            if isinstance(obj, dict) and "sub_query" in obj:
                obj["sub_query"] = re.sub(r"\{step_(\d+)_result\}", r"{{step_\1_result}}", obj["sub_query"])
        return plan

    def process(self, query: str) -> list:
        prompt = self.prompt_template.format(
            db_summary=get_db_summary_for_planner_agent(),
            query=query
        )
        resp = generate_response(prompt, role="PLANNER")
        
        try:
            s = resp.find('[')
            e = resp.rfind(']')
            if s == -1 or e == -1:
                raise json.JSONDecodeError("No JSON array found in response", resp, 0)
            plan = json.loads(resp[s:e+1])
            plan = self._normalize_placeholders(plan)
            return plan
        except Exception as e:
            print(f"Planner parse fail. Raw response was: '{resp}'. Error: {e}")
            # If planning fails, default to a direct vector search of the whole query
            return [{"step": 1, "thought": "Fallback to vector search due to planning error.", "tool": "VECTOR_SEARCH", "sub_query": query}]
