import streamlit as st
import os
from dotenv import load_dotenv
import json
import re

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
    # This dictionary will store the results of each step
    step_results = {}

    for step in plan:
        step_num = step.get("step")
        thought = step.get("thought")
        tool = step.get("tool")
        sub_query = step.get("sub_query")

        step_update = f"\n  - Step {step_num}: {thought}"
        print(step_update)
        yield step_update

        # ** NEW: Check for and substitute results from previous steps **
        # This regex finds all instances of {{step_N_result}}
        placeholders = re.findall(r"\{\{step_(\d+)_result\}\}", sub_query)
        for placeholder_step_num in placeholders:
            prev_step_result = step_results.get(int(placeholder_step_num))
            if prev_step_result:
                sub_query = sub_query.replace(f"{{{{step_{placeholder_step_num}_result}}}}", f'"{prev_step_result}"')
        
        yield f"    - Executing with tool '{tool}': '{sub_query}'"

        result = ""
        if tool == "SQL":
            result = agents["text_to_sql"].process(sub_query)
        elif tool == "VECTOR_SEARCH":
            result = execute_rag_pipeline(sub_query, agents)
        elif tool == "GENERAL":
            result = "This part of the query is conversational or cannot be answered by the available tools."
        
        # Store the result of the current step
        step_results[step_num] = result
        collected_context.append(f"Result for Step {step_num} ('{sub_query}'):\n{result}")
        yield f"    - Step {step_num} finished."

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
