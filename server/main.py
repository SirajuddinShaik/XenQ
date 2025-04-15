# main.py for server/main.py
import chainlit as cl
from xenq_server.api.server_api import on_message, start, update_settings


@cl.on_chat_start(start)

@cl.on_message(on_message)

@cl.on_settings_update
async def on_settings_update(settings):
    await update_settings(settings)