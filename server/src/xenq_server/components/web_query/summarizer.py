import asyncio
import aiohttp
import json
import random


FLASK_BACKEND_URL = "http://localhost:5005"


# summarizer.py
import json
from xenq_server.api import AioHTTPSessionManager

FLASK_BACKEND_URL = "http://localhost:5005"

class Summarizer:
    def __init__(self, chunk_size=1000):
        self.chunk_size = chunk_size

    def chunk_text(self, text):
        chunks = [text[i:i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
        total = len(chunks)
        if total > 30:
            indices = sorted(random.sample(range(total), 30))  # Unique, sorted indices
            chunks = [chunks[i] for i in indices]
        return chunks

    async def summarize_chunks(self, chunks, query):
        response = await self.generate(content=chunks, query=query)
        return response

    async def summarize_text(self, text, query):
        chunks = self.chunk_text(text)
        chunk_summaries = await self.summarize_chunks(chunks, query)
        return chunk_summaries

    async def generate(self, content, query):
        url = f"{FLASK_BACKEND_URL}/summarize"
        session = await AioHTTPSessionManager.get_session()
        async with session.post(url, json={"data": {"content": content}, "query": query}) as resp:
            if resp.status == 200:
                data = await resp.json()
                summary = data.get("output", "no response")
                return summary
            else:
                return f"Request failed with status {resp.status}"

    def format_summaries_to_json(self, summaries):
        return json.dumps(summaries, indent=4)
