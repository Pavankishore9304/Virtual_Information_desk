import os
from core.rag.pdf_processor import process_pdf

if __name__ == "__main__":
    RAW_DIR = "data/documents/raw"
    PROCESSED_DIR = "data/documents/processed"

    # Ensure output directory exists
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    # Clear out old processed files to avoid stale data
    print("Clearing old processed files...")
    for f in os.listdir(PROCESSED_DIR):
        os.remove(os.path.join(PROCESSED_DIR, f))

    print("\nStarting PDF processing...")
    for filename in os.listdir(RAW_DIR):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(RAW_DIR, filename)
            process_pdf(pdf_path, PROCESSED_DIR)
    
    print("\nAll PDFs processed.")