# query_manager.py for agent/src/xenq_agent/components/query/query_manager.py

import psycopg2
class QueryManager:

    def __init__(self, uri, agent_uri = "http://localhost:5005/prompt"):
        try:
            self.agent_uri = agent_uri
            self.conn = psycopg2.connect(uri)
            self.postgres_cursor= self.conn.cursor()
            self.schema = self.get_llm_friendly_schema(self.postgres_cursor)
            self.conn_status = True
        except Exception as e:
            self.conn_status = False

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
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
            """, (table,))
            columns = cur.fetchall()

            # Get primary keys
            cur.execute(f"""
                SELECT kcu.column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                WHERE tc.table_name = %s AND tc.constraint_type = 'PRIMARY KEY'
            """, (table,))
            pk_columns = {r[0] for r in cur.fetchall()}

            # Get foreign keys
            cur.execute(f"""
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

    def execute_query(self, sql_query = "SELECT * FROM employees1 LIMIT 5;"):
        try:
            self.postgres_cursor.execute(sql_query)

            column_names = [desc[0] for desc in self.postgres_cursor.description]
            rows = self.postgres_cursor.fetchall()

            from tabulate import tabulate
            formatted_output = tabulate(rows, headers=column_names, tablefmt="github")
            print(formatted_output.strip())

        except Exception as e:
            print(f"Error type: {type(e).__name__}")
            print(f"Error message: {e}")

    def gen_template(self, text):
        prompt = self.query_gen_prompt.format(schema = self.schema, text = text)
        print(prompt)
        return prompt

    def gen_query(self, prompt):
        pass

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
  - column_name: data_type [PK|FK → referenced_table.column], [NOT NULL]

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