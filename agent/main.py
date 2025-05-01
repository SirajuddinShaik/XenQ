from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import os
import json
from uuid import uuid4
import random
from torch.cuda import temperature
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams
import torch
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.models.auto.modeling_auto import  AutoModelForSeq2SeqLM, AutoModel
from functools import lru_cache

temp_output = """Let me think this through for you…

\n<internal>
### ReAct Trace:
Thought: First, I need to get the current and weekend weather in Paris.
Action:
Observation: Weather in Paris this weekend: Saturday - 18°C, partly cloudy; Sunday - 21°C, sunny.

Thought: Now I’ll check for top-rated local events or festivals in Paris this weekend.
Action:
```json
{
  "function_calls": [
    {
      "name": "search_web",
      "parameters": {
        "query": "top events or festivals in Paris this weekend"
      }
    }
  ]
}
```
</internal>

You're in for a lovely weekend in Paris! 🌤️
Action:
```json
{
  "function_calls": [
    {
      "name": "search_web",
      "parameters": {
        "query": "top events or festivals in Paris this weekend"
      }
    }
  ]
}
```
- **Saturday**: 18°C and partly cloudy — great for exploring outdoor markets or walking tours.
- **Sunday**: 21°C and sunny — perfect weather for parks or riverside picnics.

🎉 **Top Events This Weekend**:
- **🎶 Fête de la Musique** at Parc de la Villette: Live music, outdoor vibes, and tasty food trucks.
- **🌮 Paris Food Market** near Bastille (Sunday): Street food and global flavors.
- **🎨 Montmartre Spring Art Walk**: Explore creative works from local artists in a charming neighborhood.

Pack light layers, and enjoy your Parisian adventure! 🇫🇷✨
"""
app = FastAPI()
engine = None
chat_histories = {}


@lru_cache(maxsize=1)
def get_engine():
    return AsyncLLMEngine.from_engine_args(
        AsyncEngineArgs(
            model="meta-llama/Llama-3.1-8B-Instruct",
            trust_remote_code=True,
            max_model_len=8000,
            max_num_seqs = 1,
            quantization="fp8",
            gpu_memory_utilization=0.47,
            
        )
    )

@lru_cache(maxsize=1)
def get_summarizer():
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    summarizer = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")

    return summarizer, tokenizer


async def generate_token_stream(prompt: str, user_id: str, temperature):
    engine_instance = get_engine()
    params = SamplingParams(
        top_p=0.9,
        temperature=temperature,
        max_tokens=2000,
        stop=["<|eot_id|>", ":::", "</tool>"],
        include_stop_str_in_output = True,
    )
    prev_text = ""
    async for output in engine_instance.generate(prompt, params, user_id):
        new_text = output.outputs[0].text
        delta = new_text[len(prev_text):]
        prev_text = new_text
        yield f"data: {json.dumps({'token': delta})}\n\n"


# FastAPI route with async SSE stream
@app.post("/stream")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    temperature  =body.get("temperature", float(0.5))
    # print(prompt)
    user_id = body.get("user_id", str(uuid4()))
    if not prompt:
        return {"error": "Missing prompt"}

    async def event_stream():
        async for token in generate_token_stream(prompt, user_id, temperature):
            yield token

    return StreamingResponse(event_stream(), media_type="text/event-stream")
    
async def generate_output(prompt: str, user_id: str, temperature, mode="None"):
    engine_instance = get_engine()
    params = SamplingParams(
        top_p=0.9,
        temperature=temperature,
        max_tokens=2000,
        stop=["<|eot_id|>", ":::", "</tool>", "}" if mode == "extract" else "</tool>"],
        include_stop_str_in_output = True,
    )

    gen_text = ""

    async for output in engine_instance.generate(prompt, params, user_id):
        gen_text = output.outputs[0].text  # Accumulate chunks

    return gen_text



async def generate_fake_tokens(prompt: str, user_id, temp):
    fake_response = temp_output.split()
    for token in fake_response:
        await asyncio.sleep(0.1)  # simulate delay between tokens
        yield f"data: {json.dumps({'token': ' '+token})}\n\n"



@app.post("/prompt")
async def gen_from_prompt(request: Request):
    # prompt = request.query_params.get("prompt","str")
    body = await request.json()
    prompt = body.get("prompt", "")
    mode = body.get("mode", "None")
    temperature = request.query_params.get("temperature",0.7)
    # print(temperature)
    
    output = await generate_output(prompt, str(uuid4()),temperature=float(temperature), mode=mode)
    
    return {"output":output, "status":200}


summarize_prompt = (
    "{content}\n\n"
    "Above is some content.\n"
    "Your task: If this content contains information relevant to the query \"{query}\", "
    "summarize only the relevant parts. "
    "If it is not relevant at all, respond only with this exact token: </s>"
)


@app.post("/summarize")
async def gen_summary(request: Request):
    body = await request.json()
    data = body.get("data", [])
    content = data["content"]
    query = body.get("query", "How to Become an AI engineer")
    summarizer, tokenizer = get_summarizer()
    # Prepare content for summarization
    content = [summarize_prompt.format(query=query, content=data) for data in content]
    
    # Tokenize inputs
    inputs = tokenizer(content, return_tensors="pt", padding=True, truncation=True, max_length=1024)

    # Move to GPU if available
    input_ids = inputs["input_ids"].to(summarizer.device)
    attention_mask = inputs["attention_mask"].to(summarizer.device)
    
    # Add batching (size 4)
    batch_size = 4
    num_batches = (len(content) + batch_size - 1) // batch_size  # Ceiling division to get number of batches
    print(num_batches, len(content))
    summaries = []
    
    # Process in batches
    for i in range(num_batches):
        # Create batch slice
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(content))
        
        print((start_idx, end_idx))
        # Get the batch of inputs
        batch_input_ids = input_ids[start_idx:end_idx]
        batch_attention_mask = attention_mask[start_idx:end_idx]
        # Generate summaries
        summaries_ids = summarizer.generate(
            input_ids=batch_input_ids,
            attention_mask=batch_attention_mask,
            max_length=130,
            min_length=0,
            do_sample=False
        )
        
        # Decode summaries
        batch_summaries = tokenizer.batch_decode(summaries_ids, skip_special_tokens=True)
        summaries.extend(batch_summaries)
    summaries = [chunk for chunk in summaries if query not in chunk]
    # joined_summary = summarize_prompt.format(query=query, content=" ".join(summaries))
    # inputs = tokenizer([joined_summary], return_tensors="pt", padding=True, truncation=True, max_length=1024)
    # summaries_ids = summarizer.generate(
    #         input_ids=batch_input_ids,
    #         attention_mask=batch_attention_mask,
    #         max_length=1000,
    #         min_length=100,
    #         do_sample=False
    #     )
    # print(summaries_ids)
    # summary = tokenizer.batch_decode(summaries_ids, skip_special_tokens=True)
    total = len(summaries)
    if total > 10:
        indices = sorted(random.sample(range(total), min(10,total)))
        summaries = [summaries[i] for i in indices]
    del input_ids
    del attention_mask
    return {"output": summaries, "status": 200}

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"

@lru_cache(maxsize=1)
def get_embedding_model():
    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    model = AutoModel.from_pretrained(EMBED_MODEL)
    return tokenizer, model

def compute_embedding(texts):
    tokenizer, model = get_embedding_model()
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**inputs)
    embeddings = model_output.last_hidden_state.mean(dim=1)
    return embeddings.numpy().tolist()

@app.post("/embed")
async def embed_route(request: Request):
    body = await request.json()
    texts = body.get("texts", [])
    if not texts:
        print("NO tests")
        return {"error": "Missing texts"}, 400
    try:
        embeddings = compute_embedding(texts)
        return {"embeddings": embeddings}, 200
    except Exception as e:
        print(e)
        return {"error": str(e)}, 500

# engine = get_engine()
# get_summarizer()
get_embedding_model()