from sqlalchemy.orm import Session
from sqlalchemy import text
from core.db.schema_inspector import get_db_schema_for_sql_agent
from core.llm.llm_client import generate_response
import re

class TextToSQLAgent:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.max_retries = 2  # Allow the agent to try to fix its own mistakes
        
        # The initial prompt for the first attempt
        self.base_prompt_template = """
        You are an expert PostgreSQL assistant. Convert the natural language question to a SINGLE SQL query.
        
        CRITICAL RULES:
        - Return ONLY the SQL query, no explanations, no text before/after
        - Use ONLY the schema provided - do not invent columns or tables
        - If column names have spaces, use double quotes
        - For name searches, use ILIKE with % wildcards for partial matching (e.g., name ILIKE '%arya%')
        - Consider name variations: "Arty" could be "Arti", partial names should match full names
        - If cannot answer, return exactly: "Error: Cannot answer with SQL."

        SCHEMA:
        {db_schema}

        Query: "{user_query}"
        
        SQL:
        """

        # A special prompt used for self-correction on retries
        self.retry_prompt_template = """
        You are an expert PostgreSQL assistant. Your previous attempt to generate SQL failed. You MUST correct your mistake.
        Base your new query ONLY on the schema provided. Do not invent columns or tables. The schema is the only source of truth.

        --- SCHEMA ---
        {db_schema}
        --- END SCHEMA ---

        User Query: "{user_query}"
        
        Your Previous Failed SQL:
        ```sql
        {failed_sql}
        ```

        The Database Error Was:
        "{error_message}"

        Your Corrected, New SQL Query:
        """

    def _extract_sql_from_response(self, response: str) -> str:
        """Extract clean SQL from LLM response that may contain explanatory text."""
        # Remove common prefixes and explanations
        response = response.replace('`', '').replace('```sql', '').replace('```', '').strip()
        
        # Check if it's an error response
        if "Error: Cannot answer with SQL." in response or response.startswith("Error:"):
            return "Error: Cannot answer with SQL."
        
        # Split by lines and look for SQL keywords
        lines = response.split('\n')
        sql_lines = []
        capturing = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Start capturing when we see SQL keywords
            if any(line.upper().startswith(keyword) for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']):
                capturing = True
                sql_lines.append(line)
            elif capturing and line.endswith(';'):
                # End of SQL statement
                sql_lines.append(line)
                break
            elif capturing:
                sql_lines.append(line)
        
        if sql_lines:
            return ' '.join(sql_lines)
        
        # If no SQL found but contains SELECT etc, extract the line
        for line in lines:
            line = line.strip()
            if any(keyword in line.upper() for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                # Extract just this line if it looks like SQL
                if 'FROM' in line.upper() or 'WHERE' in line.upper():
                    return line + (';' if not line.endswith(';') else '')
        
        # Final fallback: return error if no SQL found
        return "Error: Cannot answer with SQL."

    def _generate_sql(self, user_query: str, failed_sql: str = None, error_message: str = None) -> str:
        """Generates SQL using either the base or retry prompt."""
        if failed_sql and error_message:
            # Use the retry prompt for self-correction
            prompt = self.retry_prompt_template.format(
                db_schema=get_db_schema_for_sql_agent(),
                user_query=user_query,
                failed_sql=failed_sql,
                error_message=error_message
            )
        else:
            # Use the base prompt for the first attempt
            prompt = self.base_prompt_template.format(
                db_schema=get_db_schema_for_sql_agent(),
                user_query=user_query
            )
        
        response = generate_response(prompt, role="TEXT_TO_SQL")
        return self._extract_sql_from_response(response)

    def _convert_to_roman(self, num: int) -> str:
        val = [10, 9, 5, 4, 1]; syb = ["X", "IX", "V", "IV", "I"]
        roman_num = ""; i = 0
        while num > 0:
            for _ in range(num // val[i]): roman_num += syb[i]; num -= val[i]
            i += 1
        return roman_num

    def _preprocess_query_for_numerals(self, query: str) -> str:
        pattern = re.compile(r'semester\s+([1-9]|10)\b', re.IGNORECASE)
        def replace_match(match):
            return f"semester {self._convert_to_roman(int(match.group(1)))}"
        return pattern.sub(replace_match, query)

    def process(self, user_query: str) -> str:
        print(f"⚙️  TextToSQL Agent processing: '{user_query}'")
        processed_query = self._preprocess_query_for_numerals(user_query)
        
        last_error = ""
        last_sql = ""

        for attempt in range(self.max_retries):
            print(f"  - Attempt {attempt + 1}/{self.max_retries}...")
            
            generated_sql = self._generate_sql(
                processed_query, 
                failed_sql=last_sql if attempt > 0 else None,
                error_message=last_error if attempt > 0 else None
            ).replace('`', '').replace('sql', '').strip()

            print(f"  - Generated SQL: {generated_sql}")
            last_sql = generated_sql

            if "error:" in generated_sql.lower():
                last_error = "Model indicated it cannot answer with SQL."
                continue # Go to the next attempt

            try:
                # Attempt to execute the generated query
                results = self.db_session.execute(text(generated_sql)).all()
                if not results: return "No data found."
                if len(results) == 1 and len(results[0]) == 1: return str(results[0][0])
                
                # Success! Format and return the results.
                formatted_results = ["- " + ", ".join(f"{key}: {value}" for key, value in row._mapping.items()) for row in results]
                return "\n".join(formatted_results)

            except Exception as e:
                # This is the self-correction trigger
                print(f"  - ⚠️ SQL Execution failed: {e}")
                last_error = str(e)
                # The loop will now continue to the next attempt, feeding this error back to the LLM.

        # If all retries fail, return a final error message.
        return f"Error: After multiple attempts, I could not generate a valid SQL query. Last error: {last_error}"
