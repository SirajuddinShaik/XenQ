# main.py for client/main.py
# client_api.py for client/src/xenq_client/api/client_api.py
from fastapi import FastAPI
from xenq_client.components import system_manager_router, file_service_router

app = FastAPI()
SECRET_CODE = "your_secret_code_here"

@app.get("/api/verify")
async def verify_client():
    return {"code": SECRET_CODE}
# Attach router
app.include_router(system_manager_router)
app.include_router(file_service_router)