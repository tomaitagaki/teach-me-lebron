import httpx
import json
from typing import AsyncGenerator
from config import get_settings
from logging_config import get_logger

logger = get_logger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API for LLM calls."""

    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.openrouter_base_url
        self.api_key = self.settings.openrouter_api_key
        self.model = self.settings.openrouter_model
        logger.info(f"OpenRouterService initialized with model: {self.model}")

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

        logger.debug(f"Starting streaming completion with {len(messages)} messages")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    # Check for HTTP errors
                    if response.status_code == 429:
                        logger.error(f"Rate limit exceeded (429) for OpenRouter API. Model: {self.model}")
                        raise httpx.HTTPStatusError(
                            "Rate limit exceeded. Please try again in a moment.",
                            request=response.request,
                            response=response
                        )
                    elif response.status_code == 401:
                        logger.error("Authentication failed (401) - Invalid API key")
                        raise httpx.HTTPStatusError(
                            "Invalid API key. Please check your OpenRouter credentials.",
                            request=response.request,
                            response=response
                        )
                    elif response.status_code >= 400:
                        logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                        response.raise_for_status()

                    response.raise_for_status()
                    logger.debug("Successfully connected to OpenRouter stream")

                    token_count = 0
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix

                            if data == "[DONE]":
                                logger.debug(f"Stream completed. Total tokens: {token_count}")
                                break

                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        token_count += 1
                                        yield delta["content"]
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse SSE chunk: {e}")
                                continue

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during streaming: {e.response.status_code} - {str(e)}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error during streaming: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during streaming: {str(e)}", exc_info=True)
            raise

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

        logger.debug(f"Requesting non-streaming completion with {len(messages)} messages")

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )

                if response.status_code == 429:
                    logger.error(f"Rate limit exceeded (429) for OpenRouter API. Model: {self.model}")
                    raise httpx.HTTPStatusError(
                        "Rate limit exceeded. Please try again in a moment.",
                        request=response.request,
                        response=response
                    )
                elif response.status_code == 401:
                    logger.error("Authentication failed (401) - Invalid API key")
                    raise httpx.HTTPStatusError(
                        "Invalid API key. Please check your OpenRouter credentials.",
                        request=response.request,
                        response=response
                    )
                elif response.status_code >= 400:
                    logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")

                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"Received completion: {len(content)} characters")
                return content

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {str(e)}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise
