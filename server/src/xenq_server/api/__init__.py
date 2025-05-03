# __init__.py for server/src/xenq_server/api/__init__.py
# session_manager.py
import aiohttp

from xenq_server.config import AGENT_URI


class AioHTTPSessionManager:
    _session: aiohttp.ClientSession = None

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None or cls._session.closed:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        if cls._session and not cls._session.closed:
            await cls._session.close()

    @classmethod
    async def non_stream_response(cls, payload: dict) -> str:
        url = f"{AGENT_URI}/prompt"
        session = await cls.get_session()
        
        try:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    output_text = data.get("output") or "⚠️ No output received from server."
                    return output_text, True
                else:
                    return f"❌ Request failed with status {resp.status}", False
        except Exception as e:
            return f"🚨 Request failed: {type(e).__name__} - {str(e)}", True