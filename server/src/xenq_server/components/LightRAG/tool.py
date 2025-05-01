import asyncio
import nest_asyncio
from vllm import outputs
from xenq_server.api import AioHTTPSessionManager
import chainlit as cl
import json
nest_asyncio.apply()
import os
import inspect
from lightrag import LightRAG, QueryParam
from lightrag.llm.vllm_implementation import vllm_model_complete, vllm_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status
from xenq_server.config import AGENT_URI





class LightRag:
    def __init__(self):
        self.rag = None  # placeholder

    async def setup(self, WORKING_DIR):
        self.rag = await self.initialize_rag(WORKING_DIR)

    async def initialize_rag(self, WORKING_DIR):
        if not os.path.exists(WORKING_DIR):
            os.mkdir(WORKING_DIR)
        rag = LightRAG(
            working_dir=WORKING_DIR,
            llm_model_func=vllm_model_complete,
            llm_model_name="gemma2:2b",
            llm_model_max_async=4,
            llm_model_max_token_size=8000,
            llm_model_kwargs={
                "host": "http://localhost:11434",
                "options": {"num_ctx": 8000},
            },
            embedding_func=EmbeddingFunc(
                embedding_dim=768,
                max_token_size=8192,
                func=lambda texts: vllm_embed(
                    texts, embed_model="nomic-embed-text", host="http://localhost:11434"
                ),
            ),
        )

        await rag.initialize_storages()
        await initialize_pipeline_status()
        return rag

    async def insert_text(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            await self.rag.insert(f.read())

    async def query(self, question, mode="naive"):
        response = await self.rag.query(question, param=QueryParam(mode=mode))
        return response

    async def pipeline(self,query):
        try:
            context = await self.rag.query(query=query, param=QueryParam(mode="hybrid", only_need_context=True))
            print("prompted (hybrid)")
        except Exception as e:
            print(f"Hybrid mode failed with error: {e}. Trying naive mode...")
            try:
                context = self.rag.query(query=query, param=QueryParam(mode="naive", only_need_context=True))
                print("prompted (naive)")
            except Exception as e2:
                print(f"Naive mode also failed with error: {e2}")
                prompt = "No context found due to error in backend"

        prompt = rag_sys_prompt.format(user_query=query,context_chunks=context)
        # print("Prompt:", prompt)


        session = await AioHTTPSessionManager.get_session()
        headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }
        response=""
        msg = cl.Message(content = "", author="light_rag")
        try:
            async with session.post(f"{AGENT_URI}/stream", headers=headers, json={"prompt": prompt}) as resp:
                async for line in resp.content:
                    decoded = line.decode("utf-8").strip()
                    if decoded.startswith("data:"):
                        try:
                            data = json.loads(decoded[5:])
                            token = data.get("token", "")
                            response += token
                            await msg.stream_token(token)

                        except Exception as e:
                            print("Streaming error:", e)
        except Exception as e:
            print("Request failed:", e)
        await msg.update()
        return {"role": "light_rag", "content": response}

rag_sys_prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a knowledgeable assistant powered by a Graph-based Retrieval-Augmented Generation (RAG) system.  
Your job is to answer the user's question by retrieving and summarizing relevant content from their personal documents and knowledge graph.

Instructions:
- Search through the provided context to extract the most relevant details to answer the user’s query.
- If you find useful information, mention that the answer was **derived from the user’s documents**.
- Clearly explain the answer with context-driven reasoning or summary.
- If the context does not contain any relevant information, respond politely stating that **nothing helpful was found in the user's data**.
- Keep the tone helpful and professional.

You will receive:
- A user query (natural language question).
- Context chunks retrieved from the user's documents or knowledge base.

Always indicate whether your answer was found using the user's documents or if no relevant data was found.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Context:
{context_chunks}

### User Query: {user_query}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""