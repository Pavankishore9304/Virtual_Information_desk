"""
Quick test script to check if data retrieval is working properly
"""
from core.db.database import get_db
from sqlalchemy import text
from agents.text_to_sql import TextToSQLAgent
from agents.retriever_agent import RetrieverAgent
from core.rag.vector_store import VectorStore

def test_database_data():
    """Test if data is properly loaded in the database"""
    print("=== Testing Database Data ===")
    
    db_session = next(get_db())
    
    # Test lecturers table
    try:
        result = db_session.execute(text("SELECT COUNT(*) FROM lecturers")).scalar()
        print(f"Lecturers table has {result} records")
        
        # Get sample lecturer
        sample = db_session.execute(text("SELECT name, role FROM lecturers LIMIT 3")).fetchall()
        print("Sample lecturers:")
        for row in sample:
            print(f"  - {row.name} ({row.role})")
    except Exception as e:
        print(f"Error querying lecturers: {e}")
    
    # Test clubs table
    try:
        result = db_session.execute(text("SELECT COUNT(*) FROM clubs")).scalar()
        print(f"Clubs table has {result} records")
        
        # Get sample clubs
        sample = db_session.execute(text("SELECT name, category FROM clubs LIMIT 3")).fetchall()
        print("Sample clubs:")
        for row in sample:
            print(f"  - {row.name} ({row.category})")
    except Exception as e:
        print(f"Error querying clubs: {e}")

def test_sql_agent():
    """Test SQL agent with sample queries"""
    print("\n=== Testing SQL Agent ===")
    
    db_session = next(get_db())
    sql_agent = TextToSQLAgent(db_session)
    
    test_queries = [
        "Who is Dr. Sandesh BJ?",
        "Tell me about Dr. Arti Arya",
        "Show me all professors",
        "What clubs are there?",
        "Tell me about Maaya club"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = sql_agent.process(query)
            print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")

def test_vector_search():
    """Test vector search"""
    print("\n=== Testing Vector Search ===")
    
    vector_store = VectorStore("data/documents/processed")
    retriever = RetrieverAgent(vector_store)
    
    test_queries = [
        "semester 5 subjects",
        "computer science curriculum",
        "university policies"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            results = retriever.process(query)
            print(f"Found {len(results)} chunks")
            if results:
                print(f"Sample result: {results[0][:200]}...")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_database_data()
    test_sql_agent()
    test_vector_search()
