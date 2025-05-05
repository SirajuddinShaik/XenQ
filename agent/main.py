from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from xenq_agent.components.llm import generate_summary, generate_token_stream, generate_output, compute_embedding
from uuid import uuid4

app = FastAPI()

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

# FastAPI endpoint
@app.post("/summarize")
async def gen_summary(request: Request):
    body = await request.json()
    data = body.get("data", [])
    query = body.get("query", "How to Become an AI engineer")
    content = [item["content"] for item in data] if isinstance(data, list) else []
    summaries = await generate_summary(content, query)

    return {"output": summaries, "status": 200}

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