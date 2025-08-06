import os
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.rag.vector_store import VectorStore
from dotenv import load_dotenv

load_dotenv() 
# --- Configuration ---
RAW_DOCS_PATH = "data/documents/raw"
PROCESSED_VECTORS_PATH = "data/documents/processed"

def process_documents():
    """
    Processes all documents in the RAW_DOCS_PATH, chunks them,
    and builds a new vector store.
    """
    print(f"Starting document processing from '{RAW_DOCS_PATH}'...")
    all_docs = []

    # 1. Load documents from the raw directory
    for filename in os.listdir(RAW_DOCS_PATH):
        file_path = os.path.join(RAW_DOCS_PATH, filename)
        if not os.path.isfile(file_path):
            continue

        print(f"  - Loading file: {filename}")
        try:
            if filename.endswith(".pdf"):
                with fitz.open(file_path) as doc:
                    text = "".join(page.get_text() for page in doc)
                    all_docs.append({"source": filename, "content": text})
            elif filename.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    all_docs.append({"source": filename, "content": text})
            else:
                print(f"    - Skipping unsupported file type: {filename}")
        except Exception as e:
            print(f"    - Error processing file {filename}: {e}")

    if not all_docs:
        print("No documents found to process. Exiting.")
        return

    print(f"\nLoaded {len(all_docs)} documents.")

    # 2. Split the documents into smaller chunks
    print("Splitting documents into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    
    all_chunks = []
    for doc in all_docs:
        chunks = text_splitter.create_documents(
            [doc["content"]], 
            metadatas=[{"source": doc["source"]}]
        )
        all_chunks.extend(chunks)
        print(f"  - Created {len(chunks)} chunks from {doc['source']}")

    print(f"\nTotal chunks created: {len(all_chunks)}")

    # 3. Create and save the vector store
    print(f"Creating and saving vector store to '{PROCESSED_VECTORS_PATH}'...")
    vector_store = VectorStore(PROCESSED_VECTORS_PATH)
    vector_store.build_from_chunks(all_chunks)
    print("✅ Vector store built and saved successfully!")


if __name__ == "__main__":
    process_documents()