import os
import pandas as pd
import re
import shutil
from core.db.database import engine

# --- Configuration ---
STAGING_PATH = "data/staging"
ARCHIVE_PATH = "data/archive"

def clean_table_name(filename: str) -> str:
    """Cleans a filename to be a valid SQL table name."""
    # Remove the .csv extension
    name = filename.lower().replace('.csv', '')
    # Replace spaces and hyphens with underscores
    name = re.sub(r'[\s-]+', '_', name)
    # Remove any other invalid characters
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

def ingest_data():
    """
    Scans the staging directory for CSV files, loads them into PostgreSQL,
    and moves them to the archive directory.
    """
    print("🚀 Starting data ingestion process...")
    
    # Ensure staging and archive directories exist
    os.makedirs(STAGING_PATH, exist_ok=True)
    os.makedirs(ARCHIVE_PATH, exist_ok=True)

    files_to_process = [f for f in os.listdir(STAGING_PATH) if f.endswith('.csv')]

    if not files_to_process:
        print("✅ No new CSV files found in the staging directory.")
        return

    for filename in files_to_process:
        try:
            file_path = os.path.join(STAGING_PATH, filename)
            table_name = clean_table_name(filename)
            
            print(f"  - Processing '{filename}'...")
            print(f"    - Reading CSV into DataFrame.")
            df = pd.read_csv(file_path)

            print(f"    - Writing DataFrame to PostgreSQL table: '{table_name}'")
            # This will create a new table or replace an existing one.
            # The schema is inferred automatically by pandas.
            df.to_sql(table_name, engine, if_exists='replace', index=False)

            # Move the processed file to the archive
            shutil.move(file_path, os.path.join(ARCHIVE_PATH, filename))
            print(f"    - Successfully ingested. Moved '{filename}' to archive.")

        except Exception as e:
            print(f"❌ Error processing '{filename}': {e}")

    print("✅ Data ingestion process finished.")

if __name__ == "__main__":
    ingest_data()