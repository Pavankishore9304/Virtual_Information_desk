import os, json
from dotenv import load_dotenv
load_dotenv()

# Ensure key present
assert os.getenv("OPENROUTER_API_KEY"), "Missing OPENROUTER_API_KEY"

from core.llm.llm_client import generate_response
from agents.planner import PlannerAgent
from agents.text_to_sql import TextToSQLAgent
from agents.reasoner import ReasonerAgent
from agents.synthesizer import SynthesizerAgent
from core.db.database import get_db
from core.rag.vector_store import VectorStore

def test_llm_basic():
    resp = generate_response("Return exactly: OK", role="GENERIC")
    print("GENERIC model resp:", resp[:80])

def test_planner():
    agent = PlannerAgent()
    plan = agent.process("What are the objectives of the 5 credit Python course?")
    print("Planner plan:", json.dumps(plan, indent=2))

def test_text_to_sql():
    db = next(get_db())
    agent = TextToSQLAgent(db)
    out = agent.process("list 5 credit courses in semester 5")
    print("SQL agent result:\n", out)

def test_reasoner_and_synth():
    reasoner = ReasonerAgent()
    synth = SynthesizerAgent()
    chunks = [
        "Python for Computational Problem Solving: Objectives include problem decomposition, data structures, scripting."
    ]
    refined = reasoner.process("What are objectives of python course?", chunks)
    print("Reasoner refined:", refined)
    final = synth.process("What are objectives of python course?", refined)
    print("Synthesizer final:", final)

def test_rag_pipeline():
    vs = VectorStore("data/documents/processed")
    query = "Explain objectives of Python for Computational Problem Solving"
    # simple retrieve (assuming VectorStore has a .search or .similar method)
    if hasattr(vs, "search"):
        hits = vs.search(query, k=4)
    elif hasattr(vs, "similarity_search"):
        hits = vs.similarity_search(query, k=4)
    else:
        hits = []
    print(f"Vector hits: {len(hits)}")
    for i,h in enumerate(hits):
        print(f"[{i}] {(h[:140] if isinstance(h,str) else h)}")

if __name__ == "__main__":
    print("=== LLM Basic ===")
    test_llm_basic()
    print("\n=== Planner ===")
    test_planner()
    print("\n=== TextToSQL ===")
    test_text_to_sql()
    print("\n=== Reasoner + Synthesizer ===")
    test_reasoner_and_synth()
    print("\n=== Raw RAG ===")
    test_rag_pipeline()