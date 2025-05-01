# server_api.py for server/src/xenq_server/api/server_api.py

import chainlit as cl

from xenq_server.components import tool_invoker_json
from xenq_server.utils.chainlit_setup import commands, widgets
import aiohttp
import json
from xenq_server.components.query.history_store import HistoryStore
from xenq_server.api import AioHTTPSessionManager
from xenq_server.components.tool_invoker_json import ToolInvoker

import os

from xenq_server.config import AGENT_URI

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
    cl.user_session.set("psql_uri", "")
    tool_invoker = ToolInvoker()
    await tool_invoker.setup("/teamspace/studios/this_studio/dickens")
    tool_invoker.update_sql_uri("postgresql://admin:admin123@localhost:5432/college") 
    cl.user_session.set("tool_invoker", tool_invoker)


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

    url = f"{AGENT_URI}/stream"
    response = ""
    hide = False
    hidden = ""
    visible = ""
    token=""

    tag_buffer = ""
    buffer_limit = 20  # Look back over the last N characters to detect tag boundaries

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
                        await msg.stream_token(token)

                    except Exception as e:
                        print("Streaming error:", e)
    except Exception as e:
        print("Request failed:", e)

    return {
        "token": token,
        "response": response,
        "msg": msg
    }

async def stream_response1(payload: dict, msg=None):
    headers = {
        "Accept": "text/event-stream",
        "Content-Type": "application/json"
    }

    if msg is None:
        msg = cl.Message(content="")
        await msg.send()

    url = f"{AGENT_URI}/stream"
    response = ""
    hide = False
    hidden=""
    open=""

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

                        if "<internal>" in response[-10:]:
                            hide = True
                        if "</internal>" in response[-10:]:
                            hide = False
                        
                        if hide:
                            hidden+=token
                        else:
                            open+=token
                        await msg.stream_token(token)


                    except Exception as e:
                        print("Streaming error:", e)
    except Exception as e:
        print("Request failed:", e)
    print("hidden: ", hidden)
    print("open: ", open)
    return {
        "token": token,
        "response": response,
        "msg": msg
    }

# -------------------------------
# MAIN on_message HANDLER
# -------------------------------

async def on_message(message: cl.Message):
    hist: HistoryStore = cl.user_session.get("history", HistoryStore())
    temperature = cl.user_session.get("temperature", 0.5)

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
        while response.get("token") != "<|eot_id|>" and response.get("response", False) and retry_count < max_retries:
            retry_count += 1
            # Check if response ends with '</tool>​' to decide on tool use
            if "</tool>" in  response.get("response", "")[-10:]:
                tool_invoker = cl.user_session.get("tool_invoker", ToolInvoker())
                output, llm_responses = await tool_invoker.pipeline(response.get("response"))
                for llm_response in llm_responses:
                    hist.append_content("light_rag", llm_response)
                if output:
                    print("output: ", output)
                    hist.append_content("backend", output)
                    prompt = hist.build_prompt()
                    # Reset internal reasoning before the next call
                    response = await stream_response({
                        "prompt": prompt,
                        "command": message.command
                    }, response.get("msg"))
                else:
                    await response.get("msg").update() 
                    break
            else:
                await response.get("msg").update() 
                break  # No tool use trigger, break the loop
                            

    else:
        response = await non_stream_response({
            "prompt": prompt,
            "temperature": temperature
        })

async def non_stream_response(payload: dict):
    url = f"{AGENT_URI}/prompt"
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


