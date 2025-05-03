# query_manager.py for agent/src/xenq_agent/components/query/query_manager.py

import psycopg2
import re
from xenq_server.api import AioHTTPSessionManager
import chainlit as cl

class QueryManager:

    def __init__(self, uri, agent_uri = "http://localhost:5005/prompt"):
        try:
            self.agent_uri = agent_uri
            self.conn = psycopg2.connect(uri)
            self.postgres_cursor= self.conn.cursor()
            self.schema = self.get_llm_friendly_schema(self.postgres_cursor)
            self.conn_status = True
            self.output_file = "./output.txt"
            print("Connected!")
        except Exception:
            self.conn_status = False
        
    def get_status(self):
        return self.conn_status

    def get_llm_friendly_schema1(self, cur):

        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
        """)
        tables = [r[0] for r in cur.fetchall()]

        schema_output = []

        for table in tables:
            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cur.fetchone()[0]

            # Get columns
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table,))
            columns = cur.fetchall()

            # Get primary keys
            cur.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
            """, (table,))
            pk_columns = {r[0] for r in cur.fetchall()}

            # Get foreign keys
            cur.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM
                    information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE
                    tc.constraint_type = 'FOREIGN KEY' AND
                    tc.table_name = %s
            """, (table,))
            fk_map = {(r[0]): f"{r[1]}.{r[2]}" for r in cur.fetchall()}

            # Format output
            schema_output.append(f"### {table} ({row_count} rows)")
            for col, dtype, nullable in columns:
                line = f"- {col}: {dtype}"
                if col in pk_columns:
                    line += " (PK)"
                if col in fk_map:
                    line += f" (FK → {fk_map[col]})"
                if nullable == "NO":
                    line += ", NOT NULL"
                schema_output.append(line)
            schema_output.append("")  # blank line for spacing

        
        return "\n".join(schema_output)
    
    def get_llm_friendly_schema(self, cur):
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public' AND table_type='BASE TABLE'
        """)
        tables = [r[0] for r in cur.fetchall()]

        schema_output = []

        for table in tables:
            # Get row count
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cur.fetchone()[0]

            # Get columns
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table,))
            columns = cur.fetchall()

            # Get primary keys
            cur.execute("""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
            """, (table,))
            pk_columns = {r[0] for r in cur.fetchall()}

            # Get foreign keys
            cur.execute("""
                SELECT
                    kcu.column_name,
                    ccu.table_name AS foreign_table,
                    ccu.column_name AS foreign_column
                FROM
                    information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE
                    tc.constraint_type = 'FOREIGN KEY' AND
                    tc.table_name = %s
            """, (table,))
            fk_map = {(r[0]): f"{r[1]}.{r[2]}" for r in cur.fetchall()}

            # Format schema info
            schema_output.append(f"### {table} ({row_count} rows)")
            for col, dtype, nullable in columns:
                if dtype in ["character varying", "character", "text"]:
                    readable_type = "text"
                elif dtype in ["integer", "bigint", "smallint", "numeric", "decimal"]:
                    readable_type = "number"
                elif dtype in ["date", "timestamp", "timestamp without time zone"]:
                    readable_type = "date"
                elif dtype == "USER-DEFINED":
                    readable_type = "custom type"
                else:
                    readable_type = dtype

                line = f"- {col}: {readable_type}"
                if col in pk_columns:
                    line += " (Primary Key)"
                if col in fk_map:
                    line += f" (Foreign Key to {fk_map[col]})"
                if nullable == "NO":
                    line += ", required"
                schema_output.append(line)

            # Add sample rows
            cur.execute(f"SELECT * FROM {table} LIMIT 2")
            sample_rows = cur.fetchall()
            # col_names = [col[0] for col in columns]

            schema_output.append("Sample rows:")
            for row in sample_rows:
                row_str = []
                for val in row:
                    if isinstance(val, str):
                        truncated = val[:15] + "..." if len(val) > 15 else val
                    elif isinstance(val, (int, float)):
                        truncated = str(val)
                    elif val is None:
                        truncated = "NULL"
                    else:
                        truncated = str(val)[:10] + "..." if len(str(val)) > 10 else str(val)
                    row_str.append(truncated)
                schema_output.append("  - " + ", ".join(row_str))

            schema_output.append("")  # blank line for spacing

        return "\n".join(schema_output)

    def reset_curr(self):
        self.postgres_cursor.close()
        self.postgres_cursor = self.conn.cursor()


    async def execute_query(self, sql_query="SELECT * FROM employees1 LIMIT 5;"):
        try:
            self.postgres_cursor.execute(sql_query)

            column_names = [desc[0] for desc in self.postgres_cursor.description]
            rows = self.postgres_cursor.fetchall()

            from tabulate import tabulate

            max_display_rows = 15
            total_rows = len(rows)

            # Save full output
            full_output = tabulate(rows, headers=column_names, tablefmt="github")
            with open(self.output_file, "w") as f:
                f.write(full_output)

            # Trimmed output for display
            trimmed_rows = rows[:max_display_rows]
            display_output = tabulate(trimmed_rows, headers=column_names, tablefmt="github").strip()

            if total_rows > max_display_rows:
                display_output += f"\n\nNote: Showing {max_display_rows} of total count: {total_rows} rows.\nComplete output saved to {self.output_file}.\nYou can only use this data to process.You can tell user to view the file if necessary."
            else:
                display_output += f"\n\nComplete output saved to {self.output_file}"
                await cl.Message(display_output, author = "database").send()
            return display_output+"\n\nThe table is visible to user you can just continue the swag summarize if nessary."

        except Exception as e:  
            self.conn.rollback()
            return f"Error type: {type(e).__name__}, Error message: {e}"



    def build_prompt(self, text):
        prompt = self.query_gen_prompt123.format(schema = self.schema, text = text)
        return prompt

    def extract_query(self, text: str) -> str:
        """
        Extracts the last SQL query from a code block.
        Supports blocks ending with ``` or ::: after ```sql.
        Returns the SQL query as a string and a success flag (True/False).
        """
        # First try to match ```sql ... ```
        pattern_backticks = r"```sql\s+(.*?)```"
        matches = re.findall(pattern_backticks, text, re.DOTALL)

        if not matches:
            # If no ``` block, try ```sql ... ::: format
            pattern_colons = r"```sql\s+(.*?):::"
            matches = re.findall(pattern_colons, text, re.DOTALL)

        if not matches:
            return "No SQL block found", False
        
        return matches[-1].strip(), True

    async def gen_query_from_llm(self, prompt):
        output = await AioHTTPSessionManager.non_stream_response(payload={"prompt": prompt})
        return output


    async def pipeline(self, query):
        prompt = self.build_prompt(text = query)
        llm_output, status = await self.gen_query_from_llm(prompt=prompt)
        print(llm_output)
        if status:
            query, status = self.extract_query(text=llm_output)
            print()
            if status:
                output = await self.execute_query(sql_query = query)
                return output
        else:
            return llm_output

    def destroy(self):
        self.postgres_cursor.close()
        self.conn.close()




    query_gen_prompt1 ="""
You are a professional PostgreSQL database expert.

## Task
Given the following database schema and a SQL question, write the most efficient and accurate SQL query using standard PostgreSQL syntax. Add indexes or optimizations if needed. Return only the final query ready to run on the server.

## Schema (table_name (row count))
{schema}

## SQL Question
{query}

## System Message
- Ensure the SQL is compatible with PostgreSQL.
- Suggest an index or optimization if the query is expected to be slow.
- Ensure the result is ready to be copied and executed directly.
- Only return the final query and optional index creation if needed.
"""


    query_gen_prompt2="""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a professional PostgreSQL expert who generates optimized, correct SQL queries from natural language questions based on the schema provided. Always ensure the query is executable on PostgreSQL, with performance hints when needed (like CTEs). Avoid unnecessary explanations and return only final SQL queries unless explicitly asked.
Use explicit JOINs where needed. Prefer CTEs for complex aggregations.  

Schema Format:
- TableName (Row count)
  - column_name: data_type [PK|FK → referenced_table.column], [NOT NULL]

At the end, return only the final query (and optional suggestions if necessary).

<|eot_id|><|start_header_id|>user<|end_header_id|>
## Schema
{schema}

## Query Request
{text}
If the query includes unknown terms or entities not found in the schema, respond with:
```sql
SELECT 'Unable to generate query: entity not found in schema.' AS message;
```
<|eot_id|><|start_header_id|>assistant<|end_header_id|>"""

    query_gen_prompt = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a professional PostgreSQL expert who generates optimized, correct SQL queries from natural language questions based on the schema provided. 
Think step by step to break down the user's request, reason about how to join and filter relevant tables, and form an efficient SQL query. 
Use Common Table Expressions (CTEs) when needed for readability and performance. Always use explicit JOINs.

Schema Format:
- TableName (Row count)
  - column_name: data_type, (Primary Key) (Foreign Key to [referenced_table.column]), [required]

Instructions:
- Think aloud step by step and genertate.
- Explain any assumptions briefly.
- At the end, return the one final SQL query inside a single ```sql code block.
- Do not include markdown outside the code block.
- If the query includes unknown terms or entities not found in the schema, respond only with:

```sql
SELECT 'Unable to generate query: entity not found in schema.' AS message;
```

<|eot_id|><|start_header_id|>user<|end_header_id|>
## Schema
{schema}

## Query Request
{text}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""


    query_gen_prompt = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a professional PostgreSQL expert who generates optimized, correct SQL queries from natural language questions based on the schema provided. 

Think step by step only when the query is complex (e.g., involves joins, aggregation, subqueries, or CTEs). For simple queries, go straight to generating the query efficiently.

Use Common Table Expressions (CTEs) when needed for readability and performance. Always use explicit JOINs.

Schema Format:
- TableName (Row count)
  - column_name: data_type [PK|FK → referenced_table.column], [NOT NULL]

Instructions:
- Analyze the request and schema carefully.
- If any entity or field mentioned in the request is not found in the schema, return a small message to the user about the issue.
- Otherwise, return the final SQL query wrapped in a single SQL code block.
- Do not include any explanation or text after the SQL block. The SQL code block must be the last thing in the output.
- And at the after of the code block return `:::` tag
<|eot_id|><|start_header_id|>user<|end_header_id|>
## Schema
{schema}

## Query Request
{text}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""

    query_gen_prompt = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a professional PostgreSQL expert who generates optimized, correct SQL queries from natural language questions based on the schema provided.

Think step by step only when the query is complex (e.g., involves joins, aggregation, subqueries, or CTEs). For simple queries, go straight to generating the query efficiently.

Use Common Table Expressions (CTEs) when needed for readability and performance. Always use explicit JOINs.

Schema Format:
- TableName (Row count)
  - column_name: data_type [PK|FK → referenced_table.column], [NOT NULL]

Instructions:
- Analyze the request and schema carefully.
- If any entity or field mentioned in the request is not found in the schema, return a small message to the user about the issue.
- Otherwise, return the final SQL query wrapped in a single SQL code block.
- Do not include any explanation or text after the SQL block. The SQL code block must be the last thing in the output.
- After the code block, return the special token `:::`
<|eot_id|><|start_header_id|>user<|end_header_id|> 
"""


    query_gen_prompt123 = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a professional PostgreSQL expert who generates optimized, correct SQL queries from natural language questions based on the schema provided.

Schema Format:
- TableName (Row count)
  - column_name: data_type, (Primary Key) (Foreign Key to [referenced_table.column]), [required]

### Schema
{schema}

Instructions:
- Analyze the request and schema carefully.
- If any entity or field mentioned in the request is not found in the schema, return a small message to the user about the issue.
- Think step by step only when the query is complex in a human language (e.g., involves joins, aggregation, subqueries, or CTEs). For simple queries, go straight to generating the query efficiently.
- Otherwise, return the final SQL query wrapped in a single SQL code block.
- Use Common Table Expressions (CTEs) when needed for readability and performance. Always use explicit JOINs.
- When generating queries, **include additional relevant columns** in the SELECT clause beyond the ones strictly required for the answer. This helps provide richer context in the output, which may assist with further explanation or analysis later.
- After the code block, return the special token `:::`
<|eot_id|><|start_header_id|>user<|end_header_id|>


### Query Request
{text}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""