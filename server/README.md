# XenQ Server

The **XenQ Server** is the core component that processes all user requests and enables multiple AI capabilities through a seamless **Chainlit-based chat interface**.  
It acts as the central orchestrator between the **Agent** (LLM hosting), the **Client** (device control), and the user.

---

## ✨ Key Features

- **General Conversation** — Chat naturally with the AI.
- **Web Query** — Retrieve real-time information from the internet.
- **Database Query** — Query structured databases dynamically.
- **Light RAG** — Search and answer questions from your personal documents.
- **Client Control** — Open apps, run commands, and manage your machine via chat.

---

## 🏗️ Architecture Overview

- The **Server** communicates only with the **Agent** for LLM responses.
- It exposes a **Chainlit UI** for users to interact easily.
- All operations are handled asynchronously using **FastAPI**.
- Web search uses **DuckDuckGo** for free querying.
- Database operations are auto-generated and executed in the backend.
- Light RAG is customized to support **vLLM streaming**, making document retrieval lightning fast and smooth.

---

## 🔥 Components Details

### 1. General Conversation
- Enables natural language conversation with the hosted AI agent.
- Fully asynchronous interaction over FastAPI.

---

### 2. Web Query
- Uses **DuckDuckGo Search API** (no API key needed).
- Fetches top results and integrates into AI responses.

---

### 3. Database Query
- Dynamically generates and executes SQL queries based on user input.
- Returns query results as part of the chat conversation.
- Currently uses **psycopg2** for PostgreSQL database connectivity.
- **Note:** The remote URL of the database must be set in the Chainlit settings.  
  Example format: `postgresql://admin:admin123@localhost:5432/college`

---

### 4. Light RAG (Light Retrieval-Augmented Generation)
- Based on research from [LightRAG GitHub Repository](https://github.com/HKUDS/LightRAG) (October 2024).
- Adapted and extended for compatibility with **vLLM streaming outputs**.
- Allows efficient querying over **personal user documents** within chat.

> 📌 **Reference:**  
> ```markdown
> GitHub Repository: [https://github.com/HKUDS/LightRAG](https://github.com/HKUDS/LightRAG)
> ```

---

### 5. Client Control
- Sends remote commands to the Client machine:
  - Open installed applications
  - Run terminal/bash commands
  - Create or modify files
  - Kill running processes
- Useful for automating local system tasks directly from chat.

---


## 🚀 How to Run

1. **Go to the Server Directory**

   ```bash
   cd xenq/server
   ```

2. **Install Python Requirements**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**

   ```bash
   chainlit run main.py -w
   ```

   > `-w` enables **hot reloading** during development (auto-reload on code changes).

4. **Open Chainlit UI**

   * Visit: [http://localhost:8000](http://localhost:8000)

---

## 📌 Notes

* **Chainlit** provides the chat frontend.
* **LightRAG + vLLM streaming** integration was a technically challenging task.
* **Asynchronous programming** ensures high concurrency and fast responses.
* Server does not directly host LLMs — all model inference is handled by the **Agent**.
* Future improvements can include more modular services and advanced control features.

---

## 🔮 Future Updates

- **🛢️ Multi-Database Support:**  
  Enable querying across multiple databases (PostgreSQL, MySQL, MongoDB) based on user context.

- **🔐 Enhanced Security:**  
  Implement API key and Auth systems to secure agent access and control who can send prompts.

- **🧩 Modular Plugin System:**  
  Add support for plugins (like Calculator, Weather, File Search) to extend XenQ's capabilities easily.


---

# 🚀 About XenQ

**XenQ** is an agentic AI system designed to combine general conversation, database reasoning, personal document search (RAG), internet knowledge, and device control — in a seamless and extensible way.

---
