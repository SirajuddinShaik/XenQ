import sys
import json
from typing import Union, AsyncIterator

if sys.version_info < (3, 9):
    from typing import AsyncIterator
else:
    from collections.abc import AsyncIterator
import os
from xenq_server.config import AGENT_URI

import numpy as np
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from lightrag.exceptions import (
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)

from xenq_server.api import AioHTTPSessionManager


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError, APITimeoutError)),
)
async def _vllm_model_if_cache(
    model,
    prompt,
    system_prompt=None,
    history_messages=[],
    md="",
    **kwargs,
) -> Union[str, AsyncIterator[str]]:
    stream = kwargs.get("stream", False)
    temperature = kwargs.get("temperature", 0.7)

    # Build the prompt from history + system message
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})
    full_prompt = "\n".join([m["content"] for m in messages])
    print("full-prompt: ", full_prompt)
    print(md)
    if not stream:
        payload = {
            "prompt": full_prompt,
            "temperature": temperature,
            "mode": md,
        }
        response,status = await AioHTTPSessionManager.non_stream_response(payload)
        print("response:",response)
        return response

    else:
        session = await AioHTTPSessionManager.get_session()
        url = f"{AGENT_URI}/stream"
        headers = {"Accept": "text/event-stream"}
        payload = {
            "prompt": full_prompt,
            "temperature": temperature,
        }

        try:
            async with session.post(url, json=payload, headers=headers) as resp:
                async def stream():
                    async for line in resp.content:
                        try:
                            line = line.decode("utf-8").strip()
                            if line.startswith("data:"):
                                token_data = json.loads(line[5:].strip())
                                yield token_data.get("token", "")
                        except Exception:
                            continue

                return stream()
        except Exception as e:
            print(f"vLLM request failed: {e}")
            return f"vLLM request failed: {e}"


async def vllm_model_complete(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> Union[str, AsyncIterator[str]]:
    keyword_extraction = kwargs.pop("keyword_extraction", None)
    if keyword_extraction:
        kwargs["format"] = "json"
    model_name = kwargs["hashing_kv"].global_config["llm_model_name"]
    return await _vllm_model_if_cache(
        model_name,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        **kwargs,
    )


# Optional embedding function (placeholder for compatibility)
async def vllm_embed(texts: list[str], embed_model: str = "None", **kwargs) -> np.ndarray:
    session = await AioHTTPSessionManager.get_session()
    url = f"{AGENT_URI}/embed"
    payload = {"texts": texts}

    try:
        async with session.post(url, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return np.array(data[0].get("embeddings",[]))
            else:
                raise RuntimeError(f"Embed request failed with status {resp.status}")
    except Exception as e:
        raise RuntimeError(f"Failed to get embeddings from server: {str(e)}")
