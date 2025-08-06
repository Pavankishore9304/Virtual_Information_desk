from sqlalchemy import inspect, text
from .database import engine

def get_db_schema_for_sql_agent() -> str:
    """
    Inspects the database and generates a detailed schema string for the TextToSQL agent.
    """
    inspector = inspect(engine)
    schema_info = []
    table_names = inspector.get_table_names()

    if not table_names:
        return "No tables found in the database."

    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        column_details = [f"- {col['name']} ({col['type']})" for col in columns]
        schema_info.append(f"Table `{table_name}`:\n" + "\n".join(column_details))
    
    return "\n\n".join(schema_info)

def get_db_summary_for_planner_agent() -> str:
    """
    Inspects the database and generates a high-level summary of each table's purpose,
    using table comments from the database. This is for the Planner agent.
    """
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    summaries = []

    with engine.connect() as connection:
        for table_name in table_names:
            # Query to get the comment for a table in PostgreSQL
            query = text(f"""
                SELECT obj_description('"{table_name}"'::regclass, 'pg_class')
            """)
            result = connection.execute(query).scalar()
            comment = result if result else "No description available."
            summaries.append(f"- **{table_name}**: {comment}")
            
    return "\n".join(summaries)