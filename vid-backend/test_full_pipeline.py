"""
Test the complete agentic pipeline to identify where the issue is
"""
from agents.planner import PlannerAgent
from agents.text_to_sql import TextToSQLAgent
from agents.retriever_agent import RetrieverAgent
from agents.reasoner import ReasonerAgent
from agents.synthesizer import SynthesizerAgent
from core.rag.vector_store import VectorStore
from core.db.database import get_db

def execute_rag_pipeline(query: str, agents: dict) -> str:
    print(f"  - Executing RAG pipeline for: '{query}'")
    retrieved_chunks = agents["retriever"].process(query)
    if not retrieved_chunks:
        return "No relevant information found in documents."
    refined_context = agents["reasoner"].process(query, retrieved_chunks)
    return refined_context

def test_full_pipeline(query: str):
    """Test the complete pipeline with a sample query"""
    print(f"\n{'='*60}")
    print(f"Testing Query: {query}")
    print(f"{'='*60}")
    
    # Initialize agents
    db_session = next(get_db())
    vector_store = VectorStore("data/documents/processed")
    
    agents = {
        "planner": PlannerAgent(),
        "text_to_sql": TextToSQLAgent(db_session),
        "retriever": RetrieverAgent(vector_store),
        "reasoner": ReasonerAgent(),
        "synthesizer": SynthesizerAgent()
    }
    
    # Step 1: Planning
    print("\n🚦 [Step 1: Planner] Breaking down the query...")
    plan = agents["planner"].process(query)
    print(f"Generated Plan: {plan}")
    
    # Step 2: Execute plan
    print("\n🔎 [Step 2: Execution] Running the plan...")
    collected_context = []
    step_results = {}
    
    for step in plan:
        step_num = step.get("step")
        thought = step.get("thought")
        tool = step.get("tool")
        sub_query = step.get("sub_query")
        
        print(f"\n  - Step {step_num}: {thought}")
        print(f"    Tool: {tool}, Query: '{sub_query}'")
        
        result = ""
        if tool == "SQL":
            result = agents["text_to_sql"].process(sub_query)
        elif tool == "VECTOR_SEARCH":
            result = execute_rag_pipeline(sub_query, agents)
        elif tool == "GENERAL":
            result = "This part of the query is conversational."
        
        step_results[step_num] = result
        collected_context.append(f"Result for Step {step_num} ('{sub_query}'):\n{result}")
        print(f"    Result: {result[:200]}...")
    
    # Step 3: Synthesis
    print("\n✍️ [Step 3: Synthesizer] Generating final answer...")
    final_context = "\n\n---\n\n".join(collected_context)
    final_answer = agents["synthesizer"].process(query, final_context)
    
    print(f"\n🎯 Final Answer: {final_answer}")
    return final_answer

if __name__ == "__main__":
    test_queries = [
        "Who is Dr. Sandesh BJ?",
        "Tell me about Maaya club",
        "What subjects are taught in semester 5?",
        "Tell me about Dr. Arti Arya and her research interests"
    ]
    
    for query in test_queries:
        test_full_pipeline(query)
