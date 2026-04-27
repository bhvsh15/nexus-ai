import ollama
from .config import settings
from typing import Optional

client = ollama.Client(host=settings.ollama_base_url)

def chat(model: str, messages: list[dict], temperature: Optional[float] = None):
    options = {"temperature": temperature} if temperature is not None else None
    response = client.chat(model=model, messages=messages, options=options)
    return response

def get_embeddings(model: str, prompt: str):
    response = client.embeddings(model=model, prompt=prompt)
    return response

def list_models():
    response = client.list()
    return response

