# server_api.py for server/src/xenq_server/api/server_api.py

import chainlit as cl

from xenq_server.components import tool_invoker_json
from xenq_server.utils.chainlit_setup import commands, widgets
import aiohttp
import json
from xenq_server.components.query.history_store import HistoryStore
from xenq_server.api import AioHTTPSessionManager
from xenq_server.components.tool_invoker_json import ToolInvoker

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

tool_invoker = ToolInvoker()

async def start(*args):
    await cl.ChatSettings(widgets).send()
    await cl.context.emitter.set_commands(commands)
    cl.user_session.set("history", HistoryStore())
    cl.user_session.set("temperature", 0.8)


async def update_settings(settings):
    cl.user_session.set("temperature",settings["Temperature"])
    print("on_settings_update", settings)



async def stream_response(payload: dict, msg=None):
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }

    if msg is None:
        msg = cl.Message(content="")
        await msg.send()

    url = f"{FLASK_BACKEND_URL}/stream"
    hist: HistoryStore = cl.user_session.get("history", HistoryStore())
    response = ""
    internal_reasoning = ""
    hide = False

    session = await AioHTTPSessionManager.get_session()

    try:
        async with session.post(url, headers=headers, json=payload) as resp:
            async for line in resp.content:
                decoded = line.decode("utf-8").strip()
                if decoded.startswith("data:"):
                    try:
                        data = json.loads(decoded[5:])
                        token = data.get("token", "")
                        response += token

                        if response.endswith("::internal"):
                            hide = True
                        await msg.stream_token(token)
                        
                        if hide:
                            internal_reasoning += token
                        if response.endswith(":::"):  # Tool invocation
                            hist.append_content("assistant", response)
                            hist.append_reasoning(internal_reasoning)
                            await msg.update()
                            return {
                                "token": token,
                                "internal_reasoning": internal_reasoning,
                                "response": response,
                                "msg": msg
                            }

                        if token == "<|eot_id|>":  # End of response
                            await msg.update()
                            hist.add_reasoning(response)
                            return {
                                "token": token,
                                "response": response
                            }


                    except Exception as e:
                        print("Streaming error:", e)
    except Exception as e:
        print("Request failed:", e)

    await msg.update()
    return {
        "token": "error",
        "response": response,
        "internal_reasoning": internal_reasoning,
        "msg": msg
    }

# -------------------------------
# MAIN on_message HANDLER
# -------------------------------

async def on_message(message: cl.Message):
    hist: HistoryStore = cl.user_session.get("history", HistoryStore())
    temperature = cl.user_session.get("temperature", 0.7)
    cl.user_session.set("history", hist)

    status = hist.append_content(role="user", content=message.content)
    if not status:
        await cl.Message(content="The message length is too big 💪!").send()
        return

    prompt = hist.build_prompt()
    print(prompt)

    if message.command != "stream":
        response = await stream_response({"prompt": prompt, "command": message.command})
        retry_count = 0
        max_retries = 5  # Avoid infinite loops
        hist.append_content("assistant", response.get("response", ""))
        
        while response and response.get("internal_reasoning", "") and retry_count < max_retries:
            retry_count += 1
            # Check if response ends with ':::' to decide on tool use
            if response.get("internal_reasoning", "").endswith(":::"):
                output = await tool_invoker.pipeline(response["internal_reasoning"])
                hist.append_content("backend", output)
                prompt = hist.build_prompt()
                print(prompt)
                # Reset internal reasoning before the next call
                response = await stream_response({
                    "prompt": prompt,
                    "command": message.command
                }, response.get("msg"))

            else:
                break  # No tool use trigger, break the loop

    else:
        response = await non_stream_response({
            "prompt": prompt,
            "temperature": temperature
        })

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


