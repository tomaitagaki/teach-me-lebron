import httpx
import json
from typing import AsyncGenerator
from config import get_settings


class OpenRouterService:
    """Service for interacting with OpenRouter API for LLM calls."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.openrouter_base_url
        self.api_key = self.settings.openrouter_api_key
        self.model = self.settings.openrouter_model

    async def stream_chat_completion(
        self,
        messages: list[dict],
        system_prompt: str = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion from OpenRouter.

        Yields tokens as they arrive for real-time streaming UX.
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/teach-me-lebron",
            "X-Title": "Teach Me LeBron - Sports Lore Chatbot",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix

                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue

    async def get_chat_completion(
        self,
        messages: list[dict],
        system_prompt: str = None
    ) -> str:
        """
        Get non-streaming chat completion from OpenRouter.

        Returns the complete response.
        """
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/teach-me-lebron",
            "X-Title": "Teach Me LeBron - Sports Lore Chatbot",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
