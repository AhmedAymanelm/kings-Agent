"""
ai/llm.py — Unified LLM client
Supports: OpenAI, Anthropic, Google Gemini
"""
from __future__ import annotations
from typing import Optional, List, Dict
from backend.config import settings


async def chat_complete(messages: List[Dict], max_tokens: Optional[int] = None) -> str:
    """
    Send messages to the configured LLM and return the reply as a string.
    """
    provider = settings.AI_PROVIDER.lower()

    if provider == "openai":
        return await _openai(messages, max_tokens)
    elif provider == "anthropic":
        return await _anthropic(messages, max_tokens)
    elif provider in ("gemini", "google"):
        return await _gemini(messages, max_tokens)
    else:
        return "[AI provider not configured]"


async def _openai(messages: List[Dict], max_tokens: Optional[int]) -> str:
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        resp = await client.chat.completions.create(
            model=settings.AI_MODEL or "gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens or settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE,
        )
        return resp.choices[0].message.content or ""
    except Exception as e:
        print(f"[llm/openai] Error: {e}")
        return ""


async def _anthropic(messages: List[Dict], max_tokens: Optional[int]) -> str:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_msgs = [m for m in messages if m["role"] != "system"]

        resp = await client.messages.create(
            model=settings.AI_MODEL or "claude-3-haiku-20240307",
            system=system,
            messages=user_msgs,
            max_tokens=max_tokens or settings.AI_MAX_TOKENS,
        )
        return resp.content[0].text if resp.content else ""
    except Exception as e:
        print(f"[llm/anthropic] Error: {e}")
        return ""


async def _gemini(messages: List[Dict], max_tokens: Optional[int]) -> str:
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.AI_MODEL or "gemini-1.5-flash")

        prompt = "\n".join(
            f"{'[System]' if m['role'] == 'system' else m['role'].title()}: {m['content']}"
            for m in messages
        )
        resp = await model.generate_content_async(prompt)
        return resp.text or ""
    except Exception as e:
        print(f"[llm/gemini] Error: {e}")
        return ""
