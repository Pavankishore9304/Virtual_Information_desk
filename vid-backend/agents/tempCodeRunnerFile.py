import json
import re
from core.db.schema_inspector import get_db_summary_for_planner_agent
from core.llm.llm_client import generate_response

class PlannerAgent:
    def __init__(self):
        self.prompt_template = (
            "You are an expert planner. Your task is to decompose a query into a sequence of tool calls. "
            "Return ONLY a JSON array. No prose, no markdown.\n"
            "Each element must have keys: step (int), thought (string), tool (SQL|VECTOR_SEARCH|GENERAL), sub_query (string).\n"
            "Rules:\n"
            "- Isolate greetings and conversational text into a separate `GENERAL` tool step.\n"
            "- Use `SQL` for specific, factual lookups (counts, credits, exact names).\n"
- Use `VECTOR_SEARCH` for descriptive, open-ended, or explanatory questions (objectives, history, 'tell me about').\n"
            "- If a query requires both factual filtering (SQL) and descriptive info (VECTOR_SEARCH), create a multi-step plan.\n"
            "- Pass prior results using `{{{{step_N_result}}}}`.\n"
            "Schema for SQL tool:\n{db_summary}\n"
            "User Query: \"{query}\"\n"
            "Plan:\n"
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