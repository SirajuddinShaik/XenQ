# model_loader.py for agent/src/xenq_agent/components/llm/model_loader.py
from vllm import AsyncEngineArgs, AsyncLLMEngine
import torch
from transformers.models.auto.tokenization_auto import AutoTokenizer
from transformers.models.auto.modeling_auto import  AutoModelForSeq2SeqLM, AutoModel
from functools import lru_cache

EMBED_MODEL = "sentence-transformers/all-mpnet-base-v2"

@lru_cache(maxsize=1)
def get_engine():
    return AsyncLLMEngine.from_engine_args(
        AsyncEngineArgs(
            model="meta-llama/Llama-3.1-8B-Instruct",
            trust_remote_code=True,
            max_model_len=16000,
            max_num_seqs = 1,
            quantization="fp8",
            gpu_memory_utilization=0.6,
            
        )
    )

@lru_cache(maxsize=1)
def get_summarizer():
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    summarizer = AutoModelForSeq2SeqLM.from_pretrained(model_name).to("cuda" if torch.cuda.is_available() else "cpu")

    return summarizer, tokenizer



@lru_cache(maxsize=1)
def get_embedding_model():
    tokenizer = AutoTokenizer.from_pretrained(EMBED_MODEL)
    model = AutoModel.from_pretrained(EMBED_MODEL)
    return tokenizer, model


get_engine()
# get_summarizer()
get_embedding_model()