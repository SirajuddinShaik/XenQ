import aiohttp
import chainlit as cl

SECRET_CODE = "your_secret_code_here"
class ClientConnect:
    _session: aiohttp.ClientSession = None
    def __init__(self, client_uri: str):
        self.client_uri = client_uri

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession:
        if cls._session is None or cls._session.closed:
            cls._session = aiohttp.ClientSession()
        return cls._session

    @classmethod
    async def close_session(cls):
        if cls._session and not cls._session.closed:
            await cls._session.close()

    async def non_stream_response(self,method: str, main: str, sub: str, **payload) -> dict:
        url = f"{self.client_uri}/{main}/{sub}"  # Build URL dynamically
        session = await self.get_session()

        try:
            if method.lower() == "post":
                request_coro = session.post(url, json=payload)
            elif method.lower() == "get":
                request_coro = session.get(url, params=payload)
            else:
                raise ValueError(f"Unsupported method: {method}")

            async with request_coro as resp:
                resp.raise_for_status()
                response = await resp.json()
                return response
        except aiohttp.ClientResponseError as e:
            return {"error":f"HTTP Error {e.status}: {e.message}"}
        except aiohttp.ClientConnectionError as e:
            return {"error":f"Connection Error: {str(e)}"}
        except Exception as e:
            return {"error":f"Unexpected Error: {str(e)}"}

    async def stream_command_output(self, method: str, main: str, sub: str, **payload):
        msg = cl.Message("")
        url = f"{self.client_uri}/{main}/{sub}"
        session = await self.get_session()

        try:
            if method.lower() == "post":
                request_context = session.post(url, json=payload)
            elif method.lower() == "get":
                request_context = session.get(url, params=payload)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            async with request_context as resp:
                resp.raise_for_status()

                async for line_bytes in resp.content:
                    decoded_line = line_bytes.decode('utf-8').strip()
                    if decoded_line:
                        await msg.stream_token("\n>"+decoded_line)
                        yield decoded_line

        except aiohttp.ClientError as e:
            yield f"Error: {str(e)}"

    async def verify(self):
        res = await self.non_stream_response("get", "api", "verify")
        if SECRET_CODE == res.get("code","none"):
            return True
        else:
            return False

    async def run_cmd(self, **payload):
        async for line in self.stream_command_output(main="system_manager",sub = "run_command", method="post",stream =True, **payload):
            pass
    