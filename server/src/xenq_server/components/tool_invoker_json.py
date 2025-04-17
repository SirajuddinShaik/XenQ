import json
import re
import random
from xenq_server.components.web_query import WebQuery

class ToolInvoker:
    def __init__(self):
        self.web_query = WebQuery()
        self.functions  = {
            "search_web": self.search_web,
            "sql_query":self.none ,
            "execute_python":self.none,
            "get_weather": self.none,
            "create_file": self.none
        }
    

    def extract_tool_invocation(self, llm_output):
        # Match all JSON blocks inside ```json ... ```
        json_blocks = re.findall(r"```json\s*(\{.*?\})\s*```", llm_output, re.DOTALL)

        result = []
        for i, block in enumerate(json_blocks):
            try:
                parsed = json.loads(block)
                result.append(parsed)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON block {i+1}: {e}")
        
        if not result:
            print("No valid JSON blocks found.")
        
        return result

    async def search_web(self, query: str, top_k = 2, **kwargs):
        output = await self.web_query.search_web(query, top_k)
        return output

    async def pipeline(self, internal_text):
        try:
            tool_dicts = self.extract_tool_invocation(internal_text)  # List of dicts
        except Exception as e:
            return {"error": f"Failed to extract tool invocation: {e}"}

        outputs = []
        seen_calls = set()  # To store (func_name, parameters_as_str) tuples for uniqueness

        for tool_dict in tool_dicts:
            if "function_calls" in tool_dict:
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
        # print(outputs)
        return self.format_output(outputs)

    def format_output(self, outputs):
        """
        Formats a list of outputs into markdown-style text for LLM input.
        """
        if not outputs:
            return "\n### Output From Backend\n\n1. No results found."

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