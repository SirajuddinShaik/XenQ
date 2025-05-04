import json
import re
import chainlit as cl
from xenq_server.components import QueryManager, WebQuery, LightRag, ClientConnect

class ToolInvoker:
    client_params={
        "create_file":{"method": "post", "main": "file_service", "sub": "create_file"},
        "write_file":{"method": "post", "main": "file_service", "sub": "write_file"},
        "delete_file":{"method": "post", "main": "file_service", "sub": "delete_file"},
        "kill_process":{"method": "post", "main": "system_manager", "sub": "kill_process"},
        "get_config":{"method": "get", "main": "system_manager", "sub": "get_config"},
        "list_process":{"method": "get", "main": "system_manager", "sub": "list_process"},
        "run_command":{"method": "post", "main": "system_manager", "sub": "run_command"},
    }
    def __init__(self):
        self.web_query = WebQuery()
        self.query_manager = None
        self.functions  = {
            "search_web": self.search_web,
            "database_query":self.sql_query ,
            "execute_python":self.none,
            "knowledge_query": self.knowledge_query,
            "remote_controller": self.remote_controller,
        }
        self.light_rag = LightRag()
        self.client_manager = None
    
    async def setup(self, WORKING_DIR = "./dickens"):
        await self.light_rag.setup(WORKING_DIR)

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
            return { "function_calls": result }
        else:
            print("No valid tool blocks found.")
            return ""


    async def search_web(self, query: str, top_k = 2, **kwargs):
        output = await self.web_query.search_web(query, top_k)
        return output
    
    async def sql_query(self, text, **kwargs):
        if self.query_manager is None:
            msg = "Database not connected. Connect to continue."
            await cl.Message(msg).send()
            return {"role": "client", "content": msg}
        output = await self.query_manager.pipeline(query=text)
        return output
    
    async def update_sql_uri(self, uri):
        self.query_manager = None
        if uri is None:
            self.query_manager = None
            return
        query_manager = QueryManager(uri=uri)
        if query_manager.get_status():
            self.query_manager = query_manager
            cl.user_session.set("psql_uri", uri)
            await cl.Message("Database is Connected!").send()
        else:
            await cl.Message("Database Url is Incorrect!").send()

    async def update_client_uri(self, uri):
        self.client_manager = None
        if uri is None:
            self.client_manager = None
            return
        client_manager = ClientConnect(uri)
        if await client_manager.verify():
            self.client_manager = client_manager
            cl.user_session.set("client_uri", uri)
            await cl.Message("Client Machine Connected!").send()
        else:
            await cl.Message("Client Url is Incorrect!").send()

    async def knowledge_query(self,query):
        if self.light_rag is None:
            return "No File Found"
        output = await self.light_rag.pipeline(query=query)
        return output

    async def pipeline(self, internal_text):
        try:
            tool_dict = self.extract_tool_invocation(internal_text)  # List of dicts
            print("tool_dicts", tool_dict)
        except Exception as e:
            return {"error": f"Failed to extract tool invocation: {e}"}

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
                    except Exception as e:
                        function["output"] = f"Function `{func_name}` failed: {e}"
                else:
                    function["output"] = f"Unknown function: {func_name}"
        return self.format_output(tool_dict["function_calls"])

    def format_output(self, outputs):
        """
        Formats a list of outputs into markdown-style text for LLM input.
        """
        if not outputs:
            return "\n### Output From Backend\n\n- No results found."

        formatted = "\n### Output From Backend\n\n"
        responses = []
        for idx, item in enumerate(outputs, start=1):
            if item.get("name") in ["knowledge_query", "search_web", "remote_controller"]:
                responses.append(item.get("output"))
            elif isinstance(item["output"], dict):
                item_str = ", ".join(f"{k}: {v}" for k, v in item["output"].items())
                formatted += f"{idx}. {item_str}\n"
            else:
                item_str = str(item["output"])
                formatted += f"{idx}. {item_str}\n"

        return formatted if len(responses)!=len(outputs) else "", responses

    async def none(self, **kwargs):
        return "Just Testing the llm Asume Something! the function is not Implement yet..."
    
    async def run_cmd(self, command: str):
        if self.client_manager:
            try:
                if command.startswith(">"):
                    cmd = command[1:].split()
                    params = {}
                    for param in cmd[1:]:
                        key, val = param.split("=")
                        params[key]=val
                    cmd = cmd[0]
                    if cmd=="kill":
                        res = await self.client_manager.non_stream_response("post", "system_manager", "kill_process",**params)
                        await cl.Message(res.get("message","Unknown Error!")).send()
                    elif cmd == "create_file":
                        res = await self.client_manager.non_stream_response("post", "file_service", "create_file",**params)
                        await cl.Message(res.get("message", "Unknown Error!")).send()
                    elif cmd == "del_file":
                        res = await self.client_manager.non_stream_response("post", "file_service", "delete_file",**params)
                        await cl.Message(res.get("message", "Unknown Error!")).send()
                    elif cmd == "config":
                        res = await self.client_manager.non_stream_response("get", "system_manager", "get_config",**params)
                        await cl.Message(res.get("response", "Unknown Error!")).send()
                    elif cmd == "list_process":
                        res = await self.client_manager.non_stream_response("get", "system_manager", "list_process",**params)
                        await cl.Message(res.get("response", "Unknown Error!")).send()
                    else:
                        await cl.Message("Invalid Command!").send()
                else:
                    await self.client_manager.run_cmd(command=command)
            except Exception as e:
                await cl.Message(f"Invalid Command: {e}").send()
        else:
            await cl.Message("Client Machine not connected. Connect to continue.").send()

    async def remote_controller(self, action, **kwargs):
        if self.client_manager is None:
            msg = "Client machine not connected. Connect to continue."
            await cl.Message(msg).send()
            return {"role": "client", "content": msg}
        try:
            params  = self.client_params[action]
            method = params["method"]
            main = params["main"]
            sub = params["sub"]
            
            result = await self.client_manager.non_stream_response(method, main, sub, **kwargs)
            result["role"] = "client"
            result["content"] = result.get("response")
            if action in ["get_config", "list_process"]:
                await cl.Message(result.get("response","")).send()
            return result
        except Exception as e:
            return f"Error {e}"