# main.py for client/main.py
from flask import Flask, jsonify, request

from xenq_client.components.python_executor import PythonExecutor
py_executor = PythonExecutor()

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Simple Flask App!"

@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from Flask API!", "status": "success"})


@app.route('/api/execute_code', methods=['POST'])
def execute_command():
    code = request.json.get('code')
    # code = request.data.decode("utf-8")
    print(code)
    try:
        result = py_executor.execute_code(code)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/edit_file', methods=['POST'])
def edit_file():
    file_path = request.json.get('file_path')
    content = request.json.get('content')
    try:
        result = py_executor.edit_file(file_path, content)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/read_file', methods=['POST'])
def read_file():
    file_path = request.json.get('file_path')
    try:
        result = py_executor.read_file(file_path)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/delete_file', methods=['POST'])
def delete_file():
    file_path = request.json.get('file_path')
    try:
        result = py_executor.delete_file(file_path)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
