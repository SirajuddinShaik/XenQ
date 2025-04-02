import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s]: %(message)s:")

project_name = "XenQ"

# List of files to create with their relative paths
list_of_files = [
    # CI/CD & Documentation
    ".github/workflows/ci.yml",
    "docs/architecture.md",
    "research/trials.ipynb",
    "schema.yaml",
    "params.yaml",
    "setup.py",
    "README.md",
    
    # ---------------- CLIENT Application ----------------
    "client/src/xenq_client/__init__.py",
    "client/src/xenq_client/api/__init__.py",
    "client/src/xenq_client/api/client_api.py",
    "client/src/xenq_client/components/__init__.py",
    "client/src/xenq_client/components/file_manager.py",
    "client/src/xenq_client/components/ui_manager.py",
    "client/src/xenq_client/config/__init__.py",
    "client/src/xenq_client/config/settings.py",
    "client/src/xenq_client/utils/__init__.py",
    "client/src/xenq_client/utils/helpers.py",
    "client/main.py",
    "client/templates/index.html",
    "client/tests/__init__.py",
    "client/tests/test_client.py",
    "client/requirements.txt",
    "client/Dockerfile",
    "client/setup.py",

    # ---------------- SERVER Application ----------------
    "server/src/xenq_server/__init__.py",
    "server/src/xenq_server/api/__init__.py",
    "server/src/xenq_server/api/server_api.py",
    "server/src/xenq_server/components/__init__.py",
    "server/src/xenq_server/components/authentication.py",
    "server/src/xenq_server/components/user_management.py",
    "server/src/xenq_server/config/__init__.py",
    "server/src/xenq_server/config/settings.py",
    "server/src/xenq_server/utils/__init__.py",
    "server/src/xenq_server/utils/logger.py",
    "server/main.py",
    "server/config/config.yaml",
    "server/tests/__init__.py",
    "server/tests/test_server.py",
    "server/requirements.txt",
    "server/Dockerfile",
    "server/setup.py",

    # ---------------- AGENT Application (Middleware Layer) ----------------
    "agent/src/xenq_agent/__init__.py",
    "agent/src/xenq_agent/api/__init__.py",
    "agent/src/xenq_agent/api/agent_api.py",
    "agent/src/xenq_agent/components/__init__.py",
    
    # LLM (Language Model) Handling
    "agent/src/xenq_agent/components/llm/__init__.py",
    "agent/src/xenq_agent/components/llm/llama_inference.py",
    "agent/src/xenq_agent/components/llm/model_loader.py",

    # Retrieval Augmented Generation (RAG) Components
    "agent/src/xenq_agent/components/retrieval/__init__.py",
    "agent/src/xenq_agent/components/retrieval/context_manager.py",
    "agent/src/xenq_agent/components/retrieval/vector_store.py",
    
    # Query Processing
    "agent/src/xenq_agent/components/query/__init__.py",
    "agent/src/xenq_agent/components/query/query_manager.py",
    "agent/src/xenq_agent/components/query/history_store.py",

    # Code Execution Engine (for running Python code remotely)
    "agent/src/xenq_agent/components/code_execution/__init__.py",
    "agent/src/xenq_agent/components/code_execution/python_executor.py",
    
    # Internet Query Processing (Web Search, API Calls)
    "agent/src/xenq_agent/components/web_query/__init__.py",
    "agent/src/xenq_agent/components/web_query/search_engine.py",

    # Agent Configuration & Utilities
    "agent/src/xenq_agent/config/__init__.py",
    "agent/src/xenq_agent/config/settings.py",
    "agent/src/xenq_agent/utils/__init__.py",
    "agent/src/xenq_agent/utils/logger.py",
    "agent/main.py",

    # Agent Tests and Dependencies
    "agent/tests/__init__.py",
    "agent/tests/test_agent.py",
    "agent/requirements.txt",
    "agent/Dockerfile",
    "agent/setup.py",
]

# Create each directory and file if they do not exist
for file_path in list_of_files:
    path = Path(file_path)
    directory = path.parent

    if directory and not directory.exists():
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Created directory: {directory}")

    # Create the file if it doesn't exist or is empty
    if not path.exists() or os.path.getsize(path) == 0:
        with open(path, "w") as file:
            # Optionally, write a simple header to each file to indicate its purpose
            file.write(f"# {path.name} for {file_path}\n")
        logging.info(f"Created file: {path}")
    else:
        logging.info(f"File already exists: {path}")
