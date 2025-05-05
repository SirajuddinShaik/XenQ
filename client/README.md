# 🖥️ XenQ Client

The **XenQ Client** is a lightweight **FastAPI server** that listens for remote commands from the XenQ Server.  
It enables full remote control of a machine over the internet — including file operations, system management, and application handling.

---

## ✨ Key Features

- **📁 File Operations**
  - Create, write, and delete files.
  - Operations are restricted to a safe shared folder: **`xenq_shared_folder/`**.

- **⚙️ System Operations**
  - Get system configurations (CPU, RAM, OS).
  - List running user processes.
  - Kill processes by PID.
  - Execute terminal/bash commands.
  - Run Python scripts remotely.

- **🖥️ Application Control**
  - Open installed applications (e.g., Chrome, VS Code).
  - Kill or start applications by name.

- **🌐 Remote Access**
  - Exposes the local FastAPI server to the internet via **Ngrok**.
  - XenQ Server communicates through the generated public URL.

---

## 🚀 How to Run the Client

1. **Navigate to the Client Directory**

   ```bash
   cd xenq/client
````

2. **Install Python Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the FastAPI Server with Ngrok**

   ```bash
   uvicorn main:app
   ```

   This will:

   * Start a local FastAPI server.
   * Create an Ngrok tunnel automatically.
   * Display the public URL in the terminal.

4. **Update XenQ Server Settings**

   * Copy the generated Ngrok URL.
   * Set it in Chainlit or the XenQ Server configuration for remote connection.

---

## 🔑 Setting Up Ngrok

1. [Sign up for Ngrok](https://ngrok.com/signup) (Free account).
2. Retrieve your **Ngrok Auth Token**.
3. Set it locally:

   ```bash
   ngrok config add-authtoken <YOUR_AUTH_TOKEN>
   ```

*(This is also handled programmatically inside XenQ.)*

---

## 📂 Folder Structure

```plaintext
xenq_shared_folder/
    └── [All remote file operations happen here]
```

* No system files outside this folder are touched.
* Ensures safer file operations and easier management.

---

## 📌 Important Notes

* Ensure the client machine remains **online** for uninterrupted remote control.
* Ngrok free accounts rotate URLs approximately every 8 hours (consider upgrading for static URLs).
* Be cautious with remote command execution — proper security measures are essential.

---

# 🚀 About XenQ

**XenQ** is an agentic AI platform built for:

* Advanced natural conversations
* Internet search queries
* SQL/Database interactions
* Document RAG (Retrieval-Augmented Generation)
* Full remote machine control — all via a powerful, simple interface.

---
