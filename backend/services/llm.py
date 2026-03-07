from __future__ import annotations
import os
from typing import List, Dict, Optional
from openai import OpenAI
from ..config import get_settings

def _client() -> Optional[OpenAI]:
    settings = get_settings()
    provider = (settings.LLM_PROVIDER or "").lower()
    print(f"DEBUG: LLM_PROVIDER = {provider}")  # Debug info
    
    if provider in {"ollama", "lmstudio"}:
        base_url = os.getenv("LLM_BASE_URL") or ("http://127.0.0.1:11434/v1" if provider == "ollama" else "http://127.0.0.1:1234/v1")
        api_key  = os.getenv("LLM_API_KEY") or "nokey"
        print(f"DEBUG: Using {provider} at {base_url}")  # Debug info
        return OpenAI(base_url=base_url, api_key=api_key)
    
    if provider == "openai":
        key = settings.OPENAI_API_KEY
        print(f"DEBUG: OpenAI API Key exists: {bool(key)}")  # Debug info
        if not key:
            print("DEBUG: No OpenAI API key found!")  # Debug info
            return None
        print("DEBUG: Creating OpenAI client")  # Debug info
        return OpenAI(api_key=key)
    
    print(f"DEBUG: Unknown provider: {provider}")  # Debug info
    return None

def is_enabled() -> bool:
    return _client() is not None

def chat(messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> Optional[str]:
    client = _client()
    if client is None:
        return None
    
    # Use OpenAI model by default if provider is OpenAI
    settings = get_settings()
    provider = (settings.LLM_PROVIDER or "").lower()
    if provider == "openai":
        model = model or settings.OPENAI_MODEL or "gpt-4o-mini"
    else:
        model = model or os.getenv("LLM_MODEL") or "llama3.2:3b-instruct"
    
    print(f"DEBUG: Using model: {model}")  # Debug info
    params = dict(
        model=model,
        messages=messages,
        temperature=settings.LLM_TEMPERATURE,
        max_completion_tokens=settings.LLM_MAX_TOKENS,
    )
    params.update(kwargs)
    
    try:
        resp = client.chat.completions.create(**params)
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        print(f"LLM Error: {e}")  # Debug info
        return None
