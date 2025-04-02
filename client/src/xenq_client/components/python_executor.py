# python_executor.py for client/src/xenq_client/components/python_executor.py
import sys
import io
import os
import json
import requests

class PythonExecutor:
    def __init__(self):
        pass

    def execute_code(self, code):
        try:
            # Redirect stdout to capture output
            # print(code)
            stdout_buffer = io.StringIO()
            sys.stdout = stdout_buffer
            exec(code, {})
            
            # Restore stdout
            sys.stdout = sys.__stdout__
            
            return {"status": "success", "output": stdout_buffer.getvalue()}
        except Exception as e:
            sys.stdout = sys.__stdout__  # Restore stdout in case of error
            return {"status": "error", "message": str(e)}

    def edit_file(self, file_path, data = ""):
        try:
            with open(file_path, 'w') as file:
                file.write(data)
            return {"status": "success", "message": f"File {file_path} updated successfully."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = file.read()
            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def delete_file(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {"status": "success", "message": f"File {file_path} deleted successfully."}
            else:
                return {"status": "error", "message": f"File {file_path} does not exist."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        
# Example usage
if __name__ == "__main__":
    code_snippet = """print("Hello, World!")
x = 10
y = 20
print("Sum:", x + y)
"""
    
    # Sending the request to the server
    url = "http://127.0.0.1:5000/api/execute"  # Change this URL if needed
    headers = {"Content-Type": "application/json"}
    payload = json.dumps({"code": code_snippet})
    
    response = requests.post(url, data=payload, headers=headers)
    
    print("Server Response:", response.json())