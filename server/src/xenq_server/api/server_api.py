# server_api.py for server/src/xenq_server/api/server_api.py

import chainlit as cl

from xenq_server.utils.chainlit_setup import commands, widgets
import aiohttp
import json
from xenq_server.components.query.history_store import HistoryStore
from xenq_server.api import AioHTTPSessionManager

from xenq_server.utils.sys_p import p1, p2

FLASK_BACKEND_URL = "http://localhost:5005"
from typing import Optional

# @cl.password_auth_callback
# def auth_callback(username: str, password: str):
#     # Fetch the user matching username from your database
#     # and compare the hashed password with the value stored in the database
#     if (username, password) == ("admin", "admin"):
#         return cl.User(
#             identifier="admin", metadata={"role": "admin", "provider": "credentials"}
#         )
#     else:
#         return None

async def start(*args):
    await cl.ChatSettings(widgets).send()
    await cl.context.emitter.set_commands(commands)
    cl.user_session.set("history", HistoryStore())
    cl.user_session.set("temperature", 0.8)


async def on_message(message: cl.Message):
    hist: HistoryStore = cl.user_session.get("history", HistoryStore())
    temperature = cl.user_session.get("temperature")
    status = hist.append_content(role = "user", content = message.content)
    
    if not status:
        cl.Message(content = "The Message length is to Big 💪!")
        return
    prompt = hist.build_prompt()
    
    if message.command == "stream": # Stream response
        await stream_response({"prompt": p2, "command": message.command})

    else:  # Non-stream response
        await non_stream_response({"prompt": p2, "temperature": temperature})

async def update_settings(settings):
    cl.user_session.set("temperature",settings["Temperature"])
    print("on_settings_update", settings)



    
async def non_stream_response1(payload: dict):
    url = f"{FLASK_BACKEND_URL}/prompt"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                output_text = data.get("output", "no response")
                await cl.Message(content=output_text).send()  # Or use msg.update if not streaming
            else:
                await cl.Message(content=f"Request failed with status {resp.status}").send()

async def stream_response1(payload: dict):
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }
    url = f"{FLASK_BACKEND_URL}/stream"

    msg = cl.Message(content="")

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if decoded.startswith("data:"):
                    try:
                        data = json.loads(decoded[5:])
                        token = data["token"]
                        await msg.stream_token(token)
                    except Exception as e:
                        print("Streaming error:", e)
    await msg.update()



async def stream_response(payload: dict):
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }
    url = f"{FLASK_BACKEND_URL}/stream"

    msg = cl.Message(content="")

    session = await AioHTTPSessionManager.get_session()
    try:
        async with session.post(url, headers=headers, json=payload) as resp:
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if decoded.startswith("data:"):
                    try:
                        data = json.loads(decoded[5:])
                        
                        token = data["token"]
                        await msg.stream_token(token)
                    except Exception as e:
                        print("Streaming error:", e)
    except Exception as e:
        print("Request failed:", e)

    await msg.update()


async def non_stream_response(payload: dict):
    url = f"{FLASK_BACKEND_URL}/prompt"
    session = await AioHTTPSessionManager.get_session()
    
    try:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                output_text = data.get("output", "no response")
                await cl.Message(content=output_text).send()  # Or use msg.update if applicable
            else:
                await cl.Message(content=f"Request failed with status {resp.status}").send()
    except Exception as e:
        await cl.Message(content=f"Request failed: {str(e)}").send()


