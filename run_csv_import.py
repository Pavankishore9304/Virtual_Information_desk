import pandas as pd
from sqlalchemy.orm import Session
from core.db.database import get_db, Lecturer
import numpy as np
import sys

def import_csv_to_db(csv_path: str, db: Session):
    """
    Clears the lecturers table and imports new data from a CSV file.
    """
    try:
        # 1. Read the CSV file into a pandas DataFrame
        print(f"Reading data from {csv_path}...")
        df = pd.read_csv(csv_path)
        print(f"Found {len(df)} records in the CSV file.")

        # 2. IMPORTANT: Replace pandas' default NaN (Not a Number) with empty strings
        # This prevents errors when inserting into the database.
        df = df.replace(np.nan, '', regex=True)

        # 3. Clear the existing lecturers table to prevent duplicates
        print("Clearing existing data from the 'lecturers' table...")
        num_deleted = db.query(Lecturer).delete()
        db.commit()
        print(f"  - Deleted {num_deleted} old records.")

        # 4. Iterate through the DataFrame and add each lecturer to the database
        print("Inserting new records into the database...")
        for index, row in df.iterrows():
            lecturer = Lecturer(
                name=row.get("name", ""),
                role=row.get("role", ""),
                education=row.get("education", ""),
                experience_in_pes=row.get("experience_in_pes", ""),
                teaching_subjects=row.get("teaching_subjects", ""),
                responsibilities=row.get("responsibilities", ""),
                research_interest=row.get("research_interest", "")
            )
            db.add(lecturer)
        
        # 5. Commit all the new records to the database
        db.commit()
        print(f"\nSuccessfully imported {len(df)} lecturers into the database.")

    except FileNotFoundError:
        print(f"Error: The file was not found at {csv_path}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        db.rollback()

if __name__ == "__main__":
    CSV_FILE_PATH = "data/processed/lecturers.csv"
    db_session = next(get_db())
    import_csv_to_db(CSV_FILE_PATH, db_session)