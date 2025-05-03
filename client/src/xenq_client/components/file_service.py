import os
from fastapi import UploadFile, File, APIRouter, Request

router = APIRouter(
    prefix="/file_service",
    tags=["File Service"]
)

SHARED_FOLDER = "../xenq_shared_folder"
os.makedirs(SHARED_FOLDER, exist_ok=True)

def secure_path(file_name: str) -> str:
    """Prevent path traversal, always save inside SHARED_FOLDER."""
    file_name = os.path.basename(file_name)
    return os.path.join(SHARED_FOLDER, file_name)

@router.post("/execute")
async def execute_code(request: Request):
    try:
        body = await request.json()
        code = body.get("code", "")
        
        import sys
        import io

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        exec(code)

        sys.stdout = old_stdout
        output = redirected_output.getvalue()

        return {"status": True, "output": output}
    except Exception as e:
        sys.stdout = old_stdout
        return {"status": False, "response": str(e)}

@router.post("/create_file")
async def create_file(request: Request):
    try:
        body = await request.json()
        file_name = body.get("file_name")
        content = body.get("content", "")

        if not file_name:
            return {"status": False, "response": "file_name is required."}

        file_path = secure_path(file_name)

        if os.path.exists(file_path):
            return {"status": False, "response": f"File '{file_name}' already exists."}

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"status": True, "response": f"File '{file_name}' created successfully."}
    except Exception as e:
        return {"status": False, "response": str(e)}

@router.post("/write_file")
async def write_file(request: Request):
    try:
        body = await request.json()
        file_name = body.get("file_name")
        content = body.get("content", "")
        mode = body.get("mode", "overwrite")  # default is overwrite, can be "append"

        if not file_name:
            return {"status": False, "response": "file_name is required."}

        file_path = secure_path(file_name)

        if not os.path.exists(file_path):
            return {"status": False, "response": f"File '{file_name}' does not exist."}

        if mode == "append":
            file_mode = "a"  # append mode
        else:
            file_mode = "w"  # overwrite mode

        with open(file_path, file_mode, encoding="utf-8") as f:
            f.write(content)

        action = "appended to" if mode == "append" else "overwritten"
        return {"status": True, "response": f"Content successfully {action} '{file_name}'."}

    except Exception as e:
        return {"status": False, "response": str(e)}
        
@router.post("/read_file")
async def read_file(request: Request):
    try:
        body = await request.json()
        file_name = body.get("file_name")
        
        if not file_name:
            return {"status": False, "response": "file_name is required."}

        file_path = secure_path(file_name)

        if not os.path.exists(file_path):
            return {"status": False, "response": f"File '{file_name}' not found."}

        with open(file_path, 'r', encoding="utf-8") as file:
            data = file.read()
        return {"status": True, "data": data}
    except Exception as e:
        return {"status": False, "response": str(e)}

@router.post("/delete_file")
async def delete_file(request: Request):
    try:
        body = await request.json()
        file_name = body.get("file_name")

        if not file_name:
            return {"status": False, "response": "file_name is required."}

        file_path = secure_path(file_name)

        if os.path.exists(file_path):
            os.remove(file_path)
            return {"status": True, "response": f"File '{file_name}' deleted successfully."}
        else:
            return {"status": False, "response": f"File '{file_name}' does not exist."}
    except Exception as e:
        return {"status": False, "response": str(e)}

@router.post("/download_file")
async def download_file(request: Request):
    try:
        body = await request.json()
        file_name = body.get("file_name")

        if not file_name:
            return {"status": False, "response": "file_name is required."}

        file_path = secure_path(file_name)

        if not os.path.exists(file_path):
            return {"status": False, "response": "File not found."}

        with open(file_path, "rb") as f:
            content = f.read()

        return {
            "status": True,
            "file_name": file_name,
            "content": content.decode('latin1')
        }

    except Exception as e:
        return {"status": False, "response": str(e)}

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = secure_path(file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        return {"status": True, "filename": file.filename, "saved_to": file_path}
    except Exception as e:
        return {"status": False, "response": str(e)}
