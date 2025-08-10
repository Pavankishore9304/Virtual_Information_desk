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
    Inspects the database and generates a high-level summary of each table's purpose.
    This provides detailed information about what data is available for the Planner agent.
    """
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    
    if not table_names:
        return "No tables found in the database."
    
    summaries = []
    
    # Define what each table contains
    table_descriptions = {
        "lecturers": "Contains detailed information about faculty members including: name, role (Professor/Associate Professor/Assistant Professor), education background, experience at PES, teaching subjects, responsibilities, and research interests. Use this for queries about specific lecturers, their qualifications, subjects they teach, research areas, etc.",
        "clubs": "Contains information about student clubs including: name, category, description/about, founded year, recruitment procedures, recruitment timing, and goals. Use this for queries about student organizations, clubs, activities, etc.",
        "course": "Contains basic course metadata including: semester, subject name, credits, core/elective status, prerequisites, course codes. For detailed course content, subject descriptions, what is taught in each semester, use VECTOR_SEARCH instead.",
        "campuses": "Contains basic campus information including: pincode, campus_name, location, infrastructure level. NOTE: Does NOT contain founding/establishment dates - use VECTOR_SEARCH for historical information about university establishment.",
        "categories": "Contains course category information (category_id, category_name).",
        "courses": "Contains course offerings (course_id, pincode, category_id, course_name).",
        "specialization": "Contains specialization information (specialization_id, course_id, specialization_name)."
    }
    
    with engine.connect() as connection:
        for table_name in table_names:
            # Get column information for better context
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            # Use predefined description or generate from columns
            if table_name in table_descriptions:
                description = table_descriptions[table_name]
            else:
                description = f"Contains data with columns: {', '.join(column_names)}"
            
            # Get approximate row count for context
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                row_count = connection.execute(count_query).scalar()
                description += f" (Currently has {row_count} records)"
            except:
                description += " (Row count unavailable)"
            
            summaries.append(f"- **{table_name}**: {description}")
            
    return "\n".join(summaries)
