# routes/ask.py

from fastapi import APIRouter
from pydantic import BaseModel
from agents.query_rewriter import QueryRewriterAgent
from agents.retriever_agent import RetrieverAgent
from rag.vector_store import VectorStore
from agents.synthesizer import SynthesizerAgent  # you'll define this next

router = APIRouter()

# Load once
rewriter = QueryRewriterAgent()
store = VectorStore("data/documents/processed")
store.build_index()
retriever = RetrieverAgent(store)
synthesizer = SynthesizerAgent()  # We'll build this next

class QueryInput(BaseModel):
    query: str

@router.post("/ask")
def handle_query(q: QueryInput):
    user_query = q.query

    # Step 1: Rewrite
    rewritten = rewriter.process(user_query)

    # Step 2: Retrieve relevant chunks
    chunks = retriever.process(rewritten)

    # Step 3: Synthesize final answer
    response = synthesizer.process(user_query, chunks)

    return {"answer": response}
