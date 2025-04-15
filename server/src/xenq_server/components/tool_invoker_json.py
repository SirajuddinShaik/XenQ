import json
import re
import random
from xenq_server.components.web_query import WebQuery

class ToolInvoker:

    functions = ["search_web", "sql_query", "execute_python"]
    def __init__(self):
        self.web_query = WebQuery()
        pass

    def extract_tool_invocation(self, llm_output):
        json_block = re.search(r'\{.*\}', llm_output, re.DOTALL)  # Regex to match JSON block
        if json_block:
            json_str = json_block.group(0)  # Extracted JSON string

            # Step 2: Convert the JSON string to a Python dictionary
            try:
                data_dict = json.loads(json_str)
                print(data_dict)  # This is now a Python dictionary
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
        else:
            print("No JSON block found.")

    async def search_web(self, query: str, top_k = 2):
        output = await self.web_query.search_web(query, top_k)
        for data in output:
            processed = [chunk for chunk in data["processed"] if query not in chunk]
            total = len(processed)
            if total <= 10:
                data["processed"] = processed  # Keep all if 10 or fewer
            else:
                indices = sorted(random.sample(range(total), 10))  # Unique, sorted indices
                data["processed"] = [processed[i] for i in indices]
        return output