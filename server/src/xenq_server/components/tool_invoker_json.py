import json
import re
import random
from xenq_server.components.web_query import WebQuery
from xenq_server.components.query import QueryManager

class ToolInvoker:
    def __init__(self):
        self.web_query = WebQuery()
        self.query_manager = None
        self.functions  = {
            "search_web": self.search_web,
            "database_query":self.sql_query ,
            "execute_python":self.none,
            "get_weather": self.none,
            "create_file": self.none
        }
    

    def extract_tool_invocation(self, llm_output):
        # Find all <tool>...</tool> blocks (regardless of format inside)
        tool_blocks = re.findall(r"<tool>(.*?)</tool>", llm_output, re.DOTALL)
        result = []

        for i, block in enumerate(tool_blocks):
            block = block.strip()

            # Remove backticks and markdown code fencing if present
            if block.startswith("```json"):
                block = re.sub(r"^```json\s*|\s*```$", "", block, flags=re.DOTALL).strip()
            elif block.startswith("```"):
                block = re.sub(r"^```|\s*```$", "", block, flags=re.DOTALL).strip()

            try:
                data = json.loads(block)
                # Normalize: if it's a single function call, wrap it into function_calls
                if "function_calls" in data:
                    result.extend(data["function_calls"])
                elif "name" in data and "parameters" in data:
                    result.append(data)
                else:
                    print(f"Warning: Unexpected JSON structure in block {i+1}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON block {i+1}: {e}")

        if result:
            print(result)
            return { "function_calls": result }
        else:
            print("No valid tool blocks found.")
            return ""


    async def search_web(self, query: str, top_k = 2, **kwargs):
        output = await self.web_query.search_web(query, top_k)
        return output
    
    async def sql_query(self, text, **kwargs):
        if self.query_manager is None:
            return "No Sql url is provided, Please Provide the uri in settings!"
        output = await self.query_manager.pipeline(query=text)
        return output
    
    def update_sql_uri(self, uri):
        query_manager = QueryManager(uri=uri)
        if query_manager.get_status():
            self.query_manager = query_manager

    async def pipeline(self, internal_text):
        print("text",internal_text)
        try:
            tool_dict = self.extract_tool_invocation(internal_text)  # List of dicts
            print("tool_dicts", tool_dict)
        except Exception as e:
            return {"error": f"Failed to extract tool invocation: {e}"}

        outputs = []
        seen_calls = set()  # To store (func_name, parameters_as_str) tuples for uniqueness

        for function in tool_dict["function_calls"]:
            for function in tool_dict["function_calls"]:
                func_name = function.get("name")
                parameters = function.get("parameters", {})

                # Check for uniqueness
                key = (func_name, json.dumps(parameters, sort_keys=True))
                if key in seen_calls:
                    continue  # Skip duplicates
                seen_calls.add(key)

                if func_name in self.functions:
                    try:
                        result = await self.functions[func_name](**parameters)
                        function["output"] = result
                        outputs.append(result)
                    except Exception as e:
                        outputs.append(f"Function `{func_name}` failed: {e}")
                else:
                    outputs.append(f"Unknown function: {func_name}")
        return self.format_output(outputs)

    def format_output(self, outputs):
        """
        Formats a list of outputs into markdown-style text for LLM input.
        """
        if not outputs:
            return "\n### Output From Backend\n\n- No results found."

        formatted = "\n### Output From Backend\n\n"
        for idx, item in enumerate(outputs, start=1):
            if isinstance(item, dict):
                item_str = ", ".join(f"{k}: {v}" for k, v in item.items())
            else:
                item_str = str(item)
            formatted += f"{idx}. {item_str}\n"

        return formatted

    async def none(self, **kwargs):
        return "Just Testing the llm Asume Something! the function is not Implement yet..."
    
json1={
  "function_calls": [
    {
      "name": "search_web",
      "parameters": {
        "query": "latest news"
      }
    },
    ...
  ]
}