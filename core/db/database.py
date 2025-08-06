import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# --- Database Connection ---
DB_USER = os.getenv("DB_USER")
# Get the raw password
raw_password = os.getenv("DB_PASSWORD")
# Encode the password to handle special characters like '@'
encoded_password = quote_plus(raw_password)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Use the new encoded password in the URL
DATABASE_URL = f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Table Model (Refined Schema) ---
class Lecturer(Base):
    __tablename__ = "lecturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True) # Added unique=True to prevent duplicates at DB level
    role = Column(String)
    education = Column(String)
    experience_in_pes = Column(String)
    teaching_subjects = Column(Text)
    responsibilities = Column(Text)
    research_interest = Column(Text)

    # --- NEW: Database Table Model for Clubs ---
class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)
    about = Column(Text)
    founded_year = Column(String)
    recruitment_procedure = Column(Text)
    recruitment_time = Column(Text)
    goal = Column(Text)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("Attempting to connect to the database and set up tables...")
    try:
        # This will explicitly drop the tables if they exist
        print("  - Dropping existing tables (if they exist) to ensure a clean slate...")
        Lecturer.__table__.drop(engine, checkfirst=True)
        Club.__table__.drop(engine, checkfirst=True) # <-- Added this line

        # This will create the new tables with the correct, updated schema
        print("  - Creating new tables...")
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"An error occurred during table setup: {e}")