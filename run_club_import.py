import pandas as pd
from sqlalchemy.orm import Session
from core.db.database import get_db, Club
import numpy as np
import sys

def import_clubs_csv_to_db(csv_path: str, db: Session):
    """
    Clears the clubs table and imports new data from a CSV file.
    """
    try:
        # 1. Read the CSV file
        print(f"Reading club data from {csv_path}...")
        df = pd.read_csv(csv_path)
        # Use the first row for column names and handle potential spaces
        df.columns = [col.strip().replace(' ', '_') for col in df.columns]
        print(f"Found {len(df)} club records in the CSV file.")

        # 2. Replace NaN values with empty strings
        df = df.replace(np.nan, '', regex=True)

        # 3. Clear the existing clubs table
        print("Clearing existing data from the 'clubs' table...")
        num_deleted = db.query(Club).delete()
        db.commit()
        print(f"  - Deleted {num_deleted} old records.")

        # 4. Iterate and insert new records
        print("Inserting new club records into the database...")
        for index, row in df.iterrows():
            club = Club(
                name=row.get("club_name", ""),
                category=row.get("club_category", ""),
                about=row.get("about_club", ""),
                founded_year=row.get("founded_year", ""),
                recruitment_procedure=row.get("recruitment_procedure", ""),
                recruitment_time=row.get("recruitment_time", ""),
                goal=row.get("goal_of_club", "")
            )
            db.add(club)
        
        # 5. Commit all the new records
        db.commit()
        print(f"\nSuccessfully imported {len(df)} clubs into the database.")

    except FileNotFoundError:
        print(f"Error: The file was not found at {csv_path}", file=sys.stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        db.rollback()

if __name__ == "__main__":
    CSV_FILE_PATH = "data/processed/clubs.csv"
    db_session = next(get_db())
    import_clubs_csv_to_db(CSV_FILE_PATH, db_session)