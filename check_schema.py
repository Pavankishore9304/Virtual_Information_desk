from core.db.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()

print("DATABASE TABLES:")
for table in tables:
    print(f"\nTable: {table}")
    columns = inspector.get_columns(table)
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")
