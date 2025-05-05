# 🤖 XenQ - Agentic AI System

![FastAPI](https://img.shields.io/badge/FastAPI-0078FF?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white)
![vLLM](https://img.shields.io/badge/vLLM-v0.1.0-orange?style=for-the-badge)

**XenQ** is an agentic AI platform designed to blend natural conversation, document search (RAG), database querying, web search, and full client machine control — all powered through a modular and scalable architecture.

---

# ✨ System Overview

XenQ is composed of **three core applications**:

| Application | Purpose |
|:------------|:--------|
| **Agent**   | Hosts all AI models (LLM, Summarizer, Embedding Model, Whisper for future audio support). |
| **Server**  | Manages user requests, integrates all five modules (conversation, web, database, RAG, client control). |
| **Client**  | Lightweight agent installed on a remote machine for executing system commands securely over the internet. |

---

# 🧠 XenQ Agent

The **Agent** focuses purely on hosting and serving AI models efficiently.

## 🛠️ Components

- **LLM (Chat Model):**
  - **Model:** Llama 3.1 Instruct 8B (FP8 quantized)
  - **Library:** `vLLM` with `AsyncLLMEngine` for streaming responses
  - **Note:**  
    > Achieves strong results compared to much larger OpenAI models — highly efficient at only ~8 billion parameters!

- **Summarizer:**
  - **Model:** `facebook/bart-large-cnn`
  - **Library:** Hugging Face Transformers
  - **Purpose:** Summarizes large documents for quick insights.

- **Embedding Model (for RAG):**
  - **Model:** `sentence-transformers/all-mpnet-base-v2`
  - **Library:** Sentence-Transformers
  - **Purpose:** Generates high-quality embeddings for document retrieval.

- **Future Support:**
  - **Whisper Model** integration for audio chat — allowing voice-to-text input processing.

## 🖥️ Hosted With
- **FastAPI** for high-speed async programming.
- Only the Server communicates with the Agent directly.

---

# 🖧 XenQ Server

The **Server** is the central brain of XenQ — orchestrating all requests and routing tasks to appropriate modules.

## 🛠️ Main Responsibilities

- **General Conversation Handling** via LLM.
- **Web Querying** (search and retrieval from the internet).
- **Database Querying** (convert natural language to SQL and fetch results).
- **Lightweight RAG** (Retrieve documents from user-provided data).
- **Remote Client Control** (launch apps, kill processes, manage files).

## ⚙️ Tech Stack
- Built on **FastAPI** for asynchronous request handling.
- Communicates with both the **Agent** and **Client**.
- Future support for multiple databases and external plugins planned!

---

# 🖥️ XenQ Client

The **Client** enables full remote machine control through FastAPI and Ngrok tunneling.

## ✨ Features

- **📁 File Operations**
  - Create, write, and delete files inside `xenq_shared_folder/`.

- **⚙️ System Operations**
  - View system info, list processes, kill processes.
  - Run terminal/bash commands.
  - Execute Python scripts remotely.

- **🖥️ Application Control**
  - Open/kill applications by name.

- **🌐 Internet Exposure**
  - Uses **Ngrok** to expose the local server to the internet securely.

## 📂 Folder Structure

```plaintext
xenq_shared_folder/
    └── [All remote file operations happen here]
````

---

# 🛤️ Future Updates

* **🛢️ Multi-Database Query Support:**

  * Query different databases (PostgreSQL, MySQL, MongoDB) dynamically.
  * Example commands:

    * "Fetch the latest 5 entries from the sales database."
    * "Show me pending tasks from the HR database."

* **🔐 Enhanced Security:**

  * Add API keys and authentication for secured access.

* **🧩 Modular Plugin System:**

  * Add third-party plugins (calculator, weather info, file search, etc.).

* **🎙️ Audio Chat Support:**

  * Whisper-based mic input for voice interactions.

---

# 🚀 Quick Start

1. **Setup Agent**

   ```bash
   cd xenq/agent
   pip install -r requirements.txt
   uvicorn main:app
   ```

2. **Setup Server**

   ```bash
   cd xenq/server
   pip install -r requirements.txt
   chainlit run main.py -w
   ```

3. **Setup Client**

   ```bash
   cd xenq/client
   pip install -r requirements.txt
   uvicorn main:app
   ```

4. **Update Ngrok Settings for Client Remote Control**

---

# 📞 Contact

* **Developer:** Shaik Sirajuddin
* **Email:** [shaiksirajuddin012@gmail.com](mailto:shaiksirajuddin012@gmail.com)

---
