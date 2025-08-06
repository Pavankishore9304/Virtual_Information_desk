import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

from agents.planner import PlannerAgent
from agents.text_to_sql import TextToSQLAgent
from agents.retriever_agent import RetrieverAgent
from agents.reasoner import ReasonerAgent
from agents.synthesizer import SynthesizerAgent
from core.rag.vector_store import VectorStore
from core.db.database import get_db

@st.cache_resource
def initialize_agents_and_services():
    print("🚀 Initializing Agents and Services...")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("API key not found. Please set GOOGLE_API_KEY in your .env file.")
    genai.configure(api_key=api_key)

    db_session = next(get_db())
    vector_store = VectorStore("data/documents/processed")

    agents = {
        "planner": PlannerAgent(),
        "text_to_sql": TextToSQLAgent(db_session),
        "retriever": RetrieverAgent(vector_store),
        "reasoner": ReasonerAgent(),
        "synthesizer": SynthesizerAgent()
    }
    print("✅ Agents and Services Initialized.")
    return agents

def execute_rag_pipeline(query: str, agents: dict) -> str:
    print(f"  - Executing RAG pipeline for: '{query}'")
    retrieved_chunks = agents["retriever"].process(query)
    if not retrieved_chunks:
        return "No relevant information found in documents."
    refined_context = agents["reasoner"].process(query, retrieved_chunks)
    return refined_context

def run_agentic_pipeline(user_query: str, agents: dict):
    status_update = "🚦 [Agent 1: Planner] Breaking down the query into a plan..."
    print(f"\n{status_update}")
    yield status_update
    plan = agents["planner"].process(user_query)
    
    plan_str = f"  - Generated Plan: {json.dumps(plan, indent=2)}"
    print(plan_str)
    yield plan_str

    status_update = "\n🔎 [Execution Engine] Running the plan..."
    print(status_update)
    yield status_update
    
    collected_context = []
    for i, step in enumerate(plan):
        sub_query = step.get("sub_query")
        tool = step.get("tool")
        
        step_update = f"\n  - Step {i+1}: Executing '{sub_query}' using tool '{tool}'"
        print(step_update)
        yield step_update

        if tool == "SQL":
            result = agents["text_to_sql"].process(sub_query)
            collected_context.append(f"Result for '{sub_query}':\n{result}")
        elif tool == "VECTOR_SEARCH":
            result = execute_rag_pipeline(sub_query, agents)
            collected_context.append(f"Information regarding '{sub_query}':\n{result}")
        elif tool == "GENERAL":
            result = "This part of the query is conversational or cannot be answered by the available tools."
            collected_context.append(result)
        
        yield f"    - Tool '{tool}' finished."

    status_update = "\n✍️ [Final Agent: Synthesizer] Generating final answer..."
    print(status_update)
    yield status_update
    
    final_context = "\n\n---\n\n".join(collected_context)
    final_answer = agents["synthesizer"].process(user_query, final_context)
    
    yield final_answer

# --- Streamlit UI ---
st.set_page_config(page_title="VID AI Assistant", page_icon="🤖")
st.title("🤖 VID AI Assistant")
st.caption("Your intelligent assistant for all information about PES University.")

agents = initialize_agents_and_services()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask me anything about lecturers, clubs, or courses..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("🧠 Thinking...", expanded=True) as status:
            final_response = ""
            for response_part in run_agentic_pipeline(prompt, agents):
                final_response = response_part
                status.update(label=f"🧠 Thinking... {final_response}", state="running")
            
            status.update(label="✅ Done!", state="complete")
        
        st.markdown(final_response)

    st.session_state.messages.append({"role": "assistant", "content": final_response})