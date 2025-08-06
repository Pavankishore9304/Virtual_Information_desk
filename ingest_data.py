import os
import shutil
import fitz  # PyMuPDF
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.rag.vector_store import VectorStore
from core.db.database import get_db, engine
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
STAGING_PATH = "data/staging"
ARCHIVE_PATH = "data/archive"
PROCESSED_VECTORS_PATH = "data/documents/processed"

def process_unstructured_files(file_path, filename):
    """Processes PDF and TXT files and returns document chunks."""
    print(f"  - Processing unstructured file: {filename}")
    all_docs = []
    try:
        if filename.endswith(".pdf"):
            with fitz.open(file_path) as doc:
                text = "".join(page.get_text() for page in doc)
                all_docs.append({"source": filename, "content": text})
        elif filename.endswith(".txt"):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                all_docs.append({"source": filename, "content": text})
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        all_chunks = []
        for doc in all_docs:
            chunks = text_splitter.create_documents([doc["content"]], metadatas=[{"source": doc["source"]}])
            all_chunks.extend(chunks)
        print(f"    - Created {len(all_chunks)} chunks.")
        return all_chunks
    except Exception as e:
        print(f"    - 🚨 Error processing {filename}: {e}")
        return []

def process_structured_file(file_path, filename):
    """Processes CSV files and ingests them into the corresponding SQL table."""
    print(f"  - Processing structured file: {filename}")
    try:
        table_name = os.path.splitext(filename)[0] # Assumes 'lecturers.csv' -> 'lecturers' table
        df = pd.read_csv(file_path)
        
        print(f"    - Ingesting {len(df)} rows into PostgreSQL table '{table_name}'...")
        # Use pandas to_sql to append data to the existing table
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"    - ✅ Successfully ingested data into '{table_name}'.")
        return True
    except Exception as e:
        print(f"    - 🚨 Error processing {filename}: {e}")
        return False

def run_ingestion():
    """
    Main function to run the intelligent data ingestion pipeline.
    """
    print("🚀 Starting Intelligent Ingestion Pipeline...")
    os.makedirs(STAGING_PATH, exist_ok=True)
    os.makedirs(ARCHIVE_PATH, exist_ok=True)

    files_to_process = [f for f in os.listdir(STAGING_PATH) if os.path.isfile(os.path.join(STAGING_PATH, f))]
    if not files_to_process:
        print("✅ No new files found in the staging directory. Exiting.")
        return

    unstructured_chunks = []
    processed_files = []

    for filename in files_to_process:
        file_path = os.path.join(STAGING_PATH, filename)
        
        if filename.lower().endswith(('.pdf', '.txt')):
            chunks = process_unstructured_files(file_path, filename)
            if chunks:
                unstructured_chunks.extend(chunks)
                processed_files.append(filename)

        elif filename.lower().endswith('.csv'):
            success = process_structured_file(file_path, filename)
            if success:
                processed_files.append(filename)

    # Update the vector store if there were any new unstructured files
    if unstructured_chunks:
        print("\n🔄 Updating Vector Store with new documents...")
        vector_store = VectorStore(PROCESSED_VECTORS_PATH)
        # This assumes your VectorStore can be updated. A simple approach is to rebuild.
        # For a true "update", the VectorStore class would need an `add_chunks` method.
        # For now, we will stick to the robust build method.
        vector_store.build_from_chunks(unstructured_chunks)
        print("✅ Vector Store updated.")

    # Move processed files to the archive
    print("\n🗄️ Archiving processed files...")
    for filename in processed_files:
        shutil.move(os.path.join(STAGING_PATH, filename), os.path.join(ARCHIVE_PATH, filename))
        print(f"  - Moved {filename} to archive.")

    print("\n🎉 Intelligent Ingestion Pipeline finished successfully!")

if __name__ == "__main__":
    run_ingestion()