import os
import json
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from core.db.database import Lecturer

# --- Initialization ---
load_dotenv()

# Configure the client to use OpenRouter
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    raise ValueError("OPENROUTER_API_KEY not found in .env file. Please add it.")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openrouter_api_key,
)

def _clean_json_string(s: str) -> str | None:
    """Cleans the LLM response to extract a valid JSON array string."""
    s = s.strip().replace("```json", "").replace("```", "")
    start_index = s.find('[')
    end_index = s.rfind(']')
    if start_index != -1 and end_index != -1:
        return s[start_index:end_index+1]
    return None

def process_faculty_pdf_to_db(pdf_path: str, db: Session):
    """
    Processes a faculty PDF using OpenRouter with checkpointing to allow for resuming.
    Extracts data, de-duplicates it, and populates the 'lecturers' table.
    """
    CHECKPOINT_FILE = "ingestion_checkpoint.json"
    all_lecturers_data = []
    start_page = 0

    # 1. Check for a checkpoint file to resume progress
    if os.path.exists(CHECKPOINT_FILE):
        print(f"  - Found checkpoint file: {CHECKPOINT_FILE}. Attempting to resume...")
        with open(CHECKPOINT_FILE, 'r') as f:
            try:
                checkpoint_data = json.load(f)
                all_lecturers_data = checkpoint_data.get("data", [])
                last_processed_page = checkpoint_data.get("last_processed_page", -1)
                start_page = last_processed_page + 1
                print(f"  - Resuming from page {start_page + 1}.")
            except json.JSONDecodeError:
                print("  - Warning: Checkpoint file is corrupted. Starting from scratch.")
    
    print(f"Processing faculty data from {pdf_path} using OpenRouter...")
    doc = fitz.open(pdf_path)

    # 2. Loop through each page of the PDF, starting from the correct page
    if start_page < len(doc):
        for page_num in range(start_page, len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if not page_text.strip():
                continue

            print(f"  - Processing Page {page_num + 1}/{len(doc)}...")

            prompt = f"""
            You are a highly precise data extraction assistant. Your task is to analyze the text from a single page of a university document and extract details for each faculty member.

            Carefully extract the following fields for each person:
            - "name": The full name of the person (e.g., "Dr. Jane Smith").
            - "role": Their primary job title (e.g., "Professor", "Assistant Professor").
            - "education": Their educational qualifications (e.g., "Ph.D. in CSE, M.Tech").
            - "experience_in_pes": Their years of experience at PES or total experience if specified.
            - "teaching_subjects": A list of subjects they teach.
            - "responsibilities": Their key roles or responsibilities.
            - "research_interest": Their specific areas of research.

            RULES:
            1. Return the data as a JSON array of objects.
            2. If a specific piece of information for a field is not found, use an empty string "". DO NOT guess or invent data.
            3. Pay close attention to the document's structure to avoid mixing data from different people.
            4. If no faculty members are found on this page, return an empty array [].

            Here is the text from the current page:
            ---
            {page_text} 
            ---
            JSON Array:
            """
            
            try:
                # Use the OpenRouter client for the API call
                response = client.chat.completions.create(
                    model="google/gemini-2.0-flash-exp:free", # A capable and cost-effective model on OpenRouter
                    messages=[
                        {"role": "system", "content": "You are a JSON extraction expert."},
                        {"role": "user", "content": prompt}
                    ]
                )
                response_content = response.choices[0].message.content
                cleaned_json = _clean_json_string(response_content)
                
                if cleaned_json:
                    page_data = json.loads(cleaned_json)
                    if page_data:
                        all_lecturers_data.extend(page_data)
                        print(f"    - Found {len(page_data)} potential entries on this page.")
                
                # Save progress to the checkpoint file after each successful page
                with open(CHECKPOINT_FILE, 'w') as f:
                    checkpoint = {"last_processed_page": page_num, "data": all_lecturers_data}
                    json.dump(checkpoint, f, indent=4)

            except Exception as e:
                print(f"    - Warning: Could not process page {page_num + 1}. Error: {e}")

    doc.close()
    print(f"\nFinished processing all pages. Total entries found: {len(all_lecturers_data)}")

    # 3. De-duplicate the results before saving
    print("  - De-duplicating entries...")
    unique_lecturers = {}
    for lecturer in all_lecturers_data:
        name = lecturer.get("name", "").strip()
        if name:
            if name not in unique_lecturers:
                unique_lecturers[name] = lecturer

    final_data = list(unique_lecturers.values())
    print(f"  - Total unique lecturers after de-duplication: {len(final_data)}")

    # 4. Insert all unique data into the database
    if final_data:
        try:
            print("  - Saving unique data to the database...")
            for data in final_data:
                lecturer = Lecturer(
                    name=data.get("name", ""),
                    role=data.get("role", ""),
                    education=data.get("education", ""),
                    experience_in_pes=data.get("experience_in_pes", ""),
                    teaching_subjects=str(data.get("teaching_subjects", "")),
                    responsibilities=str(data.get("responsibilities", "")),
                    research_interest=str(data.get("research_interest", ""))
                )
                db.add(lecturer)
            
            db.commit()
            print(f"  - Successfully saved {len(final_data)} unique lecturers to the database.")
            
            # Clean up the checkpoint file on success
            if os.path.exists(CHECKPOINT_FILE):
                os.remove(CHECKPOINT_FILE)
                print("  - Checkpoint file removed.")
        except Exception as e:
            print(f"  - An error occurred during database insertion: {e}")
            print("  - Checkpoint file has been kept for the next run.")
            db.rollback()