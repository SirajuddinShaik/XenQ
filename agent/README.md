# 📄 Agent - XenQ Project

The **Agent** application hosts all the AI models required by XenQ to perform tasks like conversation, summarization, and document retrieval. It is built for fast, efficient, and scalable model serving.

---

## ✨ Models Hosted

- **LLM (Chat Model):**
  - **Model:** Llama 3.1 Instruct 8B (FP8 quantized)
  - **Hosted using:** `vLLM` with `AsyncLLMEngine` for efficient streaming responses.
  - **Note:** Despite being a smaller model (~8B parameters) compared to OpenAI's GPT models (175B parameters), it delivers highly competitive performance for most tasks.

- **Summarization Model:**
  - **Model:** `facebook/bart-large-cnn`
  - **Library:** Hugging Face Transformers
  - **Purpose:** To generate concise and accurate summaries.

- **Embedding Model (for RAG):**
  - **Model:** `sentence-transformers/all-mpnet-base-v2`
  - **Library:** Sentence-Transformers
  - **Purpose:** To create high-quality embeddings for document retrieval.

- **(Upcoming) Audio-to-Text Model:**
  - **Model:** `openai/whisper`
  - **Purpose:** To convert user microphone audio to text for audio-based chatting.
  - **Status:** Planned for future updates.
---

## 🛠️ Tech Stack

- **vLLM** — High-performance inference engine for LLMs.
- **FastAPI** — Async API framework for serving all model endpoints.
- **Python 3.10+**

---

## 🧩 Architecture Overview

- The **Agent** exposes API endpoints for:
  - **/prompt** — For normal chat completions.
  - **/stream** — For streaming responses.
  - **/summarize** — For summarization tasks.
  - **/embed** — For embedding generation.

- The **Server** is the **only component** that communicates with the Agent.  
  No direct access from external Clients for security and simplicity.

---

## 🚀 Running the Agent

### 1. Install Requirements

```bash
pip install -r requirements.txt
````

### 2. Start the Agent Server

```bash
uvicorn main:app
```

---

## 📌 Notes

* The Llama 3.1 model is quantized to **FP8** for optimal memory and performance usage, enabling it to run even on local or Colab GPUs.
* All endpoints are built with **async** programming for maximum throughput.
* The Agent is modular — you can easily swap models in the future if needed.

---

## ✅ Status

* Audio chat support using Whisper(Ongoing).
* Core functionality completed and tested.
* Improved batching and error handling. 
* Future upgrades can include model auto-reloading.

---
