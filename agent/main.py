from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import os
import json
from uuid import uuid4
from vllm import AsyncEngineArgs, AsyncLLMEngine, SamplingParams
import torch
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.models.auto.modeling_auto import  AutoModelForSeq2SeqLM
from functools import lru_cache


app = FastAPI()
engine = None
chat_histories = {}

# Initialize vLLM engine
async def out(engine):
    params = SamplingParams(
        top_k=1,
        temperature=0.8,
        max_tokens=1000,
        stop=["<|eot_id|>"],
    )
    prompt = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\nYou are a professional PostgreSQL expert who generates optimized, correct SQL queries from natural language questions based on the schema provided. \nThink step by step to break down the user's request, reason about how to join and filter relevant tables, and form an efficient SQL query. \nUse Common Table Expressions (CTEs) when needed for readability and performance. Always use explicit JOINs.\n\nSchema Format:\n- TableName (Row count)\n  - column_name: data_type [PK|FK → referenced_table.column], [NOT NULL]\n\nInstructions:\n- Think aloud step by step and genertate.\n- Explain any assumptions briefly.\n- At the end, return the one final SQL query inside a single ```sql code block.\n- Do not include markdown outside the code block.\n- If the query includes unknown terms or entities not found in the schema, respond only with:\n\n```sql\nSELECT 'Unable to generate query: entity not found in schema.' AS message;\n```\n\n<|eot_id|><|start_header_id|>user<|end_header_id|>\n## Schema\n### departments (9 rows)\n- dept_no: character (PK), NOT NULL\n- dept_name: character varying, NOT NULL\n\n### dept_emp (331041 rows)\n- emp_no: integer (PK) (FK → employees.emp_no), NOT NULL\n- from_date: date, NOT NULL\n- to_date: date, NOT NULL\n- dept_no: character (PK) (FK → departments.dept_no), NOT NULL\n\n### employees (299509 rows)\n- emp_no: integer (PK), NOT NULL\n- birth_date: date, NOT NULL\n- gender: USER-DEFINED\n- hire_date: date, NOT NULL\n- first_name: character varying, NOT NULL\n- last_name: character varying, NOT NULL\n\n### dept_manager (24 rows)\n- emp_no: integer (PK) (FK → employees.emp_no), NOT NULL\n- from_date: date, NOT NULL\n- to_date: date, NOT NULL\n- dept_no: character (PK) (FK → departments.dept_no), NOT NULL\n\n### salaries (2839079 rows)\n- emp_no: integer (PK) (FK → employees.emp_no), NOT NULL\n- salary: integer, NOT NULL\n- from_date: date (PK), NOT NULL\n- to_date: date, NOT NULL\n\n### titles (442547 rows)\n- emp_no: integer (PK) (FK → employees.emp_no), NOT NULL\n- from_date: date (PK), NOT NULL\n- to_date: date\n- title: character varying (PK), NOT NULL\n\n\n## Query Request\nWhich departments have more than 70% of employees of one gender (current employees only)? Show dept_name, gender, and percentage.\n<|eot_id|><|start_header_id|>assistant<|end_header_id|>"
    output = await engine.generate(prompt, params, "user_id")
    # print(output[0].outputs[0].text)

@lru_cache(maxsize=1)
def get_engine():
    return AsyncLLMEngine.from_engine_args(
        AsyncEngineArgs(
            model="meta-llama/Llama-3.1-8B-Instruct",
            trust_remote_code=True,
            max_model_len=2000,
            max_num_seqs = 1,
            max_num_batched_tokens=2048,
            quantization="fp8",
            gpu_memory_utilization=0.44,
            
        )
    )

@lru_cache(maxsize=1)
def get_summarizer():
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    summarizer = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")

    return summarizer, tokenizer


async def generate_token_stream(prompt: str, user_id: str):
    engine_instance = get_engine()
    params = SamplingParams(
        top_p=0.9,
        temperature=0.8,
        max_tokens=2000,
        stop=["<|eot_id|>", ":::"],
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
    # print(prompt)
    user_id = body.get("user_id", str(uuid4()))
    if not prompt:
        return {"error": "Missing prompt"}

    async def event_stream():
        async for token in generate_token_stream(prompt, user_id):
            yield token

    return StreamingResponse(event_stream(), media_type="text/event-stream")
    
async def generate_output(prompt: str, user_id: str, temperature):
    engine_instance = get_engine()
    params = SamplingParams(
        top_p=0.9,
        temperature=temperature,
        max_tokens=2000,
        stop=["<|eot_id|>"],
        include_stop_str_in_output = True,
    )

    gen_text = ""

    async for output in engine_instance.generate(prompt, params, user_id):
        gen_text = output.outputs[0].text  # Accumulate chunks

    return gen_text



async def generate_fake_tokens(prompt: str):
    fake_response = [prompt]
    for token in fake_response:
        await asyncio.sleep(0.3)  # simulate delay between tokens
        yield f"data: {json.dumps({'token': token})}\n\n"



@app.post("/prompt")
async def gen_from_prompt(request: Request):
    # prompt = request.query_params.get("prompt","str")
    body = await request.json()
    prompt = body.get("prompt", "")
    # print(prompt)
    temperature = request.query_params.get("temperature",0.7)
    # print(temperature)
    output = await generate_output(prompt, "params",temperature=float(temperature))
    
    return {"output":output, "status":200}


summarize_prompt = (
    "{content}\n\n"
    "Above is some content.\n"
    "Your task: If this content contains information relevant to the query \"{query}\", "
    "summarize only the relevant parts. "
    "If it is not relevant at all, respond only with this exact token: </s>"
)


# @app.post("/summarize")
async def gen_summary1(request: Request):
    # prompt = request.query_params.get("prompt","str")
    print("request")
    body = await request.json()
    content = body.get("content", [])
    content = content["content"]
    query = body.get("query", "How to Become an NLP Scientist")
    content = [summarize_prompt.format(query=query, content=data ) for data in content]
    summarizer, tokenizer = get_summarizer()
    inputs = tokenizer(content, return_tensors="pt", padding=True, truncation=True, max_length=1024)
    # Move to GPU if available
    input_ids = inputs["input_ids"].to(summarizer.device)
    attention_mask = inputs["attention_mask"].to(summarizer.device)
    summaries_ids = summarizer.generate(input_ids=input_ids, attention_mask=attention_mask, 
                               max_length=130, min_length=0, do_sample=False)

    # Decode summaries
    summaries = tokenizer.batch_decode(summaries_ids, skip_special_tokens=True)
    return {"output":[summary for summary in summaries], "status":200}

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
    del input_ids
    del attention_mask
    return {"output": summaries, "status": 200}


engine = get_engine()
get_summarizer()
