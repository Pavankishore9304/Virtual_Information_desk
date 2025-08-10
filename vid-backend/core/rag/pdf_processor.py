import os
import json
import fitz  # PyMuPDF
import tiktoken
import google.generativeai as genai
from dotenv import load_dotenv

# --- Initialization ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set GEMINI_API_KEY or GOOGLE_API_KEY in your .env file.")
genai.configure(api_key=api_key)

# Using tiktoken for accurate token-based chunking
tokenizer = tiktoken.get_encoding("cl100k_base")

def _extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def _chunk_text(text, chunk_size=512, chunk_overlap=50):
    """Splits text into chunks based on token count."""
    tokens = tokenizer.encode(text)
    chunks = []
    for i in range(0, len(tokens), chunk_size - chunk_overlap):
        chunk_tokens = tokens[i:i + chunk_size]
        chunks.append(tokenizer.decode(chunk_tokens))
    return chunks

def process_pdf(pdf_path, processed_dir):
    """
    Processes a single PDF file:
    1. Extracts text.
    2. Chunks the text.
    3. Generates embeddings for each chunk.
    4. Saves the structured data to a JSON file.
    """
    print(f"Processing {pdf_path}...")
    
    # 1. Extract text
    full_text = _extract_text_from_pdf(pdf_path)
    if not full_text.strip():
        print(f"Warning: No text extracted from {pdf_path}. Skipping.")
        return

    # 2. Chunk text
    text_chunks = _chunk_text(full_text)
    print(f"  - Extracted {len(text_chunks)} chunks.")

    # 3. Generate embeddings in a single batch call for efficiency
    print("  - Generating embeddings...")
    try:
        embedding_result = genai.embed_content(
            model="models/embedding-001",
            content=text_chunks,
            task_type="RETRIEVAL_DOCUMENT"
        )
        embeddings = embedding_result['embedding']
    except Exception as e:
        print(f"  - Error generating embeddings: {e}")
        return

    # 4. Combine chunks with their embeddings
    structured_data = [{'text': text, 'embedding': emb} for text, emb in zip(text_chunks, embeddings)]

    # 5. Save to a JSON file
    output_filename = os.path.basename(pdf_path).replace('.pdf', '.json')
    output_path = os.path.join(processed_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_data, f, indent=2)
        
    print(f"  - Successfully saved processed data to {output_path}")
