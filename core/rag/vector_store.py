import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from typing import List

class VectorStore:
    def __init__(self, store_path: str):
        self.store_path = store_path
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.db = self._load_store()

    def _load_store(self):
        """Loads an existing FAISS vector store if it exists."""
        if os.path.exists(self.store_path):
            print(f"  - Loading existing vector store from: {self.store_path}")
            try:
                return FAISS.load_local(self.store_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"  - Error loading vector store: {e}. A new one will be created if you build it.")
                return None
        else:
            return None

    def build_from_chunks(self, chunks: List[Document]):
        """
        Builds a new FAISS vector store from a list of document chunks
        and saves it to the specified path.
        """
        if not chunks:
            print("Warning: No chunks provided to build the vector store.")
            return
            
        print(f"  - Building vector store with {len(chunks)} chunks...")
        try:
            db = FAISS.from_documents(chunks, self.embeddings)
            db.save_local(self.store_path)
            self.db = db
            print(f"  - Vector store successfully built and saved to {self.store_path}")
        except Exception as e:
            print(f"  - 🚨 An error occurred while building the vector store: {e}")

    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Performs a similarity search on the vector store.
        """
        if self.db is None:
            print("Error: Vector store is not loaded or built. Cannot perform search.")
            return []
        
        try:
            results = self.db.similarity_search(query, k=k)
            return [doc.page_content for doc in results]
        except Exception as e:
            print(f"An error occurred during vector search: {e}")
            return []