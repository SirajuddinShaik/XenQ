# python_executor.py for client/src/xenq_client/components/python_executor.py
import os
import mimetypes
from fastapi import  UploadFile, File, HTTPException, APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel

router = APIRouter(
    prefix="/file_service",
    tags=["File Service"]
)
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class CodeSnippet(BaseModel):
    code: str

@router.post("/execute")
async def execute_code(snippet: CodeSnippet):
    try:
        import sys
        import io

        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        exec(snippet.code)

        sys.stdout = old_stdout
        output = redirected_output.getvalue()

        return {"status": "success", "output": output}
    except Exception as e:
        sys.stdout = old_stdout
        return {"status": "error", "message": str(e)}

@router.get("/read_file")
async def read_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete_file")
async def delete_file(file_path: str):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"status": "success", "message": f"File {file_path} deleted successfully."}
        else:
            raise HTTPException(status_code=404, detail=f"File {file_path} does not exist.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download_file")
async def download_file(file_path: str):
    try:
        file_path = os.path.normpath(file_path)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(
            path=file_path,
            media_type=mimetypes.guess_type(file_path)[0] or "application/octet-stream",
            filename=os.path.basename(file_path),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = os.path.join(UPLOAD_FOLDER, str(file.filename))
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {"status": "success", "filename": file.filename, "saved_to": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
