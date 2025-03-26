import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="[%(asctime)s]: %(message)s:")

project_name = "XenQ"

# List of files to create with their relative paths
list_of_files = [
    # CI/CD & Documentation
    "docs/architecture.md",
    "research/trials.ipynb",
    "schema.yaml",
    "params.yaml",
    "setup.py",
    "README.md",
    # ---------------- Client Application ----------------
    # Client Source Files
    "client/src/xenq_client/__init__.py",
    "client/src/xenq_client/api/client_api.py",
    "client/src/xenq_client/components/file_manager.py",
    "client/src/xenq_client/components/ui_manager.py",
    "client/src/xenq_client/config/__init__.py",
    "client/src/xenq_client/utils/__init__.py",
    "client/src/xenq_client/main.py",
    # Client Templates & Tests
    "client/templates/index.html",
    "client/tests/test_client.py",
    # Client dependencies and Dockerfile
    "client/requirements.txt",
    "client/Dockerfile",
    "client/setup.py",
    # ---------------- Server Application ----------------
    # Server Source Files
    "server/src/xenq_server/__init__.py",
    "server/src/xenq_server/api/server_api.py",
    # LLM Components
    "server/src/xenq_server/components/llm/__init__.py",
    "server/src/xenq_server/components/llm/llama_inference.py",
    "server/src/xenq_server/components/llm/model_loader.py",
    # Retrieval Components
    "server/src/xenq_server/components/retrieval/__init__.py",
    # Query Management Components
    "server/src/xenq_server/components/query/__init__.py",
    "server/src/xenq_server/components/query/query_manager.py",
    "server/src/xenq_server/components/query/history_store.py",
    # Server Configuration & Utilities
    "server/src/xenq_server/config/settings.py",
    "server/src/xenq_server/config/__init__.py",
    "server/src/xenq_server/utils/__init__.py",
    "server/src/xenq_server/main.py",
    # Server Config, Tests and Docker
    "server/config/config.yaml",
    "server/tests/test_server.py",
    "server/requirements.txt",
    "server/Dockerfile",
    "server/setup.py",
]


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
    # ---------------- Client Application ----------------
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
    "client/src/xenq_client/main.py",
    # Client Templates & Tests
    "client/templates/index.html",
    "client/tests/__init__.py",
    "client/tests/test_client.py",
    # Client dependencies and Dockerfile
    "client/requirements.txt",
    "client/Dockerfile",
    "client/setup.py",
    # ---------------- Server Application ----------------
    "server/src/xenq_server/__init__.py",
    "server/src/xenq_server/api/__init__.py",
    "server/src/xenq_server/api/server_api.py",
    # LLM Components
    "server/src/xenq_server/components/__init__.py",
    "server/src/xenq_server/components/llm/__init__.py",
    "server/src/xenq_server/components/llm/llama_inference.py",
    "server/src/xenq_server/components/llm/model_loader.py",
    # Retrieval Components
    "server/src/xenq_server/components/retrieval/__init__.py",
    "server/src/xenq_server/components/retrieval/context_manager.py",
    "server/src/xenq_server/components/retrieval/vector_store.py",
    # Query Management Components
    "server/src/xenq_server/components/query/__init__.py",
    "server/src/xenq_server/components/query/query_manager.py",
    "server/src/xenq_server/components/query/history_store.py",
    # Server Configuration & Utilities
    "server/src/xenq_server/config/__init__.py",
    "server/src/xenq_server/config/settings.py",
    "server/src/xenq_server/utils/__init__.py",
    "server/src/xenq_server/utils/logger.py",
    "server/src/xenq_server/main.py",
    # Server Config, Tests, and Docker
    "server/config/config.yaml",
    "server/tests/__init__.py",
    "server/tests/test_server.py",
    "server/requirements.txt",
    "server/Dockerfile",
    "server/setup.py",
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
