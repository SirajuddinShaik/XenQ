import asyncio
# import inspect
import logging
import os

from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.llm.vllm_implementation import vllm_embed, vllm_model_complete
from lightrag.utils import EmbeddingFunc
import nest_asyncio

nest_asyncio.apply()


WORKING_DIR = "./dickens"

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def initialize_rag():
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


async def print_stream(stream):
    async for chunk in stream:
        print(chunk, end="", flush=True)


def main():
    # Initialize RAG instance
    rag = asyncio.run(initialize_rag())

    # Insert example text
    with open("./book.txt", "r", encoding="utf-8") as f:
        rag.insert(f.read())

    # # Test different query modes
    # print("\nNaive Search:")
    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="naive")
    #     )
    # )

    # print("\nLocal Search:")
    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="local")
    #     )
    # )

    # print("\nGlobal Search:")
    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="global")
    #     )
    # )

    # print("\nHybrid Search:")
    # print(
    #     rag.query(
    #         "What are the top themes in this story?", param=QueryParam(mode="hybrid")
    #     )
    # )

    # # stream response
    # resp = rag.query(
    #     "What are the top themes in this story?",
    #     param=QueryParam(mode="hybrid", stream=True),
    # )

    # if inspect.isasyncgen(resp):
    #     asyncio.run(print_stream(resp))
    # else:
    #     print(resp)


if __name__ == "__main__":
    main()
