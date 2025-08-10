from core.rag.vector_store import VectorStore

class RetrieverAgent:
    """
    An agent responsible for retrieving relevant information from the vector store.
    """
    def __init__(self, vector_store: VectorStore):
        """
        Initializes the RetrieverAgent with a VectorStore instance.

        Args:
            vector_store (VectorStore): An instance of the vector store to search in.
        """
        self.vector_store = vector_store

    def process(self, query: str) -> list[str]:
        """
        Processes a query by searching the vector store for relevant document chunks.

        Args:
            query (str): The query to search for.

        Returns:
            list[str]: A list of relevant document chunks.
        """
        print(f"🔎 Searching with query: {query}")
        # Changed from 'hybrid_search' to the new 'search' method
        results = self.vector_store.search(query)
        return results