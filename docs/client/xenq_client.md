# Flask API Documentation for XenQ Client

## Overview
The `main.py` module serves as the entry point for the Flask-based API of the XenQ client. This API provides endpoints for executing Python code, managing files, and interacting with the system through the `PythonExecutor` component.

## Dependencies
Ensure that the following dependencies are installed:

- Flask
- `xenq_client.components.python_executor.PythonExecutor`

## Running the API
To start the Flask application, execute:
```bash
python main.py
```
The API runs in debug mode by default.

## Endpoints

### 1. Home Endpoint
**URL:** `/`
**Method:** `GET`
**Description:** Returns a welcome message.

#### Response:
```json
{"message": "Welcome to the Simple Flask App!"}
```

---

### 2. Get Data
**URL:** `/api/data`
**Method:** `GET`
**Description:** Returns a simple JSON response.

#### Response:
```json
{"message": "Hello from Flask API!", "status": "success"}
```

---

### 3. Execute Python Code
**URL:** `/api/execute_code`
**Method:** `POST`
**Description:** Executes Python code received from the client and returns the output.

#### Request Body:
```json
{"code": "print('Hello World')"}
```
#### Response:
```json
{"output": "Hello World\n", "status": "success"}
```

---

### 4. Edit File
**URL:** `/api/edit_file`
**Method:** `POST`
**Description:** Modifies the content of a file.

#### Request Body:
```json
{"file_path": "test.py", "content": "print('Modified content')"}
```
#### Response:
```json
{"status": "success", "message": "File updated successfully"}
```

---

### 5. Read File
**URL:** `/api/read_file`
**Method:** `POST`
**Description:** Reads the content of a specified file.

#### Request Body:
```json
{"file_path": "test.py"}
```
#### Response:
```json
{"status": "success", "content": "print('Modified content')"}
```

---

### 6. Delete File
**URL:** `/api/delete_file`
**Method:** `POST`
**Description:** Deletes a specified file.

#### Request Body:
```json
{"file_path": "test.py"}
```
#### Response:
```json
{"status": "success", "message": "File deleted successfully"}
```

---

### 7. Upload File
**URL:** `/api/upload_file`
**Method:** `POST`
**Description:** Uploads a file to the server.

#### Request Body:
```json
{"file_path": "test.py"}
```
#### Response:
```json
{"status": "success", "message": "File uploaded successfully"}
```

## Error Handling
If an error occurs, the API returns a JSON response with status `error` and an error message.

#### Example Error Response:
```json
{"status": "error", "message": "File not found"}
```

## Notes
- Ensure that `PythonExecutor` is properly implemented for handling file operations and code execution.
- Security checks should be in place to prevent arbitrary code execution risks.

---

**Author:** Sirajuddin Shaik  
**Project:** XenQ  
**Email:** shaiksirajuddin9949@gmail.com