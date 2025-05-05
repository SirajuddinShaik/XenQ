# llama_inference.py for agent/src/xenq_agent/components/llm/llama_inference.py


import random
import torch
import json
from xenq_agent.components.llm.model_loader import get_embedding_model, get_engine, get_summarizer
from vllm import SamplingParams


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



# async def generate_fake_tokens(prompt: str, user_id, temp):
#     fake_response = temp_output.split()
#     for token in fake_response:
#         await asyncio.sleep(0.1)  # simulate delay between tokens
#         yield f"data: {json.dumps({'token': ' '+token})}\n\n"


def compute_embedding(texts):
    tokenizer, model = get_embedding_model()
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        model_output = model(**inputs)
    embeddings = model_output.last_hidden_state.mean(dim=1)
    return embeddings.numpy().tolist()


# Core summarization function
async def generate_summary(data_list, query):
    summarizer, tokenizer = get_summarizer()
    
    # Prepare content
    content = [summarize_prompt.format(query=query, content=data) for data in data_list]
    
    # Tokenize
    inputs = tokenizer(content, return_tensors="pt", padding=True, truncation=True, max_length=1024)
    input_ids = inputs["input_ids"].to(summarizer.device)
    attention_mask = inputs["attention_mask"].to(summarizer.device)

    batch_size = 4
    num_batches = (len(content) + batch_size - 1) // batch_size
    summaries = []

    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, len(content))

        batch_input_ids = input_ids[start_idx:end_idx]
        batch_attention_mask = attention_mask[start_idx:end_idx]

        summaries_ids = summarizer.generate(
            input_ids=batch_input_ids,
            attention_mask=batch_attention_mask,
            max_length=130,
            min_length=0,
            do_sample=False
        )

        batch_summaries = tokenizer.batch_decode(summaries_ids, skip_special_tokens=True)
        summaries.extend(batch_summaries)

    # Remove summaries containing the query itself
    summaries = [chunk for chunk in summaries if query not in chunk]

    # Limit to 10 random summaries
    total = len(summaries)
    if total > 10:
        indices = sorted(random.sample(range(total), 10))
        summaries = [summaries[i] for i in indices]

    # Cleanup
    del input_ids
    del attention_mask

    return summaries

summarize_prompt = (
    "{content}\n\n"
    "Above is some content.\n"
    "Your task: If this content contains information relevant to the query \"{query}\", "
    "summarize only the relevant parts. "
    "If it is not relevant at all, respond only with this exact token: </s>"
)