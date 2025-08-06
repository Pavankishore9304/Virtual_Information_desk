import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import text
from core.db.schema_inspector import get_db_schema_for_sql_agent
import re

class TextToSQLAgent:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.prompt_template = """
        You are an expert PostgreSQL assistant. Your task is to convert natural language questions into SQL queries.
        You have access to a database with the following schema:

        --- SCHEMA ---
        {db_schema}
        --- END SCHEMA ---

        Based on a user's question, generate a SINGLE, executable SQL query.
        - For questions about counting, use COUNT(*).
        - For questions about specific details, select the relevant columns.
        - If a column name contains spaces, enclose it in double quotes (e.g., "subject name").
        - If you cannot answer the question with the given tables, respond with "I cannot answer this question with SQL."

        User Query: "{user_query}"
        SQL Query:
        """

    def _convert_to_roman(self, num: int) -> str:
        """Converts an integer to a Roman numeral for numbers 1-10."""
        val = [10, 9, 5, 4, 1]
        syb = ["X", "IX", "V", "IV", "I"]
        roman_num = ""
        i = 0
        # This is a standard integer-to-roman conversion algorithm
        while num > 0:
            for _ in range(num // val[i]):
                roman_num += syb[i]
                num -= val[i]
            i += 1
        return roman_num

    def _preprocess_query_for_numerals(self, query: str) -> str:
        """
        Finds patterns like 'semester 5' and converts the number to a Roman numeral.
        """
        # This regex looks for the word "semester" followed by a space and a number (1-10)
        pattern = re.compile(r'semester\s+([1-9]|10)\b', re.IGNORECASE)
        
        def replace_match(match):
            # The number is in the first captured group
            arabic_num = int(match.group(1))
            roman_num = self._convert_to_roman(arabic_num)
            return f"semester {roman_num}"

        # Substitute all found patterns in the query
        processed_query = pattern.sub(replace_match, query)
        
        if processed_query != query:
            print(f"  - Pre-processed query: '{query}' -> '{processed_query}'")
            
        return processed_query

    def _generate_sql(self, user_query: str) -> str:
        prompt = self.prompt_template.format(
            db_schema=get_db_schema_for_sql_agent(),
            user_query=user_query
        )
        response = self.model.generate_content(prompt)
        return response.text.strip().replace('`', '').replace('sql', '').strip()

    def _execute_sql(self, sql_query: str) -> str:
        try:
            results = self.db_session.execute(text(sql_query)).all()
            if not results:
                return "No data found for the given query."
            if len(results) == 1 and len(results[0]) == 1:
                return str(results[0][0])
            
            formatted_results = []
            for row in results:
                row_str = ", ".join(f"{key}: {value}" for key, value in row._mapping.items())
                formatted_results.append(row_str)
            return "\n".join(formatted_results)
        except Exception as e:
            print(f"Error executing SQL: {e}")
            return "An error occurred while querying the database."

    def process(self, user_query: str) -> str:
        print(f"⚙️ TextToSQL Agent processing: '{user_query}'")
        
        # NEW: Pre-process the query before sending it to the LLM
        processed_query = self._preprocess_query_for_numerals(user_query)
        
        generated_sql = self._generate_sql(processed_query)
        print(f"  - Generated SQL: {generated_sql}")

        if "cannot answer" in generated_sql.lower():
            return generated_sql

        return self._execute_sql(generated_sql)