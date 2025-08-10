# utils/retrieval.py

def search_faiss_with_fallback(query, vector_store, top_k=5):
    try:
        return vector_store.search_faiss(query, top_k)
    except Exception as e:
        print("FAISS failed, falling back to BM25:", e)
        return vector_store.search_bm25(query, top_k)
