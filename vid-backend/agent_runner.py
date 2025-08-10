import streamlit as st
import json
from services.database import get_db_session
from services.vector_store import get_vector_store
from agents.planner import PlannerAgent
from agents.text_to_sql import TextToSQLAgent
from agents.retriever import RetrieverAgent
from agents.reasoner import ReasonerAgent
from agents.synthesizer import SynthesizerAgent
from agents.web_search import WebSearchAgent # Import the new agent

# --- Agent and Service Initialization ---
print("🚀 Initializing Agents and Services...")
db_session = get_db_session()
vector_store = get_vector_store()

# Agents
planner = PlannerAgent()
text_to_sql = TextToSQLAgent(db_session)
retriever = RetrieverAgent(vector_store)
reasoner = ReasonerAgent()
synthesizer = SynthesizerAgent()
web_search = WebSearchAgent() # Initialize the new agent
print("✅ Agents and Services Initialized.")

def execute_rag_pipeline(query: str) -> str:
    """Helper function to run the standard RAG (Vector Search) pipeline."""
    print(f"  - Executing RAG pipeline for: '{query}'")
    retrieved_chunks = retriever.process(query)
    if not retrieved_chunks:
        print("  - RAG: No relevant chunks found.")
        return "" # Return empty string to indicate no results
    print(f"  - RAG: Retrieved {len(retrieved_chunks)} information chunks.")
    refined_context = reasoner.process(query, retrieved_chunks)
    return refined_context

# --- Pipeline Execution ---
def run_agentic_pipeline(user_query: str):
    """
    Runs the full agentic pipeline with fallback logic.
    """
    print(f"\n👤 Original User Query: {user_query}")

    # 1. Planner Agent creates a multi-step plan
    print("\n🚦 [Agent 1: Planner] Breaking down the query into a plan...")
    plan = planner.process(user_query)
    print(f"  - ✅ Generated Plan: {json.dumps(plan, indent=2)}")

    # 2. Execute the plan step-by-step
    print("\n🔎 [Execution Engine] Running the plan...")
    collected_context = []
    for i, step in enumerate(plan):
        sub_query = step.get("sub_query")
        tool = step.get("tool")
        print(f"\n  - Step {i+1}: Executing sub_query '{sub_query}' using tool '{tool}'")

        result = ""
        if tool == "SQL":
            # Primary Tool: SQL
            result = text_to_sql.process(sub_query)
            # Check if SQL failed or returned no results
            if not result or "No results found" in result or "error" in result.lower():
                print(f"  - ⚠️ SQL failed or returned no results. Falling back to Vector Search.")
                # Fallback 1: Vector Search
                result = execute_rag_pipeline(sub_query)
                if not result:
                    print(f"  - ⚠️ Vector Search also failed. Falling back to Web Search.")
                    # Fallback 2: Web Search
                    result = web_search.process(sub_query)
        elif tool == "VECTOR_SEARCH":
            # Primary Tool: Vector Search
            result = execute_rag_pipeline(sub_query)
            if not result:
                print(f"  - ⚠️ Vector Search failed. Falling back to Web Search.")
                # Fallback: Web Search
                result = web_search.process(sub_query)
        elif tool == "GENERAL":
            result = "This part of the query is conversational and does not require a data lookup."
        
        print(f"  - ✅ Result from Step {i+1}: {result}")
        collected_context.append(f"Context for '{sub_query}':\n{result}")

    # 3. Synthesizer Agent creates the final answer
    print("\n✍️ [Agent 5: Synthesizer] Generating final answer from all collected context...")
    final_context = "\n\n---\n\n".join(collected_context)
    print("\n" + "="*20 + " FINAL CONTEXT " + "="*20)
    print(final_context)
    print("="*55 + "\n")

    final_answer = synthesizer.process(user_query, final_context)
    return final_answer

# --- Streamlit UI ---
st.title("VID - Virtual Information Desk")
# ... (rest of your app.py file)